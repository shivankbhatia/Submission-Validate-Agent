import { useState } from "react";

function SubmissionPage() {
  const [formData, setFormData] = useState({
    studentName: "",
    rollNumber: "",
    emailAddress: "",
    courseraLink: "",
    linkedinLink: "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.studentName || !formData.rollNumber || !formData.emailAddress ||
        !formData.courseraLink || !formData.linkedinLink) {
      setErrorMessage("All fields are required.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);
    setResult(null);
    setSubmitStatus("Evaluating");

    const llmTimer = setTimeout(() => {
      setSubmitStatus("LLM Validation (may take 1-2 minutes)");
    }, 4000);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/submit-evaluation`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          student_name: formData.studentName,
          roll_number: formData.rollNumber,
          email_address: formData.emailAddress,
          coursera_certificate_link: formData.courseraLink,
          linkedin_post_link: formData.linkedinLink,
        }),
      });

      const data = await response.json();

      if (data.status === "DUPLICATE") {
        clearTimeout(llmTimer);
        setSubmitStatus(null);
        setErrorMessage(data.message || "This project has already been submitted and passed.");
        setIsSubmitting(false);
        return;
      }

      if (data.duplicate === true) {
        clearTimeout(llmTimer);
        setSubmitStatus(null);
        setErrorMessage("Duplicate submission: This certificate or LinkedIn post has already been used.");
        setIsSubmitting(false);
        return;
      }

      if (!response.ok || data.error) {
        clearTimeout(llmTimer);
        setSubmitStatus(null);
        setErrorMessage(data.error || "Something went wrong.");
        setIsSubmitting(false);
        return;
      }

      clearTimeout(llmTimer);
      setSubmitStatus(null);
      setResult(data);
      setIsSubmitting(false);
    } catch (error) {
      clearTimeout(llmTimer);
      setSubmitStatus(null);
      setErrorMessage("Failed to connect to the server. Please try again.");
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      studentName: "",
      rollNumber: "",
      emailAddress: "",
      courseraLink: "",
      linkedinLink: "",
    });
    setResult(null);
    setErrorMessage(null);
  };

  if (result) {
    return (
      <div className="flex flex-col items-center justify-center p-8 pb-32 w-full max-w-3xl mx-auto h-full min-h-[80vh]">
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 w-full rounded-2xl shadow-sm p-8 transition-colors duration-300">
           <div className="text-center mb-8">
              {result.status === "PASS" ? (
                <div>
                  <div className="w-16 h-16 mx-auto mb-4 bg-green-50 rounded-full flex items-center justify-center border border-green-100 dark:bg-green-900/30 dark:border-green-800">
                    <svg className="w-8 h-8 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Evaluation Passed</h2>
                </div>
              ) : (
                <div>
                  <div className="w-16 h-16 mx-auto mb-4 bg-red-50 rounded-full flex items-center justify-center border border-red-100 dark:bg-red-900/30 dark:border-red-800">
                    <svg className="w-8 h-8 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Evaluation Failed</h2>
                </div>
              )}
            </div>

            <div className="space-y-4 max-w-lg mx-auto">
              <div className="flex justify-between py-3 border-b border-gray-100 dark:border-gray-700">
                <span className="text-sm text-gray-500">Project</span>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100 text-right">{result.project && result.project !== "-" ? result.project : "N/A"}</span>
              </div>
              <div className="flex justify-between py-3 border-b border-gray-100 dark:border-gray-700">
                <span className="text-sm text-gray-500">Submitted At</span>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100 text-right">{result.submitted_at && result.submitted_at !== "-" ? result.submitted_at : "N/A"}</span>
              </div>
              <div className="flex justify-between py-3">
                <span className="text-sm text-gray-500">Reason</span>
                <span className="text-sm font-medium text-red-600 dark:text-red-400 text-right max-w-xs">{result.reason || "No reason provided."}</span>
              </div>
            </div>

            <div className="mt-10 flex justify-center">
              <button
                onClick={resetForm}
                className="px-6 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 hover:text-gray-900 transition-colors shadow-sm
                           dark:bg-gray-800 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700 dark:hover:text-white"
              >
                Submit Another Project
              </button>
            </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center p-8 pb-32 w-full max-w-3xl mx-auto min-h-[80vh]">
      
      <div className="text-center mb-10 mt-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight mb-3">
          Submit Your Project Details
        </h1>
        <p className="text-gray-500 dark:text-gray-400 text-base">
          Our agents will process your submission and grade you in under 2 minutes.
        </p>
      </div>

      <div className="w-full bg-white dark:bg-[#1a1d24] border-2 border-dashed border-indigo-200 dark:border-indigo-900/50 rounded-3xl p-8 md:p-12 shadow-sm transition-all hover:border-indigo-300">
        <div className="flex justify-center mb-8">
           <div className="w-16 h-16 bg-indigo-600 rounded-2xl flex items-center justify-center shadow-md shadow-indigo-200 dark:shadow-none">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
           </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5 max-w-md mx-auto">
          {/* Form Fields */}
          <div className="space-y-4">
              <div>
                <input type="text" name="studentName" value={formData.studentName} onChange={handleChange} placeholder="Student Name"
                  className="w-full px-4 py-3 bg-gray-50/50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white dark:focus:bg-gray-800 transition-all text-gray-900 dark:text-gray-100" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <input type="text" name="rollNumber" value={formData.rollNumber} onChange={handleChange} placeholder="Roll Number"
                  className="w-full px-4 py-3 bg-gray-50/50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white dark:focus:bg-gray-800 transition-all text-gray-900 dark:text-gray-100" />
                <input type="email" name="emailAddress" value={formData.emailAddress} onChange={handleChange} placeholder="Email Address"
                  className="w-full px-4 py-3 bg-gray-50/50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white dark:focus:bg-gray-800 transition-all text-gray-900 dark:text-gray-100" />
              </div>
              <div>
                <input type="url" name="courseraLink" value={formData.courseraLink} onChange={handleChange} placeholder="Coursera Certificate Link"
                  className="w-full px-4 py-3 bg-gray-50/50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white dark:focus:bg-gray-800 transition-all text-gray-900 dark:text-gray-100" />
              </div>
              <div>
                <input type="url" name="linkedinLink" value={formData.linkedinLink} onChange={handleChange} placeholder="LinkedIn Post Link"
                  className="w-full px-4 py-3 bg-gray-50/50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white dark:focus:bg-gray-800 transition-all text-gray-900 dark:text-gray-100" />
              </div>
          </div>

          <div className="flex flex-col items-center mt-8">
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-8 py-3 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-xl transition-all shadow-md hover:shadow-lg disabled:opacity-70 flex items-center justify-center w-full"
            >
              {isSubmitting ? (
                <span className="flex items-center space-x-2">
                  <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>{submitStatus === "LLM Validation (may take 1-2 minutes)" ? "AI Validation..." : "Evaluating..."}</span>
                </span>
              ) : (
                "Submit Evaluation"
              )}
            </button>
            
            <div className="flex space-x-6 mt-6 text-xs text-gray-400 dark:text-gray-500 w-full justify-center">
               <span className="flex items-center"><svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg> Secure Validation</span>
               <span className="flex items-center"><svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg> Fast Processing</span>
               <span className="flex items-center"><svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg> API Live</span>
            </div>
          </div>
        </form>
      </div>

      {errorMessage && (
        <div className="mt-6 w-full max-w-md bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800 text-red-600 dark:text-red-400 text-sm px-4 py-3 rounded-xl flex items-center justify-center">
          <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" /></svg>
          {errorMessage}
        </div>
      )}

    </div>
  );
}

export default SubmissionPage;
