import React from 'react';

export default function ClaimEvidenceList({
  claims,
  selectedClaimId,
  hoveredClaimId,
  onSelectClaim,
  onHoverClaim
}) {
  if (!claims || claims.length === 0) return null;

  return (
    <div className="matrix-container">
      <div className="matrix-header-bar">
        <span>Claim Decomposition Matrix (Atomic Propositions)</span>
        <span className="mono-num" style={{ color: 'var(--text-muted)' }}>
          {claims.length} {claims.length === 1 ? 'PROPOSITION CROSS-EXAMINED' : 'PROPOSITIONS CROSS-EXAMINED'}
        </span>
      </div>

      {/* Responsive Horizontal Scroll Wrapper for Mobile / Tablet Devices */}
      <div className="matrix-viewport-wrapper">
        {/* Grid Matrix Header (CSS Grid, Constraint 3) */}
        <div className="matrix-grid-header">
          <div>PROP ID</div>
          <div>VERDICT</div>
          <div>PROPOSITION (HYPOTHESIS)</div>
          <div>GROUND-TRUTH CITATION</div>
          <div>NLI TENSOR READOUT</div>
        </div>

        {/* Grid Matrix Scrollable Body (Constraint 1 Viewport-Locked) */}
        <div className="matrix-scroll-body">
        {claims.map((claim, idx) => {
          const isSelected = selectedClaimId === claim.claim_id;
          const isHovered = hoveredClaimId === claim.claim_id;
          const probs = claim.probabilities || {};
          const eVal = typeof probs.entailment === 'number' ? probs.entailment.toFixed(2) : '0.00';
          const nVal = typeof probs.neutral === 'number' ? probs.neutral.toFixed(2) : '0.00';
          const cVal = typeof probs.contradiction === 'number' ? probs.contradiction.toFixed(2) : '0.00';

          const claimIdStr = String(claim.claim_id || `c_${idx + 1}`);
          const propIdFormatted = claimIdStr.startsWith('c_')
            ? `[PROP-${claimIdStr.replace('c_', '').padStart(2, '0')}]`
            : `[${claimIdStr.toUpperCase()}]`;

          const conflicts = Array.isArray(claim.entity_conflicts) ? claim.entity_conflicts : [];
          const hasConflict = conflicts.length > 0;
          const firstConflict = hasConflict ? conflicts[0] : null;
          const conflictType = String(firstConflict?.discrepancy_type || firstConflict?.type || firstConflict?.entity_type || 'CONFLICT').toUpperCase();
          const conflictDesc = firstConflict?.description || 'Entity discrepancy detected against reference evidence.';

          const simScore = claim.best_evidence && typeof claim.best_evidence.similarity_score === 'number'
            ? Math.round(claim.best_evidence.similarity_score * 100)
            : null;

          const confVal = typeof claim.confidence === 'number' ? (claim.confidence * 100).toFixed(1) : '92.0';
          const verdictStr = String(claim.verdict || 'UNGROUNDED');
          const sourceStr = String(claim.arbitration_source || 'LOCAL-DEBERTA').toUpperCase();

          return (
            <div
              key={claim.claim_id || idx}
              id={`claim-card-${claim.claim_id || idx}`}
              className={`matrix-row-item ${isSelected ? 'row-selected' : ''} ${isHovered ? 'row-hovered' : ''}`}
              onClick={() => onSelectClaim && onSelectClaim(claim.claim_id)}
              onMouseEnter={() => onHoverClaim && onHoverClaim(claim.claim_id)}
              onMouseLeave={() => onHoverClaim && onHoverClaim(null)}
            >
              {/* Main Grid Row (Constraint 3) */}
              <div className="matrix-grid-row">
                {/* 1. Monospace Prop ID */}
                <div className="col-prop-id">
                  {propIdFormatted}
                </div>

                {/* 2. Matte Verdict Badge */}
                <div>
                  <span className={`col-verdict-badge ${verdictStr}`}>
                    {verdictStr}
                  </span>
                </div>

                {/* 3. Hypothesis Proposition Text (leading-relaxed 1.625) */}
                <div className="col-text" title={claim.claim_text}>
                  "{claim.claim_text || ''}"
                </div>

                {/* 4. Ground-Truth Citation Chunk (leading-relaxed 1.625) */}
                <div className="col-evidence">
                  {claim.best_evidence ? (
                    <div>
                      <span className="mono-num" style={{ fontSize: '10.5px', color: 'var(--accent-cyan)', marginRight: '6px' }}>
                        [{claim.best_evidence.passage_id || 'p_00'} · {simScore !== null ? `${simScore}% match` : 'match'}]
                      </span>
                      <span>"{claim.best_evidence.text || ''}"</span>
                    </div>
                  ) : (
                    <span className="mono-num" style={{ color: 'var(--text-muted)' }}>
                      [NO_REFERENCE_SUPPLIED · OPEN_WORLD]
                    </span>
                  )}
                </div>

                {/* 5. Monospace NLI Tensor String: E: 0.00 | N: 0.10 | C: 0.95 */}
                <div className="col-tensor-readout">
                  <span>
                    <span style={{ color: 'var(--text-muted)' }}>E:</span>{' '}
                    <span className="tensor-val-entail mono-num">{eVal}</span>
                  </span>
                  <span style={{ color: 'var(--border-active)' }}>|</span>
                  <span>
                    <span style={{ color: 'var(--text-muted)' }}>N:</span>{' '}
                    <span className="tensor-val-neut mono-num">{nVal}</span>
                  </span>
                  <span style={{ color: 'var(--border-active)' }}>|</span>
                  <span>
                    <span style={{ color: 'var(--text-muted)' }}>C:</span>{' '}
                    <span className="tensor-val-contra mono-num">{cVal}</span>
                  </span>
                </div>
              </div>

              {/* Softened Compiler Log Trace (Refactor 4) */}
              {(hasConflict || isSelected || verdictStr !== 'VERIFIED') && (
                <div className="compiler-log-drawer">
                  {hasConflict && (
                    <div className="compiler-log-header">
                      <span>[ERR: {conflictType}]</span>
                      <span>{conflictDesc}</span>
                    </div>
                  )}

                  <div className="compiler-log-body">
                    <span style={{ color: 'var(--text-muted)' }}>[NLI ARBITRATION]</span>{' '}
                    <span className="mono-num" style={{ color: 'var(--text-primary)' }}>
                      Source: {sourceStr} · Confidence: {confVal}%
                    </span>
                    <div style={{ marginTop: '3px', color: 'var(--compiler-text)' }}>
                      <span style={{ color: 'var(--text-muted)' }}>TRACE:</span> {claim.explanation || 'Proposition evaluated against grounding baseline.'}
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
      </div>
    </div>
  );
}
