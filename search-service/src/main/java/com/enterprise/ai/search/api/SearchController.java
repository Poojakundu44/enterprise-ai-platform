package com.enterprise.ai.search.api;

import com.enterprise.ai.common.PlatformConstants;
import com.enterprise.ai.common.api.ApiResponse;
import com.enterprise.ai.common.dto.SearchRequest;
import com.enterprise.ai.common.dto.SearchResponse;
import com.enterprise.ai.search.client.EmbeddingSearchClient;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping(PlatformConstants.API_PREFIX + "/search")
public class SearchController {

    private final EmbeddingSearchClient embeddingSearchClient;

    public SearchController(EmbeddingSearchClient embeddingSearchClient) {
        this.embeddingSearchClient = embeddingSearchClient;
    }

    @PostMapping("/query")
    public ApiResponse<SearchResponse> query(@Valid @RequestBody SearchRequest request) {
        return ApiResponse.of(embeddingSearchClient.search(request));
    }
}
