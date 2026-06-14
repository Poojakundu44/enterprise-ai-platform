package com.enterprise.ai.ingestion.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class PlatformClientsConfig {

    @Bean
    WebClient embeddingWebClient(@Value("${platform.clients.embedding-base-url}") String baseUrl) {
        return WebClient.builder().baseUrl(baseUrl).build();
    }
}
