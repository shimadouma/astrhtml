from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import re
from pathlib import Path

from .data_loader import load_json

@dataclass
class StageUnlockCondition:
    stage_id: str
    complete_state: str

@dataclass  
class StageInfo:
    stage_id: str
    code: str
    name: str
    stage_type: str
    danger_level: str
    unlock_conditions: List[StageUnlockCondition]
    zone_id: str
    level_id: Optional[str] = None

def load_stage_table(data_path: Path) -> Dict[str, StageInfo]:
    """Load stage_table.json and return dictionary of StageInfo objects"""
    stage_table_path = data_path / "gamedata" / "excel" / "stage_table.json"
    data = load_json(stage_table_path)
    if not data:
        return {}
    
    stages = {}
    stages_data = data.get('stages', {})
    
    for stage_id, stage_data in stages_data.items():
        unlock_conditions = []
        for condition in stage_data.get('unlockCondition', []):
            unlock_conditions.append(
                StageUnlockCondition(
                    stage_id=condition.get('stageId', ''),
                    complete_state=condition.get('completeState', '')
                )
            )
        
        stages[stage_id] = StageInfo(
            stage_id=stage_id,
            code=stage_data.get('code', ''),
            name=stage_data.get('name', ''),
            stage_type=stage_data.get('stageType', ''),
            danger_level=stage_data.get('dangerLevel', ''),
            unlock_conditions=unlock_conditions,
            zone_id=stage_data.get('zoneId', ''),
            level_id=stage_data.get('levelId', None)
        )
    
    return stages

def build_stage_dependency_graph(stages: Dict[str, StageInfo]) -> Dict[str, List[str]]:
    """Build stage dependency graph"""
    graph = {}
    
    for stage_id, stage_info in stages.items():
        graph[stage_id] = []
        
        for condition in stage_info.unlock_conditions:
            if condition.stage_id in stages:
                graph[stage_id].append(condition.stage_id)
    
    return graph

def is_ministory_story_file(file_name: str) -> bool:
    """
    Check if a file is a MINISTORY story file (level_*_st*.json pattern)
    
    Args:
        file_name: Story file name
        
    Returns:
        True if it's a MINISTORY story file
    """
    import re
    return bool(re.match(r'level_.+_st\d+\.json$', file_name))

def get_ministory_stages(event_id: str, story_files: List[str]) -> List[Tuple[str, StageInfo]]:
    """
    Generate virtual stage info for MINISTORY events from story files only.
    MINISTORY events have separate gameplay and story stages - we only process story stages.
    
    Args:
        event_id: Event ID
        story_files: List of story file names (only st* files)
        
    Returns:
        List of (file_name, virtual_stage_info) tuples in order
    """
    import re
    
    ministory_stages = []
    
    # Filter and sort MINISTORY story files
    story_files_filtered = [f for f in story_files if is_ministory_story_file(f)]
    story_files_sorted = sorted(story_files_filtered)
    
    for file_name in story_files_sorted:
        # Extract stage number from filename: level_act15mini_st01.json -> 01
        match = re.match(r'level_(.+)_st(\d+)\.json$', file_name)
        if match:
            event_part, stage_num = match.groups()
            
            # Create virtual stage info for MINISTORY story stage
            # These don't correspond to actual gameplay stages
            virtual_stage_id = f"{event_part}_st{stage_num}"
            virtual_stage_code = f"ST-{int(stage_num)}"  # ST-1, ST-2, etc.
            
            # Create virtual StageInfo for this story stage
            virtual_stage = StageInfo(
                stage_id=virtual_stage_id,
                code=virtual_stage_code,
                name=f"シナリオ {int(stage_num)}",  # "Scenario 1", "Scenario 2", etc.
                stage_type="MINISTORY_STORY",
                danger_level="",
                unlock_conditions=[],
                zone_id=f"{event_id}_zone1"
            )
            
            ministory_stages.append((file_name, virtual_stage))
    
    return ministory_stages

