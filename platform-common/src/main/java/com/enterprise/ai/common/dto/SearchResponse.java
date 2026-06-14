package com.enterprise.ai.common.dto;

import java.util.List;

public record SearchResponse(List<SearchHit> hits) {
}
