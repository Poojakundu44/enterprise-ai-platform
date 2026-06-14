package com.enterprise.ai.common.dto;

import java.util.UUID;

public record SearchHit(
        UUID chunkId,
        UUID documentId,
        String documentTitle,
        String content,
        double score
) {
}
