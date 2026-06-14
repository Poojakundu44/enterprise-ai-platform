package com.enterprise.ai.common.dto;

import java.util.UUID;

public record Citation(
        UUID chunkId,
        UUID documentId,
        String documentTitle,
        String excerpt
) {
}
