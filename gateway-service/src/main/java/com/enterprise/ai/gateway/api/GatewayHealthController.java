package com.enterprise.ai.gateway.api;

import com.enterprise.ai.common.PlatformConstants;
import com.enterprise.ai.common.PlatformService;
import com.enterprise.ai.common.api.ApiResponse;
import com.enterprise.ai.common.api.ServiceHealthResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping(PlatformConstants.API_PREFIX)
public class GatewayHealthController {

    @GetMapping("/health")
    public ApiResponse<ServiceHealthResponse> health() {
        return ApiResponse.of(ServiceHealthResponse.up(PlatformService.GATEWAY.getServiceName()));
    }
}
