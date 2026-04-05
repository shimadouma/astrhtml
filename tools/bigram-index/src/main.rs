use clap::Parser;
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, HashMap, HashSet};
use std::fs;
use std::path::PathBuf;
use std::time::Instant;

#[derive(Parser)]
#[command(name = "bigram-index", about = "Build bi-gram inverted index for full-text search")]
struct Cli {
    /// Path to the intermediate stages JSON file
    #[arg(long, default_value = "stages.json")]
    input: PathBuf,

    /// Output directory for index.json and chunks/
    #[arg(long, default_value = "dist/static/data/search")]
    output_dir: PathBuf,

    /// Maximum chunk size in bytes (approximate)
    #[arg(long, default_value_t = 500_000)]
    max_chunk_size: usize,

    /// Enable debug output
    #[arg(long)]
    debug: bool,
}

#[derive(Deserialize)]
struct Stage {
    stage_id: String,
    stage_name: String,
    event_id: String,
    event_name: String,
    stage_type: String,
    stage_info: String,
    url: String,
    full_content: String,
    speakers: Vec<String>,
    content_length: usize,
}

#[derive(Serialize)]
struct ChunkOutput {
    chunk_id: usize,
    metadata: ChunkMetadata,
    stages: Vec<StageOutput>,
}

#[derive(Serialize)]
struct ChunkMetadata {
    chunk_size_bytes: usize,
    total_stages: usize,
    events_included: Vec<String>,
}

#[derive(Serialize)]
struct StageOutput {
    stage_id: String,
    stage_name: String,
    event_id: String,
    event_name: String,
    stage_type: String,
    stage_info: String,
    url: String,
    full_content: String,
    speakers: Vec<String>,
    content_length: usize,
}

#[derive(Serialize)]
struct IndexOutput {
    metadata: IndexMetadata,
    stage_chunk_map: BTreeMap<String, usize>,
    event_chunk_map: BTreeMap<String, EventChunkInfo>,
    /// Chunk-level inverted index: bigram -> sorted list of chunk IDs.
    /// Stage-level filtering is deferred to the client after chunk loading.
    inverted_index: BTreeMap<String, Vec<usize>>,
}

#[derive(Serialize)]
struct IndexMetadata {
    total_chunks: usize,
    total_stages: usize,
    average_chunk_size: usize,
    ngram_config: NgramConfig,
    index_stats: IndexStats,
}

#[derive(Serialize)]
struct NgramConfig {
    sizes: Vec<usize>,
    min_frequency: usize,
}

#[derive(Serialize)]
struct IndexStats {
    total_ngrams: usize,
    unique_ngrams: usize,
    compression_ratio: f64,
}

#[derive(Serialize)]
struct EventChunkInfo {
    chunks: Vec<usize>,
    stages: Vec<String>,
}

impl From<&Stage> for StageOutput {
    fn from(s: &Stage) -> Self {
        StageOutput {
            stage_id: s.stage_id.clone(),
            stage_name: s.stage_name.clone(),
            event_id: s.event_id.clone(),
            event_name: s.event_name.clone(),
            stage_type: s.stage_type.clone(),
            stage_info: s.stage_info.clone(),
            url: s.url.clone(),
            full_content: s.full_content.clone(),
            speakers: s.speakers.clone(),
            content_length: s.content_length,
        }
    }
}

fn estimate_stage_size(stage: &Stage) -> usize {
    200 + stage.full_content.len()
        + stage.speakers.iter().map(|s| s.len()).sum::<usize>()
        + stage.stage_name.len()
        + stage.stage_info.len()
}

/// Build chunks respecting stage boundaries.
fn build_chunks(stages: &[Stage], max_chunk_size: usize) -> Vec<Vec<usize>> {
    let mut chunks: Vec<Vec<usize>> = Vec::new();
    let mut current_chunk: Vec<usize> = Vec::new();
    let mut current_size: usize = 0;

    for (i, stage) in stages.iter().enumerate() {
        let stage_size = estimate_stage_size(stage);

        // If single stage exceeds chunk size, create dedicated chunk
        if stage_size > max_chunk_size {
            if !current_chunk.is_empty() {
                chunks.push(current_chunk);
                current_chunk = Vec::new();
                current_size = 0;
            }
            chunks.push(vec![i]);
            continue;
        }

        if current_size + stage_size > max_chunk_size && !current_chunk.is_empty() {
            chunks.push(current_chunk);
            current_chunk = Vec::new();
            current_size = 0;
        }

        current_chunk.push(i);
        current_size += stage_size;
    }

    if !current_chunk.is_empty() {
        chunks.push(current_chunk);
    }

    chunks
}

