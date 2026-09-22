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
        {claims.map((claim) => {
          const isSelected = selectedClaimId === claim.claim_id;
          const isHovered = hoveredClaimId === claim.claim_id;
          const probs = claim.probabilities || { entailment: 0, neutral: 0, contradiction: 0 };
          const eVal = probs.entailment.toFixed(2);
          const nVal = probs.neutral.toFixed(2);
          const cVal = probs.contradiction.toFixed(2);

          const propIdFormatted = claim.claim_id.startsWith('c_')
            ? `[PROP-${claim.claim_id.replace('c_', '').padStart(2, '0')}]`
            : `[${claim.claim_id.toUpperCase()}]`;

          const hasConflict = claim.entity_conflicts && claim.entity_conflicts.length > 0;
          const simScore = claim.best_evidence ? Math.round(claim.best_evidence.similarity_score * 100) : null;

          return (
            <div
              key={claim.claim_id}
              id={`claim-card-${claim.claim_id}`}
              className={`matrix-row-item ${isSelected ? 'row-selected' : ''} ${isHovered ? 'row-hovered' : ''}`}
              onClick={() => onSelectClaim(claim.claim_id)}
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
                  <span className={`col-verdict-badge ${claim.verdict}`}>
                    {claim.verdict}
                  </span>
                </div>

                {/* 3. Hypothesis Proposition Text (leading-relaxed 1.625) */}
                <div className="col-text" title={claim.claim_text}>
                  "{claim.claim_text}"
                </div>

                {/* 4. Ground-Truth Citation Chunk (leading-relaxed 1.625) */}
                <div className="col-evidence">
                  {claim.best_evidence ? (
                    <div>
                      <span className="mono-num" style={{ fontSize: '10.5px', color: 'var(--accent-cyan)', marginRight: '6px' }}>
                        [{claim.best_evidence.passage_id} · {simScore}% match]
                      </span>
                      <span>"{claim.best_evidence.text}"</span>
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
              {(hasConflict || isSelected || claim.verdict !== 'VERIFIED') && (
                <div className="compiler-log-drawer">
                  {hasConflict && (
                    <div className="compiler-log-header">
                      <span>[ERR: {claim.entity_conflicts[0].discrepancy_type.toUpperCase()}]</span>
                      <span>{claim.entity_conflicts[0].description}</span>
                    </div>
                  )}

                  <div className="compiler-log-body">
                    <span style={{ color: 'var(--text-muted)' }}>[NLI ARBITRATION]</span>{' '}
                    <span className="mono-num" style={{ color: 'var(--text-primary)' }}>
                      Source: {claim.arbitration_source?.toUpperCase() || 'LOCAL-DEBERTA'} · Confidence: {(claim.confidence * 100).toFixed(1)}%
                    </span>
                    <div style={{ marginTop: '3px', color: 'var(--compiler-text)' }}>
                      <span style={{ color: 'var(--text-muted)' }}>TRACE:</span> {claim.explanation}
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
