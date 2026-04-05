"""Bi-gram search index generator.

Extracts stage data from events, then delegates index building to
the Rust bigram-index CLI tool for speed. Falls back to a pure-Python
implementation if the Rust binary is not available.
"""
import json
import shutil
import subprocess
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Any, Set

from .base_generator import BaseGenerator
from ..models.event import Event
from ..config import DIST_PATH


# Path to the pre-built Rust binary (release build)
_RUST_BINARY = Path(__file__).resolve().parents[2] / "tools" / "bigram-index" / "target" / "release" / "bigram-index"


class NGramConfig:
    """Configuration for search index generation."""

    def __init__(self, max_chunk_size: int = 500_000, debug_output: bool = False, **_kwargs):
        self.max_chunk_size = max_chunk_size
        self.debug_output = debug_output


class NGramSearchIndexGenerator(BaseGenerator):
    """Generator for bi-gram search index with Rust acceleration."""

    def __init__(self, config: NGramConfig = None):
        self.config = config or NGramConfig()

    def generate(self, events: List[Event], output_path: Path = DIST_PATH):
        """Generate bi-gram search index.

        1. Extract stage data from events (Python).
        2. Write intermediate stages.json.
        3. Call Rust bigram-index binary to build index + chunks.
        4. Fall back to Python if Rust binary is unavailable.
        """
        start = time.time()

        search_dir = output_path / "static" / "data" / "search"
        search_dir.mkdir(parents=True, exist_ok=True)
        chunks_dir = search_dir / "chunks"
        chunks_dir.mkdir(exist_ok=True)

        # Step 1: Extract stages
        stages = self._extract_stages(events)

        if self.config.debug_output:
            print(f"Extracted {len(stages)} stages from {len(events)} events")

        # Step 2: Write intermediate JSON
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(stages, f, ensure_ascii=False)
            stages_file = f.name

        try:
            # Step 3: Try Rust binary
            if _RUST_BINARY.exists():
                self._run_rust_indexer(stages_file, search_dir)
            else:
                if self.config.debug_output:
                    print(f"Rust binary not found at {_RUST_BINARY}, using Python fallback")
                self._python_fallback(stages, search_dir, chunks_dir)
        finally:
            Path(stages_file).unlink(missing_ok=True)

        elapsed_ms = int((time.time() - start) * 1000)
        print(f"Search index generation completed in {elapsed_ms}ms")

    def _run_rust_indexer(self, stages_file: str, search_dir: Path):
        """Call the Rust bigram-index binary."""
        cmd = [
            str(_RUST_BINARY),
            "--input", stages_file,
            "--output-dir", str(search_dir),
            "--max-chunk-size", str(self.config.max_chunk_size),
        ]
        if self.config.debug_output:
            cmd.append("--debug")

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Rust indexer failed: {result.stderr}")
            raise RuntimeError("Rust bigram-index failed")
        print(result.stdout.strip())
        if self.config.debug_output and result.stderr:
            print(result.stderr.strip())

    def _python_fallback(self, stages: List[Dict], search_dir: Path, chunks_dir: Path):
        """Pure-Python bi-gram index builder (fallback)."""
        # Build chunks
        chunks = self._build_chunks(stages)

        # Build stage -> chunk_id map
        stage_chunk_map = {}
        for chunk_id, chunk_stages in enumerate(chunks):
            for stage in chunk_stages:
                stage_chunk_map[stage["stage_id"]] = chunk_id

        # Build chunk-level inverted index (bigram -> set of chunk IDs)
        inverted = defaultdict(set)
        total_bigrams = 0

        for chunk_id, chunk_stages in enumerate(chunks):
            chunk_bgs = set()
            for stage in chunk_stages:
                searchable = " ".join([
                    stage.get("stage_name", ""),
                    stage.get("event_name", ""),
                    stage.get("stage_info", ""),
                    stage.get("full_content", ""),
                ])
                chunk_bgs.update(self._generate_bigrams(searchable))
            total_bigrams += len(chunk_bgs)
            for bg in chunk_bgs:
                inverted[bg].add(chunk_id)

        # Convert to serializable format: bigram -> sorted list of chunk IDs
        inverted_index = {bg: sorted(cids) for bg, cids in sorted(inverted.items())}

        # Build event_chunk_map
        event_chunk_map = defaultdict(lambda: {"chunks": [], "stages": []})
        for chunk_id, chunk_stages in enumerate(chunks):
            for stage in chunk_stages:
                info = event_chunk_map[stage["event_id"]]
                if chunk_id not in info["chunks"]:
                    info["chunks"].append(chunk_id)
                info["stages"].append(stage["stage_id"])

        # Write chunk files
        for chunk_id, chunk_stages in enumerate(chunks):
            chunk_data = {
                "chunk_id": chunk_id,
                "metadata": {
                    "chunk_size_bytes": sum(self._estimate_size(s) for s in chunk_stages),
                    "total_stages": len(chunk_stages),
                    "events_included": sorted(set(s["event_id"] for s in chunk_stages)),
                },
                "stages": chunk_stages,
            }
            with open(chunks_dir / f"chunk_{chunk_id}.json", "w", encoding="utf-8") as f:
                json.dump(chunk_data, f, ensure_ascii=False)

        # Write index.json
        total_size = sum(
            sum(self._estimate_size(s) for s in cs) for cs in chunks
        )
        avg_size = total_size // len(chunks) if chunks else 0

        index_data = {
            "metadata": {
                "total_chunks": len(chunks),
                "total_stages": len(stages),
                "average_chunk_size": avg_size,
                "ngram_config": {"sizes": [2], "min_frequency": 0},
                "index_stats": {
                    "total_ngrams": total_bigrams,
                    "unique_ngrams": len(inverted_index),
                    "compression_ratio": 1.0,
                },
            },
            "stage_chunk_map": stage_chunk_map,
            "event_chunk_map": dict(event_chunk_map),
            "inverted_index": inverted_index,
        }

        index_file = search_dir / "index.json"
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, ensure_ascii=False)

        print(f"Generated bi-gram search index (Python fallback): {index_file}")

    def _extract_stages(self, events: List[Event]) -> List[Dict[str, Any]]:
        """Extract stage-level data from events."""
        stages = []

        for event in events:
            stories = event.get_sorted_stories()

            stage_stories = defaultdict(list)
            for story in stories:
                stage_id = self._extract_stage_id(story.story_code)
                stage_stories[stage_id].append(story)

            for stage_id, story_list in stage_stories.items():
                full_content = []
                all_speakers: Set[str] = set()

                for story in story_list:
                    story_content = self._extract_story_content(story)
                    full_content.append(story_content)
                    all_speakers.update(self._extract_speakers(story))

                combined_content = " ".join(full_content)
                stage = {
                    "stage_id": stage_id,
                    "stage_name": story_list[0].story_name or "",
                    "event_id": event.event_id,
                    "event_name": event.event_name or "",
                    "stage_type": self._determine_stage_type(stage_id),
                    "stage_info": story_list[0].story_info or "",
                    "url": f"events/{event.event_id}/stories/{Path(story_list[0].story_code).stem if story_list[0].story_code else 'story'}.html",
                    "full_content": combined_content,
                    "speakers": sorted(all_speakers),
                    "content_length": len(combined_content),
                }
                stages.append(stage)

        return stages

    def _extract_stage_id(self, story_code: str) -> str:
        if not story_code:
            return "unknown"
        return Path(story_code).stem

    def _extract_story_content(self, story) -> str:
        text_parts = []
        for element in story.story_list:
            prop = element.prop.lower()
            if prop in ("name", "dialog"):
                content = element.get_text()
                if content:
                    text_parts.append(content)
            elif prop == "subtitle":
                subtitle = element.attributes.get("text")
                if subtitle:
                    text_parts.append(subtitle)
        return " ".join(text_parts)

    def _extract_speakers(self, story) -> Set[str]:
        speakers = set()
        for element in story.story_list:
            speaker = element.get_speaker()
            if speaker:
                speakers.add(speaker)
        return speakers

    def _determine_stage_type(self, stage_id: str) -> str:
        if "-ST-" in stage_id:
            return "STORY"
        elif "-EX" in stage_id:
            return "EXTRA"
        return "MAIN"

    # -- Python fallback helpers --

    def _estimate_size(self, stage: Dict) -> int:
        return 200 + len(stage.get("full_content", "")) + sum(len(s) for s in stage.get("speakers", []))

    def _build_chunks(self, stages: List[Dict]) -> List[List[Dict]]:
        chunks = []
        current = []
        current_size = 0
        max_size = self.config.max_chunk_size

        for stage in stages:
            size = self._estimate_size(stage)
            if size > max_size:
                if current:
                    chunks.append(current)
                chunks.append([stage])
                current = []
                current_size = 0
                continue
            if current_size + size > max_size and current:
                chunks.append(current)
                current = []
                current_size = 0
            current.append(stage)
            current_size += size

        if current:
            chunks.append(current)
        return chunks

    @staticmethod
    def _generate_bigrams(text: str) -> Set[str]:
        chars = list(text.lower())
        bigrams = set()
        for i in range(len(chars) - 1):
            bg = chars[i] + chars[i + 1]
            if bg.strip():
                bigrams.add(bg)
        return bigrams


def run_performance_tuning(events: List[Event], output_path: Path = DIST_PATH):
    """Run a simple build and report timing."""
    gen = NGramSearchIndexGenerator(NGramConfig(debug_output=True))
    gen.generate(events, output_path)
