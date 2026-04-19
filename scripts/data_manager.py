#!/usr/bin/env python3
"""
万象绘卷数据管理工具
提供故事、角色、世界状态等数据的 CRUD 操作
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
STORIES_DIR = BASE_DIR / "stories"
DB_PATH = DATA_DIR / "wanxiang.db"


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        if not self.db_path.exists():
            from init_database import init_database
            init_database()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()


class StoryManager:
    """故事管理器"""
    
    def __init__(self, db: DatabaseManager = None):
        self.db = db or DatabaseManager()
    
    def create_story(self, name: str, story_type: str = "life_simulation", 
                     world_type: str = None, style: str = "default",
                     metadata: dict = None) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO stories (name, type, world_type, style, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, story_type, world_type, style, json.dumps(metadata or {})))
            conn.commit()
            story_id = cursor.lastrowid
            
            story_dir = STORIES_DIR / name
            story_dir.mkdir(parents=True, exist_ok=True)
            
            return story_id
    
    def get_story(self, story_id: int = None, name: str = None) -> Optional[Dict]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if story_id:
                cursor.execute('SELECT * FROM stories WHERE id = ?', (story_id,))
            elif name:
                cursor.execute('SELECT * FROM stories WHERE name = ?', (name,))
            else:
                return None
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_stories(self, active_only: bool = True) -> List[Dict]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if active_only:
                cursor.execute('SELECT * FROM stories WHERE is_active = 1 ORDER BY updated_at DESC')
            else:
                cursor.execute('SELECT * FROM stories ORDER BY updated_at DESC')
            return [dict(row) for row in cursor.fetchall()]
    
    def update_story(self, story_id: int, **kwargs) -> bool:
        allowed_fields = ['name', 'type', 'world_type', 'style', 'metadata', 'is_active']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        updates['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join(f'{k} = ?' for k in updates.keys())
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE stories SET {set_clause} WHERE id = ?', 
                         list(updates.values()) + [story_id])
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_story(self, story_id: int, soft_delete: bool = True) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if soft_delete:
                cursor.execute('UPDATE stories SET is_active = 0 WHERE id = ?', (story_id,))
            else:
                cursor.execute('DELETE FROM stories WHERE id = ?', (story_id,))
            conn.commit()
            return cursor.rowcount > 0


class CharacterManager:
    """角色管理器"""
    
    def __init__(self, db: DatabaseManager = None):
        self.db = db or DatabaseManager()
    
    def create_character(self, story_id: int, name: str, role: str = "protagonist",
                         attributes: dict = None, traits: list = None,
                         relationships: dict = None, is_legacy: bool = False) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO characters (story_id, name, role, attributes, traits, relationships, is_legacy)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (story_id, name, role, json.dumps(attributes or {}),
                  json.dumps(traits or []), json.dumps(relationships or {}), is_legacy))
            conn.commit()
            return cursor.lastrowid
    
    def get_character(self, character_id: int) -> Optional[Dict]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['attributes'] = json.loads(result['attributes'] or '{}')
                result['traits'] = json.loads(result['traits'] or '[]')
                result['relationships'] = json.loads(result['relationships'] or '{}')
                return result
            return None
    
    def list_characters(self, story_id: int) -> List[Dict]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM characters WHERE story_id = ?', (story_id,))
            characters = []
            for row in cursor.fetchall():
                char = dict(row)
                char['attributes'] = json.loads(char['attributes'] or '{}')
                char['traits'] = json.loads(char['traits'] or '[]')
                char['relationships'] = json.loads(char['relationships'] or '{}')
                characters.append(char)
            return characters
    
    def update_character(self, character_id: int, **kwargs) -> bool:
        allowed_fields = ['name', 'role', 'attributes', 'traits', 'relationships', 'is_legacy']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        for field in ['attributes', 'traits', 'relationships']:
            if field in updates and isinstance(updates[field], (dict, list)):
                updates[field] = json.dumps(updates[field])
        
        updates['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join(f'{k} = ?' for k in updates.keys())
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE characters SET {set_clause} WHERE id = ?',
                         list(updates.values()) + [character_id])
            conn.commit()
            return cursor.rowcount > 0


class WorldStateManager:
    """世界状态管理器"""
    
    def __init__(self, db: DatabaseManager = None):
        self.db = db or DatabaseManager()
    
    def save_state(self, story_id: int, turn: int, state_data: dict,
                   year: int = None, season: str = None, location: str = None) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO world_state (story_id, turn, year, season, location, state_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (story_id, turn, year, season, location, json.dumps(state_data)))
            conn.commit()
            return cursor.lastrowid
    
    def get_state(self, story_id: int, turn: int = None) -> Optional[Dict]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if turn is not None:
                cursor.execute('SELECT * FROM world_state WHERE story_id = ? AND turn = ?',
                             (story_id, turn))
            else:
                cursor.execute('SELECT * FROM world_state WHERE story_id = ? ORDER BY turn DESC LIMIT 1',
                             (story_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['state_data'] = json.loads(result['state_data'] or '{}')
                return result
            return None


class HiddenFloorManager:
    """隐藏楼层管理器"""
    
    def __init__(self, db: DatabaseManager = None):
        self.db = db or DatabaseManager()
    
    def add_note(self, story_id: int, content: str, note_type: str = "foreshadowing") -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO hidden_floors (story_id, content, note_type)
                VALUES (?, ?, ?)
            ''', (story_id, content, note_type))
            conn.commit()
            return cursor.lastrowid
    
    def list_notes(self, story_id: int, unresolved_only: bool = False) -> List[Dict]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if unresolved_only:
                cursor.execute('SELECT * FROM hidden_floors WHERE story_id = ? AND is_resolved = 0',
                             (story_id,))
            else:
                cursor.execute('SELECT * FROM hidden_floors WHERE story_id = ?', (story_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def resolve_note(self, note_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE hidden_floors SET is_resolved = 1 WHERE id = ?', (note_id,))
            conn.commit()
            return cursor.rowcount > 0


class NovelManager:
    """小说管理器"""
    
    def __init__(self, db: DatabaseManager = None):
        self.db = db or DatabaseManager()
    
    def save_chapter(self, story_id: int, chapter_num: int, content: str,
                     chapter_title: str = None) -> int:
        story = StoryManager(self.db).get_story(story_id)
        if not story:
            raise ValueError(f"Story {story_id} not found")
        
        story_dir = STORIES_DIR / story['name']
        story_dir.mkdir(parents=True, exist_ok=True)
        
        novel_path = story_dir / "novel.md"
        
        with open(novel_path, 'a', encoding='utf-8') as f:
            title = chapter_title or f"第{chapter_num}章"
            f.write(f"\n\n## {title}\n\n{content}\n")
        
        word_count = len(content)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO novel_chapters (story_id, chapter_num, chapter_title, content_path, word_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (story_id, chapter_num, chapter_title, str(novel_path), word_count))
            conn.commit()
            return cursor.lastrowid
    
    def get_novel(self, story_id: int) -> Optional[str]:
        story = StoryManager(self.db).get_story(story_id)
        if not story:
            return None
        
        novel_path = STORIES_DIR / story['name'] / "novel.md"
        if novel_path.exists():
            return novel_path.read_text(encoding='utf-8')
        return None
    
    def get_chapters(self, story_id: int) -> List[Dict]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM novel_chapters WHERE story_id = ? ORDER BY chapter_num',
                         (story_id,))
            return [dict(row) for row in cursor.fetchall()]


class DataManager:
    """统一数据管理接口"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db = DatabaseManager(db_path)
        self.stories = StoryManager(self.db)
        self.characters = CharacterManager(self.db)
        self.world_state = WorldStateManager(self.db)
        self.hidden_floors = HiddenFloorManager(self.db)
        self.novels = NovelManager(self.db)
    
    def export_story(self, story_id: int, output_dir: Path = None) -> Path:
        story = self.stories.get_story(story_id)
        if not story:
            raise ValueError(f"Story {story_id} not found")
        
        output_dir = output_dir or STORIES_DIR / story['name']
        output_dir.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            'story': story,
            'characters': self.characters.list_characters(story_id),
            'world_states': [],
            'hidden_floors': self.hidden_floors.list_notes(story_id),
            'chapters': self.novels.get_chapters(story_id)
        }
        
        export_file = output_dir / "export.json"
        export_file.write_text(json.dumps(export_data, ensure_ascii=False, indent=2, default=str),
                              encoding='utf-8')
        
        return export_file


if __name__ == "__main__":
    dm = DataManager()
    
    print("万象绘卷数据管理工具")
    print("=" * 40)
    print(f"数据库: {DB_PATH}")
    print(f"故事目录: {STORIES_DIR}")
    print()
    
    stories = dm.stories.list_stories(active_only=False)
    print(f"已有故事: {len(stories)} 个")
    for s in stories:
        print(f"  - [{s['id']}] {s['name']} ({s['type']})")
