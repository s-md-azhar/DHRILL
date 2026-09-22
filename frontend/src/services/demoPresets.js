// Standalone Client-Side Demo Presets & Precomputed Results
// Allows 100% functional interactive demo on GitHub Pages and Vercel without a live backend

export const CLIENT_DEMO_CASES = [
  {
    "case_id": "clinical_dosage",
    "title": "Clinical Pharmacology: Renal Dosage Mutation",
    "category": "medical",
    "prompt": "Summarize the safe dosing guidelines and contraindications for Metformin in patients with renal dysfunction.",
    "response_text": "Metformin is safely indicated in patients with renal dysfunction down to an eGFR of 15 mL/min/1.73 m\u00b2. For individuals with moderate impairment between 30 and 44 mL/min, clinicians can safely escalate dosages up to 2500 mg daily. Annual creatinine monitoring is strictly required.",
    "reference_context": "Metformin is contraindicated in patients with severe renal impairment, specifically an estimated glomerular filtration rate (eGFR) below 30 mL/min/1.73 m\u00b2. For patients with an eGFR between 30 and 44 mL/min/1.73 m\u00b2, the maximum recommended daily dose is 1000 mg. Starting metformin in patients with an eGFR between 30 and 44 is not recommended. Serum creatinine and eGFR must be monitored at least annually.",
    "expected_hallucinations": [
      "Safe down to eGFR of 15 mL/min (Contraindicated below 30)",
      "Escalate dosage up to 2500 mg daily (Max is 1000 mg)"
    ],
    "description": "Dangerous pharmacological numerical mutation: alters life-critical eGFR contraindication boundary and safe dosage caps."
  },
  {
    "case_id": "historical_distortion",
    "title": "Historical Record: Treaty of Portsmouth Distortion",
    "category": "history",
    "prompt": "When was the Treaty of Portsmouth signed, who mediated the negotiations, and where did it take place?",
    "response_text": "The Treaty of Portsmouth was signed in November 1912 in Geneva, Switzerland. The diplomatic accords were brokered by President Woodrow Wilson following the Balkan Wars. Theodore Roosevelt later endorsed the treaty during his presidency.",
    "reference_context": "The Treaty of Portsmouth was formally signed on September 5, 1905, at the Portsmouth Naval Shipyard in Kittery, Maine, United States. The treaty officially concluded the Russo-Japanese War of 1904\u20131905. Negotiations were brokered by United States President Theodore Roosevelt, who subsequently received the Nobel Peace Prize in 1906 for his diplomatic mediation.",
    "expected_hallucinations": [
      "Signed in November 1912 (Actual: September 5, 1905)",
      "Located in Geneva, Switzerland (Actual: Portsmouth Naval Shipyard, Maine)",
      "Brokered by Woodrow Wilson (Actual: Theodore Roosevelt)"
    ],
    "description": "Classic hallucination triad: date transposition, geographic fabrication, and entity substitution."
  },
  {
    "case_id": "earnings_metrics",
    "title": "Financial Intelligence: SaaS Q3 Earnings Inflation",
    "category": "finance",
    "prompt": "Analyze Datadog's Q3 fiscal performance, revenue growth, and operating cash flow based on the report.",
    "response_text": "Datadog reported Q3 revenue of $890 million, representing a robust 45% year-over-year growth rate. Operating income reached $115 million. However, free cash flow declined into negative territory at -$42 million.",
    "reference_context": "Datadog announced Q3 revenue of $690 million, representing an increase of 26% year-over-year. Operating income was $115 million under non-GAAP measures. Free cash flow for the quarter was $204 million with a 30% margin. The company had 3,490 customers with ARR of $100k or more.",
    "expected_hallucinations": [
      "Revenue of $890 million (Actual: $690 million)",
      "Growth of 45% (Actual: 26%)",
      "Free cash flow -$42 million (Actual: +$204 million)"
    ],
    "description": "Subtle numerical inflation designed to trigger the symbolic entity and financial sieve."
  },
  {
    "case_id": "scientific_fabrication",
    "title": "Sycophancy & Pure Fabrication: Graviton Discovery",
    "category": "science",
    "prompt": "Detail the 2023 discovery of the 'L-elemental graviton particle' at CERN's Large Hadron Collider.",
    "response_text": "In October 2023, CERN researchers at the ATLAS detector confirmed the empirical discovery of the L-elemental graviton particle. The paper was authored by Dr. Elena Rostova and reported a 5.2 sigma significance level. This confirms quantum gravitational coupling at tera-electronvolt scales.",
    "reference_context": "The Large Hadron Collider (LHC) at CERN completed Run 3 collisions in 2023 studying proton-proton interactions. Physics collaborations ATLAS and CMS continued investigations into Higgs boson properties and supersymmetric dark matter candidates. No experimental evidence for gravitons or hypothetical 'L-elemental' particles exists, and no such particle has ever been observed at CERN.",
    "expected_hallucinations": [
      "Empirical discovery of the L-elemental graviton particle (Fictitious)",
      "Authored by Dr. Elena Rostova (Fabricated entity)",
      "Reported 5.2 sigma significance (Completely fabricated)"
    ],
    "description": "Sycophantic hallucination: LLM accepts a false premise and invents names, dates, and experimental sigma values."
  },
  {
    "case_id": "grounded_truth",
    "title": "Verified Ground Truth: Scaled Dot-Product Attention",
    "category": "grounded_truth",
    "prompt": "Explain the mathematical formulation of Scaled Dot-Product Attention according to Vaswani et al. (2017).",
    "response_text": "Scaled Dot-Product Attention operates on query, key, and value matrices Q, K, and V. It is formulated as Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V. The factor 1 / sqrt(d_k) is applied as a scaling coefficient to counteract vanishing gradients when the inner dimension d_k is large.",
    "reference_context": "In 'Attention Is All You Need' (Vaswani et al., 2017), Scaled Dot-Product Attention is computed on queries Q, keys K, and values V with dimension d_k. The attention matrix is calculated as Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V. Scaling by 1 / sqrt(d_k) prevents dot products from growing excessively large for large dimensions, which would push softmax into regions with extremely small gradients.",
    "expected_hallucinations": [],
    "description": "100% faithful and entailed generation: demonstrates zero false positives on rigorous technical text."
  }
];