def handle_type_act4d0_events(event_id: str, event_stages: Dict[str, StageInfo], story_files: List[str]) -> List[Tuple[str, StageInfo, bool]]:
    """
    Handle special TYPE_ACT4D0 events (act4d0, act6d5, act7d5) that have level_*_st*.json files
    Like MINISTORY events, these have separate gameplay and story stages - only show story stages
    Creates virtual story-only stages (ST-1, ST-2, etc.) instead of using gameplay stages
    """
    import re
    
    # Filter story files to only level_*_st*.json files for this event
    story_json_files = []
    for f in story_files:
        if f.startswith(f'level_{event_id}_st') and f.endswith('.json'):
            story_json_files.append(f)
    
    story_json_files.sort()  # level_act4d0_st01.json, level_act4d0_st02.json, etc.
    
    ordered_stories = []
    
    # Create virtual story-only stages like MINISTORY events
    # Do NOT use gameplay stages from event_stages - create story-only stages instead
    for i, story_file in enumerate(story_json_files):
        # Extract stage number from filename: level_act4d0_st01.json -> 01
        match = re.match(r'level_(.+)_st(\d+)\.json$', story_file)
        if match:
            event_part, stage_num = match.groups()
            stage_num_int = int(stage_num)
            
            # Create virtual story stage info (similar to MINISTORY handling)
            virtual_stage = StageInfo(
                stage_id=f"{event_id}_st{stage_num}",
                code=f"ST-{stage_num_int}",  # ST-1, ST-2, etc. (story stages, not gameplay)
                name=f"シナリオ {stage_num_int}",  # "Scenario 1", "Scenario 2", etc.
                stage_type="TYPE_ACT4D0_STORY",
                danger_level="",
                unlock_conditions=[],
                zone_id=f"{event_id}_zone1"
            )
            
            # For event generator compatibility, return the original JSON filename for story matching
            # The event generator and story generator will handle HTML filename mapping
            ordered_stories.append((story_file, virtual_stage, False))
    
    return ordered_stories

def get_event_related_stages(event_id: str, stages: Dict[str, StageInfo]) -> Dict[str, StageInfo]:
    """
    Find all stages related to an event ID.
    This handles cases where stage IDs don't match event IDs directly.
    """
    event_stages = {}
    event_id_upper = event_id.upper()
    
    for stage_id, stage_info in stages.items():
        # Method 1: Direct stage_id prefix match (most common case)
        if stage_id.startswith(event_id):
            event_stages[stage_id] = stage_info
            continue
            
        # Method 2: Check levelId for event reference 
        level_id = stage_info.level_id or ''
        if event_id_upper in level_id.upper():
            event_stages[stage_id] = stage_info
            continue
            
        # Method 3: Handle special cases where stage prefix doesn't match event_id
        # For example: act3d0 -> a003_*, act4d0 -> a004_*, etc.
        if event_id == 'act3d0' and stage_id.startswith('a003_'):
            event_stages[stage_id] = stage_info
        elif event_id == 'act4d0' and stage_id.startswith('a004_'):
            event_stages[stage_id] = stage_info
        # Add more special mappings as needed
    
    return event_stages

def natural_sort_key(text: str) -> List:
    """
    Generate a key for natural sorting that handles numbers correctly.
    For example: ['act17side_01', 'act17side_02', ..., 'act17side_10']
    """
    def convert(text):
        return int(text) if text.isdigit() else text.lower()
    
    return [convert(c) for c in re.split('([0-9]+)', text)]

