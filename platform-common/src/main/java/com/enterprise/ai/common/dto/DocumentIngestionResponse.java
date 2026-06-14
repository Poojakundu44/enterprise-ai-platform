package com.enterprise.ai.common.dto;

import java.util.UUID;

public record DocumentIngestionResponse(
        UUID documentId,
        int chunkCount,
        String status
) {
}