export const CLIENT_DEMO_RESULTS = {
  "clinical_dosage": {
    "inspection_id": "demo-clinical-dosage-001",
    "cached": true,
    "latency_ms": 0.42,
    "device_used": "precomputed_demo",
    "metrics": {
      "hallucination_score": 0.667,
      "faithfulness_score": 0.333,
      "total_claims": 3,
      "verified_claims": 1,
      "contradicted_claims": 2,
      "ungrounded_claims": 0,
      "ambiguous_claims": 0,
      "hallucination_density": 0.667
    },
    "claims": [
      {
        "claim_id": "c_01",
        "claim_text": "Metformin is safely indicated in patients with renal dysfunction down to an eGFR of 15 mL/min/1.73 m\u00b2",
        "start_char": 0,
        "end_char": 102,
        "verdict": "CONTRADICTED",
        "confidence": 0.96,
        "probabilities": {
          "entailment": 0.02,
          "neutral": 0.02,
          "contradiction": 0.96
        },
        "best_evidence": {
          "passage_id": "p_00",
          "text": "Metformin is contraindicated in patients with severe renal impairment, specifically an estimated glomerular filtration rate (eGFR) below 30 mL/min/1.73 m\u00b2.",
          "similarity_score": 0.912,
          "source": "ref_passage:sentences_1-2"
        },
        "alternative_evidence": [],
        "entity_conflicts": [
          {
            "entity_type": "NUMBER",
            "claim_value": "15",
            "context_value": "30",
            "discrepancy_type": "NUMERICAL_MISMATCH",
            "description": "eGFR limit '15' in claim directly contradicts contraindicated threshold '30' in reference."
          }
        ],
        "arbitration_source": "entity_sieve",
        "explanation": "Critical clinical mismatch: Claim claims safety down to eGFR 15, whereas reference explicitly contraindicates below 30 mL/min."
      },
      {
        "claim_id": "c_02",
        "claim_text": "For individuals with moderate impairment between 30 and 44 mL/min, clinicians can safely escalate dosages up to 2500 mg daily",
        "start_char": 103,
        "end_char": 229,
        "verdict": "CONTRADICTED",
        "confidence": 0.94,
        "probabilities": {
          "entailment": 0.03,
          "neutral": 0.03,
          "contradiction": 0.94
        },
        "best_evidence": {
          "passage_id": "p_01",
          "text": "For patients with an eGFR between 30 and 44 mL/min/1.73 m\u00b2, the maximum recommended daily dose is 1000 mg.",
          "similarity_score": 0.884,
          "source": "ref_passage:sentences_2-3"
        },
        "alternative_evidence": [],
        "entity_conflicts": [
          {
            "entity_type": "NUMBER",
            "claim_value": "2500",
            "context_value": "1000",
            "discrepancy_type": "NUMERICAL_MISMATCH",
            "description": "Daily dose '2500 mg' in claim exceeds maximum recommended cap of '1000 mg'."
          }
        ],
        "arbitration_source": "entity_sieve",
        "explanation": "Dosage inflation: Reference caps dose at 1000 mg for eGFR 30-44, but response dangerously advises escalating to 2500 mg."
      },
      {
        "claim_id": "c_03",
        "claim_text": "Annual creatinine monitoring is strictly required",
        "start_char": 230,
        "end_char": 280,
        "verdict": "VERIFIED",
        "confidence": 0.93,
        "probabilities": {
          "entailment": 0.93,
          "neutral": 0.05,
          "contradiction": 0.02
        },
        "best_evidence": {
          "passage_id": "p_02",
          "text": "Serum creatinine and eGFR must be monitored at least annually.",
          "similarity_score": 0.895,
          "source": "ref_passage:sentences_3-4"
        },
        "alternative_evidence": [],
        "entity_conflicts": [],
        "arbitration_source": "local_nli",
        "explanation": "Fully grounded and entailed by reference mandate for annual monitoring."
      }
    ],
    "annotated_spans": [
      {
        "claim_id": "c_01",
        "start": 0,
        "end": 102,
        "verdict": "CONTRADICTED",
        "confidence": 0.96,
        "text": "Metformin is safely indicated in patients with renal dysfunction down to an eGFR of 15 mL/min/1.73 m\u00b2."
      },
      {
        "claim_id": "c_02",
        "start": 103,
        "end": 229,
        "verdict": "CONTRADICTED",
        "confidence": 0.94,
        "text": "For individuals with moderate impairment between 30 and 44 mL/min, clinicians can safely escalate dosages up to 2500 mg daily."
      },
      {
        "claim_id": "c_03",
        "start": 230,
        "end": 280,
        "verdict": "VERIFIED",
        "confidence": 0.93,
        "text": "Annual creatinine monitoring is strictly required."
      }
    ],
    "telemetry": {
      "demo_mode": true,
      "acoustic_bore_depth": 3,
      "passages_indexed": 3
    }
  },
  "historical_distortion": {
    "inspection_id": "demo-history-002",
    "cached": true,
    "latency_ms": 0.38,
    "device_used": "precomputed_demo",
    "metrics": {
      "hallucination_score": 0.75,
      "faithfulness_score": 0.25,
      "total_claims": 4,
      "verified_claims": 1,
      "contradicted_claims": 3,
      "ungrounded_claims": 0,
      "ambiguous_claims": 0,
      "hallucination_density": 0.75
    },
    "claims": [
      {
        "claim_id": "c_01",
        "claim_text": "The Treaty of Portsmouth was signed in November 1912",
        "start_char": 0,
        "end_char": 52,
        "verdict": "CONTRADICTED",
        "confidence": 0.98,
        "probabilities": {
          "entailment": 0.01,
          "neutral": 0.01,
          "contradiction": 0.98
        },
        "best_evidence": {
          "passage_id": "p_00",
          "text": "The Treaty of Portsmouth was formally signed on September 5, 1905, at the Portsmouth Naval Shipyard.",
          "similarity_score": 0.93,
          "source": "ref_passage:sentences_1-2"
        },
        "alternative_evidence": [],
        "entity_conflicts": [
          {
            "entity_type": "DATE",
            "claim_value": "1912",
            "context_value": "1905",
            "discrepancy_type": "DATE_MISMATCH",
            "description": "Year '1912' conflicts with actual signing year '1905'."
          }
        ],
        "arbitration_source": "entity_sieve",
        "explanation": "Chronological conflict: Claim asserts 1912; reference confirms treaty was signed September 5, 1905."
      },
      {
        "claim_id": "c_02",
        "claim_text": "in Geneva, Switzerland",
        "start_char": 53,
        "end_char": 75,
        "verdict": "CONTRADICTED",
        "confidence": 0.91,
        "probabilities": {
          "entailment": 0.04,
          "neutral": 0.05,
          "contradiction": 0.91
        },
        "best_evidence": {
          "passage_id": "p_00",
          "text": "at the Portsmouth Naval Shipyard in Kittery, Maine, United States.",
          "similarity_score": 0.87,
          "source": "ref_passage:sentences_1-2"
        },
        "alternative_evidence": [],
        "entity_conflicts": [
          {
            "entity_type": "ENTITY",
            "claim_value": "Geneva, Switzerland",
            "context_value": "Portsmouth Naval Shipyard, Maine",
            "discrepancy_type": "UNGROUNDED_ENTITY",
            "description": "Location 'Geneva, Switzerland' conflicts with actual location 'Portsmouth Naval Shipyard in Kittery, Maine'."
          }
        ],
        "arbitration_source": "local_nli",
        "explanation": "Geographic fabrication: Signed in Maine, USA, not Geneva, Switzerland."
      },
      {
        "claim_id": "c_03",
        "claim_text": "The diplomatic accords were brokered by President Woodrow Wilson following the Balkan Wars",
        "start_char": 77,
        "end_char": 168,
        "verdict": "CONTRADICTED",
        "confidence": 0.95,
        "probabilities": {
          "entailment": 0.02,
          "neutral": 0.03,
          "contradiction": 0.95
        },
        "best_evidence": {
          "passage_id": "p_01",
          "text": "Negotiations were brokered by United States President Theodore Roosevelt, concluding the Russo-Japanese War.",
          "similarity_score": 0.89,
          "source": "ref_passage:sentences_2-3"
        },
        "alternative_evidence": [],
        "entity_conflicts": [
          {
            "entity_type": "ENTITY",
            "claim_value": "Woodrow Wilson",
            "context_value": "Theodore Roosevelt",
            "discrepancy_type": "UNGROUNDED_ENTITY",
            "description": "Mediator asserted as Woodrow Wilson instead of Theodore Roosevelt."
          }
        ],
        "arbitration_source": "entity_sieve",
        "explanation": "Presidential mediator substitution: Brokered by Theodore Roosevelt, not Woodrow Wilson."
      },
      {
        "claim_id": "c_04",
        "claim_text": "Theodore Roosevelt later endorsed the treaty during his presidency",
        "start_char": 170,
        "end_char": 236,
        "verdict": "VERIFIED",
        "confidence": 0.81,
        "probabilities": {
          "entailment": 0.81,
          "neutral": 0.15,
          "contradiction": 0.04
        },
        "best_evidence": {
          "passage_id": "p_01",
          "text": "Negotiations were brokered by United States President Theodore Roosevelt, who received the Nobel Peace Prize.",
          "similarity_score": 0.84,
          "source": "ref_passage:sentences_2-3"
        },
        "alternative_evidence": [],
        "entity_conflicts": [],
        "arbitration_source": "local_nli",
        "explanation": "Entailed: Roosevelt was intimately connected to the treaty as its chief architect."
      }
    ],
    "annotated_spans": [
      {
        "claim_id": "c_01",
        "start": 0,
        "end": 52,
        "verdict": "CONTRADICTED",
        "confidence": 0.98,
        "text": "The Treaty of Portsmouth was signed in November 1912"
      },
      {
        "claim_id": "c_02",
        "start": 53,
        "end": 75,
        "verdict": "CONTRADICTED",
        "confidence": 0.91,
        "text": "in Geneva, Switzerland."
      },
      {
        "claim_id": "c_03",
        "start": 77,
        "end": 168,
        "verdict": "CONTRADICTED",
        "confidence": 0.95,
        "text": "The diplomatic accords were brokered by President Woodrow Wilson following the Balkan Wars."
      },
      {
        "claim_id": "c_04",
        "start": 170,
        "end": 236,
        "verdict": "VERIFIED",
        "confidence": 0.81,
        "text": "Theodore Roosevelt later endorsed the treaty during his presidency."
      }
    ],
    "telemetry": {
      "demo_mode": true,
      "acoustic_bore_depth": 4
    }
  },
  "grounded_truth": {
    "inspection_id": "demo-truth-005",
    "cached": true,
    "latency_ms": 0.35,
    "device_used": "precomputed_demo",
    "metrics": {
      "hallucination_score": 0.0,
      "faithfulness_score": 1.0,
      "total_claims": 3,
      "verified_claims": 3,
      "contradicted_claims": 0,
      "ungrounded_claims": 0,
      "ambiguous_claims": 0,
      "hallucination_density": 0.0
    },
    "claims": [
      {
        "claim_id": "c_01",
        "claim_text": "Scaled Dot-Product Attention operates on query, key, and value matrices Q, K, and V",
        "start_char": 0,
        "end_char": 83,
        "verdict": "VERIFIED",
        "confidence": 0.97,
        "probabilities": {
          "entailment": 0.97,
          "neutral": 0.02,
          "contradiction": 0.01
        },
        "best_evidence": {
          "passage_id": "p_00",
          "text": "Scaled Dot-Product Attention is computed on queries Q, keys K, and values V with dimension d_k.",
          "similarity_score": 0.95,
          "source": "ref_passage:sentences_1-2"
        },
        "alternative_evidence": [],
        "entity_conflicts": [],
        "arbitration_source": "local_nli",
        "explanation": "Strict semantic entailment from Attention Is All You Need (Vaswani et al., 2017)."
      },
      {
        "claim_id": "c_02",
        "claim_text": "It is formulated as Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V",
        "start_char": 85,
        "end_char": 154,
        "verdict": "VERIFIED",
        "confidence": 0.99,
        "probabilities": {
          "entailment": 0.99,
          "neutral": 0.01,
          "contradiction": 0.0
        },
        "best_evidence": {
          "passage_id": "p_01",
          "text": "The attention matrix is calculated as Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V.",
          "similarity_score": 0.98,
          "source": "ref_passage:sentences_1-2"
        },
        "alternative_evidence": [],
        "entity_conflicts": [],
        "arbitration_source": "local_nli",
        "explanation": "Exact mathematical identity verified against canonical definition."
      },
      {
        "claim_id": "c_03",
        "claim_text": "The factor 1 / sqrt(d_k) is applied as a scaling coefficient to counteract vanishing gradients when the inner dimension d_k is large",
        "start_char": 156,
        "end_char": 288,
        "verdict": "VERIFIED",
        "confidence": 0.95,
        "probabilities": {
          "entailment": 0.95,
          "neutral": 0.04,
          "contradiction": 0.01
        },
        "best_evidence": {
          "passage_id": "p_02",
          "text": "Scaling by 1 / sqrt(d_k) prevents dot products from growing excessively large for large dimensions, which would push softmax into regions with extremely small gradients.",
          "similarity_score": 0.94,
          "source": "ref_passage:sentences_2-3"
        },
        "alternative_evidence": [],
        "entity_conflicts": [],
        "arbitration_source": "local_nli",
        "explanation": "Theoretical rationale matches original publication."
      }
    ],
    "annotated_spans": [
      {
        "claim_id": "c_01",
        "start": 0,
        "end": 83,
        "verdict": "VERIFIED",
        "confidence": 0.97,
        "text": "Scaled Dot-Product Attention operates on query, key, and value matrices Q, K, and V."
      },
      {
        "claim_id": "c_02",
        "start": 85,
        "end": 154,
        "verdict": "VERIFIED",
        "confidence": 0.99,
        "text": "It is formulated as Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V."
      },
      {
        "claim_id": "c_03",
        "start": 156,
        "end": 288,
        "verdict": "VERIFIED",
        "confidence": 0.95,
        "text": "The factor 1 / sqrt(d_k) is applied as a scaling coefficient to counteract vanishing gradients when the inner dimension d_k is large."
      }
    ],
    "telemetry": {
      "demo_mode": true,
      "acoustic_bore_depth": 3
    }
  },
  "earnings_metrics": {
    "inspection_id": "cd62c5ec-2bfa-48de-bc3b-b01e8afe5739",
    "cached": true,
    "latency_ms": 0.45,
    "device_used": "precomputed_demo",
    "routing_tier": "local-only",
    "metrics": {
      "hallucination_score": 0.667,
      "faithfulness_score": 0.333,
      "total_claims": 3,
      "verified_claims": 1,
      "contradicted_claims": 2,
      "ungrounded_claims": 0,
      "ambiguous_claims": 0,
      "hallucination_density": 0.667
    },
    "claims": [
      {
        "claim_id": "c_01",
        "claim_text": "Datadog reported Q3 revenue of $890 million, representing a robust 45% year-over-year growth rate",
        "start_char": 0,
        "end_char": 98,
        "verdict": "CONTRADICTED",
        "confidence": 0.95,
        "probabilities": {
          "entailment": 0.0002,
          "neutral": 0.0015,
          "contradiction": 0.95
        },
        "best_evidence": {
          "passage_id": "p_00",
          "text": "Datadog announced Q3 revenue of $690 million, representing an increase of 26% year-over-year. Operating income was $115 million under non-GAAP measures.",
          "similarity_score": 0.7975,
          "source": "ref_passage:sentences_1-2"
        },
        "alternative_evidence": [
          {
            "passage_id": "p_01",
            "text": "Operating income was $115 million under non-GAAP measures. Free cash flow for the quarter was $204 million with a 30% margin.",
            "similarity_score": 0.3439,
            "source": "ref_passage:sentences_2-3"
          },
          {
            "passage_id": "p_02",
            "text": "Free cash flow for the quarter was $204 million with a 30% margin. The company had 3,490 customers with ARR of $100k or more.",
            "similarity_score": 0.3049,
            "source": "ref_passage:sentences_3-4"
          }
        ],
        "entity_conflicts": [
          {
            "entity_type": "PERCENT",
            "claim_value": "45%",
            "context_value": "26%",
            "discrepancy_type": "NUMERICAL_MISMATCH",
            "description": "Percentage '45%' in claim contradicts reference percentage(s): 26%."
          },
          {
            "entity_type": "CURRENCY",
            "claim_value": "$890 million",
            "context_value": "$690 million, $115 million",
            "discrepancy_type": "NUMERICAL_MISMATCH",
            "description": "Financial figure '$890 million' in claim conflicts with reference: $690 million, $115 million."
          }
        ],
        "arbitration_source": "entity_sieve",
        "explanation": "Entity/Numerical conflict detected: Percentage '45%' in claim contradicts reference percentage(s): 26%."
      },
      {
        "claim_id": "c_02",
        "claim_text": "Operating income reached $115 million",
        "start_char": 99,
        "end_char": 137,
        "verdict": "VERIFIED",
        "confidence": 0.987,
        "probabilities": {
          "entailment": 0.9871,
          "neutral": 0.0126,
          "contradiction": 0.0003
        },
        "best_evidence": {
          "passage_id": "p_01",
          "text": "Operating income was $115 million under non-GAAP measures. Free cash flow for the quarter was $204 million with a 30% margin.",
          "similarity_score": 0.6959,
          "source": "ref_passage:sentences_2-3"
        },
        "alternative_evidence": [
          {
            "passage_id": "p_00",
            "text": "Datadog announced Q3 revenue of $690 million, representing an increase of 26% year-over-year. Operating income was $115 million under non-GAAP measures.",
            "similarity_score": 0.5688,
            "source": "ref_passage:sentences_1-2"
          },
          {
            "passage_id": "p_02",
            "text": "Free cash flow for the quarter was $204 million with a 30% margin. The company had 3,490 customers with ARR of $100k or more.",
            "similarity_score": 0.3043,
            "source": "ref_passage:sentences_3-4"
          }
        ],
        "entity_conflicts": [],
        "arbitration_source": "local_nli",
        "explanation": "Factually grounded and entailed by reference (P=0.99). Grounded in: \"Operating income was $115 million under non-GAAP measures. Free cash flow for the quarter was $204 million with a 30% ma...\""
      },
      {
        "claim_id": "c_03",
        "claim_text": "However, free cash flow declined into negative territory at -$42 million",
        "start_char": 138,
        "end_char": 211,
        "verdict": "CONTRADICTED",
        "confidence": 0.95,
        "probabilities": {
          "entailment": 0.0007,
          "neutral": 0.1,
          "contradiction": 0.95
        },
        "best_evidence": {
          "passage_id": "p_02",
          "text": "Free cash flow for the quarter was $204 million with a 30% margin. The company had 3,490 customers with ARR of $100k or more.",
          "similarity_score": 0.5593,
          "source": "ref_passage:sentences_3-4"
        },
        "alternative_evidence": [
          {
            "passage_id": "p_01",
            "text": "Operating income was $115 million under non-GAAP measures. Free cash flow for the quarter was $204 million with a 30% margin.",
            "similarity_score": 0.5084,
            "source": "ref_passage:sentences_2-3"
          },
          {
            "passage_id": "p_00",
            "text": "Datadog announced Q3 revenue of $690 million, representing an increase of 26% year-over-year. Operating income was $115 million under non-GAAP measures.",
            "similarity_score": 0.2391,
            "source": "ref_passage:sentences_1-2"
          }
        ],
        "entity_conflicts": [
          {
            "entity_type": "CURRENCY",
            "claim_value": "$42 million",
            "context_value": "$204 million, $100 k",
            "discrepancy_type": "NUMERICAL_MISMATCH",
            "description": "Financial figure '$42 million' in claim conflicts with reference: $204 million, $100 k."
          }
        ],
        "arbitration_source": "entity_sieve",
        "explanation": "Entity/Numerical conflict detected: Financial figure '$42 million' in claim conflicts with reference: $204 million, $100 k."
      }
    ],
    "annotated_spans": [
      {
        "claim_id": "c_01",
        "start": 0,
        "end": 98,
        "verdict": "CONTRADICTED",
        "confidence": 0.95,
        "text": "Datadog reported Q3 revenue of $890 million, representing a robust 45% year-over-year growth rate."
      },
      {
        "claim_id": "c_02",
        "start": 99,
        "end": 137,
        "verdict": "VERIFIED",
        "confidence": 0.987,
        "text": "Operating income reached $115 million."
      },
      {
        "claim_id": "c_03",
        "start": 138,
        "end": 211,
        "verdict": "CONTRADICTED",
        "confidence": 0.95,
        "text": "However, free cash flow declined into negative territory at -$42 million."
      }
    ],
    "telemetry": {
      "routing_tier": "local-only",
      "claims_extracted": 3,
      "passages_indexed": 4,
      "cache_key": "ee11fd54373cb9d911332d1686d3c162be49fcfced3915fd4743b38340297d37",
      "nli_model": "cross-encoder/nli-deberta-v3-small",
      "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
      "throttles": {
        "gemini": {
          "active_rpm": 0,
          "limit_rpm": 12,
          "throttled": false
        },
        "groq": {
          "active_rpm": 0,
          "limit_rpm": 25,
          "throttled": false
        },
        "openrouter": {
          "active_rpm": 0,
          "limit_rpm": 15,
          "throttled": false
        }
      }
    }
  },
  "scientific_fabrication": {
    "inspection_id": "b6237874-7cb8-4d4c-bc52-51bc7ebc2208",
    "cached": true,
    "latency_ms": 0.48,
    "device_used": "precomputed_demo",
    "routing_tier": "local-only",
    "metrics": {
      "hallucination_score": 1.0,
      "faithfulness_score": 0.0,
      "total_claims": 3,
      "verified_claims": 0,
      "contradicted_claims": 3,
      "ungrounded_claims": 0,
      "ambiguous_claims": 0,
      "hallucination_density": 1.0
    },
    "claims": [
      {
        "claim_id": "c_01",
        "claim_text": "In October 2023, CERN researchers at the ATLAS detector confirmed the empirical discovery of the L-elemental graviton particle",
        "start_char": 0,
        "end_char": 127,
        "verdict": "CONTRADICTED",
        "confidence": 0.95,
        "probabilities": {
          "entailment": 0.0,
          "neutral": 0.0002,
          "contradiction": 0.95
        },
        "best_evidence": {
          "passage_id": "p_01",
          "text": "Physics collaborations ATLAS and CMS continued investigations into Higgs boson properties and supersymmetric dark matter candidates. No experimental evidence for gravitons or hypothetical 'L-elemental' particles exists, and no such particle has ever been observed at CERN.",
          "similarity_score": 0.636,
          "source": "ref_passage:sentences_2-3"
        },
        "alternative_evidence": [
          {
            "passage_id": "p_02",
            "text": "No experimental evidence for gravitons or hypothetical 'L-elemental' particles exists, and no such particle has ever been observed at CERN.",
            "similarity_score": 0.5991,
            "source": "ref_passage:sentences_3-3"
          },
          {
            "passage_id": "p_00",
            "text": "The Large Hadron Collider (LHC) at CERN completed Run 3 collisions in 2023 studying proton-proton interactions. Physics collaborations ATLAS and CMS continued investigations into Higgs boson properties and supersymmetric dark matter candidates.",
            "similarity_score": 0.5259,
            "source": "ref_passage:sentences_1-2"
          }
        ],
        "entity_conflicts": [
          {
            "entity_type": "ENTITY",
            "claim_value": "In October",
            "context_value": "Not found in reference",
            "discrepancy_type": "UNGROUNDED_ENTITY",
            "description": "Entity 'In October' is completely absent from the reference passage."
          }
        ],
        "arbitration_source": "entity_sieve",
        "explanation": "Entity/Numerical conflict detected: Entity 'In October' is completely absent from the reference passage."
      },
      {
        "claim_id": "c_02",
        "claim_text": "The paper was authored by Dr. Elena Rostova and reported a 5.2 sigma significance level",
        "start_char": 128,
        "end_char": 216,
        "verdict": "CONTRADICTED",
        "confidence": 0.95,
        "probabilities": {
          "entailment": 0.0001,
          "neutral": 0.1,
          "contradiction": 0.95
        },
        "best_evidence": {
          "passage_id": "p_00",
          "text": "The Large Hadron Collider (LHC) at CERN completed Run 3 collisions in 2023 studying proton-proton interactions. Physics collaborations ATLAS and CMS continued investigations into Higgs boson properties and supersymmetric dark matter candidates.",
          "similarity_score": 0.2095,
          "source": "ref_passage:sentences_1-2"
        },
        "alternative_evidence": [
          {
            "passage_id": "p_01",
            "text": "Physics collaborations ATLAS and CMS continued investigations into Higgs boson properties and supersymmetric dark matter candidates. No experimental evidence for gravitons or hypothetical 'L-elemental' particles exists, and no such particle has ever been observed at CERN.",
            "similarity_score": 0.1566,
            "source": "ref_passage:sentences_2-3"
          },
          {
            "passage_id": "p_02",
            "text": "No experimental evidence for gravitons or hypothetical 'L-elemental' particles exists, and no such particle has ever been observed at CERN.",
            "similarity_score": 0.1025,
            "source": "ref_passage:sentences_3-3"
          }
        ],
        "entity_conflicts": [
          {
            "entity_type": "ENTITY",
            "claim_value": "Elena Rostova",
            "context_value": "Not found in reference",
            "discrepancy_type": "UNGROUNDED_ENTITY",
            "description": "Entity 'Elena Rostova' is completely absent from the reference passage."
          }
        ],
        "arbitration_source": "entity_sieve",
        "explanation": "Entity/Numerical conflict detected: Entity 'Elena Rostova' is completely absent from the reference passage."
      },
      {
        "claim_id": "c_03",
        "claim_text": "This confirms quantum gravitational coupling at tera-electronvolt scales",
        "start_char": 217,
        "end_char": 290,
        "verdict": "CONTRADICTED",
        "confidence": 0.999,
        "probabilities": {
          "entailment": 0.0,
          "neutral": 0.0015,
          "contradiction": 0.9985
        },
        "best_evidence": {
          "passage_id": "p_01",
          "text": "Physics collaborations ATLAS and CMS continued investigations into Higgs boson properties and supersymmetric dark matter candidates. No experimental evidence for gravitons or hypothetical 'L-elemental' particles exists, and no such particle has ever been observed at CERN.",
          "similarity_score": 0.2408,
          "source": "ref_passage:sentences_2-3"
        },
        "alternative_evidence": [
          {
            "passage_id": "p_02",
            "text": "No experimental evidence for gravitons or hypothetical 'L-elemental' particles exists, and no such particle has ever been observed at CERN.",
            "similarity_score": 0.199,
            "source": "ref_passage:sentences_3-3"
          },
          {
            "passage_id": "p_00",
            "text": "The Large Hadron Collider (LHC) at CERN completed Run 3 collisions in 2023 studying proton-proton interactions. Physics collaborations ATLAS and CMS continued investigations into Higgs boson properties and supersymmetric dark matter candidates.",
            "similarity_score": 0.1987,
            "source": "ref_passage:sentences_1-2"
          }
        ],
        "entity_conflicts": [],
        "arbitration_source": "local_nli",
        "explanation": "Direct factual contradiction detected (P=1.00). Reference asserts: \"Physics collaborations ATLAS and CMS continued investigations into Higgs boson properties and supersymmetric dark matter...\""
      }
    ],
    "annotated_spans": [
      {
        "claim_id": "c_01",
        "start": 0,
        "end": 127,
        "verdict": "CONTRADICTED",
        "confidence": 0.95,
        "text": "In October 2023, CERN researchers at the ATLAS detector confirmed the empirical discovery of the L-elemental graviton particle."
      },
      {
        "claim_id": "c_02",
        "start": 128,
        "end": 216,
        "verdict": "CONTRADICTED",
        "confidence": 0.95,
        "text": "The paper was authored by Dr. Elena Rostova and reported a 5.2 sigma significance level."
      },
      {
        "claim_id": "c_03",
        "start": 217,
        "end": 290,
        "verdict": "CONTRADICTED",
        "confidence": 0.999,
        "text": "This confirms quantum gravitational coupling at tera-electronvolt scales."
      }
    ],
    "telemetry": {
      "routing_tier": "local-only",
      "claims_extracted": 3,
      "passages_indexed": 3,
      "cache_key": "23dcd29165f18bd81439d842d279a396e66be46f1b9b079d86f310da5e273836",
      "nli_model": "cross-encoder/nli-deberta-v3-small",
      "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
      "throttles": {
        "gemini": {
          "active_rpm": 0,
          "limit_rpm": 12,
          "throttled": false
        },
        "groq": {
          "active_rpm": 0,
          "limit_rpm": 25,
          "throttled": false
        },
        "openrouter": {
          "active_rpm": 0,
          "limit_rpm": 15,
          "throttled": false
        }
      }
    }
  }
};
