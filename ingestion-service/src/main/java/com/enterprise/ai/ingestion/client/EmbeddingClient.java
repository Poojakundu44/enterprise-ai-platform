package com.enterprise.ai.ingestion.client;

import com.enterprise.ai.common.dto.ChunkIndexRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

@Component
public class EmbeddingClient {

    private final WebClient embeddingWebClient;

    public EmbeddingClient(WebClient embeddingWebClient) {
        this.embeddingWebClient = embeddingWebClient;
    }

    public void indexChunks(ChunkIndexRequest request) {
        embeddingWebClient.post()
                .uri("/api/v1/embeddings/index")
                .bodyValue(request)
                .retrieve()
                .toBodilessEntity()
                .block();
    }
}
