package com.enterprise.ai.auth.service;

import com.enterprise.ai.auth.domain.User;
import com.enterprise.ai.auth.repository.UserRepository;
import com.enterprise.ai.common.dto.AuthLoginRequest;
import com.enterprise.ai.common.dto.AuthRegisterRequest;
import com.enterprise.ai.common.dto.AuthTokenResponse;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenService jwtTokenService;

    public AuthService(
            UserRepository userRepository,
            PasswordEncoder passwordEncoder,
            JwtTokenService jwtTokenService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtTokenService = jwtTokenService;
    }

    @Transactional
    public AuthTokenResponse register(AuthRegisterRequest request) {
        if (userRepository.existsByEmailIgnoreCase(request.email())) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Email already registered");
        }
        User user = new User(
                request.email().toLowerCase(),
                passwordEncoder.encode(request.password()),
                request.displayName());
        userRepository.save(user);
        return issueToken(user);
    }

    public AuthTokenResponse login(AuthLoginRequest request) {
        User user = userRepository.findByEmailIgnoreCase(request.email())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid credentials"));
        if (!passwordEncoder.matches(request.password(), user.getPasswordHash())) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid credentials");
        }
        return issueToken(user);
    }

    private AuthTokenResponse issueToken(User user) {
        return AuthTokenResponse.bearer(
                jwtTokenService.createToken(user),
                jwtTokenService.expirationSeconds());
    }
}
