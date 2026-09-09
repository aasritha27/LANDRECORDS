import React, { useState, useEffect } from 'react';
import { getDocuments } from '../api/client';
import { LayoutDashboard, CheckCircle2, Clock, AlertTriangle, FileCheck, TrendingUp, Cpu } from 'lucide-react';

export default function Dashboard() {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        setLoading(true);
        const data = await getDocuments();
        setDocs(data);
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  const totalProcessed = docs.length;
  const needsReview = docs.filter(d => d.status === 'needs_review').length;
  const autoValidated = docs.filter(d => d.status === 'auto_validated' || d.status === 'verified').length;
  const avgConfidence = totalProcessed > 0
    ? (docs.reduce((acc, curr) => acc + curr.overall_confidence, 0) / totalProcessed * 100).toFixed(1)
    : '0.0';

  return (
    <div className="max-w-7xl mx-auto px-6 py-4 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2 font-outfit">
          <LayoutDashboard className="w-6 h-6 text-emerald-400" />
          Land Record Digitization & Validation Analytics
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Real-time operational metrics, AI confidence scoring throughput, and verifier queue status.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        
        <div className="glass-panel p-6 space-y-2 border-l-4 border-l-cyan-500">
          <div className="flex justify-between items-center text-slate-400 text-xs">
            <span>Total Ingested Scans</span>
            <FileCheck className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-3xl font-bold text-white font-mono">{totalProcessed}</p>
          <p className="text-[11px] text-cyan-400 flex items-center gap-1">
            <TrendingUp className="w-3 h-3" /> Live Pipeline Activity
          </p>
        </div>

        <div className="glass-panel p-6 space-y-2 border-l-4 border-l-emerald-500">
          <div className="flex justify-between items-center text-slate-400 text-xs">
            <span>Auto Validated & Verified</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-3xl font-bold text-white font-mono">{autoValidated}</p>
          <p className="text-[11px] text-emerald-400">
            {totalProcessed > 0 ? `${((autoValidated / totalProcessed) * 100).toFixed(0)}% auto-pass rate` : '0%'}
          </p>
        </div>

        <div className="glass-panel p-6 space-y-2 border-l-4 border-l-amber-500">
          <div className="flex justify-between items-center text-slate-400 text-xs">
            <span>Pending Review Queue</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-3xl font-bold text-white font-mono">{needsReview}</p>
          <p className="text-[11px] text-amber-400">Awaiting verifier approval</p>
        </div>

        <div className="glass-panel p-6 space-y-2 border-l-4 border-l-indigo-500">
          <div className="flex justify-between items-center text-slate-400 text-xs">
            <span>Avg OCR/NLP Confidence</span>
            <Cpu className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-3xl font-bold text-white font-mono">{avgConfidence}%</p>
          <p className="text-[11px] text-indigo-400">Weighted model score</p>
        </div>

      </div>

      {/* System Status & Processing Logs */}
      <div className="glass-panel p-6 space-y-4">
        <h2 className="text-base font-semibold text-white font-outfit">Pipeline Operational Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-2">
            <span className="font-semibold text-slate-300">OCR Engine</span>
            <p className="text-slate-400">Tesseract 5.3 + PaddleOCR Dual Path</p>
            <span className="badge badge-auto_validated">Active</span>
          </div>
          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-2">
            <span className="font-semibold text-slate-300">Rules Engine</span>
            <p className="text-slate-400">RapidFuzz Village Lookup + Format Rules</p>
            <span className="badge badge-auto_validated">Active</span>
          </div>
          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-2">
            <span className="font-semibold text-slate-300">PostGIS Canonical Database</span>
            <p className="text-slate-400">PostgreSQL 15 + PostGIS Spatial Engine</p>
            <span className="badge badge-auto_validated">Active</span>
          </div>
        </div>
      </div>
    </div>
  );
}
