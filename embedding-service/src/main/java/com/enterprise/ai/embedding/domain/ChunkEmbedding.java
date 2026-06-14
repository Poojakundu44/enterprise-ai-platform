package com.enterprise.ai.embedding.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "chunk_embeddings")
@Getter
@Setter
@NoArgsConstructor
public class ChunkEmbedding {

    @Id
    @Column(name = "chunk_id")
    private UUID chunkId;

    @Column(name = "document_id", nullable = false)
    private UUID documentId;

    @Column(name = "document_title", nullable = false, length = 500)
    private String documentTitle;

    @Column(name = "chunk_content", nullable = false, columnDefinition = "TEXT")
    private String chunkContent;

    @Column(name = "embedding_json", nullable = false, columnDefinition = "TEXT")
    private String embeddingJson;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    public ChunkEmbedding(
            UUID chunkId,
            UUID documentId,
            String documentTitle,
            String chunkContent,
            String embeddingJson) {
        this.chunkId = chunkId;
        this.documentId = documentId;
        this.documentTitle = documentTitle;
        this.chunkContent = chunkContent;
        this.embeddingJson = embeddingJson;
        this.createdAt = Instant.now();
    }
}
