package com.enterprise.ai.embedding.service;

import com.enterprise.ai.common.dto.SearchHit;
import com.enterprise.ai.common.dto.SearchRequest;
import com.enterprise.ai.common.dto.SearchResponse;
import com.enterprise.ai.embedding.domain.ChunkEmbedding;
import com.enterprise.ai.embedding.repository.ChunkEmbeddingRepository;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class EmbeddingSearchService {

    private final ChunkEmbeddingRepository repository;

    public EmbeddingSearchService(ChunkEmbeddingRepository repository) {
        this.repository = repository;
    }

    public SearchResponse search(SearchRequest request) {
        List<ChunkEmbedding> all = repository.findAll();
        if (all.isEmpty()) {
            return new SearchResponse(List.of());
        }

        float[] queryVector = EmbeddingMath.embedText(request.query());
        List<float[]> corpus = new ArrayList<>();
        List<EmbeddingMath.ChunkEmbeddingView> views = new ArrayList<>();

        for (ChunkEmbedding item : all) {
            corpus.add(EmbeddingMath.fromJson(item.getEmbeddingJson()));
            views.add(new EmbeddingMath.ChunkEmbeddingView(
                    item.getChunkId(),
                    item.getDocumentId(),
                    item.getDocumentTitle(),
                    item.getChunkContent(),
                    item.getEmbeddingJson()));
        }

        List<EmbeddingMath.Scored> top = EmbeddingMath.topK(corpus, views, queryVector, request.topK());
        List<SearchHit> hits = top.stream()
                .map(scored -> new SearchHit(
                        scored.view().chunkId(),
                        scored.view().documentId(),
                        scored.view().documentTitle(),
                        scored.view().chunkContent(),
                        scored.score()))
                .toList();
        return new SearchResponse(hits);
    }
}
