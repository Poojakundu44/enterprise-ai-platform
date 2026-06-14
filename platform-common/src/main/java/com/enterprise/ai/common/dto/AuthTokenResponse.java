package com.enterprise.ai.common.dto;

public record AuthTokenResponse(
        String accessToken,
        String tokenType,
        long expiresInSeconds
) {
    public static AuthTokenResponse bearer(String token, long expiresInSeconds) {
        return new AuthTokenResponse(token, "Bearer", expiresInSeconds);
    }
}
