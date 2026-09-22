from typing import List, Dict, Any
from app.schemas.models import BenchmarkCase, InspectionResponse, InspectionMetrics, ClaimVerificationResult, NLIProbabilities, RetrievedEvidence, EntityDiscrepancy

DEMO_CASES: List[BenchmarkCase] = [
    BenchmarkCase(
        case_id="clinical_dosage",
        title="Clinical Pharmacology: Renal Dosage Mutation",
        category="medical",
        prompt="Summarize the safe dosing guidelines and contraindications for Metformin in patients with renal dysfunction.",
        reference_context="Metformin is contraindicated in patients with severe renal impairment, specifically an estimated glomerular filtration rate (eGFR) below 30 mL/min/1.73 m². For patients with an eGFR between 30 and 44 mL/min/1.73 m², the maximum recommended daily dose is 1000 mg. Starting metformin in patients with an eGFR between 30 and 44 is not recommended. Serum creatinine and eGFR must be monitored at least annually.",
        response_text="Metformin is safely indicated in patients with renal dysfunction down to an eGFR of 15 mL/min/1.73 m². For individuals with moderate impairment between 30 and 44 mL/min, clinicians can safely escalate dosages up to 2500 mg daily. Annual creatinine monitoring is strictly required.",
        expected_hallucinations=[
            "Safe down to eGFR of 15 mL/min (Contraindicated below 30)",
            "Escalate dosage up to 2500 mg daily (Max is 1000 mg)"
        ],
        description="Dangerous pharmacological numerical mutation: alters life-critical eGFR contraindication boundary and safe dosage caps."
    ),
    BenchmarkCase(
        case_id="historical_distortion",
        title="Historical Record: Treaty of Portsmouth Distortion",
        category="history",
        prompt="When was the Treaty of Portsmouth signed, who mediated the negotiations, and where did it take place?",
        reference_context="The Treaty of Portsmouth was formally signed on September 5, 1905, at the Portsmouth Naval Shipyard in Kittery, Maine, United States. The treaty officially concluded the Russo-Japanese War of 1904–1905. Negotiations were brokered by United States President Theodore Roosevelt, who subsequently received the Nobel Peace Prize in 1906 for his diplomatic mediation.",
        response_text="The Treaty of Portsmouth was signed in November 1912 in Geneva, Switzerland. The diplomatic accords were brokered by President Woodrow Wilson following the Balkan Wars. Theodore Roosevelt later endorsed the treaty during his presidency.",
        expected_hallucinations=[
            "Signed in November 1912 (Actual: September 5, 1905)",
            "Located in Geneva, Switzerland (Actual: Portsmouth Naval Shipyard, Maine)",
            "Brokered by Woodrow Wilson (Actual: Theodore Roosevelt)"
        ],
        description="Classic hallucination triad: date transposition, geographic fabrication, and entity substitution."
    ),
    BenchmarkCase(
        case_id="earnings_metrics",
        title="Financial Intelligence: SaaS Q3 Earnings Inflation",
        category="finance",
        prompt="Analyze Datadog's Q3 fiscal performance, revenue growth, and operating cash flow based on the report.",
        reference_context="Datadog announced Q3 revenue of $690 million, representing an increase of 26% year-over-year. Operating income was $115 million under non-GAAP measures. Free cash flow for the quarter was $204 million with a 30% margin. The company had 3,490 customers with ARR of $100k or more.",
        response_text="Datadog reported Q3 revenue of $890 million, representing a robust 45% year-over-year growth rate. Operating income reached $115 million. However, free cash flow declined into negative territory at -$42 million.",
        expected_hallucinations=[
            "Revenue of $890 million (Actual: $690 million)",
            "Growth of 45% (Actual: 26%)",
            "Free cash flow -$42 million (Actual: +$204 million)"
        ],
        description="Subtle numerical inflation designed to trigger the symbolic entity and financial sieve."
    ),
    BenchmarkCase(
        case_id="scientific_fabrication",
        title="Sycophancy & Pure Fabrication: Graviton Discovery",
        category="science",
        prompt="Detail the 2023 discovery of the 'L-elemental graviton particle' at CERN's Large Hadron Collider.",
        reference_context="The Large Hadron Collider (LHC) at CERN completed Run 3 collisions in 2023 studying proton-proton interactions. Physics collaborations ATLAS and CMS continued investigations into Higgs boson properties and supersymmetric dark matter candidates. No experimental evidence for gravitons or hypothetical 'L-elemental' particles exists, and no such particle has ever been observed at CERN.",
        response_text="In October 2023, CERN researchers at the ATLAS detector confirmed the empirical discovery of the L-elemental graviton particle. The paper was authored by Dr. Elena Rostova and reported a 5.2 sigma significance level. This confirms quantum gravitational coupling at tera-electronvolt scales.",
        expected_hallucinations=[
            "Empirical discovery of the L-elemental graviton particle (Fictitious)",
            "Authored by Dr. Elena Rostova (Fabricated entity)",
            "Reported 5.2 sigma significance (Completely fabricated)"
        ],
        description="Sycophantic hallucination: LLM accepts a false premise and invents names, dates, and experimental sigma values."
    ),
    BenchmarkCase(
        case_id="grounded_truth",
        title="Verified Ground Truth: Scaled Dot-Product Attention",
        category="grounded_truth",
        prompt="Explain the mathematical formulation of Scaled Dot-Product Attention according to Vaswani et al. (2017).",
        reference_context="In 'Attention Is All You Need' (Vaswani et al., 2017), Scaled Dot-Product Attention is computed on queries Q, keys K, and values V with dimension d_k. The attention matrix is calculated as Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V. Scaling by 1 / sqrt(d_k) prevents dot products from growing excessively large for large dimensions, which would push softmax into regions with extremely small gradients.",
        response_text="Scaled Dot-Product Attention operates on query, key, and value matrices Q, K, and V. It is formulated as Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V. The factor 1 / sqrt(d_k) is applied as a scaling coefficient to counteract vanishing gradients when the inner dimension d_k is large.",
        expected_hallucinations=[],
        description="100% faithful and entailed generation: demonstrates zero false positives on rigorous technical text."
    )
]


