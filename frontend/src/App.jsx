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

class WorkbenchErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("[DHRILL Workbench Error Intercepted]", error, errorInfo);
  }

  componentDidUpdate(prevProps) {
    if (prevProps.resetKey !== this.props.resetKey && this.state.hasError) {
      this.setState({ hasError: false, error: null });
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) this.props.onReset();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="empty-workbench-state" style={{ borderColor: 'rgba(239, 68, 68, 0.4)', background: 'rgba(239, 68, 68, 0.04)' }}>
          <div className="empty-workbench-icon" style={{ color: '#ef4444' }}>
            <Terminal size={22} />
          </div>
          <div className="empty-workbench-title" style={{ color: '#ef4444' }}>
            Visualizer Standby (Cross-Examination Anomaly Intercepted)
          </div>
          <div className="empty-workbench-desc">
            An unexpected condition occurred while displaying the proposition matrix ({this.state.error?.message || 'Verification Error'}). The workbench isolated the state to keep the workspace responsive.
          </div>
          <div style={{ marginTop: '14px' }}>
            <button
              className="btn-reset-workspace"
              style={{ padding: '6px 14px', fontSize: '12px' }}
              onClick={this.handleReset}
            >
              Reset Workbench
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  const [health, setHealth] = useState(null);
  const [demoCases, setDemoCases] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [userDraft, setUserDraft] = useState(null);

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
    // Save draft if user was working on custom text before selecting a preset
    if (!selectedCaseId && (responseText.trim() || referenceContext.trim())) {
      setUserDraft({
        responseText,
        referenceContext,
        prompt
      });
    }

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

  // When a preset scenario is un-clicked / toggled off, restore user's previous progress
  const handleToggleOffScenario = () => {
    setSelectedCaseId(null);
    setSelectedClaimId(null);
    setHoveredClaimId(null);
    setInspectionResult(null);

    if (userDraft) {
      setResponseText(userDraft.responseText || '');
      setReferenceContext(userDraft.referenceContext || '');
      setPrompt(userDraft.prompt || '');
      setUserDraft(null); // Consumed
    } else {
      setResponseText('');
      setReferenceContext('');
      setPrompt('');
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
    setUserDraft(null); // Clear any saved draft progress on explicit reset
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
            setSelectedCaseId={setSelectedCaseId}
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
            onToggleOffScenario={handleToggleOffScenario}
          />

          {/* Lower Half: Pipeline Trace / Results / Empty State */}
          <WorkbenchErrorBoundary
            resetKey={`${selectedCaseId || 'custom'}_${responseText.length}_${inspectionResult?.inspection_id || 'none'}`}
            onReset={handleReset}
          >
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
          </WorkbenchErrorBoundary>
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
