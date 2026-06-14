package com.enterprise.ai.rag.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class PlatformClientsConfig {

    @Bean
    WebClient searchWebClient(@Value("${platform.clients.search-base-url}") String baseUrl) {
        return WebClient.builder().baseUrl(baseUrl).build();
    }

    @Bean
    WebClient openAiWebClient() {
        return WebClient.builder().baseUrl("https://api.openai.com").build();
    }
}
