import React, { useState } from 'react';
import { Map, Layers, Search, Info, MapPin } from 'lucide-react';

export default function MapView() {
  const [selectedParcel, setSelectedParcel] = useState({
    khasra: "142/1",
    village: "Rampur",
    tehsil: "Sadar",
    district: "Bhopal",
    owner: "Ramesh Chandra Sharma",
    area: "1.450 Hectares",
    status: "Verified in PostGIS"
  });

  return (
    <div className="max-w-7xl mx-auto px-6 py-4 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2 font-outfit">
            <Map className="w-6 h-6 text-cyan-400" />
            GIS Parcel Spatial Viewer (PostGIS Layer)
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Visual map rendering digitized parcel boundaries cross-referenced with DILRMP cadastral vector data.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Mock Map Canvas */}
        <div className="lg:col-span-2 glass-panel p-4 flex flex-col h-[600px] relative overflow-hidden">
          <div className="absolute top-6 left-6 z-10 bg-slate-950/80 backdrop-blur-md border border-slate-800 rounded-lg p-2 flex items-center gap-2 text-xs">
            <Layers className="w-4 h-4 text-emerald-400" />
            <span className="font-semibold text-white">Layer: Cadastral Parcels</span>
          </div>

          {/* Interactive Graphic Representation of Spatial Parcels */}
          <div className="w-full h-full bg-slate-950 rounded-xl border border-slate-800 relative flex items-center justify-center p-6 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px]">
            <svg className="w-full h-full max-w-lg max-h-96" viewBox="0 0 500 400">
              {/* Parcel 1 */}
              <polygon
                points="50,50 220,40 240,180 60,200"
                fill="rgba(16, 185, 129, 0.25)"
                stroke="#10b981"
                strokeWidth="2"
                className="cursor-pointer hover:fill-emerald-500/40 transition-colors"
                onClick={() => setSelectedParcel({
                  khasra: "142/1",
                  village: "Rampur",
                  tehsil: "Sadar",
                  district: "Bhopal",
                  owner: "Ramesh Chandra Sharma",
                  area: "1.450 Hectares",
                  status: "Verified in PostGIS"
                })}
              />
              <text x="120" y="120" fill="#34d399" fontSize="12" fontWeight="bold">Khasra 142/1</text>

              {/* Parcel 2 */}
              <polygon
                points="240,40 430,60 410,220 250,180"
                fill="rgba(6, 182, 212, 0.25)"
                stroke="#06b6d4"
                strokeWidth="2"
                className="cursor-pointer hover:fill-cyan-500/40 transition-colors"
                onClick={() => setSelectedParcel({
                  khasra: "142/2",
                  village: "Rampur",
                  tehsil: "Sadar",
                  district: "Bhopal",
                  owner: "Sunita Devi",
                  area: "0.980 Hectares",
                  status: "Verified in PostGIS"
                })}
              />
              <text x="310" y="130" fill="#22d3ee" fontSize="12" fontWeight="bold">Khasra 142/2</text>

              {/* Parcel 3 */}
              <polygon
                points="60,200 250,180 230,350 80,360"
                fill="rgba(99, 102, 241, 0.25)"
                stroke="#6366f1"
                strokeWidth="2"
                className="cursor-pointer hover:fill-indigo-500/40 transition-colors"
                onClick={() => setSelectedParcel({
                  khasra: "143/A",
                  village: "Rampur",
                  tehsil: "Sadar",
                  district: "Bhopal",
                  owner: "Vikram Singh",
                  area: "2.100 Hectares",
                  status: "Verified in PostGIS"
                })}
              />
              <text x="130" y="270" fill="#818cf8" fontSize="12" fontWeight="bold">Khasra 143/A</text>
            </svg>
          </div>
        </div>

        {/* Selected Parcel Details Panel */}
        <div className="glass-panel p-6 space-y-6">
          <h2 className="text-base font-semibold text-white flex items-center gap-2 font-outfit">
            <Info className="w-5 h-5 text-cyan-400" />
            Parcel Spatial Attributes
          </h2>

          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-3 text-xs">
            <div className="flex justify-between py-1 border-b border-slate-800">
              <span className="text-slate-400">Khasra / Plot No</span>
              <span className="font-mono text-emerald-400 font-bold">{selectedParcel.khasra}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800">
              <span className="text-slate-400">Owner Name</span>
              <span className="text-white font-medium">{selectedParcel.owner}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800">
              <span className="text-slate-400">Village / Tehsil</span>
              <span className="text-slate-200">{selectedParcel.village}, {selectedParcel.tehsil}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800">
              <span className="text-slate-400">District</span>
              <span className="text-slate-200">{selectedParcel.district}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800">
              <span className="text-slate-400">Parcel Land Area</span>
              <span className="font-mono text-cyan-400 font-semibold">{selectedParcel.area}</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">Database Status</span>
              <span className="badge badge-auto_validated">{selectedParcel.status}</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
