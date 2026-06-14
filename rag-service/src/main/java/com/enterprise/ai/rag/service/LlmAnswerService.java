package com.enterprise.ai.rag.service;

import com.enterprise.ai.common.dto.Citation;
import com.enterprise.ai.common.dto.SearchHit;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class LlmAnswerService {

    private final WebClient openAiWebClient;
    private final ObjectMapper objectMapper;
    private final String openAiApiKey;
    private final String openAiModel;

    public LlmAnswerService(
            WebClient openAiWebClient,
            ObjectMapper objectMapper,
            @Value("${platform.llm.openai-api-key:}") String openAiApiKey,
            @Value("${platform.llm.openai-model:gpt-4o-mini}") String openAiModel) {
        this.openAiWebClient = openAiWebClient;
        this.objectMapper = objectMapper;
        this.openAiApiKey = openAiApiKey;
        this.openAiModel = openAiModel;
    }

    public AnswerResult generate(String question, List<SearchHit> hits) {
        List<Citation> citations = hits.stream()
                .map(hit -> new Citation(
                        hit.chunkId(),
                        hit.documentId(),
                        hit.documentTitle(),
                        excerpt(hit.content())))
                .toList();

        if (openAiApiKey == null || openAiApiKey.isBlank()) {
            return stubAnswer(question, citations);
        }

        String context = hits.stream()
                .map(hit -> "- [" + hit.documentTitle() + "] " + hit.content())
                .collect(Collectors.joining("\n"));

        String prompt = """
                You are an enterprise assistant. Answer using ONLY the context below.
                If the context is insufficient, say you do not have enough information.
                Cite document titles inline when possible.

                Context:
                %s

                Question: %s
                """.formatted(context, question);

        try {
            Map<String, Object> body = Map.of(
                    "model", openAiModel,
                    "messages", List.of(Map.of("role", "user", "content", prompt)),
                    "temperature", 0.2);

            String responseBody = openAiWebClient.post()
                    .uri("/v1/chat/completions")
                    .header(HttpHeaders.AUTHORIZATION, "Bearer " + openAiApiKey)
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(body)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();

            JsonNode root = objectMapper.readTree(responseBody);
            String answer = root.path("choices").path(0).path("message").path("content").asText();
            return new AnswerResult(answer, citations, openAiModel);
        } catch (Exception ex) {
            return stubAnswer(question, citations);
        }
    }

    private AnswerResult stubAnswer(String question, List<Citation> citations) {
        if (citations.isEmpty()) {
            return new AnswerResult(
                    "I do not have indexed knowledge to answer that yet. Upload documents via POST /api/v1/connectors/documents.",
                    List.of(),
                    "stub");
        }
        String summary = citations.stream()
                .map(c -> c.documentTitle() + ": " + c.excerpt())
                .collect(Collectors.joining(" "));
        return new AnswerResult(
                "Based on internal knowledge: " + summary,
                citations,
                "stub");
    }

    private String excerpt(String content) {
        if (content == null) {
            return "";
        }
        return content.length() > 200 ? content.substring(0, 200) + "..." : content;
    }

    public record AnswerResult(String answer, List<Citation> citations, String model) {
    }
}