def get_remaining_story_files_with_proper_mapping(event_id: str, stages: Dict[str, StageInfo],
                                                remaining_files: List[str], ordered_stories: List,
                                                event_type: str = None) -> List[Tuple[str, str, bool]]:
    """
    Process remaining story files that weren't in wordcount.json with proper mapping.
    This handles hidden stories and other special cases correctly.
    """
    # Extract event-related stages
    event_stages = get_event_related_stages(event_id, stages)
    
    # Create mapping for remaining files using the same logic as the main function
    story_stage_mapping = {}
    for file_name in remaining_files:
        base_name = file_name.replace('level_', '').replace('.json', '')
        
        if '_beg' in base_name:
            stage_id = base_name.replace('_beg', '')
            story_stage_mapping[file_name] = (stage_id, 'beg')
        elif '_end' in base_name:
            stage_id = base_name.replace('_end', '')
            
            # Special handling for hidden stories with sub-X-Y pattern
            import re
            sub_match = re.match(r'(.+)_sub-(\d+)-(\d+)', stage_id)
            if sub_match:
                event_part, sub_num1, sub_num2 = sub_match.groups()
                stage_id = f"{event_part}_s{sub_num2.zfill(2)}"
            
            story_stage_mapping[file_name] = (stage_id, 'end')
        else:
            # Story-only stage
            stage_id = base_name
            story_stage_mapping[file_name] = (stage_id, 'story')
            
            # Special handling for hidden_st pattern (hidden stories)
            if '_hidden_st' in base_name:
                import re
                match = re.match(r'(.+)_hidden_st(\d+)', base_name)
                if match:
                    event_part, stage_num = match.groups()
                    # Map hidden_st01 -> story_0, hidden_st02 -> story_1, etc. (0-indexed)
                    stage_id = f"story_{int(stage_num) - 1}"
                    story_stage_mapping[file_name] = (stage_id, 'story')
            
            # Special handling for events with st pattern in story-only files
            elif '_st' in base_name and event_type != 'MINISTORY':
                import re
                match = re.match(r'(.+)_st(\d+)', base_name)
                if match:
                    event_part, stage_num = match.groups()
                    
                    # Only transform st->numeric for specific TYPE_ACT4D0 events
                    if event_id in ['act4d0', 'act6d5', 'act7d5']:
                        stage_id = f"{event_part}_{stage_num.zfill(2)}"
                    else:
                        # For most events, keep the _st prefix
                        stage_id = f"{event_part}_st{stage_num.zfill(2)}"
                    
                    story_stage_mapping[file_name] = (stage_id, 'story')
        
        # Apply stage ID transformations for special cases
        mapped_stage_id, story_type = story_stage_mapping[file_name]
        
        # Transform stage IDs to match actual stage table entries
        if event_id == 'act3d0':
            transformed_stage_id = mapped_stage_id.replace('act3d0_', 'a003_')
            story_stage_mapping[file_name] = (transformed_stage_id, story_type)
    
    # Process remaining files in sorted order
    for file_name in remaining_files:
        if file_name in story_stage_mapping:
            mapped_stage_id, story_type = story_stage_mapping[file_name]
            
            # Look for the stage in event_stages
            stage_info = event_stages.get(mapped_stage_id)
            if stage_info:
                # Use the actual stage info
                is_battle_story = story_type in ['beg', 'end']
                ordered_stories.append((file_name, stage_info, is_battle_story))
            else:
                # Create virtual stage info for hidden stories and other special cases
                virtual_stage_code = mapped_stage_id.split('_')[-1].upper()
                
                if mapped_stage_id.startswith('story_'):
                    # For story_0, story_1, etc. (hidden stories)
                    story_num = mapped_stage_id.split('_')[-1]
                    virtual_stage_code = f"逆行{int(story_num) + 1}"  # story_0 -> 逆行1, story_1 -> 逆行2
                elif virtual_stage_code.startswith('S'):
                    # Determine the correct event prefix by looking at existing event stages
                    event_prefix = "TW"  # default fallback
                    
                    # Look for any existing stage in event_stages to get the correct prefix
                    for existing_stage in event_stages.values():
                        if existing_stage.code and '-' in existing_stage.code:
                            # Extract prefix from existing stage code (e.g., "NL-1" -> "NL")
                            event_prefix = existing_stage.code.split('-')[0]
                            break
                    
                    # Format the stage number properly
                    stage_num = virtual_stage_code[1:]  # Remove 'S' prefix
                    try:
                        stage_num_int = int(stage_num)
                        virtual_stage_code = f"{event_prefix}-ST-{stage_num_int}"
                    except ValueError:
                        virtual_stage_code = f"{event_prefix}-S{stage_num}"
                
                virtual_stage = StageInfo(
                    stage_id=mapped_stage_id,
                    code=virtual_stage_code,
                    name="隠しストーリー",  # "Hidden Story"
                    stage_type="HIDDEN_STORY",
                    danger_level="",
                    unlock_conditions=[],
                    zone_id=f"{event_id}_zone1"
                )
                
                is_battle_story = story_type in ['beg', 'end']
                ordered_stories.append((file_name, virtual_stage, is_battle_story))
        else:
            # Fallback: create basic virtual stage info
            base_name = file_name.replace('level_', '').replace('.json', '')
            virtual_stage_code = base_name.split('_')[-1].upper()
            
            virtual_stage = StageInfo(
                stage_id=base_name,
                code=virtual_stage_code,
                name="ストーリー",  # "Story"
                stage_type="UNKNOWN",
                danger_level="",
                unlock_conditions=[],
                zone_id=f"{event_id}_zone1"
            )
            
            is_battle_story = '_beg' in base_name or '_end' in base_name
            ordered_stories.append((file_name, virtual_stage, is_battle_story))
    
    return ordered_stories

