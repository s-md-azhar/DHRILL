import React from 'react';
import { Sliders, Activity, Sun, Moon } from 'lucide-react';

export default function Header({ health, routingTier, onOpenSettings, theme, onToggleTheme }) {
  const isCuda = health?.gpu?.cuda_available;
  const deviceLabel = isCuda 
    ? `CUDA: ${health.gpu.device_name}` 
    : (health?.gpu?.device_name ? `COMPUTE: ${health.gpu.device_name}` : "ENGINE: READY");

  const tier = routingTier || 'LOCAL-DEBERTA';

  return (
    <header className="top-control-bar">
      <div className="brand-cell">
        <img src={`${import.meta.env.BASE_URL}logo.png`} alt="DHRILL Logo" className="brand-logo-img" />
        <span className="brand-title">DHRILL</span>
        <span className="brand-sub">Forensic Grounding Workbench</span>
      </div>

      <div className="top-bar-controls">
        {/* Model Selection Readout */}
        <div className="control-group header-nli-group" title="Active NLI Model Engine">
          <span className="control-label">NLI:</span>
          <span className="mono-num hide-on-mobile" style={{ fontSize: '10.5px', color: 'var(--text-primary)' }}>
            cross-encoder/nli-deberta-v3-small
          </span>
          <span className="mono-num show-on-mobile" style={{ fontSize: '10.5px', color: 'var(--text-primary)' }}>
            deberta-v3-small
          </span>
        </div>

        {/* Arbitration Chain Status */}
        <div className="control-group" title="Configured Routing & Arbitration Tier">
          <span className="control-label">ARBITRATION:</span>
          <span className="mono-num" style={{ fontSize: '10px', color: tier === 'gemini' ? 'var(--accent-cyan)' : tier === 'cache-hit' ? 'var(--status-ambig-text)' : 'var(--status-verified-text)' }}>
            {tier.toUpperCase()}
          </span>
        </div>

        {/* Compute Acceleration Indicator */}
        <div className="status-badge-mono" title="Compute Accelerator">
          <span className="status-dot-sm" style={{ background: isCuda ? 'var(--status-verified-text)' : 'var(--text-muted)' }}></span>
          <span>{deviceLabel}</span>
        </div>

        {/* API Monospace Status Badge */}
        <div className="status-badge-mono" title="API Status">
          <Activity size={12} style={{ color: 'var(--status-verified-text)' }} />
          <span style={{ color: 'var(--status-verified-text)' }}>
            {health?.service?.includes('Standalone') ? 'STANDALONE: ACTIVE' : 'API: 200 OK'}
          </span>
        </div>

        {/* Theme Toggle (Dark / Light) */}
        <button 
          className="btn-control-icon theme-toggle-btn" 
          onClick={onToggleTheme} 
          title={theme === 'dark' ? "Switch to Light Mode" : "Switch to Dark Mode"}
          aria-label="Toggle color theme"
        >
          {theme === 'dark' ? <Sun size={13} /> : <Moon size={13} />}
        </button>

        {/* Config Modal */}
        <button 
          className="btn-control-icon" 
          onClick={onOpenSettings} 
          title="Engine Configuration & API Keys"
          aria-label="Engine configuration"
        >
          <Sliders size={13} />
        </button>
      </div>
    </header>
  );
}
