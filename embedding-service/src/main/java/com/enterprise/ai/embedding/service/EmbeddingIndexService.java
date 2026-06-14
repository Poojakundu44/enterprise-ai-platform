package com.enterprise.ai.embedding.service;

import com.enterprise.ai.common.dto.ChunkIndexRequest;
import com.enterprise.ai.embedding.domain.ChunkEmbedding;
import com.enterprise.ai.embedding.repository.ChunkEmbeddingRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class EmbeddingIndexService {

    private final ChunkEmbeddingRepository repository;

    public EmbeddingIndexService(ChunkEmbeddingRepository repository) {
        this.repository = repository;
    }

    @Transactional
    public void index(ChunkIndexRequest request) {
        for (ChunkIndexRequest.ChunkPayload chunk : request.chunks()) {
            float[] vector = EmbeddingMath.embedText(chunk.content());
            ChunkEmbedding entity = new ChunkEmbedding(
                    chunk.chunkId(),
                    chunk.documentId(),
                    chunk.documentTitle(),
                    chunk.content(),
                    EmbeddingMath.toJson(vector));
            repository.save(entity);
        }
    }
}
