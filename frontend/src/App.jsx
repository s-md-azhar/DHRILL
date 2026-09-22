import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import InspectionInput from './components/InspectionInput';
import DrillingVisualizer from './components/DrillingVisualizer';
import HallucinationRadar from './components/HallucinationRadar';
import SpanHighlighter from './components/SpanHighlighter';
import ClaimEvidenceList from './components/ClaimEvidenceList';
import SettingsModal from './components/SettingsModal';
import { fetchHealth, fetchDemoCases, inspectGeneration, inspectDemoCase } from './services/api';
import { Terminal } from 'lucide-react';

export default function App() {
  const [health, setHealth] = useState(null);
  const [demoCases, setDemoCases] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState(null);

  const [responseText, setResponseText] = useState('');
  const [referenceContext, setReferenceContext] = useState('');
  const [prompt, setPrompt] = useState('');

  const [loading, setLoading] = useState(false);
  const [inspectionResult, setInspectionResult] = useState(null);
  
  // State for Bi-Directional Hover (Constraint 4)
  const [selectedClaimId, setSelectedClaimId] = useState(null);
  const [hoveredClaimId, setHoveredClaimId] = useState(null);

  const [settingsOpen, setSettingsOpen] = useState(false);

  // Theme Management (Dark / Light)
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem('dhrill_theme') || 'dark';
    } catch {
      return 'dark';
    }
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    try {
      localStorage.setItem('dhrill_theme', theme);
    } catch {
      // Storage fallback
    }
  }, [theme]);

  const handleToggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const [apiKeys, setApiKeys] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('dhrill_api_keys') || '{}');
    } catch {
      return {};
    }
  });

  // Fetch health and demo presets on mount
  useEffect(() => {
    async function init() {
      const h = await fetchHealth();
      setHealth(h);

      const cases = await fetchDemoCases();
      setDemoCases(cases);
      // Clean initial state: let user view intuitive placeholders and select a benchmark preset
    }
    init();
  }, []);

  const handleSelectCase = async (caseItem) => {
    setSelectedCaseId(caseItem.case_id);
    setResponseText(caseItem.response_text);
    setReferenceContext(caseItem.reference_context);
    setPrompt(caseItem.prompt);
    setSelectedClaimId(null);
    setHoveredClaimId(null);

    // Try to load precomputed instant demo
    try {
      const precomputed = await inspectDemoCase(caseItem.case_id);
      setInspectionResult(precomputed);
    } catch {
      setInspectionResult(null);
    }
  };

  const handleDrill = async () => {
    if (!responseText.trim()) return;

    setLoading(true);
    setSelectedClaimId(null);
    setHoveredClaimId(null);

    try {
      const result = await inspectGeneration({
        response_text: responseText,
        reference_context: referenceContext.trim() || undefined,
        prompt: prompt.trim() || undefined,
        use_cache: true,
        custom_api_keys: apiKeys
      });
      const tier = result.routing_tier || result.telemetry?.routing_tier || (result.cached ? 'cache-hit' : 'local-only');
      console.log(`%c[DHRILL Router]%c Handled via: %c${tier.toUpperCase()}%c | Latency: ${result.latency_ms}ms | Cached: ${result.cached}`,
        'color: #f59e0b; font-weight: bold;',
        'color: #94a3b8;',
        'color: #10b981; font-weight: bold; font-size: 1.1em;',
        'color: #94a3b8;',
        result.telemetry
      );
      setInspectionResult(result);
    } catch (err) {
      alert(`NLI Verification Pipeline Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedCaseId(null);
    setResponseText('');
    setReferenceContext('');
    setPrompt('');
    setInspectionResult(null);
    setSelectedClaimId(null);
    setHoveredClaimId(null);
  };

  const handleSaveApiKeys = (keys) => {
    setApiKeys(keys);
    localStorage.setItem('dhrill_api_keys', JSON.stringify(keys));
  };

  const handleClearCache = async () => {
    try {
      await fetch('/api/cache/clear', { method: 'POST' });
      alert("L1 and L2 Memory Caches purged.");
    } catch (err) {
      alert(`Clear cache failed: ${err.message}`);
    }
  };

  return (
    <div className="root-frame" data-theme={theme}>
      <div className="workbench-window">
        {/* 1. Top Control Bar */}
        <Header
          health={health}
          routingTier={inspectionResult?.routing_tier}
          onOpenSettings={() => setSettingsOpen(true)}
          theme={theme}
          onToggleTheme={handleToggleTheme}
        />

        {/* 2. Telemetry Strip (Compact Monospace Ribbon) */}
        <HallucinationRadar
          metrics={inspectionResult?.metrics}
          latencyMs={inspectionResult?.latency_ms}
          cached={inspectionResult?.cached}
          deviceUsed={inspectionResult?.device_used || 'cpu'}
          routingTier={inspectionResult?.routing_tier}
        />

        {/* 3. Main Body */}
        <div className="workbench-body">
          {/* Upper Half: Split-Pane Editor */}
          <InspectionInput
            demoCases={demoCases}
            selectedCaseId={selectedCaseId}
            onSelectCase={handleSelectCase}
            responseText={responseText}
            setResponseText={setResponseText}
            referenceContext={referenceContext}
            setReferenceContext={setReferenceContext}
            prompt={prompt}
            setPrompt={setPrompt}
            onDrill={handleDrill}
            loading={loading}
            onReset={handleReset}
          />

          {/* Lower Half: Pipeline Trace / Results / Empty State */}
          {loading ? (
            <DrillingVisualizer />
          ) : inspectionResult ? (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              {/* Inference Stream Highlighter */}
              <SpanHighlighter
                fullText={responseText}
                spans={inspectionResult.annotated_spans}
                selectedClaimId={selectedClaimId}
                hoveredClaimId={hoveredClaimId}
                onSelectClaim={(id) => {
                  setSelectedClaimId(id);
                  const el = document.getElementById(`claim-card-${id}`);
                  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }}
                onHoverClaim={setHoveredClaimId}
              />

              {/* Claim Decomposition Matrix (CSS Grid, Viewport-Locked) */}
              <ClaimEvidenceList
                claims={inspectionResult.claims}
                selectedClaimId={selectedClaimId}
                hoveredClaimId={hoveredClaimId}
                onSelectClaim={setSelectedClaimId}
                onHoverClaim={setHoveredClaimId}
              />
            </div>
          ) : (
            <div className="empty-workbench-state">
              <div className="empty-workbench-icon">
                <Terminal size={22} />
              </div>
              <div className="empty-workbench-title">Workbench Standby (No Active Inference)</div>
              <div className="empty-workbench-desc">
                Select a benchmark preset from the action strip or supply custom raw inference text and reference documentation to execute cross-attention NLI verification.
              </div>
            </div>
          )}
        </div>

        {/* 4. Configuration Modal */}
        <SettingsModal
          isOpen={settingsOpen}
          onClose={() => setSettingsOpen(false)}
          apiKeys={apiKeys}
          onSaveApiKeys={handleSaveApiKeys}
          onClearCache={handleClearCache}
        />
      </div>
    </div>
  );
}
