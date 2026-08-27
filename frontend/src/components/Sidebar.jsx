import { Link, useLocation } from "react-router-dom";
import { useState } from "react";

function Sidebar() {
  const location = useLocation();
  const isActive = (path) => location.pathname === path;
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <aside className={`relative z-20 bg-white/30 dark:bg-gray-900/10 backdrop-blur-md border-r border-gray-200 dark:border-gray-800 hidden md:flex flex-col flex-shrink-0 h-screen sticky top-0 shadow-sm transition-all duration-300 ease-in-out ${isExpanded ? 'w-64' : 'w-20'}`}>

      {/* Brand area */}
      <div className={`h-16 flex items-center border-b border-gray-200/50 dark:border-gray-800/50 ${isExpanded ? 'px-6' : 'justify-center'}`}>
        <div className="text-l font-bold flex items-center gap-2 text-gray-900 dark:text-gray-100 overflow-hidden whitespace-nowrap">
          {isExpanded && <span className="animate-sidebar-text">UCS654 | Guided Projects</span>}
        </div>
      </div>

      {/* Navigation */}
      <div className={`mt-6 flex-1 space-y-2 overflow-y-auto ${isExpanded ? 'px-4' : 'px-3'}`}>
        <Link
          to="/"
          title={!isExpanded ? "Report Dashboard" : ""}
          className={`group flex items-center py-2.5 text-sm font-medium rounded-lg transition-colors ${isExpanded ? 'px-3' : 'justify-center px-0'} ${isActive('/')
            ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-400'
            : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800'
            }`}
        >
          <svg className={`h-5 w-5 flex-shrink-0 ${isExpanded ? 'mr-3' : ''}`} fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
          </svg>
          {isExpanded && <span className="animate-sidebar-text">Submissions</span>}
        </Link>
        <Link
          to="/submit"
          title={!isExpanded ? "Submit Evaluation" : ""}
          className={`group flex items-center py-2.5 text-sm font-medium rounded-lg transition-colors ${isExpanded ? 'px-3' : 'justify-center px-0'} ${isActive('/submit')
            ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-400'
            : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800'
            }`}
        >
          <svg className={`h-5 w-5 flex-shrink-0 ${isExpanded ? 'mr-3' : ''}`} fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          {isExpanded && <span className="animate-sidebar-text">Add New Submission</span>}
        </Link>
        <Link
          to="/guide"
          title={!isExpanded ? "Student Guide" : ""}
          className={`group flex items-center py-2.5 text-sm font-medium rounded-lg transition-colors ${isExpanded ? 'px-3' : 'justify-center px-0'} ${isActive('/guide')
            ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-400'
            : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800'
            }`}
        >
          <svg className={`h-5 w-5 flex-shrink-0 ${isExpanded ? 'mr-3' : ''}`} fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
          </svg>
          {isExpanded && <span className="animate-sidebar-text">Student Guide</span>}
        </Link>
      </div>

      {/* Version */}
      <div className={`p-4 border-t border-gray-100 dark:border-gray-800 ${isExpanded ? '' : 'flex justify-center'}`}>
        {isExpanded ? (
          <p className="text-xs text-gray-400 text-center whitespace-nowrap overflow-hidden">Version 1.0.0</p>
        ) : (
          <p className="text-xs text-gray-400 text-center" title="Version 1.0.0">v1</p>
        )}
      </div>

      {/* Interactive Edge Toggle */}
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        className="absolute -right-1.5 top-0 w-3 h-full cursor-col-resize group/edge z-30 flex items-center justify-center"
        title={isExpanded ? "Collapse Sidebar" : "Expand Sidebar"}
      >
        <div className="h-12 w-1 rounded-full bg-gray-300 dark:bg-gray-700 opacity-0 group-hover/edge:opacity-100 transition-opacity" />
      </div>
    </aside>
  );
}

export default Sidebar;
