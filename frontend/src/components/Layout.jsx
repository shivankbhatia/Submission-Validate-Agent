import Sidebar from "./Sidebar";
import BottomNavigation from "./BottomNavigation"; // keep for mobile fallback if desired, or we can just render BottomNav only on mobile

function Layout({ children }) {
  return (
    <div className="flex bg-gray-50 dark:bg-[#0f111a] min-h-screen text-gray-900 dark:text-gray-100 transition-colors duration-300 bg-dot-pattern">
      {/* Desktop Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top Header Placeholder (if needed, else just space) */}
        <header className="h-16 flex border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 justify-between items-center px-8 flex-shrink-0 lg:hidden">
          <div className="font-bold text-lg">Agentic Evaluator</div>
        </header>

        <main className="flex-1 overflow-y-auto w-full relative">
          <div className="h-full">
            {children}
          </div>
        </main>
        
        {/* Mobile bottom nav */}
        <div className="md:hidden">
            <BottomNavigation />
        </div>
      </div>
    </div>
  );
}

export default Layout;
