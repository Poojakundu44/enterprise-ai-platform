package com.enterprise.ai.embedding.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public final class EmbeddingMath {

    private static final int DIMENSION = 384;
    private static final ObjectMapper MAPPER = new ObjectMapper();

    private EmbeddingMath() {
    }

    public static float[] embedText(String text) {
        float[] vector = new float[DIMENSION];
        int seed = text == null ? 0 : text.hashCode();
        for (int i = 0; i < DIMENSION; i++) {
            vector[i] = (float) Math.sin(seed * (i + 1) * 0.01d);
        }
        normalize(vector);
        return vector;
    }

    public static String toJson(float[] vector) {
        try {
            List<Float> values = new ArrayList<>(vector.length);
            for (float v : vector) {
                values.add(v);
            }
            return MAPPER.writeValueAsString(values);
        } catch (JsonProcessingException ex) {
            throw new IllegalStateException("Failed to serialize embedding", ex);
        }
    }

    public static float[] fromJson(String json) {
        try {
            List<Double> values = MAPPER.readValue(
                    json,
                    MAPPER.getTypeFactory().constructCollectionType(List.class, Double.class));
            float[] vector = new float[values.size()];
            for (int i = 0; i < values.size(); i++) {
                vector[i] = values.get(i).floatValue();
            }
            return vector;
        } catch (JsonProcessingException ex) {
            throw new IllegalStateException("Failed to deserialize embedding", ex);
        }
    }

    public static double cosineSimilarity(float[] left, float[] right) {
        double dot = 0;
        double leftNorm = 0;
        double rightNorm = 0;
        int length = Math.min(left.length, right.length);
        for (int i = 0; i < length; i++) {
            dot += left[i] * right[i];
            leftNorm += left[i] * left[i];
            rightNorm += right[i] * right[i];
        }
        if (leftNorm == 0 || rightNorm == 0) {
            return 0;
        }
        return dot / (Math.sqrt(leftNorm) * Math.sqrt(rightNorm));
    }

    public static List<Scored> topK(List<float[]> corpus, List<ChunkEmbeddingView> views, float[] query, int topK) {
        List<Scored> scores = new ArrayList<>();
        for (int i = 0; i < corpus.size(); i++) {
            scores.add(new Scored(views.get(i), cosineSimilarity(query, corpus.get(i))));
        }
        scores.sort(Comparator.comparingDouble(Scored::score).reversed());
        return scores.subList(0, Math.min(topK, scores.size()));
    }

    private static void normalize(float[] vector) {
        double norm = 0;
        for (float v : vector) {
            norm += v * v;
        }
        norm = Math.sqrt(norm);
        if (norm == 0) {
            return;
        }
        for (int i = 0; i < vector.length; i++) {
            vector[i] = (float) (vector[i] / norm);
        }
    }

    public record ChunkEmbeddingView(
            java.util.UUID chunkId,
            java.util.UUID documentId,
            String documentTitle,
            String chunkContent,
            String embeddingJson
    ) {
    }

    public record Scored(ChunkEmbeddingView view, double score) {
    }
}
