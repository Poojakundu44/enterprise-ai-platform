package com.enterprise.ai.search.client;

import com.enterprise.ai.common.api.ApiResponse;
import com.enterprise.ai.common.dto.SearchRequest;
import com.enterprise.ai.common.dto.SearchResponse;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

@Component
public class EmbeddingSearchClient {

    private final WebClient embeddingWebClient;

    public EmbeddingSearchClient(WebClient embeddingWebClient) {
        this.embeddingWebClient = embeddingWebClient;
    }

    public SearchResponse search(SearchRequest request) {
        ApiResponse<SearchResponse> response = embeddingWebClient.post()
                .uri("/api/v1/embeddings/search")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<ApiResponse<SearchResponse>>() {})
                .block();
        return response == null || response.data() == null ? new SearchResponse(java.util.List.of()) : response.data();
    }
}
