import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import BaseLayout from './components/layout/BaseLayout';
import LandingPage from './pages/LandingPage';
import PredictPage from './pages/PredictPage';
import DashboardPage from './pages/DashboardPage';

function App() {
  return (
    <Router>
      <BaseLayout>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/predict" element={<PredictPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </BaseLayout>
    </Router>
  );
}

export default App;
