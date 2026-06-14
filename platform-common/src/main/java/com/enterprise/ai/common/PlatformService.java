package com.enterprise.ai.common;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public enum PlatformService {

    GATEWAY("gateway-service", 8080),
    AUTH("auth-service", 8081),
    CONNECTOR("connector-service", 8082),
    INGESTION("ingestion-service", 8083),
    EMBEDDING("embedding-service", 8084),
    SEARCH("search-service", 8085),
    RAG("rag-service", 8086),
    AGENT("agent-service", 8087),
    AUDIT("audit-service", 8088),
    NOTIFICATION("notification-service", 8089);

    private final String serviceName;
    private final int defaultPort;
}
