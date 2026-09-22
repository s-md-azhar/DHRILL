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
  const [savedStatus, setSavedStatus] = useState(false);

  const handleSave = () => {
    onSaveApiKeys({
      gemini: geminiKey.trim(),
      groq: groqKey.trim(),
      openrouter: openRouterKey.trim()
    });
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
          <span>Engine Configuration (Routing Credentials)</span>
          <button className="btn-control-icon" onClick={onClose} aria-label="Close configuration">
            <X size={14} />
          </button>
        </div>

        <div className="modal-body">
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', lineHeight: 1.5 }}>
            Configure optional external frontier API credentials for fallback escalation and compound claim arbitration. 
            All core embeddings and DeBERTa-v3 cross-encoder NLI evaluate 100% locally.
          </div>

          <div>
            <div style={{ fontSize: '10px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', marginBottom: '4px', textTransform: 'uppercase' }}>
              Gemini API Key (Primary Fallback ≤12 RPM)
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
              Groq API Key (Secondary Fallback ≤25 RPM)
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
              OpenRouter API Key (Tertiary Fallback ≤15 RPM)
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
