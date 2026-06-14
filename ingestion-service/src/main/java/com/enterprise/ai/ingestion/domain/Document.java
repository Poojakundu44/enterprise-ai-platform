package com.enterprise.ai.ingestion.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "documents")
@Getter
@Setter
@NoArgsConstructor
public class Document {

    @Id
    private UUID id;

    @Column(nullable = false, length = 500)
    private String title;

    @Column(name = "source_type", nullable = false, length = 64)
    private String sourceType;

    @Column(name = "external_id")
    private String externalId;

    @Column(name = "owner_email")
    private String ownerEmail;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    public Document(String title, String sourceType, String externalId, String ownerEmail) {
        this.id = UUID.randomUUID();
        this.title = title;
        this.sourceType = sourceType;
        this.externalId = externalId;
        this.ownerEmail = ownerEmail;
        this.createdAt = Instant.now();
    }
}
