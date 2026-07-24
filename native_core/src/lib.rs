use std::path::Path;
use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VectorChunk {
    pub file_id: String,
    pub filepath: String,
    pub text: String,
    pub embedding: Vec<f32>,
}

pub struct RustSemanticEngine {
    watch_paths: Vec<String>,
}

impl RustSemanticEngine {
    pub fn new(watch_paths: Vec<String>) -> Self {
        Self { watch_paths }
    }

    pub fn scan_and_chunk(&self) -> Vec<VectorChunk> {
        let mut chunks = Vec::new();
        for path in &self.watch_paths {
            if Path::new(path).exists() {
                for entry in walkdir::WalkDir::new(path).into_iter().filter_map(|e| e.ok()) {
                    if entry.file_type().is_file() {
                        let chunk = VectorChunk {
                            file_id: entry.path().to_string_lossy().to_string(),
                            filepath: entry.path().to_string_lossy().to_string(),
                            text: format!("Rust Native Chunk for {}", entry.file_name().to_string_lossy()),
                            embedding: vec![0.0; 384],
                        };
                        chunks.push(chunk);
                    }
                }
            }
        }
        chunks
    }
}
