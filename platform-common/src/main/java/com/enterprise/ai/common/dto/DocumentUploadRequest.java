package com.enterprise.ai.common.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record DocumentUploadRequest(
        @NotBlank @Size(max = 500) String title,
        @NotBlank @Size(max = 500_000) String content,
        @NotBlank @Size(max = 64) String sourceType,
        @Size(max = 255) String externalId
) {
    public DocumentUploadRequest(String title, String content, String sourceType) {
        this(title, content, sourceType, null);
    }
}
