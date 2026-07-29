-- PostgreSQL Database Schema for High-Throughput Vector Storage Engine
CREATE TABLE IF NOT EXISTS file_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filepath VARCHAR(1024) NOT NULL UNIQUE,
    checksum VARCHAR(64) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS embedding_chunks (
    chunk_id VARCHAR(128) PRIMARY KEY,
    document_id UUID REFERENCES file_documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    start_line INT NOT NULL,
    end_line INT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(384)
);

CREATE INDEX idx_file_documents_checksum ON file_documents(checksum);
CREATE INDEX idx_embedding_chunks_doc_id ON embedding_chunks(document_id);
