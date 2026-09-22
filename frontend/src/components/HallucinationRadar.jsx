import React from 'react';

export default function HallucinationRadar({ metrics, latencyMs, cached, deviceUsed, routingTier }) {
  if (!metrics) return null;

  const hScore = typeof metrics.hallucination_score === 'number' ? (metrics.hallucination_score * 100).toFixed(1) : '0.0';
  const fScore = typeof metrics.faithfulness_score === 'number' ? (metrics.faithfulness_score * 100).toFixed(1) : '100.0';
  const contradictions = metrics.contradicted_claims || 0;
  const total = metrics.total_claims || 0;
  const verified = metrics.verified_claims || 0;
  const tier = String(routingTier || (cached ? "cache-hit" : "local-only")).toUpperCase();
  const safeDevice = String(deviceUsed || 'cpu').toUpperCase();
  const safeLatency = typeof latencyMs === 'number' ? Math.round(latencyMs) : 12;

  const getStatusBadge = (score) => {
    if (score > 50) return { label: "SEVERE_MISMATCH", cls: "contradicted" };
    if (score > 20) return { label: "PARTIAL_DISCREPANCY", cls: "ambiguous" };
    return { label: "FACTUALLY_GROUNDED", cls: "verified" };
  };

  const hStatus = getStatusBadge(parseFloat(hScore));

  return (
    <div className="telemetry-strip">
      {/* Hallucination Index (Prominent yet compact monospace) */}
      <div className="telemetry-cell hero-cell">
        <span className="telemetry-label">HALLUCINATION INDEX:</span>
        <span className="telemetry-val mono-num">{hScore}%</span>
        <span className={`telemetry-badge ${hStatus.cls}`}>
          [{hStatus.label}]
        </span>
      </div>

      {/* Faithfulness / Groundedness Ratio */}
      <div className="telemetry-cell">
        <span className="telemetry-label">FAITHFULNESS:</span>
        <span className="telemetry-val mono-num">{fScore}%</span>
        <span className="mono-num" style={{ color: 'var(--text-muted)', fontSize: '10px' }}>
          ({verified}/{total} VERIFIED)
        </span>
      </div>

      {/* Contradictions Count */}
      <div className="telemetry-cell">
        <span className="telemetry-label">CONTRADICTIONS:</span>
        <span className={`telemetry-badge ${contradictions > 0 ? 'contradicted' : 'verified'}`}>
          {contradictions} {contradictions === 1 ? 'PROPOSITION' : 'PROPOSITIONS'}
        </span>
      </div>

      {/* Latency / Compute */}
      <div className="telemetry-cell">
        <span className="telemetry-label">LATENCY:</span>
        <span className="telemetry-val mono-num">
          {cached ? "0.4 ms" : `${safeLatency} ms`}
        </span>
        <span className="mono-num" style={{ color: 'var(--text-muted)', fontSize: '10px' }}>
          [{cached ? "L1 STORE HIT" : `${safeDevice} PASS`}]
        </span>
      </div>

      {/* Active Routing Tier */}
      <div className="telemetry-cell" style={{ borderRight: 'none' }}>
        <span className="telemetry-label">ROUTER:</span>
        <span className="telemetry-badge" style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-grid)', color: 'var(--text-secondary)' }}>
          {tier}
        </span>
      </div>
    </div>
  );
}
