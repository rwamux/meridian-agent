import { ReactNode } from "react";
import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Chat from "./pages/Chat";
import Login from "./pages/Login";

function RouteGuard({
  children,
  requireAuth,
  redirectTo,
}: {
  children: ReactNode;
  requireAuth: boolean;
  redirectTo: string;
}) {
  const { isAuthenticated } = useAuth();
  if (requireAuth && !isAuthenticated) return <Navigate to={redirectTo} replace />;
  if (!requireAuth && isAuthenticated) return <Navigate to={redirectTo} replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route
            path="/login"
            element={
              <RouteGuard requireAuth={false} redirectTo="/chat">
                <Login />
              </RouteGuard>
            }
          />
          <Route
            path="/chat"
            element={
              <RouteGuard requireAuth redirectTo="/login">
                <Chat />
              </RouteGuard>
            }
          />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
