package com.enterprise.ai.common.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;

public record ChatRequest(
        @NotBlank String message,
        @Min(1) @Max(20) int topK
) {
    public ChatRequest(String message) {
        this(message, 5);
    }
}
