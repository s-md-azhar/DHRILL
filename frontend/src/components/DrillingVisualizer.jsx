import React, { useState, useEffect } from 'react';

const EXECUTION_LOGS = [
  "INITIALIZING NLI ENGINE [cross-encoder/nli-deberta-v3-small]...",
  "PARSING SYNTACTIC CLAUSES · ISOLATING ATOMIC PROPOSITIONS...",
  "INDEXING REFERENCE CONTEXT · COMPUTING MINI-LM-L6 EMBEDDINGS (384-D)...",
  "SYMBOLIC SIEVE: EXTRACTING SCALAR, TEMPORAL & NUMERIC COHORTS...",
  "COMPUTING CROSS-ATTENTION TENSOR PAIRS [PREMISE x HYPOTHESIS]...",
  "EVALUATING ARBITRATION GATEWAY: P(NEUTRAL) >= 0.60 CALIBRATION...",
  "FUSING HEURISTICS & FORMULATING CLAIM DECOMPOSITION MATRIX..."
];

export default function DrillingVisualizer() {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev < EXECUTION_LOGS.length - 1 ? prev + 1 : prev));
    }, 450);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="execution-trace-container">
      <div className="execution-trace-console">
        <div className="console-title-bar">
          <span>Pipeline Execution Trace (NLI Tensor Runtime)</span>
          <span className="mono-num">STAGE {activeStep + 1}/{EXECUTION_LOGS.length}</span>
        </div>
        <div className="console-body">
          {EXECUTION_LOGS.slice(0, activeStep + 1).map((log, index) => {
            const isCurrent = index === activeStep;
            return (
              <div key={index} className={`console-line ${isCurrent ? 'console-active-line' : ''}`}>
                <span className="console-prompt">&gt;&gt;</span>
                <span>{log}</span>
                {isCurrent && <span className="console-cursor" />}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
