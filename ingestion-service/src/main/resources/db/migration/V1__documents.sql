CREATE TABLE documents (
    id           UUID PRIMARY KEY,
    title        VARCHAR(500) NOT NULL,
    source_type  VARCHAR(64) NOT NULL,
    external_id  VARCHAR(255),
    owner_email  VARCHAR(255),
    created_at   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE document_chunks (
    id           UUID PRIMARY KEY,
    document_id  UUID NOT NULL REFERENCES documents (id) ON DELETE CASCADE,
    sequence_no  INT NOT NULL,
    content      TEXT NOT NULL,
    created_at   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chunks_document ON document_chunks (document_id);
