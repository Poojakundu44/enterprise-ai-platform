package com.enterprise.ai.common.dto;

import java.util.List;

public record ChatResponse(
        String answer,
        List<Citation> citations,
        String model
) {
}