# Pre-computed inspection results for bulletproof offline demos
PRECOMPUTED_DEMO_RESULTS: Dict[str, Dict[str, Any]] = {   'clinical_dosage': {   'annotated_spans': [   {   'claim_id': 'c_01',
                                                      'confidence': 0.96,
                                                      'end': 102,
                                                      'start': 0,
                                                      'text': 'Metformin is safely indicated in patients with renal '
                                                              'dysfunction down to an eGFR of 15 mL/min/1.73 m².',
                                                      'verdict': 'CONTRADICTED'},
                                                  {   'claim_id': 'c_02',
                                                      'confidence': 0.94,
                                                      'end': 229,
                                                      'start': 103,
                                                      'text': 'For individuals with moderate impairment between 30 and '
                                                              '44 mL/min, clinicians can safely escalate dosages up to '
                                                              '2500 mg daily.',
                                                      'verdict': 'CONTRADICTED'},
                                                  {   'claim_id': 'c_03',
                                                      'confidence': 0.93,
                                                      'end': 280,
                                                      'start': 230,
                                                      'text': 'Annual creatinine monitoring is strictly required.',
                                                      'verdict': 'VERIFIED'}],
                           'cached': True,
                           'claims': [   {   'alternative_evidence': [],
                                             'arbitration_source': 'entity_sieve',
                                             'best_evidence': {   'passage_id': 'p_00',
                                                                  'similarity_score': 0.912,
                                                                  'source': 'ref_passage:sentences_1-2',
                                                                  'text': 'Metformin is contraindicated in patients '
                                                                          'with severe renal impairment, specifically '
                                                                          'an estimated glomerular filtration rate '
                                                                          '(eGFR) below 30 mL/min/1.73 m².'},
                                             'claim_id': 'c_01',
                                             'claim_text': 'Metformin is safely indicated in patients with renal '
                                                           'dysfunction down to an eGFR of 15 mL/min/1.73 m²',
                                             'confidence': 0.96,
                                             'end_char': 102,
                                             'entity_conflicts': [   {   'claim_value': '15',
                                                                         'context_value': '30',
                                                                         'description': "eGFR limit '15' in claim "
                                                                                        'directly contradicts '
                                                                                        'contraindicated threshold '
                                                                                        "'30' in reference.",
                                                                         'discrepancy_type': 'NUMERICAL_MISMATCH',
                                                                         'entity_type': 'NUMBER'}],
                                             'explanation': 'Critical clinical mismatch: Claim claims safety down to '
                                                            'eGFR 15, whereas reference explicitly contraindicates '
                                                            'below 30 mL/min.',
                                             'probabilities': {   'contradiction': 0.96,
                                                                  'entailment': 0.02,
                                                                  'neutral': 0.02},
                                             'start_char': 0,
                                             'verdict': 'CONTRADICTED'},
                                         {   'alternative_evidence': [],
                                             'arbitration_source': 'entity_sieve',
                                             'best_evidence': {   'passage_id': 'p_01',
                                                                  'similarity_score': 0.884,
                                                                  'source': 'ref_passage:sentences_2-3',
                                                                  'text': 'For patients with an eGFR between 30 and 44 '
                                                                          'mL/min/1.73 m², the maximum recommended '
                                                                          'daily dose is 1000 mg.'},
                                             'claim_id': 'c_02',
                                             'claim_text': 'For individuals with moderate impairment between 30 and 44 '
                                                           'mL/min, clinicians can safely escalate dosages up to 2500 '
                                                           'mg daily',
                                             'confidence': 0.94,
                                             'end_char': 229,
                                             'entity_conflicts': [   {   'claim_value': '2500',
                                                                         'context_value': '1000',
                                                                         'description': "Daily dose '2500 mg' in claim "
                                                                                        'exceeds maximum recommended '
                                                                                        "cap of '1000 mg'.",
                                                                         'discrepancy_type': 'NUMERICAL_MISMATCH',
                                                                         'entity_type': 'NUMBER'}],
                                             'explanation': 'Dosage inflation: Reference caps dose at 1000 mg for eGFR '
                                                            '30-44, but response dangerously advises escalating to '
                                                            '2500 mg.',
                                             'probabilities': {   'contradiction': 0.94,
                                                                  'entailment': 0.03,
                                                                  'neutral': 0.03},
                                             'start_char': 103,
                                             'verdict': 'CONTRADICTED'},
                                         {   'alternative_evidence': [],
                                             'arbitration_source': 'local_nli',
                                             'best_evidence': {   'passage_id': 'p_02',
                                                                  'similarity_score': 0.895,
                                                                  'source': 'ref_passage:sentences_3-4',
                                                                  'text': 'Serum creatinine and eGFR must be monitored '
                                                                          'at least annually.'},
                                             'claim_id': 'c_03',
                                             'claim_text': 'Annual creatinine monitoring is strictly required',
                                             'confidence': 0.93,
                                             'end_char': 280,
                                             'entity_conflicts': [],
                                             'explanation': 'Fully grounded and entailed by reference mandate for '
                                                            'annual monitoring.',
                                             'probabilities': {   'contradiction': 0.02,
                                                                  'entailment': 0.93,
                                                                  'neutral': 0.05},
                                             'start_char': 230,
                                             'verdict': 'VERIFIED'}],
                           'device_used': 'precomputed_demo',
                           'inspection_id': 'demo-clinical-dosage-001',
                           'latency_ms': 0.42,
                           'metrics': {   'ambiguous_claims': 0,
                                          'contradicted_claims': 2,
                                          'faithfulness_score': 0.333,
                                          'hallucination_density': 0.667,
                                          'hallucination_score': 0.667,
                                          'total_claims': 3,
                                          'ungrounded_claims': 0,
                                          'verified_claims': 1},
                           'telemetry': {'acoustic_bore_depth': 3, 'demo_mode': True, 'passages_indexed': 3}},
    'earnings_metrics': {   'annotated_spans': [   {   'claim_id': 'c_01',
                                                       'confidence': 0.95,
                                                       'end': 98,
                                                       'start': 0,
                                                       'text': 'Datadog reported Q3 revenue of $890 million, '
                                                               'representing a robust 45% year-over-year growth rate.',
                                                       'verdict': 'CONTRADICTED'},
                                                   {   'claim_id': 'c_02',
                                                       'confidence': 0.987,
                                                       'end': 137,
                                                       'start': 99,
                                                       'text': 'Operating income reached $115 million.',
                                                       'verdict': 'VERIFIED'},
                                                   {   'claim_id': 'c_03',
                                                       'confidence': 0.95,
                                                       'end': 211,
                                                       'start': 138,
                                                       'text': 'However, free cash flow declined into negative '
                                                               'territory at -$42 million.',
                                                       'verdict': 'CONTRADICTED'}],
                            'cached': True,
                            'claims': [   {   'alternative_evidence': [   {   'passage_id': 'p_01',
                                                                              'similarity_score': 0.3439,
                                                                              'source': 'ref_passage:sentences_2-3',
                                                                              'text': 'Operating income was $115 '
                                                                                      'million under non-GAAP '
                                                                                      'measures. Free cash flow for '
                                                                                      'the quarter was $204 million '
                                                                                      'with a 30% margin.'},
                                                                          {   'passage_id': 'p_02',
                                                                              'similarity_score': 0.3049,
                                                                              'source': 'ref_passage:sentences_3-4',
                                                                              'text': 'Free cash flow for the quarter '
                                                                                      'was $204 million with a 30% '
                                                                                      'margin. The company had 3,490 '
                                                                                      'customers with ARR of $100k or '
                                                                                      'more.'}],
                                              'arbitration_source': 'entity_sieve',
                                              'best_evidence': {   'passage_id': 'p_00',
                                                                   'similarity_score': 0.7975,
                                                                   'source': 'ref_passage:sentences_1-2',
                                                                   'text': 'Datadog announced Q3 revenue of $690 '
                                                                           'million, representing an increase of 26% '
                                                                           'year-over-year. Operating income was $115 '
                                                                           'million under non-GAAP measures.'},
                                              'claim_id': 'c_01',
                                              'claim_text': 'Datadog reported Q3 revenue of $890 million, representing '
                                                            'a robust 45% year-over-year growth rate',
                                              'confidence': 0.95,
                                              'end_char': 98,
                                              'entity_conflicts': [   {   'claim_value': '45%',
                                                                          'context_value': '26%',
                                                                          'description': "Percentage '45%' in claim "
                                                                                         'contradicts reference '
                                                                                         'percentage(s): 26%.',
                                                                          'discrepancy_type': 'NUMERICAL_MISMATCH',
                                                                          'entity_type': 'PERCENT'},
                                                                      {   'claim_value': '$890 million',
                                                                          'context_value': '$690 million, $115 million',
                                                                          'description': "Financial figure '$890 "
                                                                                         "million' in claim conflicts "
                                                                                         'with reference: $690 '
                                                                                         'million, $115 million.',
                                                                          'discrepancy_type': 'NUMERICAL_MISMATCH',
                                                                          'entity_type': 'CURRENCY'}],
                                              'explanation': "Entity/Numerical conflict detected: Percentage '45%' in "
                                                             'claim contradicts reference percentage(s): 26%.',
                                              'probabilities': {   'contradiction': 0.95,
                                                                   'entailment': 0.0002,
                                                                   'neutral': 0.0015},
                                              'start_char': 0,
                                              'verdict': 'CONTRADICTED'},
                                          {   'alternative_evidence': [   {   'passage_id': 'p_00',
                                                                              'similarity_score': 0.5688,
                                                                              'source': 'ref_passage:sentences_1-2',
                                                                              'text': 'Datadog announced Q3 revenue of '
                                                                                      '$690 million, representing an '
                                                                                      'increase of 26% year-over-year. '
                                                                                      'Operating income was $115 '
                                                                                      'million under non-GAAP '
                                                                                      'measures.'},
                                                                          {   'passage_id': 'p_02',
                                                                              'similarity_score': 0.3043,
                                                                              'source': 'ref_passage:sentences_3-4',
                                                                              'text': 'Free cash flow for the quarter '
                                                                                      'was $204 million with a 30% '
                                                                                      'margin. The company had 3,490 '
                                                                                      'customers with ARR of $100k or '
                                                                                      'more.'}],
                                              'arbitration_source': 'local_nli',
                                              'best_evidence': {   'passage_id': 'p_01',
                                                                   'similarity_score': 0.6959,
                                                                   'source': 'ref_passage:sentences_2-3',
                                                                   'text': 'Operating income was $115 million under '
                                                                           'non-GAAP measures. Free cash flow for the '
                                                                           'quarter was $204 million with a 30% '
                                                                           'margin.'},
                                              'claim_id': 'c_02',
                                              'claim_text': 'Operating income reached $115 million',
                                              'confidence': 0.987,
                                              'end_char': 137,
                                              'entity_conflicts': [],
                                              'explanation': 'Factually grounded and entailed by reference (P=0.99). '
                                                             'Grounded in: "Operating income was $115 million under '
                                                             'non-GAAP measures. Free cash flow for the quarter was '
                                                             '$204 million with a 30% ma..."',
                                              'probabilities': {   'contradiction': 0.0003,
                                                                   'entailment': 0.9871,
                                                                   'neutral': 0.0126},
                                              'start_char': 99,
                                              'verdict': 'VERIFIED'},
                                          {   'alternative_evidence': [   {   'passage_id': 'p_01',
                                                                              'similarity_score': 0.5084,
                                                                              'source': 'ref_passage:sentences_2-3',
                                                                              'text': 'Operating income was $115 '
                                                                                      'million under non-GAAP '
                                                                                      'measures. Free cash flow for '
                                                                                      'the quarter was $204 million '
                                                                                      'with a 30% margin.'},
                                                                          {   'passage_id': 'p_00',
                                                                              'similarity_score': 0.2391,
                                                                              'source': 'ref_passage:sentences_1-2',
                                                                              'text': 'Datadog announced Q3 revenue of '
                                                                                      '$690 million, representing an '
                                                                                      'increase of 26% year-over-year. '
                                                                                      'Operating income was $115 '
                                                                                      'million under non-GAAP '
                                                                                      'measures.'}],
                                              'arbitration_source': 'entity_sieve',
                                              'best_evidence': {   'passage_id': 'p_02',
                                                                   'similarity_score': 0.5593,
                                                                   'source': 'ref_passage:sentences_3-4',
                                                                   'text': 'Free cash flow for the quarter was $204 '
                                                                           'million with a 30% margin. The company had '
                                                                           '3,490 customers with ARR of $100k or '
                                                                           'more.'},
                                              'claim_id': 'c_03',
                                              'claim_text': 'However, free cash flow declined into negative territory '
                                                            'at -$42 million',
                                              'confidence': 0.95,
                                              'end_char': 211,
                                              'entity_conflicts': [   {   'claim_value': '$42 million',
                                                                          'context_value': '$204 million, $100 k',
                                                                          'description': "Financial figure '$42 "
                                                                                         "million' in claim conflicts "
                                                                                         'with reference: $204 '
                                                                                         'million, $100 k.',
                                                                          'discrepancy_type': 'NUMERICAL_MISMATCH',
                                                                          'entity_type': 'CURRENCY'}],
                                              'explanation': 'Entity/Numerical conflict detected: Financial figure '
                                                             "'$42 million' in claim conflicts with reference: $204 "
                                                             'million, $100 k.',
                                              'probabilities': {   'contradiction': 0.95,
                                                                   'entailment': 0.0007,
                                                                   'neutral': 0.1},
                                              'start_char': 138,
                                              'verdict': 'CONTRADICTED'}],
                            'device_used': 'precomputed_demo',
                            'inspection_id': 'cd62c5ec-2bfa-48de-bc3b-b01e8afe5739',
                            'latency_ms': 0.45,
                            'metrics': {   'ambiguous_claims': 0,
                                           'contradicted_claims': 2,
                                           'faithfulness_score': 0.333,
                                           'hallucination_density': 0.667,
                                           'hallucination_score': 0.667,
                                           'total_claims': 3,
                                           'ungrounded_claims': 0,
                                           'verified_claims': 1},
                            'routing_tier': 'local-only',
                            'telemetry': {   'cache_key': 'ee11fd54373cb9d911332d1686d3c162be49fcfced3915fd4743b38340297d37',
                                             'claims_extracted': 3,
                                             'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
                                             'nli_model': 'cross-encoder/nli-deberta-v3-small',
                                             'passages_indexed': 4,
                                             'routing_tier': 'local-only',
                                             'throttles': {   'gemini': {   'active_rpm': 0,
                                                                            'limit_rpm': 12,
                                                                            'throttled': False},
                                                              'groq': {   'active_rpm': 0,
                                                                          'limit_rpm': 25,
                                                                          'throttled': False},
                                                              'openrouter': {   'active_rpm': 0,
                                                                                'limit_rpm': 15,
                                                                                'throttled': False}}}},
    'grounded_truth': {   'annotated_spans': [   {   'claim_id': 'c_01',
                                                     'confidence': 0.97,
                                                     'end': 83,
                                                     'start': 0,
                                                     'text': 'Scaled Dot-Product Attention operates on query, key, and '
                                                             'value matrices Q, K, and V.',
                                                     'verdict': 'VERIFIED'},
                                                 {   'claim_id': 'c_02',
                                                     'confidence': 0.99,
                                                     'end': 154,
                                                     'start': 85,
                                                     'text': 'It is formulated as Attention(Q, K, V) = softmax(Q K^T / '
                                                             'sqrt(d_k)) V.',
                                                     'verdict': 'VERIFIED'},
                                                 {   'claim_id': 'c_03',
                                                     'confidence': 0.95,
                                                     'end': 288,
                                                     'start': 156,
                                                     'text': 'The factor 1 / sqrt(d_k) is applied as a scaling '
                                                             'coefficient to counteract vanishing gradients when the '
                                                             'inner dimension d_k is large.',
                                                     'verdict': 'VERIFIED'}],
                          'cached': True,
                          'claims': [   {   'alternative_evidence': [],
                                            'arbitration_source': 'local_nli',
                                            'best_evidence': {   'passage_id': 'p_00',
                                                                 'similarity_score': 0.95,
                                                                 'source': 'ref_passage:sentences_1-2',
                                                                 'text': 'Scaled Dot-Product Attention is computed on '
                                                                         'queries Q, keys K, and values V with '
                                                                         'dimension d_k.'},
                                            'claim_id': 'c_01',
                                            'claim_text': 'Scaled Dot-Product Attention operates on query, key, and '
                                                          'value matrices Q, K, and V',
                                            'confidence': 0.97,
                                            'end_char': 83,
                                            'entity_conflicts': [],
                                            'explanation': 'Strict semantic entailment from Attention Is All You Need '
                                                           '(Vaswani et al., 2017).',
                                            'probabilities': {   'contradiction': 0.01,
                                                                 'entailment': 0.97,
                                                                 'neutral': 0.02},
                                            'start_char': 0,
                                            'verdict': 'VERIFIED'},
                                        {   'alternative_evidence': [],
                                            'arbitration_source': 'local_nli',
                                            'best_evidence': {   'passage_id': 'p_01',
                                                                 'similarity_score': 0.98,
                                                                 'source': 'ref_passage:sentences_1-2',
                                                                 'text': 'The attention matrix is calculated as '
                                                                         'Attention(Q, K, V) = softmax(Q K^T / '
                                                                         'sqrt(d_k)) V.'},
                                            'claim_id': 'c_02',
                                            'claim_text': 'It is formulated as Attention(Q, K, V) = softmax(Q K^T / '
                                                          'sqrt(d_k)) V',
                                            'confidence': 0.99,
                                            'end_char': 154,
                                            'entity_conflicts': [],
                                            'explanation': 'Exact mathematical identity verified against canonical '
                                                           'definition.',
                                            'probabilities': {   'contradiction': 0.0,
                                                                 'entailment': 0.99,
                                                                 'neutral': 0.01},
                                            'start_char': 85,
                                            'verdict': 'VERIFIED'},
                                        {   'alternative_evidence': [],
                                            'arbitration_source': 'local_nli',
                                            'best_evidence': {   'passage_id': 'p_02',
                                                                 'similarity_score': 0.94,
                                                                 'source': 'ref_passage:sentences_2-3',
                                                                 'text': 'Scaling by 1 / sqrt(d_k) prevents dot '
                                                                         'products from growing excessively large for '
                                                                         'large dimensions, which would push softmax '
                                                                         'into regions with extremely small '
                                                                         'gradients.'},
                                            'claim_id': 'c_03',
                                            'claim_text': 'The factor 1 / sqrt(d_k) is applied as a scaling '
                                                          'coefficient to counteract vanishing gradients when the '
                                                          'inner dimension d_k is large',
                                            'confidence': 0.95,
                                            'end_char': 288,
                                            'entity_conflicts': [],
                                            'explanation': 'Theoretical rationale matches original publication.',
                                            'probabilities': {   'contradiction': 0.01,
                                                                 'entailment': 0.95,
                                                                 'neutral': 0.04},
                                            'start_char': 156,
                                            'verdict': 'VERIFIED'}],
                          'device_used': 'precomputed_demo',
                          'inspection_id': 'demo-truth-005',
                          'latency_ms': 0.35,
                          'metrics': {   'ambiguous_claims': 0,
                                         'contradicted_claims': 0,
                                         'faithfulness_score': 1.0,
                                         'hallucination_density': 0.0,
                                         'hallucination_score': 0.0,
                                         'total_claims': 3,
                                         'ungrounded_claims': 0,
                                         'verified_claims': 3},
                          'telemetry': {'acoustic_bore_depth': 3, 'demo_mode': True}},
    'historical_distortion': {   'annotated_spans': [   {   'claim_id': 'c_01',
                                                            'confidence': 0.98,
                                                            'end': 52,
                                                            'start': 0,
                                                            'text': 'The Treaty of Portsmouth was signed in November '
                                                                    '1912',
                                                            'verdict': 'CONTRADICTED'},
                                                        {   'claim_id': 'c_02',
                                                            'confidence': 0.91,
                                                            'end': 75,
                                                            'start': 53,
                                                            'text': 'in Geneva, Switzerland.',
                                                            'verdict': 'CONTRADICTED'},
                                                        {   'claim_id': 'c_03',
                                                            'confidence': 0.95,
                                                            'end': 168,
                                                            'start': 77,
                                                            'text': 'The diplomatic accords were brokered by President '
                                                                    'Woodrow Wilson following the Balkan Wars.',
                                                            'verdict': 'CONTRADICTED'},
                                                        {   'claim_id': 'c_04',
                                                            'confidence': 0.81,
                                                            'end': 236,
                                                            'start': 170,
                                                            'text': 'Theodore Roosevelt later endorsed the treaty '
                                                                    'during his presidency.',
                                                            'verdict': 'VERIFIED'}],
                                 'cached': True,
                                 'claims': [   {   'alternative_evidence': [],
                                                   'arbitration_source': 'entity_sieve',
                                                   'best_evidence': {   'passage_id': 'p_00',
                                                                        'similarity_score': 0.93,
                                                                        'source': 'ref_passage:sentences_1-2',
                                                                        'text': 'The Treaty of Portsmouth was formally '
                                                                                'signed on September 5, 1905, at the '
                                                                                'Portsmouth Naval Shipyard.'},
                                                   'claim_id': 'c_01',
                                                   'claim_text': 'The Treaty of Portsmouth was signed in November 1912',
                                                   'confidence': 0.98,
                                                   'end_char': 52,
                                                   'entity_conflicts': [   {   'claim_value': '1912',
                                                                               'context_value': '1905',
                                                                               'description': "Year '1912' conflicts "
                                                                                              'with actual signing '
                                                                                              "year '1905'.",
                                                                               'discrepancy_type': 'DATE_MISMATCH',
                                                                               'entity_type': 'DATE'}],
                                                   'explanation': 'Chronological conflict: Claim asserts 1912; '
                                                                  'reference confirms treaty was signed September 5, '
                                                                  '1905.',
                                                   'probabilities': {   'contradiction': 0.98,
                                                                        'entailment': 0.01,
                                                                        'neutral': 0.01},
                                                   'start_char': 0,
                                                   'verdict': 'CONTRADICTED'},
                                               {   'alternative_evidence': [],
                                                   'arbitration_source': 'local_nli',
                                                   'best_evidence': {   'passage_id': 'p_00',
                                                                        'similarity_score': 0.87,
                                                                        'source': 'ref_passage:sentences_1-2',
                                                                        'text': 'at the Portsmouth Naval Shipyard in '
                                                                                'Kittery, Maine, United States.'},
                                                   'claim_id': 'c_02',
                                                   'claim_text': 'in Geneva, Switzerland',
                                                   'confidence': 0.91,
                                                   'end_char': 75,
                                                   'entity_conflicts': [   {   'claim_value': 'Geneva, Switzerland',
                                                                               'context_value': 'Portsmouth Naval '
                                                                                                'Shipyard, Maine',
                                                                               'description': "Location 'Geneva, "
                                                                                              "Switzerland' conflicts "
                                                                                              'with actual location '
                                                                                              "'Portsmouth Naval "
                                                                                              'Shipyard in Kittery, '
                                                                                              "Maine'.",
                                                                               'discrepancy_type': 'UNGROUNDED_ENTITY',
                                                                               'entity_type': 'ENTITY'}],
                                                   'explanation': 'Geographic fabrication: Signed in Maine, USA, not '
                                                                  'Geneva, Switzerland.',
                                                   'probabilities': {   'contradiction': 0.91,
                                                                        'entailment': 0.04,
                                                                        'neutral': 0.05},
                                                   'start_char': 53,
                                                   'verdict': 'CONTRADICTED'},
                                               {   'alternative_evidence': [],
                                                   'arbitration_source': 'entity_sieve',
                                                   'best_evidence': {   'passage_id': 'p_01',
                                                                        'similarity_score': 0.89,
                                                                        'source': 'ref_passage:sentences_2-3',
                                                                        'text': 'Negotiations were brokered by United '
                                                                                'States President Theodore Roosevelt, '
                                                                                'concluding the Russo-Japanese War.'},
                                                   'claim_id': 'c_03',
                                                   'claim_text': 'The diplomatic accords were brokered by President '
                                                                 'Woodrow Wilson following the Balkan Wars',
                                                   'confidence': 0.95,
                                                   'end_char': 168,
                                                   'entity_conflicts': [   {   'claim_value': 'Woodrow Wilson',
                                                                               'context_value': 'Theodore Roosevelt',
                                                                               'description': 'Mediator asserted as '
                                                                                              'Woodrow Wilson instead '
                                                                                              'of Theodore Roosevelt.',
                                                                               'discrepancy_type': 'UNGROUNDED_ENTITY',
                                                                               'entity_type': 'ENTITY'}],
                                                   'explanation': 'Presidential mediator substitution: Brokered by '
                                                                  'Theodore Roosevelt, not Woodrow Wilson.',
                                                   'probabilities': {   'contradiction': 0.95,
                                                                        'entailment': 0.02,
                                                                        'neutral': 0.03},
                                                   'start_char': 77,
                                                   'verdict': 'CONTRADICTED'},
                                               {   'alternative_evidence': [],
                                                   'arbitration_source': 'local_nli',
                                                   'best_evidence': {   'passage_id': 'p_01',
                                                                        'similarity_score': 0.84,
                                                                        'source': 'ref_passage:sentences_2-3',
                                                                        'text': 'Negotiations were brokered by United '
                                                                                'States President Theodore Roosevelt, '
                                                                                'who received the Nobel Peace Prize.'},
                                                   'claim_id': 'c_04',
                                                   'claim_text': 'Theodore Roosevelt later endorsed the treaty during '
                                                                 'his presidency',
                                                   'confidence': 0.81,
                                                   'end_char': 236,
                                                   'entity_conflicts': [],
                                                   'explanation': 'Entailed: Roosevelt was intimately connected to the '
                                                                  'treaty as its chief architect.',
                                                   'probabilities': {   'contradiction': 0.04,
                                                                        'entailment': 0.81,
                                                                        'neutral': 0.15},
                                                   'start_char': 170,
                                                   'verdict': 'VERIFIED'}],
                                 'device_used': 'precomputed_demo',
                                 'inspection_id': 'demo-history-002',
                                 'latency_ms': 0.38,
                                 'metrics': {   'ambiguous_claims': 0,
                                                'contradicted_claims': 3,
                                                'faithfulness_score': 0.25,
                                                'hallucination_density': 0.75,
                                                'hallucination_score': 0.75,
                                                'total_claims': 4,
                                                'ungrounded_claims': 0,
                                                'verified_claims': 1},
                                 'telemetry': {'acoustic_bore_depth': 4, 'demo_mode': True}},
    'scientific_fabrication': {   'annotated_spans': [   {   'claim_id': 'c_01',
                                                             'confidence': 0.95,
                                                             'end': 127,
                                                             'start': 0,
                                                             'text': 'In October 2023, CERN researchers at the ATLAS '
                                                                     'detector confirmed the empirical discovery of '
                                                                     'the L-elemental graviton particle.',
                                                             'verdict': 'CONTRADICTED'},
                                                         {   'claim_id': 'c_02',
                                                             'confidence': 0.95,
                                                             'end': 216,
                                                             'start': 128,
                                                             'text': 'The paper was authored by Dr. Elena Rostova and '
                                                                     'reported a 5.2 sigma significance level.',
                                                             'verdict': 'CONTRADICTED'},
                                                         {   'claim_id': 'c_03',
                                                             'confidence': 0.999,
                                                             'end': 290,
                                                             'start': 217,
                                                             'text': 'This confirms quantum gravitational coupling at '
                                                                     'tera-electronvolt scales.',
                                                             'verdict': 'CONTRADICTED'}],
                                  'cached': True,
                                  'claims': [   {   'alternative_evidence': [   {   'passage_id': 'p_02',
                                                                                    'similarity_score': 0.5991,
                                                                                    'source': 'ref_passage:sentences_3-3',
                                                                                    'text': 'No experimental evidence '
                                                                                            'for gravitons or '
                                                                                            'hypothetical '
                                                                                            "'L-elemental' particles "
                                                                                            'exists, and no such '
                                                                                            'particle has ever been '
                                                                                            'observed at CERN.'},
                                                                                {   'passage_id': 'p_00',
                                                                                    'similarity_score': 0.5259,
                                                                                    'source': 'ref_passage:sentences_1-2',
                                                                                    'text': 'The Large Hadron Collider '
                                                                                            '(LHC) at CERN completed '
                                                                                            'Run 3 collisions in 2023 '
                                                                                            'studying proton-proton '
                                                                                            'interactions. Physics '
                                                                                            'collaborations ATLAS and '
                                                                                            'CMS continued '
                                                                                            'investigations into Higgs '
                                                                                            'boson properties and '
                                                                                            'supersymmetric dark '
                                                                                            'matter candidates.'}],
                                                    'arbitration_source': 'entity_sieve',
                                                    'best_evidence': {   'passage_id': 'p_01',
                                                                         'similarity_score': 0.636,
                                                                         'source': 'ref_passage:sentences_2-3',
                                                                         'text': 'Physics collaborations ATLAS and CMS '
                                                                                 'continued investigations into Higgs '
                                                                                 'boson properties and supersymmetric '
                                                                                 'dark matter candidates. No '
                                                                                 'experimental evidence for gravitons '
                                                                                 "or hypothetical 'L-elemental' "
                                                                                 'particles exists, and no such '
                                                                                 'particle has ever been observed at '
                                                                                 'CERN.'},
                                                    'claim_id': 'c_01',
                                                    'claim_text': 'In October 2023, CERN researchers at the ATLAS '
                                                                  'detector confirmed the empirical discovery of the '
                                                                  'L-elemental graviton particle',
                                                    'confidence': 0.95,
                                                    'end_char': 127,
                                                    'entity_conflicts': [   {   'claim_value': 'In October',
                                                                                'context_value': 'Not found in '
                                                                                                 'reference',
                                                                                'description': "Entity 'In October' is "
                                                                                               'completely absent from '
                                                                                               'the reference passage.',
                                                                                'discrepancy_type': 'UNGROUNDED_ENTITY',
                                                                                'entity_type': 'ENTITY'}],
                                                    'explanation': "Entity/Numerical conflict detected: Entity 'In "
                                                                   "October' is completely absent from the reference "
                                                                   'passage.',
                                                    'probabilities': {   'contradiction': 0.95,
                                                                         'entailment': 0.0,
                                                                         'neutral': 0.0002},
                                                    'start_char': 0,
                                                    'verdict': 'CONTRADICTED'},
                                                {   'alternative_evidence': [   {   'passage_id': 'p_01',
                                                                                    'similarity_score': 0.1566,
                                                                                    'source': 'ref_passage:sentences_2-3',
                                                                                    'text': 'Physics collaborations '
                                                                                            'ATLAS and CMS continued '
                                                                                            'investigations into Higgs '
                                                                                            'boson properties and '
                                                                                            'supersymmetric dark '
                                                                                            'matter candidates. No '
                                                                                            'experimental evidence for '
                                                                                            'gravitons or hypothetical '
                                                                                            "'L-elemental' particles "
                                                                                            'exists, and no such '
                                                                                            'particle has ever been '
                                                                                            'observed at CERN.'},
                                                                                {   'passage_id': 'p_02',
                                                                                    'similarity_score': 0.1025,
                                                                                    'source': 'ref_passage:sentences_3-3',
                                                                                    'text': 'No experimental evidence '
                                                                                            'for gravitons or '
                                                                                            'hypothetical '
                                                                                            "'L-elemental' particles "
                                                                                            'exists, and no such '
                                                                                            'particle has ever been '
                                                                                            'observed at CERN.'}],
                                                    'arbitration_source': 'entity_sieve',
                                                    'best_evidence': {   'passage_id': 'p_00',
                                                                         'similarity_score': 0.2095,
                                                                         'source': 'ref_passage:sentences_1-2',
                                                                         'text': 'The Large Hadron Collider (LHC) at '
                                                                                 'CERN completed Run 3 collisions in '
                                                                                 '2023 studying proton-proton '
                                                                                 'interactions. Physics collaborations '
                                                                                 'ATLAS and CMS continued '
                                                                                 'investigations into Higgs boson '
                                                                                 'properties and supersymmetric dark '
                                                                                 'matter candidates.'},
                                                    'claim_id': 'c_02',
                                                    'claim_text': 'The paper was authored by Dr. Elena Rostova and '
                                                                  'reported a 5.2 sigma significance level',
                                                    'confidence': 0.95,
                                                    'end_char': 216,
                                                    'entity_conflicts': [   {   'claim_value': 'Elena Rostova',
                                                                                'context_value': 'Not found in '
                                                                                                 'reference',
                                                                                'description': "Entity 'Elena Rostova' "
                                                                                               'is completely absent '
                                                                                               'from the reference '
                                                                                               'passage.',
                                                                                'discrepancy_type': 'UNGROUNDED_ENTITY',
                                                                                'entity_type': 'ENTITY'}],
                                                    'explanation': "Entity/Numerical conflict detected: Entity 'Elena "
                                                                   "Rostova' is completely absent from the reference "
                                                                   'passage.',
                                                    'probabilities': {   'contradiction': 0.95,
                                                                         'entailment': 0.0001,
                                                                         'neutral': 0.1},
                                                    'start_char': 128,
                                                    'verdict': 'CONTRADICTED'},
                                                {   'alternative_evidence': [   {   'passage_id': 'p_02',
                                                                                    'similarity_score': 0.199,
                                                                                    'source': 'ref_passage:sentences_3-3',
                                                                                    'text': 'No experimental evidence '
                                                                                            'for gravitons or '
                                                                                            'hypothetical '
                                                                                            "'L-elemental' particles "
                                                                                            'exists, and no such '
                                                                                            'particle has ever been '
                                                                                            'observed at CERN.'},
                                                                                {   'passage_id': 'p_00',
                                                                                    'similarity_score': 0.1987,
                                                                                    'source': 'ref_passage:sentences_1-2',
                                                                                    'text': 'The Large Hadron Collider '
                                                                                            '(LHC) at CERN completed '
                                                                                            'Run 3 collisions in 2023 '
                                                                                            'studying proton-proton '
                                                                                            'interactions. Physics '
                                                                                            'collaborations ATLAS and '
                                                                                            'CMS continued '
                                                                                            'investigations into Higgs '
                                                                                            'boson properties and '
                                                                                            'supersymmetric dark '
                                                                                            'matter candidates.'}],
                                                    'arbitration_source': 'local_nli',
                                                    'best_evidence': {   'passage_id': 'p_01',
                                                                         'similarity_score': 0.2408,
                                                                         'source': 'ref_passage:sentences_2-3',
                                                                         'text': 'Physics collaborations ATLAS and CMS '
                                                                                 'continued investigations into Higgs '
                                                                                 'boson properties and supersymmetric '
                                                                                 'dark matter candidates. No '
                                                                                 'experimental evidence for gravitons '
                                                                                 "or hypothetical 'L-elemental' "
                                                                                 'particles exists, and no such '
                                                                                 'particle has ever been observed at '
                                                                                 'CERN.'},
                                                    'claim_id': 'c_03',
                                                    'claim_text': 'This confirms quantum gravitational coupling at '
                                                                  'tera-electronvolt scales',
                                                    'confidence': 0.999,
                                                    'end_char': 290,
                                                    'entity_conflicts': [],
                                                    'explanation': 'Direct factual contradiction detected (P=1.00). '
                                                                   'Reference asserts: "Physics collaborations ATLAS '
                                                                   'and CMS continued investigations into Higgs boson '
                                                                   'properties and supersymmetric dark matter..."',
                                                    'probabilities': {   'contradiction': 0.9985,
                                                                         'entailment': 0.0,
                                                                         'neutral': 0.0015},
                                                    'start_char': 217,
                                                    'verdict': 'CONTRADICTED'}],
                                  'device_used': 'precomputed_demo',
                                  'inspection_id': 'b6237874-7cb8-4d4c-bc52-51bc7ebc2208',
                                  'latency_ms': 0.48,
                                  'metrics': {   'ambiguous_claims': 0,
                                                 'contradicted_claims': 3,
                                                 'faithfulness_score': 0.0,
                                                 'hallucination_density': 1.0,
                                                 'hallucination_score': 1.0,
                                                 'total_claims': 3,
                                                 'ungrounded_claims': 0,
                                                 'verified_claims': 0},
                                  'routing_tier': 'local-only',
                                  'telemetry': {   'cache_key': '23dcd29165f18bd81439d842d279a396e66be46f1b9b079d86f310da5e273836',
                                                   'claims_extracted': 3,
                                                   'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
                                                   'nli_model': 'cross-encoder/nli-deberta-v3-small',
                                                   'passages_indexed': 3,
                                                   'routing_tier': 'local-only',
                                                   'throttles': {   'gemini': {   'active_rpm': 0,
                                                                                  'limit_rpm': 12,
                                                                                  'throttled': False},
                                                                    'groq': {   'active_rpm': 0,
                                                                                'limit_rpm': 25,
                                                                                'throttled': False},
                                                                    'openrouter': {   'active_rpm': 0,
                                                                                      'limit_rpm': 15,
                                                                                      'throttled': False}}}}}
