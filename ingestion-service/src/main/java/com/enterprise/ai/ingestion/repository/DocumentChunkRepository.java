package com.enterprise.ai.ingestion.repository;

import com.enterprise.ai.ingestion.domain.DocumentChunk;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

public interface DocumentChunkRepository extends JpaRepository<DocumentChunk, UUID> {

    List<DocumentChunk> findByDocumentIdOrderBySequenceNoAsc(UUID documentId);
}
