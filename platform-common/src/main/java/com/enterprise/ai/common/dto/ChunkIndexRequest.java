package com.enterprise.ai.common.dto;

import java.util.List;
import java.util.UUID;

public record ChunkIndexRequest(List<ChunkPayload> chunks) {

    public record ChunkPayload(
            UUID chunkId,
            UUID documentId,
            String documentTitle,
            String content
    ) {
    }
}
