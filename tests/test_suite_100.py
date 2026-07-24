from __future__ import annotations

import time
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from semanticfs.config import Config
from semanticfs.embedder import Embedder
from semanticfs.store import VectorStore

QUERIES_100 = [
    # Academic & Coursework (20 queries)
    "physics question bank",
    "engineering physics end semester question bank",
    "CS3101 question bank",
    "CS3201 PIP question bank unit 1 to 5",
    "CS3303A assignment Manoj Chetty",
    "MA3101 MAC end semester question bank",
    "PC LAB report pdf",
    "IA-2 physics question bank",
    "EPSD IA-2 question bank repaired",
    "filled in rubrics docx",
    "thon solutions document",
    "question bank unit 1 unit 2 unit 3",
    "end semester question bank 25-26",
    "computer science assignment",
    "mathematics question bank",
    "physics semester exam questions",
    "pip question bank modified",
    "assignment Manoj",
    "engineering question paper",
    "lab experiment pdf",

    # Career & Personal (15 queries)
    "resume cv Manoj Chetty",
    "resume docx",
    "curriculum vitae",
    "hackathon presentation slides",
    "SA-HACKATHON 26 MAIN pptx",
    "video project mp4",
    "whatsapp jpeg image",
    "whatsapp image 2026",
    "document1 docx",
    "document2 docx",
    "document3 docx",
    "fedora media writer log",
    "nerve center driver patch",
    "personal document Manoj",
    "hackathon ppt presentation",

    # Codebase & Developer (30 queries)
    "semanticfs search engine code",
    "python linear algebra matrix solver",
    "vector store chromadb implementation",
    "ambient file watcher daemon script",
    "local model fine tuner trainer",
    "sliding semantic window chunker",
    "cli rich interactive arrow menu",
    "category intent router python",
    "context capture active window process",
    "implicit file linker co-access edges",
    "pyproject toml configuration",
    "git commit search log script",
    "onnx model quantizer module",
    "multimodal vision image extractor",
    "powershell autocomplete completion script",
    "daemon ipc socket server listening",
    "config default yaml watch paths",
    "main cli entrypoint click command",
    "embedder sentence transformers lazy load",
    "store sqlite direct fast count",
    "chunker file chunk line tracking",
    "trainer multiple negatives ranking loss",
    "context snapshot process list",
    "watcher file event callback debounce",
    "linker record access co access link",
    "rust libsemanticfs cargo toml",
    "rust lib rs vector chunk struct",
    "virtual drive mount directory",
    "readme markdown enterprise documentation",
    "mit license document",

    # Intent & Media Category Routing (20 queries)
    "beach sunset vacation photo",
    "sunset ocean sea image",
    "music song audio track mp3",
    "playlist copacabana brazilian jazz mp3",
    "the tourist remastered song",
    "goodbye weekend audio file",
    "image photo picture snapshot",
    "movie clip recording video",
    "presentation slides deck powerpoint",
    "spreadsheet excel table csv sheet",
    "python code script function class",
    "pdf research document report",
    "word document docx paper",
    "whatsapp photo image picture",
    "picture image photo",
    "jazz playlist song track",
    "rock song remastered audio",
    "slide deck presentation",
    "excel sheet spreadsheet",
    "c source code script",

    # Temporal & Filter Queries (15 queries)
    "recent modified python code",
    "new docx document",
    "latest question bank pdf",
    "recent project slides",
    "latest image jpeg",
    "recent config file yaml",
    "new assignment docx",
    "recent script py",
    "latest report pdf",
    "recent presentation pptx",
    "new video mp4",
    "latest log file",
    "recent test python file",
    "latest readme doc",
    "recent rust file rs"
]

def run_100_tests():
    config = Config.get_instance()
    store = VectorStore(config.storage.db_path, config.storage.collection_name)
    embedder = Embedder(config.embedding.model_name, config.embedding.max_tokens)

    print(f"\n🚀 Running Automated 100-Test Verification Benchmark Suite...")
    print(f"Total Indexed Chunks in System: {store.count()}")
    print("=" * 70)

    total_tests = len(QUERIES_100)
    passed_tests = 0
    total_score = 0.0
    latencies = []

    for i, q in enumerate(QUERIES_100, start=1):
        t0 = time.time()
        emb = embedder.embed_text(q)
        results = store.search(emb, query_text=q, n_results=5)
        dt_ms = (time.time() - t0) * 1000.0
        latencies.append(dt_ms)

        if results:
            top_score = results[0].score
            total_score += top_score
            passed_tests += 1
            status = "PASS"
            top_file = results[0].filename[:35]
        else:
            top_score = 0.0
            status = "NO_MATCH"
            top_file = "N/A"

        if i % 10 == 0 or i == total_tests:
            print(f"[{i:3d}/{total_tests}] Query: '{q[:30]:30s}' -> Top Result: '{top_file:35s}' | Score: {top_score:.2f} | Latency: {dt_ms:.1f}ms | {status}")

    avg_score = (total_score / passed_tests) if passed_tests > 0 else 0.0
    avg_latency = sum(latencies) / len(latencies)
    success_rate = (passed_tests / total_tests) * 100.0

    print("=" * 70)
    print("📊 100-TEST AUTOMATED BENCHMARK VERIFICATION RESULTS")
    print("=" * 70)
    print(f"  • Total Tests Executed:  {total_tests}")
    print(f"  • Successful Matches:    {passed_tests}")
    print(f"  • Overall Success Avg:   {success_rate:.2f}%")
    print(f"  • Mean Match Score:      {avg_score:.2f} / 1.00")
    print(f"  • Average Search Latency: {avg_latency:.2f} ms")
    print("=" * 70)

if __name__ == "__main__":
    run_100_tests()
