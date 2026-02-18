"""
Ollama Setup Verification Script

Run this before starting the API to ensure Ollama is configured correctly.
"""

import requests
import sys
import os

def check_ollama_running():
    """Check if Ollama server is running"""
    print("Checking if Ollama is running...")

    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("  ✅ Ollama server is running on port 11434")
            return True
        else:
            print("  ❌ Ollama responded with error status:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Cannot connect to Ollama on port 11434")
        print("     Make sure Ollama is installed and running")
        print("     Run: ollama serve")
        return False
    except Exception as e:
        print(f"  ❌ Error checking Ollama: {str(e)}")
        return False


def check_model_available():
    """Check if llama3.1:8b model is available"""
    print("\nChecking if llama3.1:8b model is downloaded...")

    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])

            llama_found = False
            for model in models:
                model_name = model.get("name", "")
                if "llama3.1:8b" in model_name or "llama3.1" in model_name:
                    llama_found = True
                    print(f"  ✅ Model found: {model_name}")
                    print(f"     Size: {model.get('size', 'unknown')}")
                    break

            if not llama_found:
                print("  ❌ llama3.1:8b model not found")
                print("     Run: ollama pull llama3.1:8b")
                return False

            return True
        else:
            print("  ❌ Could not retrieve model list")
            return False
    except Exception as e:
        print(f"  ❌ Error checking models: {str(e)}")
        return False


def test_ollama_generation():
    """Test if Ollama can generate text"""
    print("\nTesting Ollama text generation...")

    try:
        payload = {
            "model": "llama3.1:8b",
            "prompt": "Say 'Hello' in one word only.",
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }

        print("  Sending test request to Ollama...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "")
            print(f"  ✅ Ollama responded: {response_text[:100]}")
            return True
        else:
            print(f"  ❌ Ollama generation failed with status: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("  ❌ Request timed out (this is normal for first request)")
        print("     The model is loading. Try again in a minute.")
        return False
    except Exception as e:
        print(f"  ❌ Error testing generation: {str(e)}")
        return False


def check_env_file():
    """Check if .env file has correct OLLAMA_URL"""
    print("\nChecking environment configuration...")

    if not os.path.exists(".env"):
        print("  ⚠️  .env file not found")
        print("     Creating .env with default settings...")
        with open(".env", "w") as f:
            f.write("OLLAMA_URL=http://localhost:11434/api/generate\n")
        print("  ✅ Created .env file")
        return True

    with open(".env", "r") as f:
        content = f.read()

    if "OLLAMA_URL" in content:
        print("  ✅ OLLAMA_URL is configured in .env")

        # Check if there's still a GEMINI_API_KEY (shouldn't be there)
        if "GEMINI_API_KEY" in content:
            print("  ⚠️  Found GEMINI_API_KEY in .env (no longer needed)")
            print("     You can remove it if you want")

        return True
    else:
        print("  ❌ OLLAMA_URL not found in .env")
        print("     Add: OLLAMA_URL=http://localhost:11434/api/generate")
        return False


def main():
    print("\n" + "="*60)
    print("  OLLAMA SETUP VERIFICATION")
    print("="*60 + "\n")

    checks = [
        ("Environment File", check_env_file),
        ("Ollama Server", check_ollama_running),
        ("Llama Model", check_model_available),
        ("Text Generation", test_ollama_generation),
    ]

    results = []
    for name, check_func in checks:
        print("─" * 60)
        result = check_func()
        results.append((name, result))
        print()

    # Summary
    print("="*60)
    print("  SUMMARY")
    print("="*60 + "\n")

    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if not result:
            all_passed = False

    print("\n" + "="*60)

    if all_passed:
        print("\n✅ All checks passed! Ollama is ready to use.\n")
        print("You can now start the API server:")
        print("  python start_api.bat  (Windows)")
        print("  ./start_api.sh       (Linux/Mac)")
        print("  or: uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("\n❌ Some checks failed. Please fix the issues above.\n")
        print("Quick fixes:")
        print("  1. Install Ollama: https://ollama.com/download")
        print("  2. Pull model: ollama pull llama3.1:8b")
        print("  3. Start Ollama: ollama serve")
        print("  4. Run this script again")

    print("="*60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
