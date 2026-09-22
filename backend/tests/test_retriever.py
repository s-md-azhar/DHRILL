from app.modules.retriever import context_retriever


def test_chunking_with_overlap():
    text = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five."
    chunks = context_retriever._chunk_context(text)
    assert len(chunks) >= 2
    assert "passage_id" in chunks[0]
    assert "text" in chunks[0]


def test_lexical_overlap_calculation():
    q = "scaled dot product attention mechanism"
    d1 = "The attention mechanism uses scaled dot product matrix multiplication."
    d2 = "Cooking pasta requires boiling salted water vigorously."
    
    score1 = context_retriever._compute_lexical_overlap(q, d1)
    score2 = context_retriever._compute_lexical_overlap(q, d2)
    
    assert score1 > 0.5
    assert score2 == 0.0
