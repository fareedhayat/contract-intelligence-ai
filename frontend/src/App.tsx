import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import ContractDetail from "./pages/ContractDetail";
import Compare from "./pages/Compare";
import Obligations from "./pages/Obligations";
import { ErrorBoundary } from "./components/ErrorBoundary";

function App() {
  return (
    <ErrorBoundary>
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/contracts/:id" element={<ContractDetail />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/obligations" element={<Obligations />} />
      </Route>
    </Routes>
    </ErrorBoundary>
  );
}

export default App;
