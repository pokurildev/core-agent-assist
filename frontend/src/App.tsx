import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import Login from '@/pages/Login';
import { Toaster } from '@/components/ui/sonner';

function Dashboard() {
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
      <h1 className="text-4xl font-bold tracking-tight text-primary mb-4">
        Voice Bot Admin
      </h1>
      <p className="text-muted-foreground text-lg mb-8">
        Modern dashboard for managing your AI Voice Assistant.
      </p>
      <div className="flex gap-4">
        {/* Placeholder for future dashboard content */}
        <div className="p-6 bg-card border rounded-lg shadow-sm w-64 text-center">
          <h3 className="font-semibold mb-2">Total Calls</h3>
          <p className="text-3xl font-bold">128</p>
        </div>
        <div className="p-6 bg-card border rounded-lg shadow-sm w-64 text-center">
          <h3 className="font-semibold mb-2">Avg Duration</h3>
          <p className="text-3xl font-bold">2m 45s</p>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
        <Toaster position="top-right" />
      </Router>
    </AuthProvider>
  );
}

export default App;