def get_story_order_from_wordcount(event_id: str, stages: Dict[str, StageInfo],
                                  story_files: List[str], wordcount_order: List[str],
                                  event_type: str = None) -> List[Tuple[str, str, bool]]:
    """
    Get story order based on wordcount.json order.
    
    Args:
        event_id: Event ID
        stages: All stages from stage_table
        story_files: List of story file names
        wordcount_order: Order from wordcount.json
        event_type: Event type
    
    Returns:
        List of (file_name, stage_info, is_battle_story) tuples
    """
    # Extract event-related stages
    event_stages = get_event_related_stages(event_id, stages)
    
    # Create mapping of story files
    story_file_map = {}
    for file_name in story_files:
        # Extract base name without level_ prefix and .json extension
        base_name = file_name.replace('level_', '').replace('.json', '')
        story_file_map[base_name] = file_name
        
        # Also try without event prefix for matching
        if base_name.startswith(event_id + '_'):
            short_name = base_name[len(event_id) + 1:]
            story_file_map[short_name] = file_name
    
    ordered_stories = []
    processed_files = set()
    
    # Process files in wordcount order
    for wc_filename in wordcount_order:
        # Try to find matching story file
        matched_file = None
        
        # Direct match
        if wc_filename in story_file_map:
            matched_file = story_file_map[wc_filename]
        # Try with level_ prefix
        elif f"level_{wc_filename}" + ".json" in story_files:
            matched_file = f"level_{wc_filename}.json"
        # Try without event prefix in wordcount filename
        elif wc_filename.startswith(event_id + '_'):
            short_name = wc_filename[len(event_id) + 1:]
            if short_name in story_file_map:
                matched_file = story_file_map[short_name]
        
        if matched_file and matched_file not in processed_files:
            processed_files.add(matched_file)
            
            # Determine stage info and story type
            base_name = matched_file.replace('level_', '').replace('.json', '')
            
            # Determine story type
            is_battle_story = False
            stage_id = base_name
            
            if '_beg' in base_name:
                stage_id = base_name.replace('_beg', '')
                is_battle_story = True
            elif '_end' in base_name:
                stage_id = base_name.replace('_end', '')
                is_battle_story = True
                
                # Handle special hidden story patterns
                import re
                sub_match = re.match(r'(.+)_sub-(\d+)-(\d+)', stage_id)
                if sub_match:
                    event_part, sub_num1, sub_num2 = sub_match.groups()
                    stage_id = f"{event_part}_s{sub_num2.zfill(2)}"
            
            # Apply stage ID transformations for special cases
            if event_id == 'act3d0':
                stage_id = stage_id.replace('act3d0_', 'a003_')
            
            # Find or create stage info
            stage_info = event_stages.get(stage_id)
            
            if not stage_info:
                # Create virtual stage info
                if '_st' in base_name:
                    # Story-only stage
                    import re
                    match = re.match(r'(.+)_st(\d+)', base_name)
                    if match:
                        event_part, stage_num = match.groups()
                        stage_code = f"ST-{int(stage_num)}"
                        stage_name = f"シナリオ {int(stage_num)}"
                    else:
                        stage_code = base_name.split('_')[-1].upper()
                        stage_name = "ストーリー"
                else:
                    # Extract stage code from base_name
                    parts = base_name.split('_')
                    if len(parts) > 1:
                        stage_code = parts[-1].upper()
                        # Convert numeric codes to stage format
                        if stage_code.isdigit():
                            stage_code = f"OR-{int(stage_code)}"
                        elif stage_code.startswith('EX'):
                            stage_code = f"EX-{stage_code[2:]}"
                    else:
                        stage_code = "STORY"
                    stage_name = "ストーリー"
                
                stage_info = StageInfo(
                    stage_id=stage_id,
                    code=stage_code,
                    name=stage_name,
                    stage_type="STORY",
                    danger_level="",
                    unlock_conditions=[],
                    zone_id=f"{event_id}_zone1"
                )
            
            ordered_stories.append((matched_file, stage_info, is_battle_story))
    
    # Add any remaining files not in wordcount order
    remaining_files = [f for f in story_files if f not in processed_files]
    if remaining_files:
        print(f"Info: {len(remaining_files)} files not in wordcount order for {event_id}, adding at end")
        # Sort remaining files naturally
        remaining_files.sort(key=lambda x: natural_sort_key(x))
        
        # Use existing logic for processing remaining files to handle hidden stories properly
        return get_remaining_story_files_with_proper_mapping(
            event_id, stages, remaining_files, ordered_stories, event_type
        )
    
    return ordered_stories

