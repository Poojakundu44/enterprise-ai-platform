package com.enterprise.ai.common.api;

public record ServiceHealthResponse(String status, String service) {

    public static ServiceHealthResponse up(String service) {
        return new ServiceHealthResponse("UP", service);
    }
}
