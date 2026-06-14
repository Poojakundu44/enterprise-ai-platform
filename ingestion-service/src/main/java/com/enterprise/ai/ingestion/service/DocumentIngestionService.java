package com.enterprise.ai.ingestion.service;

import com.enterprise.ai.common.dto.ChunkIndexRequest;
import com.enterprise.ai.common.dto.DocumentIngestionResponse;
import com.enterprise.ai.common.dto.DocumentUploadRequest;
import com.enterprise.ai.ingestion.client.EmbeddingClient;
import com.enterprise.ai.ingestion.domain.Document;
import com.enterprise.ai.ingestion.domain.DocumentChunk;
import com.enterprise.ai.ingestion.repository.DocumentChunkRepository;
import com.enterprise.ai.ingestion.repository.DocumentRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;

@Service
public class DocumentIngestionService {

    private final DocumentRepository documentRepository;
    private final DocumentChunkRepository chunkRepository;
    private final TextChunker textChunker;
    private final EmbeddingClient embeddingClient;

    public DocumentIngestionService(
            DocumentRepository documentRepository,
            DocumentChunkRepository chunkRepository,
            TextChunker textChunker,
            EmbeddingClient embeddingClient) {
        this.documentRepository = documentRepository;
        this.chunkRepository = chunkRepository;
        this.textChunker = textChunker;
        this.embeddingClient = embeddingClient;
    }

    @Transactional
    public DocumentIngestionResponse ingest(DocumentUploadRequest request, String ownerEmail) {
        Document document = new Document(
                request.title(),
                request.sourceType(),
                request.externalId(),
                ownerEmail);
        documentRepository.save(document);

        List<String> parts = textChunker.chunk(request.content());
        List<DocumentChunk> savedChunks = new ArrayList<>();
        int sequence = 0;
        for (String part : parts) {
            DocumentChunk chunk = new DocumentChunk(document.getId(), sequence++, part);
            savedChunks.add(chunkRepository.save(chunk));
        }

        if (!savedChunks.isEmpty()) {
            List<ChunkIndexRequest.ChunkPayload> payloads = savedChunks.stream()
                    .map(chunk -> new ChunkIndexRequest.ChunkPayload(
                            chunk.getId(),
                            document.getId(),
                            document.getTitle(),
                            chunk.getContent()))
                    .toList();
            embeddingClient.indexChunks(new ChunkIndexRequest(payloads));
        }

        return new DocumentIngestionResponse(document.getId(), savedChunks.size(), "INDEXED");
    }
}
