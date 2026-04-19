#!/usr/bin/env python3
"""
万象绘卷存档导出系统
将数据库中的元数据导出为 Markdown 格式的存档文件
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from string import Template

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
STORIES_DIR = BASE_DIR / "stories"
SAVES_DIR = BASE_DIR / "saves"
DB_PATH = DATA_DIR / "wanxiang.db"


class SaveTemplate:
    """存档模板类"""
    
    TEMPLATES = {
        "life_simulation": """# ${story_name} — 人生纪行

## 世界信息
- **存档名**：${story_name}
- **世界类型**：${world_type}
- **创建时间**：${created_at}
- **当前回合**：第 ${current_turn} 回合
- **当前年份**：${current_year}年 ${current_season}

## 世界观设定
${world_settings}

## 角色信息
${character_info}

## 属性面板
${attributes}

## 技能与特质
${skills_traits}

## 人际关系
${relationships}

## 物品与财富
${inventory_wealth}

## 历史事件
${history_events}

## 线索与伏笔
${clues_seeds}

---
*存档导出于 ${export_time}*
""",
        
        "interactive_story": """# ${story_name} — 交互式故事存档

## 故事信息
- **存档名**：${story_name}
- **故事类型**：交互式故事
- **文风**：${style}
- **创建时间**：${created_at}

## 当前状态
${current_state}

## 角色信息
${character_info}

## 剧情进度
${plot_progress}

## 隐藏楼层
${hidden_floors}

## 已完成章节
${chapters}

---
*存档导出于 ${export_time}*
""",
        
        "minecraft_survival": """# ${story_name} — 游戏日志

## 世界信息
- **存档名**：${story_name}
- **世界类型**：${world_type}
- **创建时间**：${created_at}
- **世界种子**：${world_seed}

## 核心规则
${core_rules}

## 世界规则
${world_rules}

## 生物图鉴
${mob_guide}

## 资源层级
${resource_tiers}

## 进度系统
${advancements}

## 环境状态
${environment}

## 游戏日志
${game_log}

---
*存档导出于 ${export_time}*
""",
        
        "fusion_project": """# ${project_name} — 拆书融合项目

## 项目信息
- **项目名**：${project_name}
- **目标长度**：${target_length}
- **当前状态**：${status}
- **当前步骤**：第 ${current_step} 步

## 源素材
${source_novels}

## 融合要素
${fusion_elements}

## 输出成果
${outputs}

