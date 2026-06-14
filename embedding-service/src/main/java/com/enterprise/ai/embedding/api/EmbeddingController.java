package com.enterprise.ai.embedding.api;

import com.enterprise.ai.common.PlatformConstants;
import com.enterprise.ai.common.api.ApiResponse;
import com.enterprise.ai.common.dto.ChunkIndexRequest;
import com.enterprise.ai.common.dto.SearchRequest;
import com.enterprise.ai.common.dto.SearchResponse;
import com.enterprise.ai.embedding.service.EmbeddingIndexService;
import com.enterprise.ai.embedding.service.EmbeddingSearchService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping(PlatformConstants.API_PREFIX + "/embeddings")
public class EmbeddingController {

    private final EmbeddingIndexService indexService;
    private final EmbeddingSearchService searchService;

    public EmbeddingController(EmbeddingIndexService indexService, EmbeddingSearchService searchService) {
        this.indexService = indexService;
        this.searchService = searchService;
    }

    @PostMapping("/index")
    public ApiResponse<String> index(@Valid @RequestBody ChunkIndexRequest request) {
        indexService.index(request);
        return ApiResponse.of("INDEXED");
    }

    @PostMapping("/search")
    public ApiResponse<SearchResponse> search(@Valid @RequestBody SearchRequest request) {
        return ApiResponse.of(searchService.search(request));
    }
}
