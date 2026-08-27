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

function HomePage({
  roll,
  setRoll,
  records,
  setRecords,
  isStreaming,
  setIsStreaming,
  errorMessage,
  setErrorMessage,
  serviceDown,
  setServiceDown,
  currentStudent,
  setCurrentStudent
}) {
  const eventSourceRef = useRef(null);
  const [studentNameSearch, setStudentNameSearch] = useState("");
  const [studentRecordsCount, setStudentRecordsCount] = useState(null);
  const [isBatchMode, setIsBatchMode] = useState(false);
  const [batchCompleted, setBatchCompleted] = useState(false);
  const [totalBatchRecords, setTotalBatchRecords] = useState(0);

  const handleCancel = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsStreaming(false);
    setErrorMessage("Evaluation canceled by user.");
  };

  const handleAllRecords = () => {
    setRecords([]);
    setErrorMessage(null);
    setServiceDown(false);
    setCurrentStudent(null);
    setIsStreaming(true);
    setIsBatchMode(true);
    setBatchCompleted(false);
    setTotalBatchRecords(0);

    let connectionEstablished = false;

    const eventSource = new EventSource(
      `${import.meta.env.VITE_API_URL}/batch-evaluate-all`
    );
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      connectionEstablished = true;
    };

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "init") {
        setTotalBatchRecords(data.total);
        return;
      }

      if (data.error) {
        setErrorMessage(data.error);
        eventSource.close();
        setIsStreaming(false);
        return;
      }

      if (data.type === "done") {
        eventSource.close();
        setIsStreaming(false);
        setBatchCompleted(true);
        return;
      }

      if (data.type === "progress") {
        setRecords((prev) => {
          const updated = [...prev];
          const rowId = data.row_id;

          if (!updated[rowId]) {
            updated[rowId] = {
              status: data.status,
              result: null,
            };
          } else {
            updated[rowId].status = data.status;
          }

          if (data.full_name && !currentStudent) {
            setCurrentStudent(data.full_name);
          }

          if (data.result) {
            updated[rowId].result = data.result;
            if (!currentStudent && data.result["Full Name"]) {
              setCurrentStudent(data.result["Full Name"]);
            }
          }

          return updated;
        });
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      setIsStreaming(false);

      if (!connectionEstablished) {
        setServiceDown(true);
      }
    };
  };




  const handleEvaluate = () => {
    if (!roll || !studentNameSearch) {
      setErrorMessage("Please enter both a roll number and a student name.");
      return;
    }

    setRecords([]);
    setErrorMessage(null);
    setServiceDown(false);
    setCurrentStudent(null);
    setIsStreaming(true);
    setIsBatchMode(false);
    setBatchCompleted(false);
    setStudentRecordsCount(null);

    let connectionEstablished = false;

    const eventSource = new EventSource(
      `${import.meta.env.VITE_API_URL}/evaluate-cached?roll_number=${encodeURIComponent(roll)}&name=${encodeURIComponent(studentNameSearch)}`
    );
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      connectionEstablished = true;
    };

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.count !== undefined) {
        setStudentRecordsCount(data.count);
        return;
      }

      if (data.error) {
        setErrorMessage("No records found for the provided details.");
        eventSource.close();
        setIsStreaming(false);
        return;
      }

      if (data.done) {
        eventSource.close();
        setIsStreaming(false);
        return;
      }

      setRecords((prev) => {
        const updated = [...prev];

        if (!updated[data.row_id]) {
          updated[data.row_id] = {
            status: data.status,
            result: null,
          };
        } else {
          updated[data.row_id].status = data.status;
        }

        if (data.full_name && !currentStudent) {
          setCurrentStudent(data.full_name);
        }

        if (data.result) {
          updated[data.row_id].result = data.result;

          if (!currentStudent && data.result["Full Name"]) {
            setCurrentStudent(data.result["Full Name"]);
          }
        }

        return updated;
      });
    };

    eventSource.onerror = () => {
      eventSource.close();
      setIsStreaming(false);

      if (!connectionEstablished) {
        setServiceDown(true);
      }
    };
  };

  const handleReevaluate = (rollNum, targetIdx, courseraLink) => {

    if (!rollNum) return;

    setRecords((prev) => {
      const updated = [...prev];
      if (updated[targetIdx]) {
        updated[targetIdx] = {
          ...updated[targetIdx],
          status: "Evaluating",
          result: { ...updated[targetIdx].result, Status: undefined }
        };
      }
      return updated;
    });

    const eventSource = new EventSource(
      `${import.meta.env.VITE_API_URL}/evaluate-cached?roll_number=${encodeURIComponent(rollNum)}&target_link=${encodeURIComponent(courseraLink || "")}&force=true`
    );

    eventSourceRef.current = eventSource;


    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.count !== undefined) return;
      if (data.error) {
        eventSource.close();
        return;
      }
      if (data.done) {
        eventSource.close();
        return;
      }

      setRecords((prev) => {
        const updated = [...prev];
        if (updated[targetIdx]) {
          updated[targetIdx] = {
            status: data.status,
            result: data.result || updated[targetIdx].result
          };
        }
        return updated;
      });
    };

    eventSource.onerror = () => {
      eventSource.close();
    };
  };

  const validRecords = records.filter(rec => rec);
  const passCount = validRecords.filter(
    (r) => r.result?.Status === "PASS"
  ).length;


  const calculateMarks = (passes) => {
    if (passes >= 24) return 8;
    if (passes >= 22) return 7;
    if (passes >= 18) return 6;
    if (passes >= 15) return 5;
    if (passes >= 12) return 4;
    if (passes >= 10) return 3;
    if (passes >= 8) return 2;
    if (passes >= 5) return 1;
    return 0;
  };

  const marks = calculateMarks(passCount);

  const allEvaluated =
    validRecords.length > 0 &&
    validRecords.every((r) => r.result?.Status);

  return (
    <div className="p-8 pb-20 w-full h-full">

      <div className="flex items-center justify-end mb-8">
        {currentStudent && (
          <div className="bg-white dark:bg-gray-800 px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm flex items-center">
            <span className="text-sm text-gray-500 mr-2">Evaluating:</span>
            <span className="text-sm font-semibold text-indigo-600 dark:text-indigo-400">{currentStudent}</span>
          </div>
        )}
      </div>

      {/* Control Row */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4 mb-4 flex flex-col xl:flex-row gap-4 items-center justify-between shadow-sm">
        <div className="flex items-center space-x-2 w-full xl:w-auto">
          <span className="text-lg font-semibold text-gray-900 dark:text-gray-100 px-2">
            Submissions Dashboard
          </span>

        </div>

        <div className="flex flex-col md:flex-row w-full xl:w-auto gap-3 items-center">
          {studentRecordsCount !== null && !isBatchMode && (
            <span className="text-sm font-medium text-indigo-600 dark:text-indigo-400 whitespace-nowrap bg-indigo-50 dark:bg-indigo-900/30 px-3 py-2 rounded-md border border-indigo-100 dark:border-indigo-800 flex items-center">
              {studentRecordsCount} record(s) found
            </span>
          )}

          {isBatchMode && totalBatchRecords > 0 && (
            <span className="text-sm font-medium text-purple-600 dark:text-purple-400 whitespace-nowrap bg-purple-50 dark:bg-purple-900/30 px-3 py-2 rounded-md border border-purple-100 dark:border-purple-800 flex items-center">
              Total: {totalBatchRecords} record(s)
            </span>
          )}

          {!isBatchMode && (
            <>
              <div className="relative w-full md:w-56">
                <input
                  type="text"
                  className="pl-4 pr-4 py-2 w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-900 dark:text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                  placeholder="Student Name..."
                  value={studentNameSearch}
                  onChange={(e) => {
                    setStudentNameSearch(e.target.value);
                  }}
                  onKeyDown={(e) => e.key === 'Enter' && handleEvaluate()}
                />
              </div>

              <div className="relative w-full md:w-56">
                <input
                  type="text"
                  className="pl-4 pr-4 py-2 w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-900 dark:text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                  placeholder="Roll Number..."
                  value={roll}
                  onChange={(e) => setRoll(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleEvaluate()}
                />
              </div>

              <div className="flex gap-2 w-full md:w-auto">
                <button
                  onClick={handleEvaluate}
                  disabled={isStreaming}
                  className="px-5 py-2 w-full md:w-auto bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-70 flex items-center justify-center shadow-sm"
                >
                  {isStreaming ? (
                    <>Evaluating<LoadingDots /></>
                  ) : (
                    "Fetch"
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
            </>
          )}

          {isBatchMode && isStreaming && (
            <button
              onClick={handleCancel}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
            >
              Cancel
            </button>
          )}
        </div>
      </div>

      {/* Errors */}
      {errorMessage && (
        <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800 text-red-600 dark:text-red-400 text-sm px-4 py-3 rounded-lg flex items-center shadow-sm">
          <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" /></svg>
          {errorMessage}
        </div>
      )}

      {serviceDown && (
        <div className="mb-6 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-100 dark:border-yellow-800 text-yellow-700 dark:text-yellow-400 text-sm px-4 py-3 rounded-lg flex items-center shadow-sm">
          Service is currently unavailable. Please try again later.
        </div>
      )}

      {/* Metrics Row (Appears when grading finishes) */}
      {!isStreaming && allEvaluated && validRecords.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-center">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Total Submissions</span>
            <span className="text-2xl font-bold text-gray-900 dark:text-white">{validRecords.length}</span>
          </div>
          <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-center">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Total Passed</span>
            <span className="text-2xl font-bold text-green-600 dark:text-green-500">{passCount}</span>
          </div>
          <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-center">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Total Failed</span>
            <span className="text-2xl font-bold text-red-600 dark:text-red-500">{validRecords.length - passCount}</span>
          </div>
          <div className="bg-indigo-600 p-5 rounded-xl border border-indigo-700 shadow-md flex flex-col justify-center relative overflow-hidden">
            <div className="absolute opacity-10 -right-4 -top-4">
              <svg className="w-24 h-24 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" /></svg>
            </div>
            <span className="text-xs font-semibold text-indigo-200 uppercase tracking-wider mb-1 relative z-10">Final Score</span>
            <div className="flex items-end gap-2 relative z-10">
              <span className="text-3xl font-bold text-white leading-none">{marks}</span>
              <span className="text-sm text-indigo-200 mb-0.5">/ 8</span>
            </div>
          </div>
        </div>
      )}

      {/* Results Table */}
      {records.filter(rec => rec).length > 0 && (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left whitespace-nowrap">
              <thead className="bg-gray-50/50 dark:bg-gray-900/30 border-b border-gray-200 dark:border-gray-700">
                <tr>
                  <th className="px-6 py-4 font-semibold text-gray-500 uppercase tracking-wider text-xs w-16">#</th>
                  <th className="px-6 py-4 font-semibold text-gray-500 uppercase tracking-wider text-xs">Project</th>
                  <th className="px-6 py-4 font-semibold text-gray-500 uppercase tracking-wider text-xs">Submitted At</th>
                  <th className="px-6 py-4 font-semibold text-gray-500 uppercase tracking-wider text-xs">Status</th>
                  <th className="px-6 py-4 font-semibold text-gray-500 uppercase tracking-wider text-xs">Verdict</th>
                  <th className="px-6 py-4 font-semibold text-gray-500 uppercase tracking-wider text-xs">Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                {records.filter(rec => rec).map((rec, idx) => (
                  <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                    <td className="px-6 py-4 text-gray-500">{idx + 1}</td>

                    <td className="px-6 py-4">
                      {rec.result?.Project ? (
                        <span className="font-medium text-gray-900 dark:text-gray-100">{rec.result.Project}</span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>

                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                      {rec.result?.["Submitted At"] || "-"}
                    </td>

                    <td className="px-6 py-4">
                      {rec.status === "LLM Validation (may take 1-2 minutes)" ? (
                        <span className="inline-flex items-center text-indigo-600 dark:text-indigo-400 font-medium text-xs bg-indigo-50 dark:bg-indigo-900/30 px-2 py-1 rounded-md">
                          <svg className="animate-spin -ml-1 mr-1.5 h-3 w-3 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                          AI Validation...
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
                        <div className="flex items-center gap-2">
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 border border-red-200 dark:border-red-800">
                            <span className="w-1.5 h-1.5 rounded-full bg-red-600 dark:bg-red-500"></span> FAIL
                          </span>
                          {rec.result["Roll Number"] && (
                            <button
                              onClick={() => handleReevaluate(rec.result["Roll Number"], idx, rec.result["Coursera Link"])}

                              className="bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded px-1.5 py-1.5 flex items-center transition-colors"
                              title="Force Re-evaluate"
                            >
                              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                            </button>
                          )}
                        </div>
                      )}
                      {rec.result?.Status === "INVALID" && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400 border border-yellow-200 dark:border-yellow-800">
                          <span className="w-1.5 h-1.5 rounded-full bg-yellow-600 dark:bg-yellow-500"></span> INVALID
                        </span>
                      )}
                      {rec.result?.Status === "-" && (
                        <div className="flex items-center gap-2">
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-600 dark:bg-amber-400"></span> AI PENDING
                          </span>
                          {rec.result?.["Roll Number"] && (
                            <button
                              onClick={() => handleReevaluate(rec.result["Roll Number"], idx, rec.result["Coursera Link"])}

                              className="bg-purple-100 hover:bg-purple-200 dark:bg-purple-900/40 dark:hover:bg-purple-800/60 text-purple-700 dark:text-purple-300 rounded px-1.5 py-1.5 flex items-center transition-colors"
                              title="Run AI Evaluation"
                            >
                              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                            </button>
                          )}
                        </div>
                      )}
                      {!rec.result?.Status && <span className="text-gray-400">-</span>}
                    </td>

                    <td className="px-6 py-4">
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

export default HomePage;
