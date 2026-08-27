function FailureReasons() {
  return (
    <div className="p-8 pb-32 w-full h-full flex flex-col pt-12 items-center">

      <div className="text-center mb-10 w-full max-w-5xl">
         <h1 className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight mb-3">
           Student Evaluation Guide
         </h1>
         <p className="text-gray-500 dark:text-gray-400 text-base">
           Learn the criteria behind the PASS, FAIL, and INVALID evaluation statuses.
         </p>
      </div>

      <div className="w-full max-w-5xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm rounded-3xl p-8 md:p-12 transition-all">

        {/* ---------------- INVALID SECTION ---------------- */}
        <section className="mb-16">
          <div className="flex items-center gap-3 mb-6">
             <div className="w-10 h-10 rounded-xl bg-yellow-50 dark:bg-yellow-900/30 flex items-center justify-center border border-yellow-100 dark:border-yellow-800">
               <svg className="w-5 h-5 text-yellow-600 dark:text-yellow-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" /></svg>
             </div>
             <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
               INVALID Status
             </h2>
          </div>

          <p className="leading-relaxed mb-8 text-gray-600 dark:text-gray-400 max-w-3xl text-sm md:text-base">
            <strong className="text-gray-900 dark:text-gray-200 font-semibold">INVALID</strong> means the Coursera certificate link was not provided correctly. 
            The link must be the official certificate completion URL issued by Coursera for public verification.
            Any other link (e.g., your public profile, the course home page, a screenshot) will result in an INVALID score.
          </p>

          {/* Images Section */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">

            {/* Correct Example 1 */}
            <div className="flex flex-col items-center">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 mb-4 rounded-full text-xs font-semibold bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-400 border border-green-200 dark:border-green-800">
                 <span className="w-1.5 h-1.5 rounded-full bg-green-600"></span> Correct URL Form
              </span>
              <div className="w-full bg-gray-50 dark:bg-gray-900 rounded-2xl p-2 border border-gray-100 dark:border-gray-700 shadow-sm">
                <img
                  src="/images/correct1.png"
                  alt="Correct Certificate Example 1"
                  className="rounded-xl w-full object-cover"
                />
              </div>
            </div>

            {/* Correct Example 2 */}
            <div className="flex flex-col items-center">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 mb-4 rounded-full text-xs font-semibold bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-400 border border-green-200 dark:border-green-800">
                 <span className="w-1.5 h-1.5 rounded-full bg-green-600"></span> Correct Certificate
              </span>
              <div className="w-full bg-gray-50 dark:bg-gray-900 rounded-2xl p-2 border border-gray-100 dark:border-gray-700 shadow-sm">
                <img
                  src="/images/correct2.png"
                  alt="Correct Certificate Example 2"
                  className="rounded-xl w-full object-cover"
                />
              </div>
            </div>

            {/* Incorrect Example */}
            <div className="flex flex-col items-center">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 mb-4 rounded-full text-xs font-semibold bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400 border border-red-200 dark:border-red-800">
                 <span className="w-1.5 h-1.5 rounded-full bg-red-600"></span> Incorrect URL
              </span>
              <div className="w-full bg-gray-50 dark:bg-gray-900 rounded-2xl p-2 border border-gray-100 dark:border-gray-700 shadow-sm">
                <img
                  src="/images/incorrect.png"
                  alt="Incorrect Certificate Example"
                  className="rounded-xl w-full object-cover"
                />
              </div>
            </div>

          </div>

        </section>

        <hr className="border-gray-100 dark:border-gray-700 mb-12" />

        {/* ---------------- FAIL SECTION ---------------- */}
        <section>
           
          <div className="flex items-center gap-3 mb-6">
             <div className="w-10 h-10 rounded-xl bg-red-50 dark:bg-red-900/30 flex items-center justify-center border border-red-100 dark:border-red-800">
               <svg className="w-5 h-5 text-red-600 dark:text-red-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" /></svg>
             </div>
             <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
               FAIL Status
             </h2>
          </div>

          <div className="bg-gray-50 dark:bg-gray-900/50 rounded-2xl p-6 md:p-8 border border-gray-100 dark:border-gray-700">
             <p className="leading-relaxed text-gray-600 dark:text-gray-400 text-sm md:text-base mb-4">
               <strong className="text-gray-900 dark:text-gray-200 font-semibold">FAIL</strong> means that the provided LinkedIn post does not clearly mention
               or describe the Coursera guided project that was submitted. 
             </p>
             <p className="leading-relaxed text-gray-600 dark:text-gray-400 text-sm md:text-base">
               Our evaluation system runs a hybrid rule-based check followed by an AI Context validation pass to check whether the project is referenced intelligently. 
               If the project is missing, vaguely referenced without specifics, or unrelated to the Coursera certificate, the submission will be marked as FAIL.
             </p>
          </div>

        </section>

      </div>
    </div>
  );
}

export default FailureReasons;
