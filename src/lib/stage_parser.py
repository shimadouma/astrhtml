from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
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

def get_story_order_for_event(event_id: str, stages: Dict[str, StageInfo], 
                            story_files: List[str], event_type: str = None) -> List[Tuple[str, str, bool]]:
    """
    Sort event story files in correct order
    
    Returns:
        List[Tuple[str, str, bool]]: List of (file_name, stage_info, is_battle_story)
    """
    
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
        # For MINISTORY: level_act17mini_st01.json -> act17mini_01 (remove 'st')
        base_name = file_name.replace('level_', '').replace('.json', '')
        
        if '_beg' in base_name:
            stage_id = base_name.replace('_beg', '')
            story_stage_mapping[file_name] = (stage_id, 'beg')
        elif '_end' in base_name:
            stage_id = base_name.replace('_end', '')
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
            
            # Special handling for events with st pattern in story-only files
            # These events have story files like level_act4d0_st01.json but stages like act4d0_01
            if '_st' in base_name and event_type != 'MINISTORY':
                import re
                match = re.match(r'(.+)_st(\d+)', base_name)
                if match:
                    event_part, stage_num = match.groups()
                    # For these events, st01 -> 01, st02 -> 02, etc.
                    stage_id = f"{event_part}_{stage_num.zfill(2)}"
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
    
    # Order story files based on sort results
    ordered_stories = []
    
    for stage_id in ordered_stages:
        if stage_id in event_stages:
            stage_info = event_stages[stage_id]
            
            # Find pre-battle story
            beg_file = None
            end_file = None
            
            for file_name, (mapped_stage_id, story_type) in story_stage_mapping.items():
                if mapped_stage_id == stage_id:
                    if story_type == 'beg':
                        beg_file = file_name
                    elif story_type == 'end':
                        end_file = file_name
                    elif story_type == 'story':
                        # Story-only stage
                        ordered_stories.append((file_name, stage_info, False))
            
            # Add pre-battle story
            if beg_file:
                ordered_stories.append((beg_file, stage_info, True))
            
            # Add post-battle story
            if end_file:
                ordered_stories.append((end_file, stage_info, True))
    
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
    display_info = {
        'code': stage_info.code,
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