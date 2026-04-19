#!/usr/bin/env python3
"""
万象绘卷数据库初始化脚本 V2.0
基于完整系统文档设计的数据库结构
包含：故事、世界观、角色、事件、文风、剧情管理、代代相传等全部系统
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
STORIES_DIR = BASE_DIR / "stories"

DB_PATH = DATA_DIR / "wanxiang.db"


def init_database():
    """初始化完整数据库表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ==================== 核心故事系统 ====================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL DEFAULT 'life_simulation',
            world_type TEXT,
            style TEXT DEFAULT 'default',
            current_turn INTEGER DEFAULT 0,
            current_year INTEGER,
            current_season TEXT,
            era_name TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            metadata TEXT,
            FOREIGN KEY (style) REFERENCES style_configs(name)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS worlds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            world_name TEXT,
            world_type TEXT NOT NULL,
            magic_system TEXT,
            races TEXT,
            nations TEXT,
            history_events TEXT,
            special_settings TEXT,
            current_era TEXT,
            current_year INTEGER DEFAULT 1,
            core_conflict TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (story_id) REFERENCES stories(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS world_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            turn INTEGER DEFAULT 0,
            year INTEGER,
            season TEXT,
            location TEXT,
            weather TEXT,
            political_state TEXT,
            economic_state TEXT,
            social_state TEXT,
            state_data TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (story_id) REFERENCES stories(id)
        )
    ''')

    # ==================== 角色系统 ====================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'protagonist',
            gender TEXT,
            age INTEGER DEFAULT 0,
            race TEXT,
            origin TEXT,
            background TEXT,
            personality TEXT,
            goals TEXT,
            appearance TEXT,
            special_marks TEXT,
            is_alive BOOLEAN DEFAULT 1,
            is_legacy BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (story_id) REFERENCES stories(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS character_attributes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER NOT NULL,
            str INTEGER DEFAULT 10,
            dex INTEGER DEFAULT 10,
            int INTEGER DEFAULT 10,
            cha INTEGER DEFAULT 10,
            luk INTEGER DEFAULT 10,
            san INTEGER DEFAULT 100,
            hp INTEGER DEFAULT 100,
            mp INTEGER DEFAULT 100,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (character_id) REFERENCES characters(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS character_traits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER NOT NULL,
            trait_name TEXT NOT NULL,
            trait_type TEXT DEFAULT 'neutral',
            description TEXT,
            effects TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (character_id) REFERENCES characters(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS character_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            skill_level INTEGER DEFAULT 1,
            skill_type TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (character_id) REFERENCES characters(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            character_a_id INTEGER NOT NULL,
            character_b_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            relation_level INTEGER DEFAULT 50,
            history TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (story_id) REFERENCES stories(id),
            FOREIGN KEY (character_a_id) REFERENCES characters(id),
            FOREIGN KEY (character_b_id) REFERENCES characters(id)
        )
    ''')

    # ==================== 事件系统 ====================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            turn INTEGER,
            event_type TEXT NOT NULL,
            event_category TEXT,
            title TEXT,
            description TEXT,
            choices TEXT,
            outcome TEXT,
            consequences TEXT,
            weight INTEGER DEFAULT 100,
            is_chain BOOLEAN DEFAULT 0,
            chain_id INTEGER,
            chain_order INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (story_id) REFERENCES stories(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_chains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            chain_name TEXT NOT NULL,
            chain_type TEXT,
            total_events INTEGER,
            current_progress INTEGER DEFAULT 0,
            reward TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (story_id) REFERENCES stories(id)
        )
    ''')

    # ==================== 剧情管理系统 ====================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plot_arcs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            arc_name TEXT NOT NULL,
            arc_type TEXT,
            arc_category TEXT,
            start_turn INTEGER,
            end_turn INTEGER,
            start_chapter INTEGER,
            end_chapter INTEGER,
            status TEXT DEFAULT 'active',
            summary TEXT,
            key_events TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (story_id) REFERENCES stories(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hidden_floors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            note_type TEXT DEFAULT 'foreshadowing',
            related_arc_id INTEGER,
            related_event_id INTEGER,
            priority INTEGER DEFAULT 50,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            is_resolved BOOLEAN DEFAULT 0,
            resolution_note TEXT,
            FOREIGN KEY (story_id) REFERENCES stories(id),
            FOREIGN KEY (related_arc_id) REFERENCES plot_arcs(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            summary_type TEXT DEFAULT 'period',
            summary_order INTEGER,
            start_turn INTEGER,
            end_turn INTEGER,
            content TEXT NOT NULL,
            key_events TEXT,
            character_states TEXT,
            world_state TEXT,
            seeds TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (story_id) REFERENCES stories(id)
        )
    ''')

    # ==================== 小说生成系统 ====================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS novel_chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            chapter_num INTEGER,
            chapter_title TEXT,
            chapter_type TEXT DEFAULT 'story',
            life_stage TEXT,
            content_path TEXT,
            word_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (story_id) REFERENCES stories(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS novel_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_id INTEGER NOT NULL,
            section_order INTEGER,
            content TEXT,
            word_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chapter_id) REFERENCES novel_chapters(id)
        )
    ''')

    # ==================== 文风系统 ====================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS style_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT,
            sub_category TEXT,
            description TEXT,
            keywords TEXT,
            tone TEXT,
            sentence_structure TEXT,
            dialogue_style TEXT,
            description_style TEXT,
            rhythm TEXT,
            sample_text TEXT,
            forbidden_words TEXT,
            recommended_words TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS style_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            from_style TEXT,
            to_style TEXT,
            turn INTEGER,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (story_id) REFERENCES stories(id)
        )
    ''')

    # ==================== 代代相传系统 ====================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS legacies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            generation INTEGER DEFAULT 1,
            predecessor_id INTEGER,
            successor_id INTEGER,
            relation_type TEXT,
            inherited_traits TEXT,
            inherited_skills TEXT,
            inherited_items TEXT,
            family_reputation INTEGER DEFAULT 50,
            family_curse TEXT,
            family_secret TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (story_id) REFERENCES stories(id),
            FOREIGN KEY (predecessor_id) REFERENCES characters(id),
            FOREIGN KEY (successor_id) REFERENCES characters(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS family_tree (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            family_name TEXT,
            generation INTEGER,
            member_id INTEGER,
            parent_id INTEGER,
            achievement TEXT,
            death_type TEXT,
            death_age INTEGER,
            reputation INTEGER DEFAULT 50,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (story_id) REFERENCES stories(id),
            FOREIGN KEY (member_id) REFERENCES characters(id),
            FOREIGN KEY (parent_id) REFERENCES characters(id)
        )
    ''')

    # ==================== 物品系统 ====================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            item_type TEXT,
            rarity TEXT DEFAULT 'common',
            description TEXT,
            effects TEXT,
            owner_id INTEGER,
            location TEXT,
            is_equipped BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (story_id) REFERENCES stories(id),
            FOREIGN KEY (owner_id) REFERENCES characters(id)
        )
    ''')

    # ==================== 拆书融合系统 ====================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fusion_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            target_length TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'planning',
            current_step INTEGER DEFAULT 1,
            mode TEXT DEFAULT 'auto',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS source_novels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            novel_name TEXT NOT NULL,
            author TEXT,
            genre TEXT,
            analysis_depth INTEGER DEFAULT 5,
            elements TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES fusion_projects(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fusion_elements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            element_type TEXT NOT NULL,
            source_novel_id INTEGER,
            original_content TEXT,
            fused_content TEXT,
            is_retained BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES fusion_projects(id),
            FOREIGN KEY (source_novel_id) REFERENCES source_novels(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fusion_outputs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            step_number INTEGER,
            output_type TEXT,
            content TEXT,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES fusion_projects(id)
        )
    ''')

    # ==================== 质量控制系统 ====================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quality_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER,
            chapter_id INTEGER,
            check_type TEXT NOT NULL,
            opening_score INTEGER,
            plot_score INTEGER,
            character_score INTEGER,
            language_score INTEGER,
            emotion_score INTEGER,
            total_score INTEGER,
            issues TEXT,
            suggestions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (story_id) REFERENCES stories(id),
            FOREIGN KEY (chapter_id) REFERENCES novel_chapters(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forbidden_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT UNIQUE NOT NULL,
            category TEXT,
            severity TEXT DEFAULT 'medium',
            replacement TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ==================== 模板系统 ====================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            category TEXT,
            description TEXT,
            content TEXT NOT NULL,
            variables TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS character_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_name TEXT NOT NULL,
            race TEXT,
            origin TEXT,
            personality TEXT,
            appearance TEXT,
            attributes TEXT,
            traits TEXT,
            skills TEXT,
            background TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ==================== 指令日志系统 ====================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS command_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER,
            session_id TEXT,
            turn INTEGER,
            command_type TEXT,
            command_text TEXT,
            parameters TEXT,
            result TEXT,
            execution_time_ms INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (story_id) REFERENCES stories(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            session_end TIMESTAMP,
            turns_played INTEGER DEFAULT 0,
            commands_used INTEGER DEFAULT 0,
            session_data TEXT,
            FOREIGN KEY (story_id) REFERENCES stories(id)
        )
    ''')

    # ==================== 创建索引 ====================
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stories_name ON stories(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stories_type ON stories(type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_characters_story ON characters(story_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_characters_role ON characters(role)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_story ON events(story_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_world_state_story ON world_state(story_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_plot_arcs_story ON plot_arcs(story_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_hidden_floors_story ON hidden_floors(story_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_novel_chapters_story ON novel_chapters(story_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_style_configs_category ON style_configs(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_legacies_story ON legacies(story_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fusion_projects_status ON fusion_projects(status)')

    conn.commit()
    conn.close()
    print(f"数据库表结构初始化完成: {DB_PATH}")


def init_directories():
    """初始化目录结构"""
    dirs = [
        DATA_DIR,
        STORIES_DIR,
        STORIES_DIR / "interactive",
        STORIES_DIR / "templates",
        STORIES_DIR / "fusion_projects",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"目录已创建: {d}")


def seed_default_styles():
    """插入56种文风配置"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    styles = [
        # A. 殿堂文学区 (5种)
        ("鲁迅风", "殿堂文学", "经典", "冷峻匕首，社会解剖", "冷峻、讽刺、深刻", "短句、有力、反讽", "社会批判、人性剖析", "极简", "★★★★★"),
        ("张爱玲风", "殿堂文学", "经典", "华丽苍凉，心理细描", "华丽、苍凉、细腻", "长句、意象丰富", "情感描写、都市生活", "慢节奏", "★★★★★"),
        ("白先勇风", "殿堂文学", "经典", "古典挽歌，时代惆怅", "古典、惆怅、优雅", "典雅、含蓄", "怀旧情怀、传统文化", "慢节奏", "★★★★★"),
        ("汪曾祺风", "殿堂文学", "经典", "人间烟火，温润诗意", "温润、诗意、自然", "简洁、清新", "日常生活、温情描写", "适中", "★★★★★"),
        ("卡夫卡风", "殿堂文学", "经典", "荒诞异化，存在困境", "荒诞、异化、压抑", "冷峻、超现实", "哲学思考、荒诞剧情", "慢节奏", "★★★★★"),
        
        # B. 流行通俗区 (6种)
        ("搞笑甜宠网文风", "流行通俗", "网文", "口嫌体正直、反差萌", "沙雕、欢脱、反差萌", "短句、口语化", "轻松恋爱、日常搞笑", "快节奏", "★★★★"),
        ("Priest风", "流行通俗", "网文", "家国情怀、群像刻画", "大气、群像、正剧", "细腻、有张力", "正剧向、群像戏", "适中", "★★★★★"),
        ("江南风", "流行通俗", "网文", "青春伤痛、华丽堆砌", "华丽、伤痛、青春", "长句、堆砌", "青春文学、情感纠葛", "适中", "★★★★"),
        ("日轻废萌风", "流行通俗", "轻小说", "长标题、拟声词", "萌系、轻松、吐槽", "短句、拟声词", "轻小说、日常喜剧", "快节奏", "★★★★"),
        ("网文爽文风", "流行通俗", "网文", "装逼打脸、快节奏", "爽感、直接、热血", "短句、有力", "爽文、升级流", "极快", "★★★★★"),
        ("言情偶像剧风", "流行通俗", "言情", "甜宠、误会梗", "甜宠、浪漫、轻松", "温柔、细腻", "现代言情、偶像剧", "适中", "★★★★"),
        
        # C. 二次元区 (8种)
        ("ACG萌系风", "二次元", "轻小说", "萌系美学、吐槽役", "萌、可爱、吐槽", "短句、颜文字", "变身题材、轻小说", "快节奏", "★★★★"),
        ("元喜剧风", "二次元", "轻小说", "打破第四面墙", "元叙事、搞笑、吐槽", "灵活、多变", "元叙事、搞笑", "快节奏", "★★★★"),
        ("游戏化风", "二次元", "轻小说", "游戏机制融合", "游戏感、系统、数据", "数据化、系统", "游戏穿越、系统流", "快节奏", "★★★★"),
        ("中二病风", "二次元", "轻小说", "中二台词、必杀技", "中二、热血、夸张", "夸张、必杀技", "热血、搞笑", "快节奏", "★★★★"),
        ("病娇风", "二次元", "特殊", "扭曲的爱、极端情感", "病娇、扭曲、极端", "压抑、爆发", "心理惊悚、暗黑", "慢节奏", "★★★★"),
        ("傲娇风", "二次元", "轻小说", "标准傲娇模板", "傲娇、口嫌体正直", "反差、傲娇", "恋爱喜剧", "适中", "★★★★"),
        ("腹黑风", "二次元", "轻小说", "表面温柔、内心算计", "腹黑、心机、温柔", "反差、心机", "权谋、宫斗", "适中", "★★★★"),
        ("黑化风", "二次元", "特殊", "黑暗转变、极端", "黑暗、极端、压抑", "压抑、爆发", "心理惊悚、暗黑", "慢节奏", "★★★★"),
        
        # D. 东方玄幻区 (6种)
        ("东方玄幻风", "东方玄幻", "玄幻", "意在笔先、精神交锋", "意境、精神、玄幻", "典雅、意境", "武侠、高武", "适中", "★★★★★"),
        ("田园仙侠风", "东方玄幻", "仙侠", "无敌流+种田文", "悠闲、种田、无敌", "轻松、自然", "修仙、种田", "慢节奏", "★★★★"),
        ("无敌流风", "东方玄幻", "玄幻", "时间错位金手指", "无敌、爽感、直接", "短句、有力", "无敌流、穿越", "快节奏", "★★★★"),
        ("古风言情风", "东方玄幻", "言情", "古典雅致、含蓄", "古典、雅致、含蓄", "典雅、含蓄", "古代言情", "慢节奏", "★★★★"),
        ("仙侠修真风", "东方玄幻", "仙侠", "修炼体系、境界", "修仙、境界、体系", "系统、层次", "修仙小说", "适中", "★★★★★"),
        ("武侠江湖风", "东方玄幻", "武侠", "江湖恩怨、侠义", "侠义、江湖、恩怨", "短句、有力", "武侠小说", "适中", "★★★★★"),
        
        # E. 科幻区 (4种)
        ("硬科幻风", "科幻", "硬科幻", "科学严谨、技术细节", "严谨、技术、科学", "精确、专业", "硬科幻、技术流", "适中", "★★★★★"),
        ("赛博朋克风", "科幻", "赛博", "高科技低生活、霓虹美学", "霓虹、科技、反乌托邦", "碎片、霓虹", "赛博朋克、反乌托邦", "快节奏", "★★★★★"),
        ("太空歌剧风", "科幻", "太空", "宏大叙事、星际文明", "宏大、史诗、星际", "宏大、史诗", "太空歌剧、史诗", "适中", "★★★★"),
        ("末日废土风", "科幻", "废土", "生存、人性考验", "苍凉、生存、人性", "粗砺、压抑", "末世、废土", "慢节奏", "★★★★"),
        
        # F. 悬疑推理区 (4种)
        ("本格推理风", "悬疑推理", "推理", "逻辑严密、公平竞争", "逻辑、严密、推理", "精确、逻辑", "推理小说", "适中", "★★★★★"),
        ("社会派推理风", "悬疑推理", "推理", "人性探讨、社会问题", "人性、社会、深刻", "细腻、深刻", "社会派推理", "慢节奏", "★★★★"),
        ("悬疑惊悚风", "悬疑推理", "悬疑", "紧张氛围、反转", "紧张、悬疑、反转", "短句、紧张", "惊悚、悬疑", "快节奏", "★★★★"),
        ("恐怖灵异风", "悬疑推理", "恐怖", "恐怖氛围、超自然", "恐怖、灵异、压抑", "压抑、恐怖", "恐怖小说", "慢节奏", "★★★★"),
        
        # G. 特殊感官区 (4种)
        ("克苏鲁风", "特殊感官", "克苏鲁", "不可名状、SAN值", "不可名状、疯狂、压抑", "模糊、恐怖", "克苏鲁、恐怖", "慢节奏", "★★★★★"),
        ("荒诞灰暗风", "特殊感官", "荒诞", "极度残酷与低龄化反差", "荒诞、灰暗、反差", "反差、荒诞", "黑暗童话", "慢节奏", "★★★★"),
        ("意识流风", "特殊感官", "实验", "非线性、内心独白", "意识流、内心、非线性", "流动、意识", "文学实验", "慢节奏", "★★★★"),
        ("诗意散文风", "特殊感官", "散文", "意象丰富、抒情", "诗意、意象、抒情", "优美、抒情", "散文、抒情", "慢节奏", "★★★★"),
        
        # H. 历史军事区 (4种)
        ("历史正剧风", "历史军事", "历史", "严谨考据、史诗感", "严谨、史诗、考据", "典雅、厚重", "历史小说", "适中", "★★★★★"),
        ("军事战争风", "历史军事", "军事", "战术描写、铁血", "铁血、战术、战争", "短句、有力", "军事小说", "快节奏", "★★★★"),
        ("架空历史风", "历史军事", "历史", "假设历史、推演", "架空、推演、假设", "灵活、多变", "架空历史", "适中", "★★★★"),
        ("宫廷权谋风", "历史军事", "权谋", "权力斗争、心计", "权谋、心计、宫廷", "细腻、心机", "宫斗、权谋", "适中", "★★★★"),
        
        # I. 生活日常区 (4种)
        ("日常治愈风", "生活日常", "治愈", "温馨、小确幸", "温馨、治愈、日常", "温柔、细腻", "治愈系、日常", "慢节奏", "★★★★"),
        ("美食文风", "生活日常", "美食", "美食描写、烟火气", "美食、烟火、温馨", "细腻、感官", "美食小说", "适中", "★★★★"),
        ("职场文风", "生活日常", "职场", "职场斗争、成长", "职场、现实、成长", "直接、现实", "职场小说", "适中", "★★★★"),
        ("校园青春风", "生活日常", "青春", "青春、成长、恋爱", "青春、活力、恋爱", "轻松、活泼", "校园小说", "适中", "★★★★"),
        
        # J. 奇幻冒险区 (4种)
        ("西方奇幻风", "奇幻冒险", "西幻", "魔法体系、种族", "魔法、种族、奇幻", "史诗、奇幻", "西幻、D&D", "适中", "★★★★★"),
        ("冒险探险风", "奇幻冒险", "冒险", "探险、解谜、宝藏", "冒险、探险、刺激", "紧张、刺激", "冒险小说", "快节奏", "★★★★"),
        ("异世界穿越风", "奇幻冒险", "穿越", "穿越、异世界", "穿越、异世界、新奇", "轻松、新奇", "异世界、穿越", "快节奏", "★★★★"),
        ("魔法学院风", "奇幻冒险", "学院", "魔法学习、校园", "魔法、学院、成长", "轻松、成长", "魔法学院", "适中", "★★★★"),
        
        # K. 恐怖惊悚区 (3种)
        ("心理恐怖风", "恐怖惊悚", "心理", "心理压迫、精神折磨", "心理、压抑、恐怖", "压抑、心理", "心理恐怖", "慢节奏", "★★★★"),
        ("怪物猎杀风", "恐怖惊悚", "怪物", "生存、战斗", "怪物、生存、战斗", "紧张、动作", "怪物题材", "快节奏", "★★★★"),
        ("灵异鬼怪风", "恐怖惊悚", "灵异", "鬼怪、超自然", "灵异、鬼怪、恐怖", "恐怖、灵异", "灵异小说", "慢节奏", "★★★★"),
        
        # L. 其他风格 (4种)
        ("实验文学风", "其他风格", "实验", "形式创新、先锋", "实验、先锋、创新", "创新、多变", "文学实验", "多变", "★★★★"),
        ("同人二创风", "其他风格", "同人", "原作还原+创新", "还原、创新、同人", "灵活、还原", "同人创作", "适中", "★★★★"),
        ("广播剧风", "其他风格", "广播剧", "声音导向、对话多", "声音、对话、场景", "对话为主", "广播剧剧本", "适中", "★★★★"),
        ("剧本杀风", "其他风格", "剧本杀", "线索、推理、角色", "推理、线索、角色", "线索、对话", "剧本杀", "适中", "★★★★"),
    ]

    for name, category, sub_category, description, tone, sentence_structure, dialogue_style, rhythm, rating in styles:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO style_configs 
                (name, category, sub_category, description, tone, sentence_structure, dialogue_style, description_style, rhythm)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, category, sub_category, description, tone, sentence_structure, dialogue_style, dialogue_style, rhythm))
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
    print("56种文风配置已插入")


def seed_default_templates():
    """插入默认模板"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    templates = [
        ("人生模拟世界模板", "world_gen", "世界生成", json.dumps({
            "world_types": ["奇幻中世纪", "东方玄幻", "蒸汽朋克", "黑暗奇幻", "异能都市", "原始部落", "废土末世"],
            "hidden_worlds": ["众神游戏", "轮回世界", "虚假世界", "混合世界", "倒计时世界"],
            "magic_systems": ["元素魔法", "灵魂魔法", "符文魔法", "自然魔法", "时空魔法", "亡灵魔法", "星辰魔法"],
            "races": ["人类", "精灵", "矮人", "兽人", "龙裔", "混血"],
            "governments": ["王国", "帝国", "共和国", "神权国", "部落联盟", "法师议会", "商业城邦"]
        }), "人生模拟世界观生成默认配置"),
        
        ("角色生成模板", "character", "角色", json.dumps({
            "required_fields": ["name", "gender", "age"],
            "optional_fields": ["background", "personality", "goals"],
            "attribute_range": {"min": 1, "max": 20},
            "life_stages": ["婴儿期", "童年期", "少年期", "青年期", "中年期", "老年期"],
            "origins": ["贵族", "平民", "商人", "学者", "战士", "猎人", "贫民", "孤儿"]
        }), "角色生成默认配置"),
        
        ("事件模板", "event", "事件", json.dumps({
            "event_types": ["random", "fate", "world", "relationship", "choice"],
            "weight_default": 100,
            "choice_count": {"min": 2, "max": 4},
            "fate_events": {
                "0": "出生",
                "5": "天赋觉醒",
                "10": "教育选择",
                "15": "成人礼",
                "18": "职业起点",
                "25": "人生抉择",
                "35": "中年危机",
                "50": "人生回顾",
                "60": "晚年事件"
            }
        }), "事件生成默认配置"),
        
        ("黄金三章模板", "novel", "网文", json.dumps({
            "chapter_1": {
                "goal": "吸引注意",
                "elements": ["开篇冲突", "主角登场", "金手指展现", "留下悬念"],
                "word_count": 2000
            },
            "chapter_2": {
                "goal": "展开设定",
                "elements": ["世界观介绍", "配角登场", "小高潮", "推进剧情"],
                "word_count": 2000
            },
            "chapter_3": {
                "goal": "确立主线",
                "elements": ["主线任务明确", "升级路线清晰", "大BOSS暗示", "为后续铺垫"],
                "word_count": 2000
            }
        }), "黄金三章结构模板"),
        
        ("拆书融合模板", "fusion", "融合", json.dumps({
            "steps": [
                "素材分析提取",
                "要素融合设计",
                "原创性深度验证",
                "核心看点提炼",
                "大纲详细设计",
                "文风配置",
                "开篇钩子设计",
                "正文生成",
                "质量检查",
                "保存最终成果"
            ],
            "four_replace_three": {
                "retain": 1,
                "replace": 3,
                "elements": ["背景设定", "人物构建", "金手指设计", "主剧情"]
            },
            "six_dimensions": ["故事框架", "人物", "情绪", "文风", "金手指", "世界观"]
        }), "拆书融合工作流模板"),
    ]

    for name, type_, category, content, desc in templates:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO templates (name, type, category, content, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, type_, category, content, desc))
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
    print("默认模板已插入")


def seed_forbidden_words():
    """插入禁用词库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    forbidden_words = [
        ("不禁", "连接词", "high"),
        ("不由得", "连接词", "high"),
        ("竟然", "程度词", "medium"),
        ("居然", "程度词", "medium"),
        ("缓缓地", "动作修饰", "medium"),
        ("微微", "动作修饰", "medium"),
        ("淡淡", "动作修饰", "medium"),
        ("默默", "动作修饰", "medium"),
        ("轻轻", "动作修饰", "medium"),
        ("深深", "动作修饰", "medium"),
        ("暗暗", "动作修饰", "medium"),
        ("赫然", "程度词", "medium"),
        ("霍然", "程度词", "medium"),
        ("蓦然", "程度词", "medium"),
        ("陡然", "程度词", "medium"),
        ("倏然", "程度词", "medium"),
        ("霎时", "时间词", "medium"),
        ("刹那", "时间词", "medium"),
        ("顿觉", "感受词", "medium"),
        ("顿感", "感受词", "medium"),
        ("恍若", "比喻词", "medium"),
        ("宛若", "比喻词", "medium"),
        ("犹若", "比喻词", "medium"),
        ("恰似", "比喻词", "medium"),
        ("眼中闪过一丝", "八股文", "high"),
        ("嘴角微微上扬", "八股文", "high"),
        ("那双总是带着", "八股文", "high"),
        ("一丝不易察觉", "八股文", "high"),
        ("指节因为用力", "八股文", "high"),
        ("一股前所未有", "八股文", "high"),
    ]

    for word, category, severity in forbidden_words:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO forbidden_words (word, category, severity)
                VALUES (?, ?, ?)
            ''', (word, category, severity))
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
    print("禁用词库已插入")


def create_sample_story():
    """创建示例故事目录结构"""
    sample_dir = STORIES_DIR / "_sample_story"
    sample_dir.mkdir(exist_ok=True)

    novel_md = sample_dir / "novel.md"
    if not novel_md.exists():
        novel_md.write_text("# 示例故事\n\n这是一个示例故事文件。\n\n---\n\n*故事内容将在这里生成*\n", encoding='utf-8')

    data_json = sample_dir / "data.json"
    if not data_json.exists():
        sample_data = {
            "story_name": "示例故事",
            "world_type": "东方玄幻",
            "current_turn": 0,
            "created_at": datetime.now().isoformat(),
            "protagonist": {
                "name": "未命名",
                "attributes": {"str": 10, "dex": 10, "int": 10, "cha": 10, "luk": 10, "san": 100}
            }
        }
        data_json.write_text(json.dumps(sample_data, ensure_ascii=False, indent=2), encoding='utf-8')

    world_json = sample_dir / "world_state.json"
    if not world_json.exists():
        world_data = {
            "world_name": "示例世界",
            "world_type": "东方玄幻",
            "current_year": 1,
            "current_season": "春"
        }
        world_json.write_text(json.dumps(world_data, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"示例故事目录已创建: {sample_dir}")


def main():
    print("=" * 60)
    print("万象绘卷数据库初始化 V2.0")
    print("基于完整系统文档设计")
    print("=" * 60)
    
    init_directories()
    init_database()
    seed_default_styles()
    seed_default_templates()
    seed_forbidden_words()
    create_sample_story()
    
    print("\n" + "=" * 60)
    print("初始化完成！")
    print(f"数据库位置: {DB_PATH}")
    print(f"故事目录: {STORIES_DIR}")
    print("=" * 60)
    print("\n数据表统计:")
    print("- 核心故事系统: stories, worlds, world_state")
    print("- 角色系统: characters, character_attributes, character_traits, character_skills, relationships")
    print("- 事件系统: events, event_chains")
    print("- 剧情管理: plot_arcs, hidden_floors, summaries")
    print("- 小说生成: novel_chapters, novel_sections")
    print("- 文风系统: style_configs, style_history")
    print("- 代代相传: legacies, family_tree")
    print("- 物品系统: items")
    print("- 拆书融合: fusion_projects, source_novels, fusion_elements, fusion_outputs")
    print("- 质量控制: quality_checks, forbidden_words")
    print("- 模板系统: templates, character_templates")
    print("- 日志系统: command_logs, game_sessions")
    print("=" * 60)


if __name__ == "__main__":
    main()
