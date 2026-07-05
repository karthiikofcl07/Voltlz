import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { useAuth } from './context/AuthContext.jsx';
import { SideNav, MobileTabs } from './components/Nav.jsx';
import Hero from './pages/Hero.jsx';
import Login from './pages/Login.jsx';
import Dashboard from './pages/Dashboard.jsx';
import PlanTrip from './pages/PlanTrip.jsx';
import Chargers from './pages/Chargers.jsx';
import Analytics from './pages/Analytics.jsx';
import Assistant from './pages/Assistant.jsx';
import Vehicle from './pages/Vehicle.jsx';

function Protected({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="loading-screen">Starting VoltNav intelligence layer...</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function Shell({ children }) {
  const location = useLocation();
  return (
    <Protected>
      <div className="app-shell">
        <SideNav />
        <main className="main-stage">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.28 }}
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </main>
        <MobileTabs />
      </div>
    </Protected>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/welcome" element={<Hero />} />
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Shell><Dashboard /></Shell>} />
      <Route path="/plan" element={<Shell><PlanTrip /></Shell>} />
      <Route path="/chargers" element={<Shell><Chargers /></Shell>} />
      <Route path="/analytics" element={<Shell><Analytics /></Shell>} />
      <Route path="/assistant" element={<Shell><Assistant /></Shell>} />
      <Route path="/vehicle" element={<Shell><Vehicle /></Shell>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
