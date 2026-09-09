import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { UploadCloud, CheckCircle2, LayoutDashboard, Map, ShieldCheck, Landmark } from 'lucide-react';

export default function Navbar() {
  const location = useLocation();

  const navItems = [
    { label: 'Ingest Scan', path: '/', icon: UploadCloud },
    { label: 'Review Queue', path: '/review', icon: CheckCircle2 },
    { label: 'GIS Parcel Map', path: '/map', icon: Map },
    { label: 'Analytics Dashboard', path: '/dashboard', icon: LayoutDashboard },
  ];

  return (
    <header className="gov-navbar">
      <div className="gov-navbar-inner">
        
        {/* Government Brand & Crest Logo */}
        <Link to="/" className="gov-brand">
          <div className="gov-emblem">
            <Landmark size={24} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="gov-title">BhuDrishti</span>
              <span style={{
                background: 'rgba(16, 185, 129, 0.15)',
                color: '#34d399',
                fontSize: '10px',
                fontWeight: '700',
                padding: '2px 8px',
                borderRadius: '9999px',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                textTransform: 'uppercase'
              }}>
                Govt. Portal
              </span>
            </div>
            <p className="gov-subtitle">
              Land Record Digitization & Validation Portal
            </p>
          </div>
        </Link>

        {/* Navigation Menu */}
        <nav className="nav-menu">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${isActive ? 'active' : ''}`}
              >
                <Icon size={16} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Official User Info */}
        <div className="user-badge">
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.8rem', fontWeight: '700', color: '#ffffff' }}>
              Revenue Dept. Officer
            </div>
            <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
              Verifier Level 2 (MP)
            </div>
          </div>
          <div className="user-avatar">
            RO
          </div>
        </div>

      </div>
    </header>
  );
}
