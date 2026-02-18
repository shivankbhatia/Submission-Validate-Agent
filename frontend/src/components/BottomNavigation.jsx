import { Link, useLocation } from "react-router-dom";

function BottomNavigation() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800
                    border-t border-gray-200 dark:border-gray-700
                    shadow-lg transition-colors duration-300 z-50">
      <div className="max-w-md mx-auto px-4">
        <div className="flex justify-around items-center h-16">

          {/* Report Link */}
          <Link
            to="/"
            className={`flex flex-col items-center justify-center flex-1 py-2
                       transition-colors duration-200
                       ${isActive('/')
                         ? 'text-orange-600 dark:text-orange-500'
                         : 'text-gray-600 dark:text-gray-400 hover:text-orange-500'}`}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
              className="w-6 h-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z"
              />
            </svg>
            <span className="text-xs mt-1">Report</span>
          </Link>

          {/* Submit Link (Center with Plus Icon) */}
          <Link
            to="/submit"
            className="flex flex-col items-center justify-center -mt-6"
          >
            <div className={`w-14 h-14 rounded-full shadow-lg flex items-center justify-center
                           transition-all duration-200
                           ${isActive('/submit')
                             ? 'bg-orange-600 dark:bg-orange-600'
                             : 'bg-orange-500 dark:bg-orange-500 hover:bg-orange-600'}`}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2.5}
                stroke="currentColor"
                className="w-7 h-7 text-white"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 4.5v15m7.5-7.5h-15"
                />
              </svg>
            </div>
            <span className={`text-xs mt-2 transition-colors duration-200
                           ${isActive('/submit')
                             ? 'text-orange-600 dark:text-orange-500'
                             : 'text-gray-600 dark:text-gray-400'}`}>
              Submit
            </span>
          </Link>

          {/* Guide Link */}
          <Link
            to="/guide"
            className={`flex flex-col items-center justify-center flex-1 py-2
                       transition-colors duration-200
                       ${isActive('/guide')
                         ? 'text-orange-600 dark:text-orange-500'
                         : 'text-gray-600 dark:text-gray-400 hover:text-orange-500'}`}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
              className="w-6 h-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"
              />
            </svg>
            <span className="text-xs mt-1">Guide</span>
          </Link>

        </div>
      </div>
    </nav>
  );
}

export default BottomNavigation;
