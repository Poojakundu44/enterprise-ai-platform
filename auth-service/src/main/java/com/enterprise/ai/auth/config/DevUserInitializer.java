package com.enterprise.ai.auth.config;

import com.enterprise.ai.auth.domain.User;
import com.enterprise.ai.auth.repository.UserRepository;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
@Profile("!test")
public class DevUserInitializer implements ApplicationRunner {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public DevUserInitializer(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(ApplicationArguments args) {
        if (!userRepository.existsByEmailIgnoreCase("admin@enterprise.local")) {
            userRepository.save(new User(
                    "admin@enterprise.local",
                    passwordEncoder.encode("Enterprise123!"),
                    "Platform Admin"));
        }
    }
}