/// Generate bi-grams from text (lowercased). Skips whitespace-only bi-grams.
fn generate_bigrams(text: &str) -> HashSet<String> {
    let chars: Vec<char> = text.to_lowercase().chars().collect();
    let mut bigrams = HashSet::new();

    if chars.len() < 2 {
        return bigrams;
    }

    for i in 0..chars.len() - 1 {
        let bg: String = chars[i..=i + 1].iter().collect();
        if !bg.trim().is_empty() {
            bigrams.insert(bg);
        }
    }

    bigrams
}

fn main() {
    let cli = Cli::parse();
    let start = Instant::now();

    // Read input
    let input_data = fs::read_to_string(&cli.input)
        .unwrap_or_else(|e| panic!("Failed to read {}: {}", cli.input.display(), e));

    let stages: Vec<Stage> = serde_json::from_str(&input_data)
        .unwrap_or_else(|e| panic!("Failed to parse JSON: {}", e));

    if cli.debug {
        eprintln!("Loaded {} stages", stages.len());
    }

    // Build chunks
    let chunk_indices = build_chunks(&stages, cli.max_chunk_size);
    let num_chunks = chunk_indices.len();

    if cli.debug {
        eprintln!("Created {} chunks", num_chunks);
    }

    // Build stage -> chunk_id mapping
    let mut stage_chunk_map: BTreeMap<String, usize> = BTreeMap::new();
    for (chunk_id, indices) in chunk_indices.iter().enumerate() {
        for &stage_idx in indices {
            stage_chunk_map.insert(stages[stage_idx].stage_id.clone(), chunk_id);
        }
    }

    // Build chunk-level inverted index (bi-gram -> set of chunk IDs)
    let mut inverted: HashMap<String, HashSet<usize>> = HashMap::new();
    let mut total_bigrams: usize = 0;

    for (chunk_id, indices) in chunk_indices.iter().enumerate() {
        // Collect all bigrams from all stages in this chunk
        let mut chunk_bigrams: HashSet<String> = HashSet::new();
        for &stage_idx in indices {
            let stage = &stages[stage_idx];
            let searchable = format!(
                "{} {} {} {}",
                stage.stage_name, stage.event_name, stage.stage_info, stage.full_content
            );
            chunk_bigrams.extend(generate_bigrams(&searchable));
        }
        total_bigrams += chunk_bigrams.len();

        for bg in chunk_bigrams {
            inverted.entry(bg).or_default().insert(chunk_id);
        }
    }

    // Convert to sorted output format
    let mut inverted_index: BTreeMap<String, Vec<usize>> = BTreeMap::new();
    for (bigram, chunk_ids) in &inverted {
        let mut sorted_chunks: Vec<usize> = chunk_ids.iter().copied().collect();
        sorted_chunks.sort();
        inverted_index.insert(bigram.clone(), sorted_chunks);
    }

    let unique_bigrams = inverted_index.len();

    if cli.debug {
        eprintln!(
            "Total bi-grams generated: {}, unique in index: {}",
            total_bigrams, unique_bigrams
        );
    }

    // Build event_chunk_map
    let mut event_chunk_map: BTreeMap<String, EventChunkInfo> = BTreeMap::new();
    for (chunk_id, indices) in chunk_indices.iter().enumerate() {
        for &stage_idx in indices {
            let stage = &stages[stage_idx];
            let info = event_chunk_map
                .entry(stage.event_id.clone())
                .or_insert_with(|| EventChunkInfo {
                    chunks: Vec::new(),
                    stages: Vec::new(),
                });
            if !info.chunks.contains(&chunk_id) {
                info.chunks.push(chunk_id);
            }
            info.stages.push(stage.stage_id.clone());
        }
    }

    // Calculate average chunk size
    let total_chunk_size: usize = chunk_indices
        .iter()
        .map(|indices| {
            indices
                .iter()
                .map(|&i| estimate_stage_size(&stages[i]))
                .sum::<usize>()
        })
        .sum();
    let avg_chunk_size = if num_chunks > 0 {
        total_chunk_size / num_chunks
    } else {
        0
    };

    // Write output
    let output_dir = &cli.output_dir;
    fs::create_dir_all(output_dir).expect("Failed to create output directory");
    let chunks_dir = output_dir.join("chunks");
    fs::create_dir_all(&chunks_dir).expect("Failed to create chunks directory");

    // Write chunk files
    for (chunk_id, indices) in chunk_indices.iter().enumerate() {
        let stage_outputs: Vec<StageOutput> =
            indices.iter().map(|&i| StageOutput::from(&stages[i])).collect();

        let events_included: Vec<String> = {
            let mut events: Vec<String> = indices
                .iter()
                .map(|&i| stages[i].event_id.clone())
                .collect::<HashSet<_>>()
                .into_iter()
                .collect();
            events.sort();
            events
        };

        let chunk_size: usize = indices.iter().map(|&i| estimate_stage_size(&stages[i])).sum();

        let chunk_output = ChunkOutput {
            chunk_id,
            metadata: ChunkMetadata {
                chunk_size_bytes: chunk_size,
                total_stages: stage_outputs.len(),
                events_included,
            },
            stages: stage_outputs,
        };

        let chunk_file = chunks_dir.join(format!("chunk_{}.json", chunk_id));
        let chunk_json = serde_json::to_string(&chunk_output).expect("Failed to serialize chunk");
        fs::write(&chunk_file, &chunk_json).expect("Failed to write chunk file");

        if cli.debug {
            eprintln!(
                "  Chunk {}: {} stages, {} bytes",
                chunk_id,
                indices.len(),
                chunk_json.len()
            );
        }
    }

    // Write index.json
    let index_output = IndexOutput {
        metadata: IndexMetadata {
            total_chunks: num_chunks,
            total_stages: stages.len(),
            average_chunk_size: avg_chunk_size,
            ngram_config: NgramConfig {
                sizes: vec![2],
                min_frequency: 0,
            },
            index_stats: IndexStats {
                total_ngrams: total_bigrams,
                unique_ngrams: unique_bigrams,
                compression_ratio: 1.0,
            },
        },
        stage_chunk_map,
        event_chunk_map,
        inverted_index,
    };

    let index_file = output_dir.join("index.json");
    let index_json = serde_json::to_string(&index_output).expect("Failed to serialize index");
    fs::write(&index_file, &index_json).expect("Failed to write index file");

    let elapsed = start.elapsed();
    println!(
        "Generated bi-gram search index: {} ({} bytes)",
        index_file.display(),
        index_json.len()
    );
    println!(
        "  {} stages, {} chunks, {} unique bi-grams, {:.1}ms",
        stages.len(),
        num_chunks,
        unique_bigrams,
        elapsed.as_secs_f64() * 1000.0
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_generate_bigrams_basic() {
        let result = generate_bigrams("abc");
        assert!(result.contains("ab"));
        assert!(result.contains("bc"));
        assert_eq!(result.len(), 2);
    }

    #[test]
    fn test_generate_bigrams_japanese() {
        let result = generate_bigrams("アーク");
        assert!(result.contains("アー"));
        assert!(result.contains("ーク"));
        assert_eq!(result.len(), 2);
    }

    #[test]
    fn test_generate_bigrams_skips_whitespace() {
        let result = generate_bigrams("a b");
        assert!(result.contains("a "));
        assert!(result.contains(" b"));
    }

    #[test]
    fn test_generate_bigrams_empty() {
        let result = generate_bigrams("");
        assert!(result.is_empty());
    }

    #[test]
    fn test_generate_bigrams_single_char() {
        let result = generate_bigrams("a");
        assert!(result.is_empty());
    }

    #[test]
    fn test_build_chunks_single() {
        let stages = vec![make_test_stage("s1", 100)];
        let chunks = build_chunks(&stages, 500_000);
        assert_eq!(chunks.len(), 1);
        assert_eq!(chunks[0], vec![0]);
    }

    #[test]
    fn test_build_chunks_split() {
        let stages = vec![
            make_test_stage("s1", 300),
            make_test_stage("s2", 300),
            make_test_stage("s3", 300),
        ];
        let chunks = build_chunks(&stages, 700);
        assert!(chunks.len() >= 2);
    }

    fn make_test_stage(id: &str, content_len: usize) -> Stage {
        Stage {
            stage_id: id.to_string(),
            stage_name: "Test".to_string(),
            event_id: "event1".to_string(),
            event_name: "Event 1".to_string(),
            stage_type: "MAIN".to_string(),
            stage_info: String::new(),
            url: format!("events/event1/stories/{}.html", id),
            full_content: "x".repeat(content_len),
            speakers: vec![],
            content_length: content_len,
        }
    }
}
