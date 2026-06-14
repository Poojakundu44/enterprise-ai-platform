package com.enterprise.ai.auth.api;

import com.enterprise.ai.auth.service.AuthService;
import com.enterprise.ai.common.PlatformConstants;
import com.enterprise.ai.common.api.ApiResponse;
import com.enterprise.ai.common.dto.AuthLoginRequest;
import com.enterprise.ai.common.dto.AuthRegisterRequest;
import com.enterprise.ai.common.dto.AuthTokenResponse;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping(PlatformConstants.API_PREFIX + "/auth")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/register")
    public ApiResponse<AuthTokenResponse> register(@Valid @RequestBody AuthRegisterRequest request) {
        return ApiResponse.of(authService.register(request));
    }

    @PostMapping("/login")
    public ApiResponse<AuthTokenResponse> login(@Valid @RequestBody AuthLoginRequest request) {
        return ApiResponse.of(authService.login(request));
    }
}