def get_story_order_for_event(event_id: str, stages: Dict[str, StageInfo], 
                            story_files: List[str], event_type: str = None) -> List[Tuple[str, str, bool]]:
    """
    Sort event story files in correct order
    
    Returns:
        List[Tuple[str, str, bool]]: List of (file_name, stage_info, is_battle_story)
    """
    
    # Try to use wordcount.json order first
    from src.lib.wordcount_parser import get_event_story_order, load_wordcount_data
    
    wordcount_data = load_wordcount_data()
    wordcount_order = get_event_story_order(event_id, wordcount_data)
    
    if wordcount_order:
        # Use wordcount.json order if available
        print(f"Using wordcount.json order for {event_id}")
        return get_story_order_from_wordcount(
            event_id, stages, story_files, wordcount_order, event_type
        )
    
    # Special handling for MINISTORY events
    if event_type == 'MINISTORY':
        # For MINISTORY events, ignore gameplay stages entirely
        # Only process story files (level_*_st*.json) and create virtual stages
        ministory_stages = get_ministory_stages(event_id, story_files)
        
        # Convert to the expected return format
        ordered_stories = []
        for file_name, virtual_stage in ministory_stages:
            # All MINISTORY stories are story-only (not battle stories)
            ordered_stories.append((file_name, virtual_stage, False))
        
        return ordered_stories
    
    # Regular processing for non-MINISTORY events
    # Extract event-related stages using improved detection
    event_stages = get_event_related_stages(event_id, stages)
    
    # Special handling for TYPE_ACT4D0 events with story_*.html files
    if event_id in ['act4d0', 'act6d5', 'act7d5']:
        return handle_type_act4d0_events(event_id, event_stages, story_files)
    
    # Create mapping between story files and stages
    story_stage_mapping = {}
    for file_name in story_files:
        # Extract stage ID from filename
        # level_act40side_01_beg.json -> act40side_01
        # level_act40side_st01.json -> act40side_st01
        # level_act11d0_sub-1-1_end.json -> act11d0_s01 (special hidden story mapping)
        # For MINISTORY: level_act17mini_st01.json -> act17mini_01 (remove 'st')
        base_name = file_name.replace('level_', '').replace('.json', '')
        
        if '_beg' in base_name:
            stage_id = base_name.replace('_beg', '')
            story_stage_mapping[file_name] = (stage_id, 'beg')
        elif '_end' in base_name:
            stage_id = base_name.replace('_end', '')
            
            # Special handling for hidden stories with sub-X-Y pattern
            # level_act11d0_sub-1-1_end.json -> act11d0_s01
            # level_act11d0_sub-1-2_end.json -> act11d0_s02
            import re
            sub_match = re.match(r'(.+)_sub-(\d+)-(\d+)', stage_id)
            if sub_match:
                event_part, sub_num1, sub_num2 = sub_match.groups()
                # Map sub-1-1 -> s01, sub-1-2 -> s02, etc.
                stage_id = f"{event_part}_s{sub_num2.zfill(2)}"
            
            story_stage_mapping[file_name] = (stage_id, 'end')
        else:
            # Story-only stage
            # Special handling for MINISTORY events
            if event_type == 'MINISTORY' and '_st' in base_name:
                # level_act17mini_st01.json -> act17mini_01
                # Remove 'st' from the stage number for MINISTORY events
                import re
                match = re.match(r'(.+)_st(\d+)', base_name)
                if match:
                    event_part, stage_num = match.groups()
                    stage_id = f"{event_part}_{stage_num}"
                else:
                    stage_id = base_name
            else:
                stage_id = base_name
            story_stage_mapping[file_name] = (stage_id, 'story')
            
            # Special handling for hidden_st pattern (hidden stories)
            # level_act13side_hidden_st01.json -> generates story_0.html
            if '_hidden_st' in base_name:
                import re
                match = re.match(r'(.+)_hidden_st(\d+)', base_name)
                if match:
                    event_part, stage_num = match.groups()
                    # Map hidden_st01 -> story_0, hidden_st02 -> story_1, etc. (0-indexed)
                    stage_id = f"story_{int(stage_num) - 1}"
                    story_stage_mapping[file_name] = (stage_id, 'story')
            
            # Special handling for events with st pattern in story-only files
            # Most events with _st pattern should keep the _st prefix in the stage ID
            # Only specific events like act4d0, act6d5, act7d5 need st->numeric transformation
            elif '_st' in base_name and event_type != 'MINISTORY':
                import re
                match = re.match(r'(.+)_st(\d+)', base_name)
                if match:
                    event_part, stage_num = match.groups()
                    
                    # Only transform st->numeric for specific TYPE_ACT4D0 events
                    if event_id in ['act4d0', 'act6d5', 'act7d5']:
                        # For these events, st01 -> 01, st02 -> 02, etc.
                        stage_id = f"{event_part}_{stage_num.zfill(2)}"
                    else:
                        # For most events, keep the _st prefix: act40side_st01, etc.
                        stage_id = f"{event_part}_st{stage_num.zfill(2)}"
                    
                    story_stage_mapping[file_name] = (stage_id, 'story')
        
        # Apply stage ID transformations for special cases
        # These events have mismatched story filenames vs stage IDs
        mapped_stage_id, story_type = story_stage_mapping[file_name]
        
        # Transform stage IDs to match actual stage table entries
        if event_id == 'act3d0':
            # act3d0_01 -> a003_01, act3d0_ex01 -> a003_ex01, etc.
            transformed_stage_id = mapped_stage_id.replace('act3d0_', 'a003_')
            story_stage_mapping[file_name] = (transformed_stage_id, story_type)
        elif event_id == 'act4d0':
            # Keep as is - act4d0_* stages exist directly
            pass
        # Add more transformations as needed
    
    # Build dependency graph for topological sort
    dependency_graph = build_stage_dependency_graph(event_stages)
    
    # Execute topological sort (reverse dependencies for correct order)
    ordered_stages = topological_sort(dependency_graph)
    ordered_stages.reverse()  # From start stage to end stage
    
    # For events with mixed dependencies (some stages have deps, some don't),
    # sort the stages that have no dependencies by stage ID
    stages_with_no_deps = [stage_id for stage_id, deps in dependency_graph.items() if len(deps) == 0]
    stages_with_deps = [stage_id for stage_id, deps in dependency_graph.items() if len(deps) > 0]
    
    if stages_with_no_deps and stages_with_deps:
        # Mixed dependencies: sort stages without dependencies naturally,
        # keep topological order for stages with dependencies
        sorted_no_deps = sorted(stages_with_no_deps, key=lambda x: natural_sort_key(x))
        sorted_with_deps = [stage for stage in ordered_stages if stage in stages_with_deps]
        # Combine: main story stages first, then dependent stages
        ordered_stages = sorted_no_deps + sorted_with_deps
    elif not stages_with_deps:
        # All stages have no dependencies, sort all by stage ID
        ordered_stages = sorted(event_stages.keys(), key=lambda x: natural_sort_key(x))
    
    # Order story files based on sort results
    ordered_stories = []
    
    for stage_id in ordered_stages:
        if stage_id in event_stages:
            stage_info = event_stages[stage_id]
            
            # Find pre-battle story
            beg_file = None
            end_file = None
            story_only_file = None
            
            for file_name, (mapped_stage_id, story_type) in story_stage_mapping.items():
                if mapped_stage_id == stage_id:
                    if story_type == 'beg':
                        beg_file = file_name
                    elif story_type == 'end':
                        end_file = file_name
                    elif story_type == 'story':
                        # Story-only stage
                        story_only_file = file_name
                        ordered_stories.append((file_name, stage_info, False))
            
            # Add pre-battle story
            if beg_file:
                ordered_stories.append((beg_file, stage_info, True))
            
            # Add post-battle story
            if end_file:
                ordered_stories.append((end_file, stage_info, True))
            
            # Handle stages without story files (but that exist in stage table)
            # This is a very specific fix for act9d0 DM-7/DM-8 issue and similar cases
            # Only apply this to specific events that are known to have this issue
            if not beg_file and not end_file and not story_only_file:
                # Only apply virtual story logic to specific events that are known to have this issue
                # Currently: act9d0 has DM-7 and DM-8 stages without story files
                should_create_virtual_story = False
                
                if event_id == 'act9d0' and stage_id in ['act9d0_07', 'act9d0_08']:
                    # act9d0 DM-7 and DM-8 have story content but no story files
                    should_create_virtual_story = True
                
                if should_create_virtual_story:
                    # Create a virtual story entry for stages that have generated story pages but no story files
                    virtual_file_name = f"virtual_{stage_id}_end"  # Assume post-battle story by default
                    ordered_stories.append((virtual_file_name, stage_info, True))
    
    # Add any remaining story files that weren't matched to stages
    # This handles hidden stories and other special cases
    matched_files = {file_name for file_name, _, _ in ordered_stories}
    remaining_files = [f for f in story_files if f not in matched_files]
    
    if remaining_files:
        print(f"Info: Found {len(remaining_files)} unmatched story files for {event_id}, adding them at the end")
        
        # Sort remaining files alphabetically for consistent ordering
        remaining_files.sort()
        
        for file_name in remaining_files:
            # Try to get stage info from the mapping
            if file_name in story_stage_mapping:
                mapped_stage_id, story_type = story_stage_mapping[file_name]
                
                # Look for the stage in event_stages
                stage_info = event_stages.get(mapped_stage_id)
                if stage_info:
                    # Use the actual stage info
                    is_battle_story = story_type in ['beg', 'end']
                    ordered_stories.append((file_name, stage_info, is_battle_story))
                else:
                    # Create virtual stage info for hidden stories
                    virtual_stage_code = mapped_stage_id.split('_')[-1].upper()  # s01 -> S01
                    if virtual_stage_code.startswith('S'):
                        # Determine the correct event prefix by looking at existing event stages
                        event_prefix = "TW"  # default fallback
                        
                        # Look for any existing stage in event_stages to get the correct prefix
                        for existing_stage in event_stages.values():
                            if existing_stage.code and '-' in existing_stage.code:
                                # Extract prefix from existing stage code (e.g., "SN-1" -> "SN")
                                event_prefix = existing_stage.code.split('-')[0]
                                break
                        
                        # Format the stage number properly (S01 -> ST-1, S02 -> ST-2, etc.)
                        stage_num = virtual_stage_code[1:]  # Remove 'S' prefix
                        try:
                            stage_num_int = int(stage_num)
                            virtual_stage_code = f"{event_prefix}-ST-{stage_num_int}"
                        except ValueError:
                            # If stage_num contains non-numeric characters, use it as-is
                            virtual_stage_code = f"{event_prefix}-S{stage_num}"
                    elif mapped_stage_id.startswith('story_'):
                        # For story_0, story_1, etc. (hidden stories)
                        story_num = mapped_stage_id.split('_')[-1]
                        virtual_stage_code = f"逆行{int(story_num) + 1}"  # story_0 -> 逆行1, story_1 -> 逆行2
                    
                    virtual_stage = StageInfo(
                        stage_id=mapped_stage_id,
                        code=virtual_stage_code,
                        name="隠しストーリー",  # "Hidden Story"
                        stage_type="HIDDEN_STORY",
                        danger_level="",
                        unlock_conditions=[],
                        zone_id=f"{event_id}_zone1"
                    )
                    
                    is_battle_story = story_type in ['beg', 'end']
                    ordered_stories.append((file_name, virtual_stage, is_battle_story))
            else:
                # Fallback: create basic virtual stage info
                base_name = file_name.replace('level_', '').replace('.json', '')
                virtual_stage_code = base_name.split('_')[-1].upper()
                
                virtual_stage = StageInfo(
                    stage_id=base_name,
                    code=virtual_stage_code,
                    name="ストーリー",  # "Story"
                    stage_type="UNKNOWN",
                    danger_level="",
                    unlock_conditions=[],
                    zone_id=f"{event_id}_zone1"
                )
                
                ordered_stories.append((file_name, virtual_stage, False))
    
    return ordered_stories

