package com.enterprise.ai.connector.api;

import com.enterprise.ai.common.PlatformConstants;
import com.enterprise.ai.common.api.ApiResponse;
import com.enterprise.ai.common.dto.DocumentIngestionResponse;
import com.enterprise.ai.common.dto.DocumentUploadRequest;
import com.enterprise.ai.connector.client.IngestionClient;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping(PlatformConstants.API_PREFIX + "/connectors")
public class ManualDocumentConnectorController {

    private final IngestionClient ingestionClient;

    public ManualDocumentConnectorController(IngestionClient ingestionClient) {
        this.ingestionClient = ingestionClient;
    }

    /**
     * MVP manual connector: upload text/markdown content as an enterprise document.
     * Future: Confluence, Jira, SharePoint-specific connectors behind the same API shape.
     */
    @PostMapping("/documents")
    public ApiResponse<DocumentIngestionResponse> uploadDocument(
            @Valid @RequestBody DocumentUploadRequest request,
            @RequestHeader(value = "X-User-Email", required = false) String ownerEmail) {
        DocumentUploadRequest normalized = new DocumentUploadRequest(
                request.title(),
                request.content(),
                request.sourceType() == null || request.sourceType().isBlank() ? "manual" : request.sourceType(),
                request.externalId());
        return ApiResponse.of(ingestionClient.ingest(normalized, ownerEmail));
    }
}
