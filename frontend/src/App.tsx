import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "./store/useAuthStore";
import { useEffect } from "react";

// Layout Components
import DashboardLayout from "./components/layout/DashboardLayout";

// Page Components
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import UploadPage from "./pages/UploadPage";
import LabelingPage from "./pages/LabelingPage";
import CandidatesPage from "./pages/CandidatesPage";
import CandidateDetailPage from "./pages/CandidateDetailPage";
import JobsPage from "./pages/JobsPage";
import MatchingPage from "./pages/MatchingPage";
import AccuracyPage from "./pages/AccuracyPage";
import CorrectionsPage from "./pages/CorrectionsPage";
import TaxonomyPage from "./pages/TaxonomyPage";

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, token } = useAuthStore();

  if (!isAuthenticated || !token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// Public Route Component (redirect to dashboard if authenticated)
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

function App() {
  const { token, isAuthenticated } = useAuthStore();

  // Initialize auth state from localStorage on app load
  useEffect(() => {
    if (token && isAuthenticated) {
      console.log("User authenticated from localStorage");
    }
  }, [token, isAuthenticated]);

  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />

      {/* Redirect root to login */}
      <Route path="/" element={<Navigate to="/login" replace />} />

      {/* Protected Routes — all share DashboardLayout */}
      <Route
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/candidates" element={<CandidatesPage />} />
        <Route path="/candidates/:id" element={<CandidateDetailPage />} />
        <Route path="/accuracy" element={<AccuracyPage />} />
        <Route path="/corrections" element={<CorrectionsPage />} />
        <Route path="/taxonomy" element={<TaxonomyPage />} />
        <Route path="/jobs" element={<JobsPage />} />
        <Route path="/matching" element={<MatchingPage />} />
        <Route path="/labeling" element={<LabelingPage />} />
      </Route>

      {/* Catch all route */}
      <Route
        path="*"
        element={
          isAuthenticated ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
    </Routes>
  );
}

export default App;
