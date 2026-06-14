package com.enterprise.ai.ingestion.api;

import com.enterprise.ai.common.PlatformConstants;
import com.enterprise.ai.common.api.ApiResponse;
import com.enterprise.ai.common.dto.DocumentIngestionResponse;
import com.enterprise.ai.common.dto.DocumentUploadRequest;
import com.enterprise.ai.ingestion.service.DocumentIngestionService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping(PlatformConstants.API_PREFIX + "/ingestion")
public class DocumentController {

    private final DocumentIngestionService documentIngestionService;

    public DocumentController(DocumentIngestionService documentIngestionService) {
        this.documentIngestionService = documentIngestionService;
    }

    @PostMapping("/documents")
    public ApiResponse<DocumentIngestionResponse> ingest(
            @Valid @RequestBody DocumentUploadRequest request,
            @RequestHeader(value = "X-User-Email", required = false) String ownerEmail) {
        return ApiResponse.of(documentIngestionService.ingest(request, ownerEmail));
    }
}
