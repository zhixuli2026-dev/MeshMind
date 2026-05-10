import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import '@meshmind/design-system/src/theme.css';
import { Dashboard } from './pages/Dashboard';
import { KnowledgePage } from './pages/KnowledgePage';
import { DocumentsPage } from './pages/DocumentsPage';
import { AnalysisPage } from './pages/AnalysisPage';
import { MembersPage } from './pages/MembersPage';
import { SettingsPage } from './pages/SettingsPage';

const sidebarStyle: React.CSSProperties = {
  width: 220, background: 'var(--color-bg-secondary)',
  borderRight: '1px solid var(--color-border-light)',
  padding: '24px 0', display: 'flex', flexDirection: 'column',
};

const linkStyle = ({ isActive }: { isActive: boolean }): React.CSSProperties => ({
  padding: '10px 24px', fontSize: 14, fontWeight: isActive ? 600 : 400,
  color: isActive ? 'var(--color-accent)' : 'var(--color-text-secondary)',
  textDecoration: 'none', background: isActive ? 'var(--color-bg-primary)' : 'transparent',
  margin: '0 12px', borderRadius: 'var(--radius-sm)',
});

const navItems = [
  { to: '/', label: 'Dashboard' },
  { to: '/knowledge', label: 'Knowledge' },
  { to: '/documents', label: 'Documents' },
  { to: '/analysis', label: 'Analysis' },
  { to: '/members', label: 'Members' },
  { to: '/settings', label: 'Settings' },
];

const App = () => (
  <div style={{ display: 'flex', height: '100vh' }}>
    <div style={sidebarStyle}>
      <h2 style={{ fontSize: 18, fontWeight: 700, padding: '0 24px', margin: '0 0 32px 0' }}>
        MeshMind
      </h2>
      {navItems.map(item => (
        <NavLink key={item.to} to={item.to} end={item.to === '/'} style={linkStyle}>
          {item.label}
        </NavLink>
      ))}
    </div>
    <div style={{ flex: 1, overflow: 'auto', padding: 32 }}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/knowledge" element={<KnowledgePage />} />
        <Route path="/documents" element={<DocumentsPage />} />
        <Route path="/analysis" element={<AnalysisPage />} />
        <Route path="/members" element={<MembersPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </div>
  </div>
);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode><BrowserRouter><App /></BrowserRouter></React.StrictMode>
);
