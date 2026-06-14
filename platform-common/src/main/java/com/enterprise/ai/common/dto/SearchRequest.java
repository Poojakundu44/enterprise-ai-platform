package com.enterprise.ai.common.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;

public record SearchRequest(
        @NotBlank String query,
        @Min(1) @Max(20) int topK
) {
    public SearchRequest(String query) {
        this(query, 5);
    }
}
