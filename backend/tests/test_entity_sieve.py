from app.modules.entity_sieve import entity_sieve


def test_date_mismatch_detection():
    claim = "The declaration was signed in 1982."
    evidence = "The historical declaration was formally signed in 1776 at the hall."
    discrepancies = entity_sieve.inspect_discrepancies(claim, evidence)
    
    assert len(discrepancies) > 0
    date_disc = [d for d in discrepancies if d.entity_type == "DATE"]
    assert len(date_disc) == 1
    assert date_disc[0].claim_value == "1982"
    assert "1776" in date_disc[0].context_value
    assert date_disc[0].discrepancy_type == "DATE_MISMATCH"


def test_percentage_mismatch_detection():
    claim = "The company reported an impressive 45% annual growth."
    evidence = "The annual report confirmed a modest 12% annual growth rate."
    discrepancies = entity_sieve.inspect_discrepancies(claim, evidence)
    
    pct_disc = [d for d in discrepancies if d.entity_type == "PERCENT"]
    assert len(pct_disc) == 1
    assert pct_disc[0].claim_value == "45%"
    assert "12%" in pct_disc[0].context_value
    assert pct_disc[0].discrepancy_type == "NUMERICAL_MISMATCH"


def test_currency_mismatch_detection():
    claim = "Total funding reached $500 million in Q3."
    evidence = "Total funding raised was $50 million across seed investors."
    discrepancies = entity_sieve.inspect_discrepancies(claim, evidence)
    
    curr_disc = [d for d in discrepancies if d.entity_type == "CURRENCY"]
    assert len(curr_disc) >= 1
    assert curr_disc[0].discrepancy_type == "NUMERICAL_MISMATCH"


def test_no_false_positives_on_matching_entities():
    claim = "In 2021, revenue increased by 25% to $100 million."
    evidence = "The audited statement in 2021 verified that revenue grew 25% reaching $100 million."
    discrepancies = entity_sieve.inspect_discrepancies(claim, evidence)
    assert len(discrepancies) == 0