---
*存档导出于 ${export_time}*
"""
    }
    
    @classmethod
    def get_template(cls, story_type: str) -> str:
        return cls.TEMPLATES.get(story_type, cls.TEMPLATES["life_simulation"])
    
    @classmethod
    def register_template(cls, name: str, template: str):
        cls.TEMPLATES[name] = template


class SaveExporter:
    """存档导出器"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        SAVES_DIR.mkdir(parents=True, exist_ok=True)
        STORIES_DIR.mkdir(parents=True, exist_ok=True)
    
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def export_story(self, story_id: int, output_format: str = "md") -> Path:
        """导出故事存档"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM stories WHERE id = ?', (story_id,))
            story = cursor.fetchone()
            if not story:
                raise ValueError(f"Story {story_id} not found")
            
            story_dict = dict(story)
            story_type = story_dict.get('type', 'life_simulation')
            
            if story_type == 'life_simulation':
                data = self._collect_life_simulation_data(cursor, story_id)
            elif story_type == 'interactive':
                data = self._collect_interactive_data(cursor, story_id)
            else:
                data = self._collect_generic_data(cursor, story_id)
            
            data['story_name'] = story_dict['name']
            data['created_at'] = story_dict['created_at']
            data['current_turn'] = story_dict.get('current_turn', 0)
            data['export_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            story_dir = STORIES_DIR / story_dict['name']
            story_dir.mkdir(parents=True, exist_ok=True)
            
            json_path = story_dir / "data.json"
            json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            
            template = SaveTemplate.get_template(story_type)
            md_content = Template(template).safe_substitute(data)
            md_path = story_dir / "save.md"
            md_path.write_text(md_content, encoding='utf-8')
            
            novel_path = story_dir / "novel.md"
            if not novel_path.exists():
                novel_path.write_text(f"# {story_dict['name']}\n\n*故事内容将在这里生成*\n", encoding='utf-8')
            
            return md_path
    
    def _collect_life_simulation_data(self, cursor, story_id: int) -> Dict:
        """收集人生模拟数据"""
        data = {}
        
        cursor.execute('SELECT * FROM worlds WHERE story_id = ?', (story_id,))
        world = cursor.fetchone()
        if world:
            world_dict = dict(world)
            data['world_type'] = world_dict.get('world_type', '未知')
            data['current_year'] = world_dict.get('current_year', 1)
            data['current_season'] = world_dict.get('current_era', '')
            data['world_settings'] = self._format_world_settings(world_dict)
        else:
            data['world_type'] = '未知'
            data['current_year'] = 1
            data['current_season'] = ''
            data['world_settings'] = '*世界设定待生成*'
        
        cursor.execute('SELECT * FROM characters WHERE story_id = ? AND role = ?', (story_id, 'protagonist'))
        protagonist = cursor.fetchone()
        if protagonist:
            char_dict = dict(protagonist)
            data['character_info'] = self._format_character_info(char_dict)
            char_id = char_dict['id']
            
            cursor.execute('SELECT * FROM character_attributes WHERE character_id = ?', (char_id,))
            attrs = cursor.fetchone()
            if attrs:
                data['attributes'] = self._format_attributes(dict(attrs))
            else:
                data['attributes'] = '*属性待生成*'
            
            cursor.execute('SELECT * FROM character_traits WHERE character_id = ?', (char_id,))
            traits = cursor.fetchall()
            cursor.execute('SELECT * FROM character_skills WHERE character_id = ?', (char_id,))
            skills = cursor.fetchall()
            data['skills_traits'] = self._format_skills_traits(skills, traits)
        else:
            data['character_info'] = '*主角待创建*'
            data['attributes'] = '*属性待生成*'
            data['skills_traits'] = '*技能特质待生成*'
        
        cursor.execute('SELECT * FROM relationships WHERE story_id = ?', (story_id,))
        relationships = cursor.fetchall()
        data['relationships'] = self._format_relationships(relationships)
        
        cursor.execute('SELECT * FROM items WHERE story_id = ?', (story_id,))
        items = cursor.fetchall()
        data['inventory_wealth'] = self._format_inventory(items)
        
        cursor.execute('SELECT * FROM events WHERE story_id = ? ORDER BY turn', (story_id,))
        events = cursor.fetchall()
        data['history_events'] = self._format_events(events)
        
        cursor.execute('SELECT * FROM hidden_floors WHERE story_id = ? AND is_resolved = 0', (story_id,))
        clues = cursor.fetchall()
        data['clues_seeds'] = self._format_clues(clues)
        
        data['style'] = '默认文风'
        
        return data
    
    def _collect_interactive_data(self, cursor, story_id: int) -> Dict:
        """收集交互式故事数据"""
        data = {}
        
        cursor.execute('SELECT * FROM world_state WHERE story_id = ? ORDER BY turn DESC LIMIT 1', (story_id,))
        state = cursor.fetchone()
        if state:
            data['current_state'] = self._format_world_state(dict(state))
        else:
            data['current_state'] = '*状态待初始化*'
        
        cursor.execute('SELECT * FROM characters WHERE story_id = ?', (story_id,))
        characters = cursor.fetchall()
        data['character_info'] = self._format_characters_list(characters)
        
        cursor.execute('SELECT * FROM plot_arcs WHERE story_id = ?', (story_id,))
        arcs = cursor.fetchall()
        data['plot_progress'] = self._format_plot_arcs(arcs)
        
        cursor.execute('SELECT * FROM hidden_floors WHERE story_id = ?', (story_id,))
        hidden = cursor.fetchall()
        data['hidden_floors'] = self._format_hidden_floors(hidden)
        
        cursor.execute('SELECT * FROM novel_chapters WHERE story_id = ? ORDER BY chapter_num', (story_id,))
        chapters = cursor.fetchall()
        data['chapters'] = self._format_chapters(chapters)
        
        data['style'] = '默认文风'
        data['world_type'] = '交互式故事'
        
        return data
    
    def _collect_generic_data(self, cursor, story_id: int) -> Dict:
        """收集通用数据"""
        return {
            'world_type': '通用',
            'current_year': 1,
            'current_season': '',
            'world_settings': '*设定待完善*',
            'character_info': '*角色待创建*',
            'attributes': '*属性待生成*',
            'skills_traits': '*技能特质待生成*',
            'relationships': '*关系待建立*',
            'inventory_wealth': '*物品待获取*',
            'history_events': '*事件待发生*',
            'clues_seeds': '*线索待发现*',
            'style': '默认文风'
        }
    
    def _format_world_settings(self, world: Dict) -> str:
        lines = []
        if world.get('world_name'):
            lines.append(f"- **世界名称**：{world['world_name']}")
        if world.get('magic_system'):
            try:
                magic = json.loads(world['magic_system'])
                lines.append(f"- **魔法体系**：{', '.join(magic) if isinstance(magic, list) else magic}")
            except:
                pass
        if world.get('races'):
            try:
                races = json.loads(world['races'])
                lines.append(f"- **主要种族**：{', '.join(races) if isinstance(races, list) else races}")
            except:
                pass
        if world.get('nations'):
            try:
                nations = json.loads(world['nations'])
                lines.append(f"- **国家势力**：{', '.join(nations) if isinstance(nations, list) else nations}")
            except:
                pass
        return '\n'.join(lines) if lines else '*世界设定待完善*'
    
    def _format_character_info(self, char: Dict) -> str:
        lines = [
            f"- **姓名**：{char.get('name', '未命名')}",
            f"- **种族**：{char.get('race', '未知')}",
            f"- **性别**：{char.get('gender', '未知')}",
            f"- **年龄**：{char.get('age', 0)}岁",
            f"- **出身**：{char.get('origin', '未知')}",
        ]
        if char.get('background'):
            lines.append(f"- **背景**：{char['background']}")
        if char.get('personality'):
            lines.append(f"- **性格**：{char['personality']}")
        return '\n'.join(lines)
    
    def _format_attributes(self, attrs: Dict) -> str:
        return f"""| 属性 | 数值 |
