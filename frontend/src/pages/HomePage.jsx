import { useState } from "react";

/* ---------------- Loading Dots Component ---------------- */
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

  const handleEvaluate = () => {
    if (!roll) {
      setErrorMessage("Please enter a roll number.");
      return;
    }

    setRecords([]);
    setErrorMessage(null);
    setServiceDown(false);
    setCurrentStudent(null);
    setIsStreaming(true);

    let connectionEstablished = false;

    const eventSource = new EventSource(
      `${import.meta.env.VITE_API_URL}/evaluate-cached/${roll}`
    );

    eventSource.onopen = () => {
      connectionEstablished = true;
    };

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.error) {
        setErrorMessage("No records found for this roll number.");
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

  /* ---------------- PASS + MARKS CALCULATION ---------------- */

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
    <div className="transition-colors duration-300 pb-20">

      {/* Header with Title */}
      <div className="bg-gradient-to-r from-orange-500 to-orange-600 dark:from-orange-700 dark:to-orange-800
                      py-6 shadow-md">
        <div className="container mx-auto px-4">
          <h1 className="text-2xl font-bold text-white text-center">
            Guided Project Status
          </h1>
          <p className="text-center text-sm italic text-orange-100 mt-2">
            This system is currently under production and may occasionally produce irregular results.
          </p>
        </div>
      </div>

      {/* Input Section */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-md mx-auto bg-white dark:bg-gray-800 shadow-lg rounded-2xl p-6 transition-colors duration-300
                        border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold mb-4 text-center">
            Evaluate Student Records
          </h3>

          <input
            className="w-full border border-gray-300 dark:border-gray-600
                       bg-white dark:bg-gray-700
                       text-gray-800 dark:text-gray-100
                       rounded-xl px-3 py-2
                       focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="Enter Roll Number"
            value={roll}
            onChange={(e) => setRoll(e.target.value)}
          />

          <button
            onClick={handleEvaluate}
            disabled={isStreaming}
            className="mt-4 w-full bg-gradient-to-r from-orange-500 to-orange-600
                       hover:from-orange-600 hover:to-orange-700
                       text-white py-2 rounded-xl
                       font-semibold transition-all duration-200 transform hover:scale-[1.02]
                       disabled:opacity-60 disabled:transform-none shadow-lg"
          >
            {isStreaming ? (
              <>
                Processing
                <LoadingDots />
              </>
            ) : (
              "Evaluate"
            )}
          </button>
        </div>
      </div>

      {/* Student Name */}
      {currentStudent && (
        <div className="container mx-auto px-4">
          <p className="text-lg font-semibold">
            Student:{" "}
            <span className="text-orange-600 dark:text-orange-500">
              {currentStudent}
            </span>
          </p>
        </div>
      )}

      {/* Errors */}
      {errorMessage && (
        <div className="max-w-md mx-auto mt-4 bg-yellow-50 dark:bg-yellow-900/30
                        border border-yellow-200 dark:border-yellow-800
                        text-yellow-700 dark:text-yellow-300
                        px-4 py-3 rounded-2xl shadow-md">
          {errorMessage}
        </div>
      )}

      {serviceDown && (
        <div className="max-w-md mx-auto mt-4 bg-red-50 dark:bg-red-900/30
                        border border-red-200 dark:border-red-800
                        text-red-700 dark:text-red-300
                        px-4 py-3 rounded-2xl shadow-md">
          Service is currently unavailable. Please try again later.
        </div>
      )}

      {/* Results Table */}
      {records.filter(rec => rec).length > 0 && (
        <div className="container mx-auto px-4 py-8">
          <div className="bg-white dark:bg-gray-800 shadow-lg rounded-2xl overflow-hidden transition-colors duration-300
                          border border-gray-200 dark:border-gray-700">

            <table className="min-w-full text-sm text-left">
              <thead className="bg-gray-50 dark:bg-gray-700 border-b dark:border-gray-600">
                <tr>
                  <th className="px-4 py-3">#</th>
                  <th className="px-4 py-3">Project</th>
                  <th className="px-4 py-3">Submitted At</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Verdict</th>
                  <th className="px-4 py-3">Reason</th>
                </tr>
              </thead>

              <tbody>
                {records.filter(rec => rec).map((rec, idx) => (
                  <tr
                    key={idx}
                    className="border-b dark:border-gray-700"
                  >
                    <td className="px-4 py-3">{idx + 1}</td>

                    <td className="px-4 py-3">
                      {rec.result?.Project || "-"}
                    </td>

                    <td className="px-4 py-3">
                      {rec.result?.["Submitted At"] || "-"}
                    </td>

                    <td className="px-4 py-3">
                      {rec.status ===
                      "LLM Validation (may take 1-2 minutes)" ? (
                        <span className="text-orange-600 dark:text-orange-500 font-medium">
                          {rec.status}
                        </span>
                      ) : (
                        rec.status
                      )}
                    </td>

                    <td className="px-4 py-3 font-semibold">
                      {rec.result?.Status === "PASS" && (
                        <span className="text-green-600">PASS</span>
                      )}
                      {rec.result?.Status === "FAIL" && (
                        <span className="text-red-600">FAIL</span>
                      )}
                      {rec.result?.Status === "INVALID" && (
                        <span className="text-yellow-600">INVALID</span>
                      )}
                      {!rec.result?.Status && "-"}
                    </td>

                    <td className="px-4 py-3 text-red-500">
                      {rec.result?.Reason || "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Final Grading Section */}
      {!isStreaming && allEvaluated && (
        <div className="container mx-auto px-4 pb-12">
          <div className="bg-white dark:bg-gray-800 shadow-lg rounded-2xl p-6 mt-6 transition-colors duration-300
                          border border-gray-200 dark:border-gray-700">

            <h3 className="text-lg font-semibold mb-4">
              Final Evaluation Result
            </h3>

            <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">

              <div>
                <p>
                  Total Projects Passed:
                  <span className="font-semibold text-green-600 ml-2">
                    {passCount}
                  </span>
                </p>

                <p className="mt-2">
                  Total Projects Failed:
                  <span className="font-semibold text-red-600 ml-2">
                    {validRecords.length - passCount}
                  </span>
                </p>
              </div>

              <div className="text-center md:text-right">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Final Marks
                </p>
                <p className="text-3xl font-bold text-orange-600 dark:text-orange-500">
                  {marks} / 8
                </p>
              </div>

            </div>

            <div className="mt-6">
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-5 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-orange-500 to-orange-600 h-5 transition-all duration-700"
                  style={{ width: `${(marks / 8) * 100}%` }}
                ></div>
              </div>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}

export default HomePage;