def topological_sort(graph: Dict[str, List[str]]) -> List[str]:
    """Topological sort (Kahn's algorithm)"""
    # Calculate in-degree
    in_degree = {node: 0 for node in graph}
    
    for node in graph:
        for dependency in graph[node]:
            if dependency in in_degree:
                in_degree[dependency] += 1
    
    # Find nodes with in-degree 0
    queue = [node for node, degree in in_degree.items() if degree == 0]
    result = []
    
    while queue:
        node = queue.pop(0)
        result.append(node)
        
        for dependency in graph.get(node, []):
            if dependency in in_degree:
                in_degree[dependency] -= 1
                if in_degree[dependency] == 0:
                    queue.append(dependency)
    
    return result

def get_stage_display_info(stage_info: StageInfo, story_type: str) -> Dict[str, str]:
    """Generate display information from stage info"""
    # For story_X stage IDs (hidden stories), use the stage ID as code instead of display code  
    code = stage_info.stage_id if stage_info.stage_id.startswith('story_') else stage_info.code
    
    display_info = {
        'code': code,
        'name': stage_info.name,
        'danger_level': stage_info.danger_level,
        'stage_type': stage_info.stage_type
    }
    
    # Distinguish between pre/post-battle and story-only
    if story_type == 'beg':
        display_info['story_phase'] = '戦闘前'
    elif story_type == 'end':
        display_info['story_phase'] = '戦闘後'
    elif story_type == 'story':
        display_info['story_phase'] = '間章'
    else:
        display_info['story_phase'] = ''
    
    return display_info


