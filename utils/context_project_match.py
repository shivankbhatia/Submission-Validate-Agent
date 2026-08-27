import json
import os
import requests
import logging

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = "llama3.2:3b"

logger = logging.getLogger(__name__)

# ------------------------------------
# HARDWARE DETECTION (CPU + GPU)
# ------------------------------------

def _detect_cpu_threads() -> int:
    """Returns the number of logical CPU cores available."""
    cores = os.cpu_count() or 4
    logger.info(f"[HW] Detected {cores} CPU threads")
    return cores


def _detect_gpu_layers() -> int:
    """
    Queries the Ollama runtime for GPU info.
    Returns the recommended num_gpu layers:
    - 35 (full offload) when a GPU is detected
    - 0  when no GPU is available (CPU-only mode)
    """
    try:
        resp = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        # Ollama exposes GPU info via /api/ps (running models)
        ps_resp = requests.get(f"{OLLAMA_BASE}/api/ps", timeout=3)
        if ps_resp.status_code == 200:
            ps_data = ps_resp.json()
            for model_entry in ps_data.get("models", []):
                # If any layer is GPU-offloaded Ollama reports size_vram > 0
                if model_entry.get("size_vram", 0) > 0:
                    logger.info("[HW] GPU detected via Ollama – enabling full GPU offload (num_gpu=35)")
                    return 35
        logger.info("[HW] No GPU detected – running CPU-only (num_gpu=0)")
        return 0
    except Exception:
        logger.info("[HW] GPU detection failed – defaulting to CPU-only")
        return 0


# Cache hardware profile at import time (avoid re-querying every call)
_HW_THREADS: int = _detect_cpu_threads()
# GPU detection is deferred to first call to avoid slowing startup on cold paths
_HW_GPU_LAYERS: int | None = None


def _get_gpu_layers() -> int:
    global _HW_GPU_LAYERS
    if _HW_GPU_LAYERS is None:
        _HW_GPU_LAYERS = _detect_gpu_layers()
    return _HW_GPU_LAYERS



def run_llama(prompt, temperature=0.1):
    """
    Runs a prompt on the Ollama Llama model.
    Automatically adapts to available hardware:
    - Uses all CPU cores (num_thread = cpu_count)
    - Enables GPU offload when a GPU is detected (num_gpu = 35)
    """
    num_gpu = _get_gpu_layers()
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": temperature,
            "num_predict": 100,
            "num_ctx": 1024,
            "num_thread": _HW_THREADS,
            "num_gpu": num_gpu,       # 0 = CPU-only, 35 = full GPU offload
            "num_batch": 512          # larger batch benefits both GPU and CPU
        }
    }

    logger.debug(
        f"[Ollama] Calling model={MODEL_NAME} "
        f"threads={_HW_THREADS} gpu_layers={num_gpu}"
    )

    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code != 200:
        raise RuntimeError(f"Ollama request failed: HTTP {response.status_code}")

    return response.json()["response"]


# ---------------------------------------------------
# MAIN CONTEXT MATCH FUNCTION
# ---------------------------------------------------

def llm_project_context_match(project_name, linkedin_text):
    """
    Uses Llama 3.2 to determine if LinkedIn post
    genuinely relates to the project.
    """

    if not OLLAMA_URL:
        return {
            "match": False,
            "confidence": 0,
            "reason": "LLM validation disabled in production"
        }

    prompt = f"""
You are an expert evaluator validating student project submissions. Your goal is to determine if the LinkedIn post provided refers to the Coursera project title.

Coursera Project Title: "{project_name}"
LinkedIn Post Content: "{linkedin_text}"

LinkedIn posts are often informal or use shortened titles. Be inclusive and lean towards a "match" if there is reasonable evidence.

MATCHING GUIDELINES:
1. **Partial Titles**: A mention of the core topic is a match (e.g., "Image Classification" matches "Image Classification with TensorFlow").
2. **Technology Alignment**: If the project title and post share specific tools/libraries (e.g., "PyTorch", "Tableau", "Pandas").
3. **Acronyms**: "RAG" matches "Retrieval Augmented Generation", "NLP" matches "Natural Language Processing", "BigQuery matched Big Query"etc.
4. **Semantic Similarity**: "Building a Chatbot" likely matches "Generative AI: Design Your Own Conversational Agent".
5. **Outcome Focus**: If the post describes the task performed (e.g., "Analyzed house prices using regression") it matches a project title about that task.

Only return match=false if the post is completely unrelated to the project's domain or has zero specific details.

Return EXACTLY this JSON:
{{
 "match": boolean,
 "confidence": 0-100,
 "reason": "1-sentence explanation"
}}
"""

    raw_output = run_llama(prompt)

    # -------------------------
    # SAFE JSON PARSE
    # -------------------------
    try:
        json_start = raw_output.find("{")
        json_end = raw_output.rfind("}") + 1
        json_str = raw_output[json_start:json_end]

        result = json.loads(json_str)

        # Confidence calibration - Be extremely permissive
        # Only override to false if the model is very unsure (< 40)
        if result["match"] and result["confidence"] < 40:
            result["match"] = False

        return result

    except Exception:

        # fallback if model produces messy output
        return {
            "match": False,
            "confidence": 0,
            "reason": "Parsing failed"
        }
