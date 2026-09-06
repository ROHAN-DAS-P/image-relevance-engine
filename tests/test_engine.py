import pytest
from app.models import Post, ImageMetadata
from app.services.matching import evaluate_match_with_guard

def test_mismatch_guard_blocks_wolf_for_fox():
    post = Post(title="Study of the Red Fox", content="Vulpes vulpes in forest habitat.")
    wolf_meta = ImageMetadata(subject="gray wolf", category="animal", confidence=0.95)
    
    decision = evaluate_match_with_guard(post, wolf_meta, similarity_score=0.82)
    assert decision["status"] == "guarded_mismatch"
    assert "Animal category mismatch" in decision["reason"]

def test_low_confidence_rejected():
    post = Post(title="Red Fox Habitat", content="Habitats of woodland animals.")
    low_conf_meta = ImageMetadata(subject="red fox", category="animal", confidence=0.55)
    
    decision = evaluate_match_with_guard(post, low_conf_meta, similarity_score=0.90)
    assert decision["status"] == "guarded_mismatch"
    assert "Low image tagging confidence" in decision["reason"]

def test_similarity_below_threshold():
    post = Post(title="Modern Cloud Architectures", content="Distributed microservices.")
    bear_meta = ImageMetadata(subject="brown bear", category="animal", confidence=0.98)
    
    decision = evaluate_match_with_guard(post, bear_meta, similarity_score=0.35)
    assert decision["status"] == "guarded_mismatch"