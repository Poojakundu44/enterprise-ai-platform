package com.enterprise.ai.rag.client;

import com.enterprise.ai.common.api.ApiResponse;
import com.enterprise.ai.common.dto.SearchRequest;
import com.enterprise.ai.common.dto.SearchResponse;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

@Component
public class SearchClient {

    private final WebClient searchWebClient;

    public SearchClient(WebClient searchWebClient) {
        this.searchWebClient = searchWebClient;
    }

    public SearchResponse search(SearchRequest request) {
        ApiResponse<SearchResponse> response = searchWebClient.post()
                .uri("/api/v1/search/query")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<ApiResponse<SearchResponse>>() {})
                .block();
        return response == null || response.data() == null ? new SearchResponse(java.util.List.of()) : response.data();
    }
}
