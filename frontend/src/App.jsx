import { Routes, Route } from "react-router-dom";
import FailureReasons from "./pages/FailureReasons";
import HomePage from "./pages/HomePage";
import SubmissionPage from "./pages/SubmissionPage";
import BatchWorkerPage from "./pages/BatchWorkerPage";
import Layout from "./components/Layout";
import { useState } from "react";

function App() {
  const [roll, setRoll] = useState("");
  const [records, setRecords] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [serviceDown, setServiceDown] = useState(false);
  const [currentStudent, setCurrentStudent] = useState(null);

  return (
    <Layout>
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
        {/* Hidden trapdoor — not linked in sidebar */}
        <Route path="/HomePage/all_records_fun" element={<BatchWorkerPage />} />
      </Routes>
    </Layout>
  );
}

export default App;
