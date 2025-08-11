"""N-gram based search index generator with configurable parameters."""
import json
import math
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass

from .base_generator import BaseGenerator
from ..models.event import Event
from ..config import DIST_PATH


@dataclass
class NGramConfig:
    """Configuration for N-gram index generation."""
    ngram_sizes: List[int] = None  # Default: [2, 3]
    min_frequency: int = 2  # Minimum frequency to include in index
    max_chunk_size: int = 500000  # Target chunk size in bytes
    max_index_size: int = 100000  # Maximum index size in bytes
    enable_compression: bool = True  # Enable index compression
    debug_output: bool = False  # Enable debug information
    
    def __post_init__(self):
        if self.ngram_sizes is None:
            self.ngram_sizes = [2, 3]


@dataclass 
class IndexStats:
    """Statistics for N-gram index analysis."""
    total_ngrams: int = 0
    unique_ngrams: int = 0
    index_size_bytes: int = 0
    chunk_count: int = 0
    avg_chunk_size: int = 0
    compression_ratio: float = 1.0
    generation_time_ms: int = 0


class NGramSearchIndexGenerator(BaseGenerator):
    """Generator for N-gram based search index with performance tuning."""
    
    def __init__(self, config: NGramConfig = None):
        self.config = config or NGramConfig()
        self.stats = IndexStats()
        
    def generate(self, events: List[Event], output_path: Path = DIST_PATH) -> IndexStats:
        """
        Generate N-gram search index with configurable parameters.
        
        Args:
            events: List of event objects
            output_path: Output directory path
            
        Returns:
            IndexStats: Performance statistics
        """
        import time
        start_time = time.time()
        
        # Create search directory structure
        search_dir = output_path / 'static' / 'data' / 'search'
        search_dir.mkdir(parents=True, exist_ok=True)
        chunks_dir = search_dir / 'chunks'
        chunks_dir.mkdir(exist_ok=True)
        
        if self.config.debug_output:
            print(f"N-gram config: sizes={self.config.ngram_sizes}, "
                  f"min_freq={self.config.min_frequency}, "
                  f"max_chunk={self.config.max_chunk_size}B")
        
        # Build stage-aware chunks
        stages = self._extract_stages(events)
        chunks = self._build_stage_chunks(stages)
        
        # Generate N-gram inverted index
        inverted_index = self._build_ngram_inverted_index(stages)
        
        # Apply frequency filtering and compression
        inverted_index = self._filter_and_compress_index(inverted_index)
        
        # Build metadata
        metadata = self._build_metadata(chunks, inverted_index)
        
        # Write files
        self._write_chunks(chunks, chunks_dir)
        self._write_index(metadata, inverted_index, search_dir / 'index.json')
        
        # Calculate statistics
        self.stats.generation_time_ms = int((time.time() - start_time) * 1000)
        self._calculate_stats(chunks, inverted_index)
        
        if self.config.debug_output:
            self._print_stats()
            
        return self.stats
    
    def _extract_stages(self, events: List[Event]) -> List[Dict[str, Any]]:
        """Extract stage-level data from events."""
        stages = []
        
        for event in events:
            stories = event.get_sorted_stories()
            
            # Group stories by stage (handle duplicate stage IDs)
            stage_stories = defaultdict(list)
            for story in stories:
                stage_id = self._extract_stage_id(story.story_code)
                stage_stories[stage_id].append(story)
            
            # Create stage objects
            for stage_id, story_list in stage_stories.items():
                # Combine all story parts for this stage
                full_content = []
                all_speakers = set()
                
                for story in story_list:
                    story_content = self._extract_story_content(story)
                    full_content.append(story_content)
                    all_speakers.update(self._extract_speakers(story))
                
                stage = {
                    'stage_id': stage_id,
                    'stage_name': story_list[0].story_name,
                    'event_id': event.event_id,
                    'event_name': event.event_name,
                    'stage_type': self._determine_stage_type(stage_id),
                    'stage_info': story_list[0].story_info or '',
                    'url': f"events/{event.event_id}/stories/{Path(story_list[0].story_code).stem if story_list[0].story_code else 'story'}.html",
                    'full_content': ' '.join(full_content),
                    'speakers': list(all_speakers),
                    'content_length': sum(len(content) for content in full_content)
                }
                stages.append(stage)
        
        return stages
    
    def _extract_stage_id(self, story_code: str) -> str:
        """Extract stage ID from story code."""
        if not story_code:
            return 'unknown'
        # Remove file extension and use as stage ID
        return Path(story_code).stem
    
    def _extract_story_content(self, story) -> str:
        """Extract searchable text from story."""
        text_parts = []
        
        for element in story.story_list:
            prop = element.prop.lower()
            
            if prop in ['name', 'dialog']:
                content = element.get_text()
                if content:
                    text_parts.append(content)
            elif prop == 'subtitle':
                subtitle = element.attributes.get('text')
                if subtitle:
                    text_parts.append(subtitle)
        
        return ' '.join(text_parts)
    
    def _extract_speakers(self, story) -> Set[str]:
        """Extract speaker names from story."""
        speakers = set()
        for element in story.story_list:
            speaker = element.get_speaker()
            if speaker:
                speakers.add(speaker)
        return speakers
    
    def _determine_stage_type(self, stage_id: str) -> str:
        """Determine stage type from stage ID."""
        if '-ST-' in stage_id:
            return 'STORY'
        elif '-EX' in stage_id:
            return 'EXTRA'
        else:
            return 'MAIN'
    
    def _build_stage_chunks(self, stages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build chunks respecting stage boundaries."""
        chunks = []
        current_chunk = {'chunk_id': 0, 'stages': [], 'size_bytes': 0}
        
        for stage in stages:
            stage_size = self._estimate_stage_size(stage)
            
            # If single stage exceeds chunk size, create dedicated chunk
            if stage_size > self.config.max_chunk_size:
                if current_chunk['stages']:
                    chunks.append(current_chunk)
                
                chunks.append({
                    'chunk_id': len(chunks),
                    'stages': [stage],
                    'size_bytes': stage_size,
                    'is_large_stage': True
                })
                
                current_chunk = {'chunk_id': len(chunks), 'stages': [], 'size_bytes': 0}
                continue
            
            # Check if adding stage exceeds chunk limit
            if current_chunk['size_bytes'] + stage_size > self.config.max_chunk_size:
                if current_chunk['stages']:
                    chunks.append(current_chunk)
                current_chunk = {'chunk_id': len(chunks), 'stages': [stage], 'size_bytes': stage_size}
            else:
                current_chunk['stages'].append(stage)
                current_chunk['size_bytes'] += stage_size
        
        # Add final chunk
        if current_chunk['stages']:
            chunks.append(current_chunk)
        
        self.stats.chunk_count = len(chunks)
        if chunks:
            self.stats.avg_chunk_size = sum(chunk['size_bytes'] for chunk in chunks) // len(chunks)
        
        return chunks
    
    def _estimate_stage_size(self, stage: Dict[str, Any]) -> int:
        """Estimate stage size in bytes when serialized to JSON."""
        # Rough estimation: JSON overhead + content length
        base_size = 200  # Metadata overhead
        content_size = len(stage.get('full_content', ''))
        speakers_size = sum(len(speaker) for speaker in stage.get('speakers', []))
        return base_size + content_size + speakers_size
    
    def _build_ngram_inverted_index(self, stages: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Build N-gram inverted index."""
        inverted_index = defaultdict(lambda: defaultdict(set))
        
        for chunk_id, stage in enumerate(stages):
            # Generate N-grams from all searchable text
            searchable_text = ' '.join([
                stage.get('stage_name', ''),
                stage.get('event_name', ''),
                stage.get('stage_info', ''),
                stage.get('full_content', '')
            ])
            
            ngrams = self._generate_ngrams(searchable_text)
            
            for ngram in ngrams:
                inverted_index[ngram][chunk_id].add(stage['stage_id'])
        
        # Convert to serializable format
        result = {}
        for ngram, chunks in inverted_index.items():
            result[ngram] = [
                {'chunk': chunk_id, 'stages': list(stage_ids)}
                for chunk_id, stage_ids in chunks.items()
            ]
        
        self.stats.total_ngrams = sum(len(chunks) for chunks in inverted_index.values())
        self.stats.unique_ngrams = len(inverted_index)
        
        return result
    
    def _generate_ngrams(self, text: str) -> Set[str]:
        """Generate N-grams from text."""
        if not text:
            return set()
        
        ngrams = set()
        text = text.lower().strip()
        
        for n in self.config.ngram_sizes:
            if len(text) >= n:
                for i in range(len(text) - n + 1):
                    ngram = text[i:i+n]
                    # Skip ngrams that are only whitespace or punctuation
                    if ngram.strip() and not ngram.isspace():
                        ngrams.add(ngram)
        
        return ngrams
    
    def _filter_and_compress_index(self, inverted_index: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Filter by frequency and apply compression if enabled."""
        if not self.config.enable_compression:
            return inverted_index
        
        # Calculate N-gram frequencies
        ngram_frequencies = {
            ngram: sum(len(entry['stages']) for entry in entries)
            for ngram, entries in inverted_index.items()
        }
        
        # Filter by minimum frequency
        filtered_index = {
            ngram: entries 
            for ngram, entries in inverted_index.items()
            if ngram_frequencies[ngram] >= self.config.min_frequency
        }
        
        # Check if index size is within limits
        estimated_size = self._estimate_index_size(filtered_index)
        
        if estimated_size > self.config.max_index_size:
            # Aggressive filtering: keep only high-frequency N-grams
            sorted_ngrams = sorted(
                ngram_frequencies.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Keep top N-grams that fit within size limit
            selected_ngrams = set()
            current_size = 0
            
            for ngram, freq in sorted_ngrams:
                ngram_size = len(json.dumps(filtered_index[ngram]))
                if current_size + ngram_size <= self.config.max_index_size:
                    selected_ngrams.add(ngram)
                    current_size += ngram_size
                else:
                    break
            
            filtered_index = {
                ngram: entries
                for ngram, entries in filtered_index.items()
                if ngram in selected_ngrams
            }
        
        original_size = self._estimate_index_size(inverted_index)
        final_size = self._estimate_index_size(filtered_index)
        self.stats.compression_ratio = original_size / final_size if final_size > 0 else 1.0
        
        return filtered_index
    
    def _estimate_index_size(self, index: Dict[str, Any]) -> int:
        """Estimate serialized size of index."""
        return len(json.dumps(index, ensure_ascii=False))
    
    def _build_metadata(self, chunks: List[Dict[str, Any]], inverted_index: Dict[str, Any]) -> Dict[str, Any]:
        """Build index metadata."""
        # Build stage to chunk mapping
        stage_chunk_map = {}
        event_chunk_map = defaultdict(lambda: {'chunks': set(), 'stages': []})
        
        for chunk in chunks:
            for stage in chunk['stages']:
                stage_chunk_map[stage['stage_id']] = chunk['chunk_id']
                event_chunk_map[stage['event_id']]['chunks'].add(chunk['chunk_id'])
                event_chunk_map[stage['event_id']]['stages'].append(stage['stage_id'])
        
        # Convert sets to lists for JSON serialization
        for event_data in event_chunk_map.values():
            event_data['chunks'] = list(event_data['chunks'])
        
        return {
            'metadata': {
                'total_chunks': len(chunks),
                'total_stages': sum(len(chunk['stages']) for chunk in chunks),
                'average_chunk_size': self.stats.avg_chunk_size,
                'ngram_config': {
                    'sizes': self.config.ngram_sizes,
                    'min_frequency': self.config.min_frequency
                },
                'index_stats': {
                    'total_ngrams': self.stats.total_ngrams,
                    'unique_ngrams': self.stats.unique_ngrams,
                    'compression_ratio': self.stats.compression_ratio
                }
            },
            'stage_chunk_map': stage_chunk_map,
            'event_chunk_map': dict(event_chunk_map)
        }
    
    def _write_chunks(self, chunks: List[Dict[str, Any]], chunks_dir: Path):
        """Write chunk files."""
        for chunk in chunks:
            chunk_file = chunks_dir / f'chunk_{chunk["chunk_id"]}.json'
            chunk_data = {
                'chunk_id': chunk['chunk_id'],
                'metadata': {
                    'chunk_size_bytes': chunk['size_bytes'],
                    'total_stages': len(chunk['stages']),
                    'events_included': list(set(stage['event_id'] for stage in chunk['stages']))
                },
                'stages': chunk['stages']
            }
            
            with open(chunk_file, 'w', encoding='utf-8') as f:
                json.dump(chunk_data, f, ensure_ascii=False, indent=2)
    
    def _write_index(self, metadata: Dict[str, Any], inverted_index: Dict[str, Any], index_file: Path):
        """Write main index file."""
        index_data = {
            **metadata,
            'inverted_index': inverted_index
        }
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        self.stats.index_size_bytes = index_file.stat().st_size
        
        print(f"Generated N-gram search index: {index_file}")
    
    def _calculate_stats(self, chunks: List[Dict[str, Any]], inverted_index: Dict[str, Any]):
        """Calculate final statistics."""
        # Already calculated in other methods
        pass
    
    def _print_stats(self):
        """Print performance statistics."""
        print("\n" + "="*50)
        print("N-gram Search Index Generation Statistics")
        print("="*50)
        print(f"Total N-grams generated: {self.stats.total_ngrams:,}")
        print(f"Unique N-grams in index: {self.stats.unique_ngrams:,}")
        print(f"Index size: {self.stats.index_size_bytes:,} bytes ({self.stats.index_size_bytes/1024:.1f} KB)")
        print(f"Compression ratio: {self.stats.compression_ratio:.2f}x")
        print(f"Chunks created: {self.stats.chunk_count}")
        print(f"Average chunk size: {self.stats.avg_chunk_size:,} bytes ({self.stats.avg_chunk_size/1024:.1f} KB)")
        print(f"Generation time: {self.stats.generation_time_ms:,} ms")
        print("="*50)


def create_tuning_configs() -> List[NGramConfig]:
    """Create different configurations for performance tuning."""
    return [
        NGramConfig(
            ngram_sizes=[2], 
            min_frequency=1,
            max_index_size=50000,
            debug_output=True
        ),
        NGramConfig(
            ngram_sizes=[2, 3], 
            min_frequency=2,
            max_index_size=80000,
            debug_output=True
        ),
        NGramConfig(
            ngram_sizes=[2, 3, 4], 
            min_frequency=3,
            max_index_size=100000,
            debug_output=True
        ),
        NGramConfig(
            ngram_sizes=[3], 
            min_frequency=2,
            max_index_size=60000,
            debug_output=True
        ),
    ]


def run_performance_tuning(events: List[Event], output_path: Path = DIST_PATH) -> Dict[str, IndexStats]:
    """Run performance tuning with different configurations."""
    configs = create_tuning_configs()
    results = {}
    
    print("Running N-gram performance tuning...")
    
    for i, config in enumerate(configs, 1):
        print(f"\nConfiguration {i}/{len(configs)}")
        print(f"N-gram sizes: {config.ngram_sizes}")
        print(f"Min frequency: {config.min_frequency}")
        print(f"Max index size: {config.max_index_size}")
        
        generator = NGramSearchIndexGenerator(config)
        stats = generator.generate(events, output_path)
        
        config_name = f"config_{i}_n{'+'.join(map(str, config.ngram_sizes))}_freq{config.min_frequency}"
        results[config_name] = stats
    
    # Print comparison
    print("\n" + "="*80)
    print("PERFORMANCE TUNING RESULTS COMPARISON")
    print("="*80)
    print(f"{'Config':<20} {'N-grams':<10} {'Index KB':<10} {'Chunks':<8} {'Time ms':<10} {'Compression':<12}")
    print("-" * 80)
    
    for config_name, stats in results.items():
        print(f"{config_name:<20} {stats.unique_ngrams:<10,} {stats.index_size_bytes/1024:<10.1f} "
              f"{stats.chunk_count:<8} {stats.generation_time_ms:<10,} {stats.compression_ratio:<12.2f}x")
    
    return results