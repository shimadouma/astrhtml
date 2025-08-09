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
    """stage_table.jsonを読み込んでStageInfoオブジェクトの辞書を返す"""
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
    """ステージの依存関係グラフを構築する"""
    graph = {}
    
    for stage_id, stage_info in stages.items():
        graph[stage_id] = []
        
        for condition in stage_info.unlock_conditions:
            if condition.stage_id in stages:
                graph[stage_id].append(condition.stage_id)
    
    return graph

def get_story_order_for_event(event_id: str, stages: Dict[str, StageInfo], 
                            story_files: List[str]) -> List[Tuple[str, str, bool]]:
    """
    イベントのストーリーファイルを正しい順序でソートする
    
    Returns:
        List[Tuple[str, str, bool]]: (file_name, stage_info, is_battle_story)のリスト
    """
    # イベント関連のステージを抽出
    event_stages = {
        stage_id: stage_info 
        for stage_id, stage_info in stages.items()
        if stage_info.zone_id.startswith(event_id)
    }
    
    # ストーリーファイルとステージの対応を作成
    story_stage_mapping = {}
    for file_name in story_files:
        # ファイル名からステージIDを抽出
        # level_act40side_01_beg.json -> act40side_01
        # level_act40side_st01.json -> act40side_st01
        base_name = file_name.replace('level_', '').replace('.json', '')
        
        if '_beg' in base_name:
            stage_id = base_name.replace('_beg', '')
            story_stage_mapping[file_name] = (stage_id, 'beg')
        elif '_end' in base_name:
            stage_id = base_name.replace('_end', '')
            story_stage_mapping[file_name] = (stage_id, 'end')
        else:
            # ストーリー専用ステージ
            story_stage_mapping[file_name] = (base_name, 'story')
    
    # トポロジカルソート用の依存関係グラフを構築
    dependency_graph = build_stage_dependency_graph(event_stages)
    
    # トポロジカルソート実行（依存関係を逆にして正しい順序にする）
    ordered_stages = topological_sort(dependency_graph)
    ordered_stages.reverse()  # 開始ステージから終了ステージの順に
    
    # ソート結果をベースにストーリーファイルを順序付け
    ordered_stories = []
    
    for stage_id in ordered_stages:
        if stage_id in event_stages:
            stage_info = event_stages[stage_id]
            
            # 戦闘前ストーリーを探す
            beg_file = None
            end_file = None
            
            for file_name, (mapped_stage_id, story_type) in story_stage_mapping.items():
                if mapped_stage_id == stage_id:
                    if story_type == 'beg':
                        beg_file = file_name
                    elif story_type == 'end':
                        end_file = file_name
                    elif story_type == 'story':
                        # ストーリー専用ステージ
                        ordered_stories.append((file_name, stage_info, False))
            
            # 戦闘前ストーリーを追加
            if beg_file:
                ordered_stories.append((beg_file, stage_info, True))
            
            # 戦闘後ストーリーを追加
            if end_file:
                ordered_stories.append((end_file, stage_info, True))
    
    return ordered_stories

def topological_sort(graph: Dict[str, List[str]]) -> List[str]:
    """トポロジカルソート（Kahn's algorithm）"""
    # 入次数を計算
    in_degree = {node: 0 for node in graph}
    
    for node in graph:
        for dependency in graph[node]:
            if dependency in in_degree:
                in_degree[dependency] += 1
    
    # 入次数が0のノードを探す
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
    """ステージ情報から表示用の情報を生成する"""
    display_info = {
        'code': stage_info.code,
        'name': stage_info.name,
        'danger_level': stage_info.danger_level,
        'stage_type': stage_info.stage_type
    }
    
    # 戦闘前後やストーリー専用の区別
    if story_type == 'beg':
        display_info['story_phase'] = '戦闘前'
    elif story_type == 'end':
        display_info['story_phase'] = '戦闘後'
    elif story_type == 'story':
        display_info['story_phase'] = '間章'
    else:
        display_info['story_phase'] = ''
    
    return display_info