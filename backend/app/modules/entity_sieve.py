import re
import logging
from typing import List, Dict, Any, Optional

from app.schemas.models import EntityDiscrepancy

logger = logging.getLogger("dhrill.entity_sieve")


class EntitySieve:
    """
    High-precision symbolic consistency sieve.
    Catches numerical mutations, date transpositions, and ungrounded entities
    that neural embeddings and cross-encoders often smooth over.
    """

    # Regex patterns for high-precision extraction
    YEAR_PATTERN = re.compile(r'\b(1\d{3}|20\d{2})\b')
    PERCENT_PATTERN = re.compile(r'\b(\d+(?:\.\d+)?)\s*(?:%|\bpercent\b)', re.IGNORECASE)
    CURRENCY_PATTERN = re.compile(r'([$€£¥])\s*(\d+(?:\.\d+)?)\s*(billion|million|trillion|thousand|k|m|b)?\b', re.IGNORECASE)
    GENERIC_NUMBER_PATTERN = re.compile(r'\b(\d+(?:,\d{3})*(?:\.\d+)?)\b')
    PROPER_NOUN_PATTERN = re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b')

    # Common stopwords to exclude from proper noun checks
    STOPWORDS = {
        "The", "This", "That", "These", "Those", "There", "Here", "It", "They",
        "We", "You", "He", "She", "In", "On", "At", "By", "For", "With", "About",
        "Against", "Between", "Into", "Through", "During", "Before", "After", "Above",
        "Below", "To", "From", "Up", "Down", "If", "Because", "As", "Until", "While",
        "However", "Moreover", "Furthermore", "Although", "According"
    }

    def _extract_years(self, text: str) -> set:
        return set(self.YEAR_PATTERN.findall(text))

    def _extract_percentages(self, text: str) -> set:
        return {float(m) for m in self.PERCENT_PATTERN.findall(text)}

    @staticmethod
    def _format_pct(val: float) -> str:
        return f"{int(val) if val.is_integer() else val}%"

    def _extract_currencies(self, text: str) -> List[str]:
        results = []
        for match in self.CURRENCY_PATTERN.finditer(text):
            symbol, amount, multiplier = match.groups()
            mult = f" {multiplier.lower()}" if multiplier else ""
            results.append(f"{symbol}{amount}{mult}")
        return results

    def _extract_proper_nouns(self, text: str) -> set:
        raw = set(self.PROPER_NOUN_PATTERN.findall(text))
        return {n for n in raw if n not in self.STOPWORDS and len(n) > 2}

    def inspect_discrepancies(
        self,
        claim_text: str,
        evidence_text: Optional[str] = None
    ) -> List[EntityDiscrepancy]:
        """
        Compares entities and numbers in claim vs. evidence text.
        Returns detected discrepancies.
        """
        discrepancies = []
        if not evidence_text:
            return discrepancies

        # 1. Check Years
        claim_years = self._extract_years(claim_text)
        evidence_years = self._extract_years(evidence_text)
        if claim_years:
            for cy in claim_years:
                if evidence_years and cy not in evidence_years:
                    discrepancies.append(EntityDiscrepancy(
                        entity_type="DATE",
                        claim_value=cy,
                        context_value=", ".join(sorted(evidence_years)),
                        discrepancy_type="DATE_MISMATCH",
                        description=f"Year '{cy}' asserted in claim does not match reference year(s): {', '.join(sorted(evidence_years))}."
                    ))

        # 2. Check Percentages
        claim_pcts = self._extract_percentages(claim_text)
        evidence_pcts = self._extract_percentages(evidence_text)
        if claim_pcts:
            for cp in claim_pcts:
                if evidence_pcts and cp not in evidence_pcts:
                    formatted_cp = self._format_pct(cp)
                    formatted_ev = ", ".join(self._format_pct(p) for p in sorted(evidence_pcts))
                    discrepancies.append(EntityDiscrepancy(
                        entity_type="PERCENT",
                        claim_value=formatted_cp,
                        context_value=formatted_ev,
                        discrepancy_type="NUMERICAL_MISMATCH",
                        description=f"Percentage '{formatted_cp}' in claim contradicts reference percentage(s): {formatted_ev}."
                    ))

        # 3. Check Currencies
        claim_curr = self._extract_currencies(claim_text)
        evidence_curr = self._extract_currencies(evidence_text)
        if claim_curr:
            for cc in claim_curr:
                if evidence_curr and cc not in evidence_curr:
                    discrepancies.append(EntityDiscrepancy(
                        entity_type="CURRENCY",
                        claim_value=cc,
                        context_value=", ".join(evidence_curr),
                        discrepancy_type="NUMERICAL_MISMATCH",
                        description=f"Financial figure '{cc}' in claim conflicts with reference: {', '.join(evidence_curr)}."
                    ))

        # 4. Check Key Proper Nouns (High precision check)
        claim_nouns = self._extract_proper_nouns(claim_text)
        evidence_nouns = self._extract_proper_nouns(evidence_text)
        if claim_nouns and evidence_nouns:
            # If claim introduces a specific named entity not found anywhere in evidence
            ungrounded = claim_nouns - evidence_nouns
            # Filter out substrings or case variations
            strict_ungrounded = [
                n for n in ungrounded 
                if n.lower() not in evidence_text.lower() and len(n.split()) >= 2
            ]
            for un in strict_ungrounded:
                discrepancies.append(EntityDiscrepancy(
                    entity_type="ENTITY",
                    claim_value=un,
                    context_value="Not found in reference",
                    discrepancy_type="UNGROUNDED_ENTITY",
                    description=f"Entity '{un}' is completely absent from the reference passage."
                ))

        return discrepancies


entity_sieve = EntitySieve()
