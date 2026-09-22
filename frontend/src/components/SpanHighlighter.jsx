import React from 'react';

export default function SpanHighlighter({
  fullText,
  spans,
  selectedClaimId,
  hoveredClaimId,
  onSelectClaim,
  onHoverClaim
}) {
  const safeFullText = String(fullText || '');
  if (!safeFullText.trim()) return null;

  // Render text with non-overlapping highlighted spans
  const renderAnnotatedText = () => {
    if (!spans || !Array.isArray(spans) || spans.length === 0) {
      return <span>{safeFullText}</span>;
    }

    const validSpans = spans
      .filter(s => s && typeof s.start === 'number' && typeof s.end === 'number')
      .sort((a, b) => a.start - b.start);

    if (validSpans.length === 0) {
      return <span>{safeFullText}</span>;
    }

    const elements = [];
    let lastIndex = 0;

    validSpans.forEach((span, idx) => {
      const start = Math.max(0, Math.min(span.start, safeFullText.length));
      const end = Math.max(start, Math.min(span.end, safeFullText.length));

      // Unannotated preceding text
      if (start > lastIndex) {
        elements.push(
          <span key={`text-${lastIndex}-${idx}`}>
            {safeFullText.slice(lastIndex, start)}
          </span>
        );
      }

      const isSelected = selectedClaimId === span.claim_id;
      const isHovered = hoveredClaimId === span.claim_id;
      const effectiveStart = Math.max(lastIndex, start);
      const spanText = (effectiveStart < end ? safeFullText.slice(effectiveStart, end) : '') || span.text || '';
      const verdictStr = String(span.verdict || 'UNGROUNDED');

      elements.push(
        <mark
          key={`span-${span.claim_id || idx}`}
          data-claim-id={span.claim_id}
          className={`inference-span ${verdictStr} ${isSelected ? 'selected-span' : ''} ${isHovered ? 'hovered-span' : ''}`}
          onClick={() => onSelectClaim && onSelectClaim(span.claim_id)}
          onMouseEnter={() => onHoverClaim && onHoverClaim(span.claim_id)}
          onMouseLeave={() => onHoverClaim && onHoverClaim(null)}
          title={`[${span.claim_id}] ${verdictStr} — Click to focus in Claim Decomposition Matrix`}
        >
          {spanText}
        </mark>
      );

      lastIndex = Math.max(lastIndex, end);
    });

    // Trailing text
    if (lastIndex < safeFullText.length) {
      elements.push(
        <span key={`text-end-${lastIndex}`}>
          {safeFullText.slice(lastIndex)}
        </span>
      );
    }

    return elements;
  };

  return (
    <div className="inference-stream-container">
      <div className="inference-stream-header">
        <span>Inference Stream (Annotated Propositions)</span>
        <div style={{ display: 'flex', gap: '12px' }}>
          <span className="legend-chip contradiction">■ Contradiction</span>
          <span className="legend-chip verified">■ Verified</span>
          <span className="legend-chip ungrounded">■ Ungrounded / Ambiguous</span>
        </div>
      </div>
      <div>
        {renderAnnotatedText()}
      </div>
    </div>
  );
}
