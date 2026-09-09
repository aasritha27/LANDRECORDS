import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Upload from './pages/Upload';
import ReviewQueue from './pages/ReviewQueue';
import RecordDetail from './pages/RecordDetail';
import Dashboard from './pages/Dashboard';
import MapView from './pages/MapView';

export default function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
        <Navbar />
        <main className="flex-1 pb-12">
          <Routes>
            <Route path="/" element={<Upload />} />
            <Route path="/review" element={<ReviewQueue />} />
            <Route path="/review/:id" element={<RecordDetail />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/map" element={<MapView />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
