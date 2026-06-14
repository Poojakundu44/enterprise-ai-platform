package com.enterprise.ai.connector.client;

import com.enterprise.ai.common.api.ApiResponse;
import com.enterprise.ai.common.dto.DocumentIngestionResponse;
import com.enterprise.ai.common.dto.DocumentUploadRequest;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

@Component
public class IngestionClient {

    private final WebClient ingestionWebClient;

    public IngestionClient(WebClient ingestionWebClient) {
        this.ingestionWebClient = ingestionWebClient;
    }

    public DocumentIngestionResponse ingest(DocumentUploadRequest request, String ownerEmail) {
        ApiResponse<DocumentIngestionResponse> response = ingestionWebClient.post()
                .uri("/api/v1/ingestion/documents")
                .header("X-User-Email", ownerEmail == null ? "" : ownerEmail)
                .bodyValue(request)
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<ApiResponse<DocumentIngestionResponse>>() {})
                .block();
        if (response == null || response.data() == null) {
            throw new IllegalStateException("Ingestion service returned empty response");
        }
        return response.data();
    }
}
