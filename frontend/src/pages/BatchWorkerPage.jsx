import { useState, useRef } from "react";

function LoadingDots() {
  return (
    <span className="inline-flex ml-1">
      <span className="animate-bounce [animation-delay:-0.3s]">.</span>
      <span className="animate-bounce [animation-delay:-0.15s]">.</span>
      <span className="animate-bounce">.</span>
    </span>
  );
}

function BatchWorkerPage() {
  const [records, setRecords] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isDone, setIsDone] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [serviceDown, setServiceDown] = useState(false);
  const [total, setTotal] = useState(null);
  const [runLabel, setRunLabel] = useState("fast");
  const [processedCount, setProcessedCount] = useState(0);
  const [startFrom, setStartFrom] = useState(0);
  const eventSourceRef = useRef(null);
  const completedRowIdsRef = useRef(new Set());

  const handleCancel = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsStreaming(false);
    setErrorMessage("Batch evaluation canceled by user.");
  };

  const startStream = ({ endpoint, resetRecords, label, preserveStartFrom = false }) => {
    if (resetRecords) {
      setRecords([]);
    }
    setErrorMessage(null);
    setServiceDown(false);
    setIsDone(false);
    setIsStreaming(true);
    setTotal(null);
    setRunLabel(label);
    setProcessedCount(0);
    completedRowIdsRef.current = new Set();

    // Reset startFrom to 0 unless explicitly preserved,
    // preventing stale resume-index values from accidentally
    // truncating the dataset on subsequent runs.
    if (!preserveStartFrom) {
      setStartFrom(0);
    }

    let connectionEstablished = false;

    const separator = endpoint.includes("?") ? "&" : "?";
    const fullEndpoint = `${endpoint}${separator}start_from=${startFrom}`;

    const eventSource = new EventSource(`${import.meta.env.VITE_API_URL}${fullEndpoint}`);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      connectionEstablished = true;
    };

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.error) {
        setErrorMessage(data.error);
        eventSource.close();
        setIsStreaming(false);
        return;
      }

      if (data.type === "init") {
        setTotal(data.total);
        return;
      }

      if (data.type === "done") {
        eventSource.close();
        eventSourceRef.current = null;
        setIsStreaming(false);
        setIsDone(true);
        return;
      }

      if (data.type === "progress") {
        if (
          (data.status === "Completed" || data.status === "Error") &&
          !completedRowIdsRef.current.has(data.row_id)
        ) {
          completedRowIdsRef.current.add(data.row_id);
          setProcessedCount(completedRowIdsRef.current.size);
        }

        setRecords((prev) => {
          const updated = [...prev];
          const existingIdx = updated.findIndex(
            (r) => r.row_id === data.row_id
          );
          const entry = {
            row_id: data.row_id,
            status: data.status,
            roll_number: data.roll_number,
            full_name: data.full_name,
            result: data.result || (existingIdx >= 0 ? updated[existingIdx].result : null),
          };
          if (existingIdx >= 0) {
            updated[existingIdx] = entry;
          } else {
            updated.push(entry);
          }
          return updated;
        });
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      eventSourceRef.current = null;
      setIsStreaming(false);
      if (!connectionEstablished) {
        setServiceDown(true);
      }
    };
  };

  const handleStartBatch = () => {
    startStream({
      endpoint: "/batch-evaluate-all?new_only=true",
      resetRecords: true,
      label: "fast",
    });
  };

  const handleRunAiPending = () => {
    startStream({
      endpoint: "/batch-evaluate-ai-pending",
      resetRecords: false,
      label: "ai",
    });
  };

  const handleRunNewOnly = () => {
    startStream({
      endpoint: "/batch-evaluate-all?new_only=true",
      resetRecords: true,
      label: "new",
    });
  };

  const handleForceRerunAll = () => {
    if (!window.confirm(
      "⚠️ Force Re-run All will re-evaluate EVERY record, including ones already marked PASS/FAIL. " +
      "This may overwrite existing results if links have changed or become invalid.\n\n" +
      "Are you sure you want to continue?"
    )) return;
    startStream({
      endpoint: "/batch-evaluate-all",
      resetRecords: true,
      label: "fast",
    });
  };

  const handleRunInvalid = () => {
    startStream({
      endpoint: "/batch-evaluate-invalid",
      resetRecords: false,
      label: "invalid",
      preserveStartFrom: true,
    });
  };

  const completed = records.filter((r) => r.result?.Status);
  const passCount = completed.filter((r) => r.result?.Status === "PASS").length;
  const failCount = completed.filter((r) => r.result?.Status === "FAIL").length;
  const invalidCount = completed.filter((r) => r.result?.Status === "INVALID").length;
  const aiPendingCount = completed.filter((r) => r.result?.Status === "-").length;
  const progress = total ? Math.round((processedCount / total) * 100) : 0;

  // Live count of records currently being evaluated by a worker thread
  const ACTIVE_STATUSES = [
    "Evaluating",
    "LLM Validation (may take 1-2 minutes)",
    "AI Validating",
  ];
  const activeWorkers = records.filter((r) => ACTIVE_STATUSES.includes(r.status)).length;

  return (
    <div className="p-8 pb-20 w-full h-full">

      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
            Batch Evaluation Worker
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
            Processes all records from <code className="bg-gray-100 dark:bg-gray-700 px-1 rounded">data.csv</code> in parallel across all CPU cores.
            {isStreaming && activeWorkers > 0 && (
              <span className="ml-2 inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-semibold bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-700">
                <span className="relative flex h-1.5 w-1.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-indigo-500"></span>
                </span>
                {activeWorkers} active worker{activeWorkers !== 1 ? "s" : ""}
              </span>
            )}
          </p>
        </div>
        {isStreaming && (
          <div className="bg-indigo-50 dark:bg-indigo-900/30 border border-indigo-200 dark:border-indigo-700 px-4 py-2 rounded-lg flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
            </span>
            <span className="text-sm font-medium text-indigo-600 dark:text-indigo-400">
              Running
            </span>
          </div>
        )}
      </div>

      {/* Control Row */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4 mb-4 flex flex-col xl:flex-row gap-4 items-center justify-between shadow-sm">
        <div className="flex items-center gap-3 w-full xl:w-auto">
          <span className="px-4 py-1.5 text-sm font-medium bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg">
            {runLabel === "ai" ? "AI Pending Records" : runLabel === "new" ? "New Records Only" : runLabel === "invalid" ? "Invalid Records" : "Unevaluated Records"}
          </span>
          {total !== null && (
            <span className="text-sm font-medium text-indigo-600 dark:text-indigo-400 whitespace-nowrap bg-indigo-50 dark:bg-indigo-900/30 px-3 py-2 rounded-md border border-indigo-100 dark:border-indigo-800">
              {processedCount} / {total} processed
            </span>
          )}
          {aiPendingCount > 0 && (
            <span className="text-sm font-medium text-amber-700 dark:text-amber-300 whitespace-nowrap bg-amber-50 dark:bg-amber-900/30 px-3 py-2 rounded-md border border-amber-100 dark:border-amber-800">
              {aiPendingCount} AI pending
            </span>
          )}
        </div>


        <div className="flex items-center gap-4 w-full xl:w-auto">
          <div className="flex flex-col">
            <label className="text-[10px] font-bold text-gray-500 uppercase mb-1 ml-1">Resume from Index</label>
            <input
              type="number"
              min="0"
              value={startFrom}
              onChange={(e) => setStartFrom(Math.max(0, parseInt(e.target.value) || 0))}
              disabled={isStreaming}
              className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block w-24 p-2 transition-all"
              placeholder="0"
            />
          </div>
          <div className="flex gap-2 mt-auto">
            <button
              onClick={handleStartBatch}
              disabled={isStreaming}
              className="px-5 py-2 w-full xl:w-auto bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-70 flex items-center justify-center shadow-sm"
            >
              {isStreaming && runLabel === "fast" ? (
                <>Processing<LoadingDots /></>
              ) : isDone ? (
                "Run Unevaluated"
              ) : (
                "Start Batch Evaluation"
              )}
            </button>
            {isDone && (
              <button
                onClick={handleForceRerunAll}
                disabled={isStreaming}
                className="px-5 py-2 w-full xl:w-auto bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-70 flex items-center justify-center shadow-sm"
                title="Warning: This will re-evaluate ALL records including already passed ones"
              >
                Force Re-run All
              </button>
            )}
            <button
              onClick={handleRunAiPending}
              disabled={isStreaming}
              className="px-5 py-2 w-full xl:w-auto bg-amber-600 hover:bg-amber-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-70 flex items-center justify-center shadow-sm"
            >
              {isStreaming && runLabel === "ai" ? (
                <>Running AI<LoadingDots /></>
              ) : (
                "Run AI Pending"
              )}
            </button>
            <button
              onClick={handleRunNewOnly}
              disabled={isStreaming}
              className="px-5 py-2 w-full xl:w-auto bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-70 flex items-center justify-center shadow-sm"
            >
              {isStreaming && runLabel === "new" ? (
                <>Running New<LoadingDots /></>
              ) : (
                "Run New Records"
              )}
            </button>
            <button
              onClick={handleRunInvalid}
              disabled={isStreaming}
              className="px-5 py-2 w-full xl:w-auto bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-70 flex items-center justify-center shadow-sm"
            >
              {isStreaming && runLabel === "invalid" ? (
                <>Running Invalid<LoadingDots /></>
              ) : (
                "Run Invalid Links"
              )}
            </button>
            {isStreaming && (
              <button
                onClick={handleCancel}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
              >
                Cancel
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      {total !== null && (
        <div className="mb-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4 shadow-sm">
          <div className="flex justify-between text-xs font-medium text-gray-500 mb-2">
            <span>Progress</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Errors */}
      {errorMessage && (
        <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800 text-red-600 dark:text-red-400 text-sm px-4 py-3 rounded-lg flex items-center shadow-sm">
          <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" /></svg>
          {errorMessage}
        </div>
      )}

      {serviceDown && (
        <div className="mb-6 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-100 dark:border-yellow-800 text-yellow-700 dark:text-yellow-400 text-sm px-4 py-3 rounded-lg flex items-center shadow-sm">
          API server is down. Make sure the backend is running on port 8000.
        </div>
      )}

      {/* Summary Metrics */}
      {isDone && completed.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-center">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Total Processed</span>
            <span className="text-2xl font-bold text-gray-900 dark:text-white">{completed.length}</span>
          </div>
          <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-center">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Total Passed</span>
            <span className="text-2xl font-bold text-green-600 dark:text-green-500">{passCount}</span>
          </div>
          <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-center">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Total Failed</span>
            <span className="text-2xl font-bold text-red-600 dark:text-red-500">{failCount}</span>
          </div>
          <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-center">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Invalid Links</span>
            <span className="text-2xl font-bold text-yellow-600 dark:text-yellow-500">{invalidCount}</span>
          </div>
          <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-center">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">AI Pending</span>
            <span className="text-2xl font-bold text-amber-600 dark:text-amber-400">{aiPendingCount}</span>
          </div>
        </div>
      )}

      {/* Results Table */}
      {records.length > 0 && (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left whitespace-nowrap">
              <thead className="bg-gray-50/50 dark:bg-gray-900/30 border-b border-gray-200 dark:border-gray-700">
                <tr>
                  <th className="px-6 py-4 font-semibold text-gray-500 uppercase tracking-wider text-xs w-16">CSV Index</th>
                  <th className="px-6 py-4 font-semibold text-gray-500 uppercase tracking-wider text-xs">Student</th>
                  <th className="px-6 py-4 font-semibold text-gray-500 uppercase tracking-wider text-xs">Roll No.</th>
                  <th className="px-6 py-4 font-semibold text-gray-500 uppercase tracking-wider text-xs">Project</th>
                  <th className="px-6 py-4 font-semibold text-gray-500 uppercase tracking-wider text-xs">Status</th>
                  <th className="px-6 py-4 font-semibold text-gray-500 uppercase tracking-wider text-xs">Verdict</th>
                  <th className="px-6 py-4 font-semibold text-gray-500 uppercase tracking-wider text-xs">Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                {records.map((rec, i) => (
                  <tr key={rec.row_id ?? i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                    <td className="px-6 py-4 text-gray-500 font-mono text-xs">
                      #{rec.row_id !== undefined ? rec.row_id : i + 1}
                    </td>

                    <td className="px-6 py-4 font-medium text-gray-900 dark:text-gray-100">
                      {rec.full_name || "-"}
                    </td>

                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                      {rec.roll_number || "-"}
                    </td>

                    <td className="px-6 py-4">
                      {rec.result?.Project ? (
                        <span className="font-medium text-gray-900 dark:text-gray-100">{rec.result.Project}</span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>

                    <td className="px-6 py-4">
                      {rec.status === "LLM Validation (may take 1-2 minutes)" || rec.status === "AI Validating" ? (
                        <span className="inline-flex items-center text-indigo-600 dark:text-indigo-400 font-medium text-xs bg-indigo-50 dark:bg-indigo-900/30 px-2 py-1 rounded-md">
                          <svg className="animate-spin -ml-1 mr-1.5 h-3 w-3 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                          AI Validation...
                        </span>
                      ) : rec.status === "Evaluating" ? (
                        <span className="inline-flex items-center text-blue-600 dark:text-blue-400 text-xs bg-blue-50 dark:bg-blue-900/30 px-2 py-1 rounded-md">
                          <svg className="animate-spin -ml-1 mr-1.5 h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                          Evaluating...
                        </span>
                      ) : (
                        <span className="text-gray-500 dark:text-gray-400">{rec.status}</span>
                      )}
                    </td>

                    <td className="px-6 py-4">
                      {rec.result?.Status === "PASS" && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 border border-green-200 dark:border-green-800">
                          <span className="w-1.5 h-1.5 rounded-full bg-green-600 dark:bg-green-500"></span> PASS
                        </span>
                      )}
                      {rec.result?.Status === "FAIL" && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 border border-red-200 dark:border-red-800">
                          <span className="w-1.5 h-1.5 rounded-full bg-red-600 dark:bg-red-500"></span> FAIL
                        </span>
                      )}
                      {rec.result?.Status === "INVALID" && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400 border border-yellow-200 dark:border-yellow-800">
                          <span className="w-1.5 h-1.5 rounded-full bg-yellow-600 dark:bg-yellow-500"></span> INVALID
                        </span>
                      )}
                      {rec.result?.Status === "-" && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-600 dark:bg-amber-400"></span> AI PENDING
                        </span>
                      )}
                      {!rec.result?.Status && <span className="text-gray-400">-</span>}
                    </td>

                    <td className="px-6 py-4 max-w-xs truncate">
                      {rec.result?.Reason ? (
                        <span className={`text-sm ${rec.result.Status === "PASS" ? "text-gray-500 dark:text-gray-400" : "text-red-600 dark:text-red-400 font-medium"}`}>
                          {rec.result.Reason}
                        </span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default BatchWorkerPage;
