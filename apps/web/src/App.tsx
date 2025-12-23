import { BrowserRouter as Router, Routes, Route, Navigate, Link } from "react-router-dom";
import BillingPage from "./pages/billing";
import UploadPage from "./pages/upload";
import "./App.css";

import { Header } from "./components/layout/Header";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background text-foreground">
        <Header />

        <main className="py-8">
          <Routes>
            <Route path="/" element={<Navigate to="/upload" replace />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/billing" element={<BillingPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
