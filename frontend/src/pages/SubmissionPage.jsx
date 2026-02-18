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

    // Validate form
    if (!formData.studentName || !formData.rollNumber || !formData.emailAddress ||
        !formData.courseraLink || !formData.linkedinLink) {
      setErrorMessage("All fields are required.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);
    setResult(null);

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

      // Check for duplicate submission
      if (data.duplicate === true || data.status === "DUPLICATE") {
        setErrorMessage(data.message || "Record already exists in the database.");
        setIsSubmitting(false);
        return;
      }

      if (!response.ok || data.error) {
        setErrorMessage(data.error || "Something went wrong.");
        setIsSubmitting(false);
        return;
      }

      setResult(data);
      setIsSubmitting(false);
    } catch (error) {
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-orange-100
                    dark:from-gray-900 dark:to-gray-800
                    transition-colors duration-300 px-4 py-8 pb-24">

      <div className="max-w-2xl mx-auto">

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-orange-600 dark:text-orange-500 mb-2">
            Submit Your Project
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm">
            Fill in all the details below to get your project evaluated
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-6 md:p-8
                        transition-colors duration-300 border border-gray-200 dark:border-gray-700">

          <form onSubmit={handleSubmit} className="space-y-5">

            {/* Student Name */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Student Name
              </label>
              <input
                type="text"
                name="studentName"
                value={formData.studentName}
                onChange={handleChange}
                placeholder="Enter your full name"
                className="w-full px-4 py-3
                         border border-gray-300 dark:border-gray-600
                         bg-white dark:bg-gray-700
                         text-gray-800 dark:text-gray-100
                         rounded-xl
                         focus:outline-none focus:ring-2 focus:ring-orange-500
                         transition-all duration-200"
              />
            </div>

            {/* Roll Number */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Roll Number
              </label>
              <input
                type="text"
                name="rollNumber"
                value={formData.rollNumber}
                onChange={handleChange}
                placeholder="Enter your roll number"
                className="w-full px-4 py-3
                         border border-gray-300 dark:border-gray-600
                         bg-white dark:bg-gray-700
                         text-gray-800 dark:text-gray-100
                         rounded-xl
                         focus:outline-none focus:ring-2 focus:ring-orange-500
                         transition-all duration-200"
              />
            </div>

            {/* Email Address */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Email Address
              </label>
              <input
                type="email"
                name="emailAddress"
                value={formData.emailAddress}
                onChange={handleChange}
                placeholder="Enter your email address"
                className="w-full px-4 py-3
                         border border-gray-300 dark:border-gray-600
                         bg-white dark:bg-gray-700
                         text-gray-800 dark:text-gray-100
                         rounded-xl
                         focus:outline-none focus:ring-2 focus:ring-orange-500
                         transition-all duration-200"
              />
            </div>

            {/* Coursera Certificate Link */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Coursera Certificate Link
              </label>
              <input
                type="url"
                name="courseraLink"
                value={formData.courseraLink}
                onChange={handleChange}
                placeholder="https://coursera.org/verify/..."
                className="w-full px-4 py-3
                         border border-gray-300 dark:border-gray-600
                         bg-white dark:bg-gray-700
                         text-gray-800 dark:text-gray-100
                         rounded-xl
                         focus:outline-none focus:ring-2 focus:ring-orange-500
                         transition-all duration-200"
              />
            </div>

            {/* LinkedIn Post Link */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                LinkedIn Post Link
              </label>
              <input
                type="url"
                name="linkedinLink"
                value={formData.linkedinLink}
                onChange={handleChange}
                placeholder="https://www.linkedin.com/posts/..."
                className="w-full px-4 py-3
                         border border-gray-300 dark:border-gray-600
                         bg-white dark:bg-gray-700
                         text-gray-800 dark:text-gray-100
                         rounded-xl
                         focus:outline-none focus:ring-2 focus:ring-orange-500
                         transition-all duration-200"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-gradient-to-r from-orange-500 to-orange-600
                       hover:from-orange-600 hover:to-orange-700
                       text-white font-semibold py-3 rounded-xl
                       transition-all duration-200 transform hover:scale-[1.02]
                       disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none
                       shadow-lg hover:shadow-xl"
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </span>
              ) : (
                "Submit for Evaluation"
              )}
            </button>
          </form>

        </div>

        {/* Error Message */}
        {errorMessage && (
          <div className="mt-6 bg-red-50 dark:bg-red-900/30
                        border border-red-200 dark:border-red-800
                        text-red-700 dark:text-red-300
                        px-6 py-4 rounded-2xl shadow-md">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              {errorMessage}
            </div>
          </div>
        )}

        {/* Result Display */}
        {result && (
          <div className="mt-6 bg-white dark:bg-gray-800
                        border-2 rounded-2xl shadow-xl p-6
                        transition-colors duration-300">

            {/* Result Header */}
            <div className="text-center mb-6">
              {result.status === "PASS" ? (
                <div>
                  <div className="w-16 h-16 mx-auto mb-4 bg-green-100 dark:bg-green-900/30
                                rounded-full flex items-center justify-center">
                    <svg className="w-10 h-10 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <h2 className="text-2xl font-bold text-green-600 dark:text-green-400">
                    PASS
                  </h2>
                </div>
              ) : (
                <div>
                  <div className="w-16 h-16 mx-auto mb-4 bg-red-100 dark:bg-red-900/30
                                rounded-full flex items-center justify-center">
                    <svg className="w-10 h-10 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <h2 className="text-2xl font-bold text-red-600 dark:text-red-400">
                    FAIL
                  </h2>
                </div>
              )}
            </div>

            {/* Result Reason */}
            <div className="space-y-3">

              {/* Project */}
              {result.project && result.project !== "-" && (
                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4">
                  <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
                    Project:
                  </h3>
                  <p className="text-gray-800 dark:text-gray-200">
                    {result.project}
                  </p>
                </div>
              )}

              {/* Submitted At */}
              {result.submitted_at && result.submitted_at !== "-" && (
                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4">
                  <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
                    Submitted At:
                  </h3>
                  <p className="text-gray-800 dark:text-gray-200">
                    {result.submitted_at}
                  </p>
                </div>
              )}

              {/* Reason */}
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4">
                <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">
                  Reason:
                </h3>
                <p className="text-gray-800 dark:text-gray-200">
                  {result.reason || "No reason provided."}
                </p>
              </div>

            </div>

            {/* Reset Button */}
            <button
              onClick={resetForm}
              className="w-full bg-gray-200 dark:bg-gray-700
                       hover:bg-gray-300 dark:hover:bg-gray-600
                       text-gray-800 dark:text-gray-200
                       font-semibold py-2 rounded-xl
                       transition-all duration-200 mt-4"
            >
              Submit Another
            </button>

          </div>
        )}

      </div>
    </div>
  );
}

export default SubmissionPage;