def get_main_story_order_for_chapter(chapter: int, stages: Dict[str, StageInfo], 
                                   story_files: List[str]) -> List[Tuple[str, StageInfo, bool]]:
    """
    Sort main story files in correct order for specific chapter
    
    Returns:
        List[Tuple[str, StageInfo, bool]]: List of (file_name, stage_info, is_battle_story)
    """
    # Extract chapter-related stages (main_XX-YY, st_XX-YY, spst_XX-YY)
    chapter_stages = {}
    
    for stage_id, stage_info in stages.items():
        # Main story stages: main_XX-YY
        if stage_id.startswith(f'main_{chapter:02d}-'):
            chapter_stages[stage_id] = stage_info
        # Interlude stages: st_XX-YY, spst_XX-YY
        elif stage_id.startswith(f'st_{chapter:02d}-') or stage_id.startswith(f'spst_{chapter:02d}-'):
            chapter_stages[stage_id] = stage_info
    
    # Create mapping between story files and stages
    story_stage_mapping = {}
    for file_name in story_files:
        base_name = file_name.replace('level_', '').replace('.json', '')
        
        if base_name.startswith('main_'):
            # level_main_XX-YY_beg.json or level_main_XX-YY_end.json
            if '_beg' in base_name:
                stage_id = base_name.replace('_beg', '')
                story_stage_mapping[file_name] = (stage_id, 'beg')
            elif '_end' in base_name:
                stage_id = base_name.replace('_end', '')
                story_stage_mapping[file_name] = (stage_id, 'end')
        elif base_name.startswith('st_') or base_name.startswith('spst_'):
            # level_st_XX-YY.json or level_spst_XX-YY.json
            story_stage_mapping[file_name] = (base_name, 'story')
    
    # Build dependency graph for topological sort
    dependency_graph = build_stage_dependency_graph(chapter_stages)
    
    # Execute topological sort
    ordered_stages = topological_sort(dependency_graph)
    ordered_stages.reverse()  # From start stage to end stage
    
    # Order story files based on sort results
    ordered_stories = []
    
    for stage_id in ordered_stages:
        if stage_id in chapter_stages:
            stage_info = chapter_stages[stage_id]
            
            # Find battle stories (beg/end)
            beg_file = None
            end_file = None
            
            for file_name, (mapped_stage_id, story_type) in story_stage_mapping.items():
                if mapped_stage_id == stage_id:
                    if story_type == 'beg':
                        beg_file = file_name
                    elif story_type == 'end':
                        end_file = file_name
                    elif story_type == 'story':
                        # Interlude story
                        ordered_stories.append((file_name, stage_info, False))
            
            # Add pre-battle story
            if beg_file:
                ordered_stories.append((beg_file, stage_info, True))
            
            # Add post-battle story  
            if end_file:
                ordered_stories.append((end_file, stage_info, True))
    
    return ordered_stories


def get_main_story_display_info(stage_info: StageInfo, story_type: str) -> Dict[str, str]:
    """Generate display information for main story stages"""
    display_info = {
        'code': stage_info.code,
        'name': stage_info.name, 
        'danger_level': stage_info.danger_level,
        'stage_type': stage_info.stage_type
    }
    
    # Set story phase based on story type
    if story_type == 'beg':
        display_info['story_phase'] = '戦闘前'
    elif story_type == 'end':
        display_info['story_phase'] = '戦闘後'
    elif story_type == 'story':
        display_info['story_phase'] = '間章'
    else:
        display_info['story_phase'] = ''
    
    return display_info