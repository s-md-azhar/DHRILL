import React, { useState } from 'react';
import { X, Trash2, Check } from 'lucide-react';

export default function SettingsModal({
  isOpen,
  onClose,
  apiKeys,
  onSaveApiKeys,
  onClearCache
}) {
  if (!isOpen) return null;

  const [geminiKey, setGeminiKey] = useState(apiKeys.gemini || '');
  const [groqKey, setGroqKey] = useState(apiKeys.groq || '');
  const [openRouterKey, setOpenRouterKey] = useState(apiKeys.openrouter || '');
  const [apiUrl, setApiUrl] = useState(() => localStorage.getItem('dhrill_api_url') || '');
  const [savedStatus, setSavedStatus] = useState(false);

  const handleSave = () => {
    onSaveApiKeys({
      gemini: geminiKey.trim(),
      groq: groqKey.trim(),
      openrouter: openRouterKey.trim()
    });
    if (apiUrl.trim()) {
      localStorage.setItem('dhrill_api_url', apiUrl.trim());
    } else {
      localStorage.removeItem('dhrill_api_url');
    }
    setSavedStatus(true);
    setTimeout(() => {
      setSavedStatus(false);
      onClose();
    }, 500);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span>Engine Configuration & Credentials</span>
          <button className="btn-control-icon" onClick={onClose} aria-label="Close configuration">
            <X size={14} />
          </button>
        </div>

        <div className="modal-body">
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', lineHeight: 1.5, background: 'var(--bg-card)', padding: '8px 10px', borderRadius: '4px', border: '1px solid var(--border-grid)' }}>
            <span style={{ color: 'var(--status-verified-text)', fontWeight: 'bold' }}>ZERO-CONFIG RUNTIME:</span> Core NLI decomposition and all benchmark presets operate without any API keys. Any credentials entered here remain strictly sandboxed in your browser's private localStorage.
          </div>

          <div>
            <div style={{ fontSize: '10px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', marginBottom: '4px', textTransform: 'uppercase' }}>
              Custom Backend API Endpoint (Optional)
            </div>
            <input
              type="text"
              className="input-field-mono"
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              placeholder="e.g. https://dhrill-backend.onrender.com or leave blank for /api"
            />
          </div>

          <div>
            <div style={{ fontSize: '10px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', marginBottom: '4px', textTransform: 'uppercase' }}>
              Gemini API Key (Optional Fallback Arbitration ≤12 RPM)
            </div>
            <input
              type="password"
              className="input-field-mono"
              value={geminiKey}
              onChange={(e) => setGeminiKey(e.target.value)}
              placeholder="AQ.Ab8..."
            />
          </div>

          <div>
            <div style={{ fontSize: '10px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', marginBottom: '4px', textTransform: 'uppercase' }}>
              Groq API Key (Optional Fallback Arbitration ≤25 RPM)
            </div>
            <input
              type="password"
              className="input-field-mono"
              value={groqKey}
              onChange={(e) => setGroqKey(e.target.value)}
              placeholder="gsk_..."
            />
          </div>

          <div>
            <div style={{ fontSize: '10px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', marginBottom: '4px', textTransform: 'uppercase' }}>
              OpenRouter API Key (Optional Fallback Arbitration ≤15 RPM)
            </div>
            <input
              type="password"
              className="input-field-mono"
              value={openRouterKey}
              onChange={(e) => setOpenRouterKey(e.target.value)}
              placeholder="sk-or-v1-..."
            />
          </div>

          <div style={{ borderTop: '1px solid var(--border-grid)', paddingTop: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <button
              className="btn-secondary"
              style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--status-contra-text)' }}
              onClick={onClearCache}
              title="Purge SHA-256 L1 and L2 Memory Caches"
            >
              <Trash2 size={12} />
              <span>PURGE CACHE</span>
            </button>

            <button
              className="btn-primary-sharp"
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
              onClick={handleSave}
            >
              {savedStatus ? (
                <>
                  <Check size={13} color="#86EFAC" />
                  <span>CREDENTIALS STORED</span>
                </>
              ) : (
                <span>STORE CREDENTIALS</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