|------|------|
| 力量 (STR) | {attrs.get('str', 10)} |
| 敏捷 (DEX) | {attrs.get('dex', 10)} |
| 智力 (INT) | {attrs.get('int', 10)} |
| 魅力 (CHA) | {attrs.get('cha', 10)} |
| 幸运 (LUK) | {attrs.get('luk', 10)} |
| SAN值 | {attrs.get('san', 100)} |
| HP | {attrs.get('hp', 100)} |
| MP | {attrs.get('mp', 100)} |"""
    
    def _format_skills_traits(self, skills: List, traits: List) -> str:
        lines = ["### 技能"]
        if skills:
            for s in skills:
                s_dict = dict(s)
                lines.append(f"- **{s_dict.get('skill_name', '未知')}** (Lv.{s_dict.get('skill_level', 1)})：{s_dict.get('description', '')}")
        else:
            lines.append("*暂无技能*")
        
        lines.append("\n### 特质")
        if traits:
            for t in traits:
                t_dict = dict(t)
                trait_type = t_dict.get('trait_type', 'neutral')
                emoji = "✅" if trait_type == "positive" else "⚠️" if trait_type == "negative" else "➖"
                lines.append(f"- {emoji} **{t_dict.get('trait_name', '未知')}**：{t_dict.get('description', '')}")
        else:
            lines.append("*暂无特质*")
        
        return '\n'.join(lines)
    
    def _format_relationships(self, relationships: List) -> str:
        if not relationships:
            return "*暂无关系*"
        lines = ["| 角色 | 关系 | 亲密度 |", "|------|------|--------|"]
        for r in relationships:
            r_dict = dict(r)
            lines.append(f"| 未知 | {r_dict.get('relation_type', '未知')} | {r_dict.get('relation_level', 50)} |")
        return '\n'.join(lines)
    
    def _format_inventory(self, items: List) -> str:
        if not items:
            return "*暂无物品*"
        lines = ["### 物品", "| 名称 | 类型 | 稀有度 |", "|------|------|--------|"]
        for item in items:
            i_dict = dict(item)
            lines.append(f"| {i_dict.get('item_name', '未知')} | {i_dict.get('item_type', '未知')} | {i_dict.get('rarity', '普通')} |")
        return '\n'.join(lines)
    
    def _format_events(self, events: List) -> str:
        if not events:
            return "*暂无事件记录*"
        lines = []
        for e in events:
            e_dict = dict(e)
            lines.append(f"### 第 {e_dict.get('turn', 0)} 回合 — {e_dict.get('title', '未知事件')}")
            lines.append(f"{e_dict.get('description', '')}")
            if e_dict.get('outcome'):
                lines.append(f"**结果**：{e_dict['outcome']}")
            lines.append("")
        return '\n'.join(lines)
    
    def _format_clues(self, clues: List) -> str:
        if not clues:
            return "*暂无线索*"
        lines = []
        for c in clues:
            c_dict = dict(c)
            lines.append(f"- **{c_dict.get('note_type', '线索')}**：{c_dict.get('content', '')}")
        return '\n'.join(lines)
    
    def _format_world_state(self, state: Dict) -> str:
        lines = [
            f"- **回合**：{state.get('turn', 0)}",
            f"- **年份**：{state.get('year', 1)}",
            f"- **季节**：{state.get('season', '未知')}",
            f"- **位置**：{state.get('location', '未知')}",
        ]
        return '\n'.join(lines)
    
    def _format_characters_list(self, characters: List) -> str:
        if not characters:
            return "*暂无角色*"
        lines = ["| 姓名 | 角色 | 种族 | 状态 |", "|------|------|------|------|"]
        for c in characters:
            c_dict = dict(c)
            status = "存活" if c_dict.get('is_alive', True) else "死亡"
            lines.append(f"| {c_dict.get('name', '未知')} | {c_dict.get('role', '未知')} | {c_dict.get('race', '未知')} | {status} |")
        return '\n'.join(lines)
    
    def _format_plot_arcs(self, arcs: List) -> str:
        if not arcs:
            return "*暂无剧情弧线*"
        lines = ["| 弧线名称 | 类型 | 状态 |", "|----------|------|------|"]
        for a in arcs:
            a_dict = dict(a)
            lines.append(f"| {a_dict.get('arc_name', '未知')} | {a_dict.get('arc_type', '未知')} | {a_dict.get('status', '未知')} |")
        return '\n'.join(lines)
    
    def _format_hidden_floors(self, hidden: List) -> str:
        if not hidden:
            return "*暂无隐藏楼层*"
        lines = []
        for h in hidden:
            h_dict = dict(h)
            status = "✅ 已解决" if h_dict.get('is_resolved') else "🔄 进行中"
            lines.append(f"- [{status}] {h_dict.get('content', '')}")
        return '\n'.join(lines)
    
    def _format_chapters(self, chapters: List) -> str:
        if not chapters:
            return "*暂无章节*"
        lines = ["| 章节 | 标题 | 字数 |", "|------|------|------|"]
        for c in chapters:
            c_dict = dict(c)
            lines.append(f"| 第{c_dict.get('chapter_num', 0)}章 | {c_dict.get('chapter_title', '未命名')} | {c_dict.get('word_count', 0)} |")
        return '\n'.join(lines)
    
    def export_all_stories(self) -> List[Path]:
        """导出所有故事"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM stories WHERE is_active = 1')
            story_ids = [row[0] for row in cursor.fetchall()]
        
        paths = []
        for story_id in story_ids:
            try:
                path = self.export_story(story_id)
                paths.append(path)
            except Exception as e:
                print(f"导出故事 {story_id} 失败: {e}")
        
        return paths
    
    def create_save_from_template(self, template_name: str, story_name: str, 
                                   story_type: str = "life_simulation",
                                   **kwargs) -> int:
        """从模板创建新存档"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO stories (name, type, style, metadata)
                VALUES (?, ?, ?, ?)
            ''', (story_name, story_type, kwargs.get('style', '默认文风'), 
                  json.dumps(kwargs, ensure_ascii=False)))
            conn.commit()
            story_id = cursor.lastrowid
            
            story_dir = STORIES_DIR / story_name
            story_dir.mkdir(parents=True, exist_ok=True)
            
            template = SaveTemplate.get_template(story_type)
            md_content = Template(template).safe_substitute({
                'story_name': story_name,
                'created_at': datetime.now().strftime('%Y-%m-%d'),
                'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                **kwargs
            })
            
            (story_dir / "save.md").write_text(md_content, encoding='utf-8')
            (story_dir / "novel.md").write_text(f"# {story_name}\n\n*故事内容将在这里生成*\n", encoding='utf-8')
            
            return story_id


if __name__ == "__main__":
    exporter = SaveExporter()
    
    print("万象绘卷存档导出系统")
    print("=" * 40)
    print(f"数据库: {DB_PATH}")
    print(f"存档目录: {STORIES_DIR}")
    print()
    
    paths = exporter.export_all_stories()
    print(f"已导出 {len(paths)} 个存档:")
    for p in paths:
        print(f"  - {p}")
