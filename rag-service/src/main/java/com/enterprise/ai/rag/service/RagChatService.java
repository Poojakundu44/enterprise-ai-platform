package com.enterprise.ai.rag.service;

import com.enterprise.ai.common.dto.ChatRequest;
import com.enterprise.ai.common.dto.ChatResponse;
import com.enterprise.ai.common.dto.SearchRequest;
import com.enterprise.ai.rag.client.SearchClient;
import org.springframework.stereotype.Service;

@Service
public class RagChatService {

    private final SearchClient searchClient;
    private final LlmAnswerService llmAnswerService;

    public RagChatService(SearchClient searchClient, LlmAnswerService llmAnswerService) {
        this.searchClient = searchClient;
        this.llmAnswerService = llmAnswerService;
    }

    public ChatResponse chat(ChatRequest request) {
        var searchResponse = searchClient.search(new SearchRequest(request.message(), request.topK()));
        LlmAnswerService.AnswerResult answer = llmAnswerService.generate(request.message(), searchResponse.hits());
        return new ChatResponse(answer.answer(), answer.citations(), answer.model());
    }
}
