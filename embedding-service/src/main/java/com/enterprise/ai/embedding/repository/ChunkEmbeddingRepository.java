package com.enterprise.ai.embedding.repository;

import com.enterprise.ai.embedding.domain.ChunkEmbedding;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface ChunkEmbeddingRepository extends JpaRepository<ChunkEmbedding, UUID> {
}
