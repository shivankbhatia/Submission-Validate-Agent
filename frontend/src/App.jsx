import { Routes, Route } from "react-router-dom";
import FailureReasons from "./pages/FailureReasons";
import HomePage from "./pages/HomePage";
import SubmissionPage from "./pages/SubmissionPage";
import BottomNavigation from "./components/BottomNavigation";
import { useState } from "react";


function App() {
  const [roll, setRoll] = useState("");
  const [records, setRecords] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [serviceDown, setServiceDown] = useState(false);
  const [currentStudent, setCurrentStudent] = useState(null);

  return (
    <div className="min-h-screen bg-gray-100 text-gray-800
                    dark:bg-gray-900 dark:text-gray-100 transition-colors duration-300">

      <Routes>
        <Route
          path="/"
          element={
            <HomePage
              roll={roll}
              setRoll={setRoll}
              records={records}
              setRecords={setRecords}
              isStreaming={isStreaming}
              setIsStreaming={setIsStreaming}
              errorMessage={errorMessage}
              setErrorMessage={setErrorMessage}
              serviceDown={serviceDown}
              setServiceDown={setServiceDown}
              currentStudent={currentStudent}
              setCurrentStudent={setCurrentStudent}
            />
          }
        />
        <Route path="/submit" element={<SubmissionPage />} />
        <Route path="/guide" element={<FailureReasons />} />
      </Routes>

      <BottomNavigation />

    </div>
  );
}

export default App;
