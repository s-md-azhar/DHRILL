import React from 'react';

export default function SpanHighlighter({
  fullText,
  spans,
  selectedClaimId,
  hoveredClaimId,
  onSelectClaim,
  onHoverClaim
}) {
  if (!fullText) return null;

  // Render text with non-overlapping highlighted spans
  const renderAnnotatedText = () => {
    if (!spans || spans.length === 0) {
      return <span>{fullText}</span>;
    }

    const sortedSpans = [...spans].sort((a, b) => a.start - b.start);
    const elements = [];
    let lastIndex = 0;

    sortedSpans.forEach((span, idx) => {
      // Unannotated preceding text
      if (span.start > lastIndex) {
        elements.push(
          <span key={`text-${lastIndex}`}>
            {fullText.slice(lastIndex, span.start)}
          </span>
        );
      }

      const isSelected = selectedClaimId === span.claim_id;
      const isHovered = hoveredClaimId === span.claim_id;
      const spanText = fullText.slice(span.start, span.end);

      elements.push(
        <mark
          key={`span-${span.claim_id || idx}`}
          data-claim-id={span.claim_id}
          className={`inference-span ${span.verdict} ${isSelected ? 'selected-span' : ''} ${isHovered ? 'hovered-span' : ''}`}
          onClick={() => onSelectClaim(span.claim_id)}
          onMouseEnter={() => onHoverClaim && onHoverClaim(span.claim_id)}
          onMouseLeave={() => onHoverClaim && onHoverClaim(null)}
          title={`[${span.claim_id}] ${span.verdict} — Click to focus in Claim Decomposition Matrix`}
        >
          {spanText || span.text}
        </mark>
      );

      lastIndex = Math.max(lastIndex, span.end);
    });

    // Trailing text
    if (lastIndex < fullText.length) {
      elements.push(
        <span key={`text-end`}>
          {fullText.slice(lastIndex)}
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
