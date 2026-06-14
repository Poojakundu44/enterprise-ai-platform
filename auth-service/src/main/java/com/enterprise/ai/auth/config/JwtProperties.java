package com.enterprise.ai.auth.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "platform.jwt")
public record JwtProperties(
        String secret,
        String issuer,
        long expirationSeconds
) {
}
