import React, { useState, useRef, useEffect } from 'react';
import { Play } from 'lucide-react';

export default function InspectionInput({
  demoCases,
  selectedCaseId,
  onSelectCase,
  responseText,
  setResponseText,
  referenceContext,
  setReferenceContext,
  prompt,
  setPrompt,
  onDrill,
  loading
}) {
  // Functional Resizable Split-Pane (Constraint 2)
  const [splitRatio, setSplitRatio] = useState(0.5);
  const [isResizing, setIsResizing] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const newRatio = (e.clientX - rect.left) / rect.width;
      setSplitRatio(Math.min(Math.max(newRatio, 0.20), 0.80));
    };

    const handleMouseUp = () => {
      if (isResizing) {
        setIsResizing(false);
        document.body.style.cursor = 'default';
        document.body.style.userSelect = 'auto';
      }
    };

    if (isResizing) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  const leftWords = responseText.trim() ? responseText.trim().split(/\s+/).length : 0;
  const rightWords = referenceContext.trim() ? referenceContext.trim().split(/\s+/).length : 0;

  // Curated Preset Formatting with Judicious Functional Emojis (Refactor 3)
  const getPresetConfig = (c) => {
    const id = c.case_id.toLowerCase();
    const cat = (c.category || '').toLowerCase();

    if (id.includes('clinical') || cat === 'medical') {
      return { emoji: "💊", label: "Clinical Pharmacology" };
    }
    if (id.includes('historical') || cat === 'history') {
      return { emoji: "🏛️", label: "Historical Record" };
    }
    if (id.includes('earnings') || cat === 'finance') {
      return { emoji: "📊", label: "Financial Intelligence" };
    }
    if (id.includes('scientific') || cat === 'science') {
      return { emoji: "🧬", label: "Scientific Fabrication" };
    }
    return { emoji: "📄", label: c.title.split(':')[0] || "Custom Benchmark" };
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
      {/* Resizable Split-Pane Container */}
      <div 
        ref={containerRef} 
        className="split-editor-section"
        style={{ height: '250px' }}
      >
        {/* Pane A: Raw Inference (Model Hypothesis) */}
        <div 
          className="editor-pane"
          style={{ width: `calc(${splitRatio * 100}% - 4.5px)` }}
        >
          <div className="pane-header">
            <span>Raw Model Inference (Hypothesis)</span>
            <span className="pane-tag mono-num">
              {leftWords} WORDS · {responseText.length} CHARS
            </span>
          </div>
          <div className="pane-body">
            <textarea
              className="editor-textarea"
              value={responseText}
              onChange={(e) => setResponseText(e.target.value)}
              placeholder="Paste raw model generation to cross-examine and extract atomic propositions..."
              spellCheck={false}
            />
          </div>
        </div>

        {/* Resizable Divider Handle (Constraint 2) */}
        <div
          className={`split-pane-resizer ${isResizing ? 'resizing' : ''}`}
          onMouseDown={() => setIsResizing(true)}
          title="Drag to resize split panes"
        />

        {/* Pane B: Ground-Truth Reference Chunk */}
        <div 
          className="editor-pane"
          style={{ width: `calc(${(1 - splitRatio) * 100}% - 4.5px)` }}
        >
          <div className="pane-header">
            <span>Ground-Truth Reference Context (Premise)</span>
            <span className="pane-tag mono-num">
              {referenceContext ? `${rightWords} WORDS · ${referenceContext.length} CHARS` : 'OPTIONAL (RAG CHUNK)'}
            </span>
          </div>
          <div className="pane-body">
            <textarea
              className="editor-textarea"
              value={referenceContext}
              onChange={(e) => setReferenceContext(e.target.value)}
              placeholder="Paste authoritative source document, trial protocol, or retrieved RAG context for micro-indexing..."
              spellCheck={false}
            />
          </div>
        </div>
      </div>

      {/* Preset Action Strip with Functional Emojis & Crisp White CTA */}
      <div className="workbench-action-strip">
        <div className="preset-chip-row">
          <span className="preset-label">BENCHMARK PRESETS:</span>
          {demoCases.map((c) => {
            const { emoji, label } = getPresetConfig(c);
            return (
              <button
                key={c.case_id}
                className={`preset-chip-btn ${selectedCaseId === c.case_id ? 'active' : ''}`}
                onClick={() => onSelectCase(c)}
                title={c.title}
              >
                <span>{emoji}</span>
                <span>{label}</span>
              </button>
            );
          })}
        </div>

        {/* Crisp White Primary Action Button (Refactor 5) */}
        <button
          className="btn-execute-nli"
          onClick={onDrill}
          disabled={loading || !responseText.trim()}
          title="Execute local DeBERTa-v3 cross-encoder and symbolic verification"
        >
          <Play size={13} fill="currentColor" />
          <span>{loading ? "EXECUTING NLI PIPELINE..." : "Execute NLI Verification"}</span>
        </button>
      </div>
    </div>
  );
}
