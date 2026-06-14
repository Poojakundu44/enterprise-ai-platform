CREATE TABLE chunk_embeddings (
    chunk_id        UUID PRIMARY KEY,
    document_id     UUID NOT NULL,
    document_title  VARCHAR(500) NOT NULL,
    chunk_content   TEXT NOT NULL,
    embedding_json  TEXT NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chunk_embeddings_document ON chunk_embeddings (document_id);
