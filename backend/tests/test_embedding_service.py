import numpy as np


def test_embedding_service_falls_back_when_sentence_transformer_unavailable(monkeypatch):
    import app.services.embedding_service as embedding_module

    def raise_unavailable(*args, **kwargs):
        raise RuntimeError("model is not cached")

    monkeypatch.setattr(embedding_module, "SentenceTransformer", raise_unavailable)

    service = embedding_module.EmbeddingService()
    embedding = service.embed_text("define AIML")

    assert isinstance(embedding, list)
    assert len(embedding) == 384
    assert np.linalg.norm(np.asarray(embedding, dtype=np.float32)) > 0
