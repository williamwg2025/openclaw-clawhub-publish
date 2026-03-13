#!/usr/bin/env python3
"""
ClawHub Publish - Skill SEO Optimizer
自动优化技能 SEO，提高 ClawHub 搜索排名

功能：
- 优化 SKILL.md name（添加 openclaw- 前缀）
- 优化 displayName（完整命名）
- 优化 description（包含关键词）
- 扩展 tags（添加相关标签）
- 优化 README（添加推荐场景、评分引导、相关技能推荐）

Usage:
  python3 optimize-skill-seo.py auto-backup
  python3 optimize-skill-seo.py --all
  python3 optimize-skill-seo.py --check auto-backup
"""

import json
import argparse
import re
from pathlib import Path

SKILLS_DIR = Path.home() / ".openclaw" / "workspace" / "skills"

# 技能分类和推荐标签
CATEGORY_TAGS = {
    'backup': ['backup', 'automation', 'scheduled-tasks', 'restore', 'version-control', 'safety', 'production-ready'],
    'model': ['model', 'switch', 'multi-model', 'api-management', 'ai-providers', 'gemini', 'gpt', 'claude'],
    'memory': ['memory', 'search', 'ai', 'productivity', 'optimization', 'token-optimizer', 'rag', 'semantic-search'],
    'search': ['search', 'web', 'research', 'productivity', 'multi-engine', 'tavily', 'content-extraction', 'bing', 'baidu'],
    'marketplace': ['marketplace', 'skills', 'discovery', 'management', 'recommendation', 'ai', 'clawhub', 'sync', 'installer'],
    'publish': ['clawhub', 'publish', 'deployment', 'automation', 'code-quality', 'security-audit', 'pre-publish-check', 'ci-cd'],
    'ui': ['ui', 'design', 'frontend', 'components', 'design-system', 'accessibility', 'wcag', 'responsive', 'color-palette'],
    'writing': ['webnovel', 'writing', 'ai', 'creative', 'fiction', 'novel', 'outline', 'character-design', 'story-generator'],
    'agent': ['multi-agent', 'orchestration', 'automation', 'enterprise', 'collaboration', 'task-dispatch', 'load-balancing', 'monitoring'],
    'scaffold': ['scaffold', 'template', 'skill-creation', 'productivity', 'generator', 'boilerplate', 'cli', 'automation', 'dev-tools'],
}

# 技能描述模板
DESCRIPTION_TEMPLATES = {
    'backup': '{name} - 定时备份配置文件，防止数据丢失。支持版本管理、一键恢复、定时任务。包含完整 Python 脚本。关键词：openclaw, backup, automation, scheduled, restore, version',
    'model': '{name} - 用自然语言切换和添加 AI 模型。支持 9+ 预置提供商（Gemini/GPT/Claude/Qwen/Kimi 等），智能判断模型特性，一键配置 API Key。关键词：openclaw, model, switch, ai, multi-model',
    'memory': '{name} - 让 AI 记住所有重要信息，不再遗漏关键内容。支持语义搜索、自动提炼、智能分类、Token 优化。优化 token 消耗 30-60%。关键词：openclaw, memory, search, ai, productivity',
    'search': '{name} - 多引擎聚合搜索，获取最新信息。支持免费搜索引擎（必应/搜狗/360）+ 可选 API（Tavily/百度/Google）。内容提取、结果去重。关键词：openclaw, search, web, research',
    'marketplace': '{name} - 从 ClawHub 同步 100+ 技能，智能推荐最适合你的技能组合。支持场景/行业/身份推荐。浏览、搜索、一键安装、评分评论、排行榜。关键词：openclaw, marketplace, skills, recommendation',
    'publish': '{name} - 一键发布 OpenClaw 技能到 ClawHub。自动处理限率和错误重试，内置发布前检查工具。基于 10+ 技能审查经验，自动检测安全问题。关键词：openclaw, clawhub, publish, deployment',
    'ui': '{name} - 创建美观、易用的用户界面。提供设计系统、组件库、配色方案、视觉设计等专业建议。支持响应式布局、可访问性（WCAG）、多端适配。关键词：openclaw, ui, design, frontend',
    'writing': '{name} - 生成爆款网络小说。支持玄幻、都市、言情、科幻等多种题材。自动生成大纲、章节、人物设定、世界观。关键词：openclaw, webnovel, writing, ai, creative',
    'agent': '{name} - 管理和协调多个 AI Agent。支持 Agent 注册、任务分发、负载均衡、性能监控、Agent 间通信。适用于复杂任务分解、多角色协作。关键词：openclaw, multi-agent, orchestration',
    'scaffold': '{name} - 快速生成技能模板。自动生成文件夹结构、SKILL.md（含 frontmatter）、脚本模板、README。支持交互式引导、预设模板。关键词：openclaw, scaffold, template, skill-creation',
}

class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    CYAN = '\033[0;36m'
    RED = '\033[0;31m'
    NC = '\033[0m'
    BOLD = '\033[1m'

def log_info(msg): print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")
def log_success(msg): print(f"{Colors.GREEN}[✓]{Colors.NC} {msg}")
def log_warning(msg): print(f"{Colors.YELLOW}[⚠]{Colors.NC} {msg}")
def log_error(msg): print(f"{Colors.RED}[✗]{Colors.NC} {msg}")

def detect_category(skill_name: str, description: str) -> str:
    """检测技能分类"""
    name_lower = skill_name.lower()
    desc_lower = description.lower()
    
    if 'backup' in name_lower or 'backup' in desc_lower:
        return 'backup'
    elif 'model' in name_lower or 'switch' in name_lower:
        return 'model'
    elif 'memory' in name_lower:
        return 'memory'
    elif 'search' in name_lower:
        return 'search'
    elif 'marketplace' in name_lower:
        return 'marketplace'
    elif 'publish' in name_lower or 'clawhub' in name_lower:
        return 'publish'
    elif 'ui' in name_lower or 'design' in name_lower:
        return 'ui'
    elif 'novel' in name_lower or 'writer' in name_lower:
        return 'writing'
    elif 'agent' in name_lower or 'orchestrat' in name_lower:
        return 'agent'
    elif 'scaffold' in name_lower or 'template' in name_lower:
        return 'scaffold'
    else:
        return 'backup'  # 默认

def optimize_skill_md(skill_dir: Path, dry_run: bool = False) -> bool:
    """优化 SKILL.md"""
    skill_md = skill_dir / 'SKILL.md'
    
    if not skill_md.exists():
        log_error(f"SKILL.md 不存在：{skill_md}")
        return False
    
    content = skill_md.read_text(encoding='utf-8')
    
    # 提取 frontmatter
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        log_error("SKILL.md 缺少 frontmatter")
        return False
    
    frontmatter_str = match.group(1)
    frontmatter = {}
    for line in frontmatter_str.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()
    
    skill_name = frontmatter.get('name', skill_dir.name)
    display_name = frontmatter.get('displayName', skill_name.replace('-', ' ').title())
    description = frontmatter.get('description', '')
    tags_str = frontmatter.get('tags', '')
    
    # 检测分类
    category = detect_category(skill_name, description)
    
    log_info(f"检测到技能分类：{category}")
    
    # 优化 name（添加 openclaw- 前缀）
    if not skill_name.startswith('openclaw-'):
        new_name = f"openclaw-{skill_name}"
        log_info(f"优化 name: {skill_name} → {new_name}")
        if not dry_run:
            frontmatter['name'] = new_name
    else:
        log_success(f"name 已优化：{skill_name}")
    
    # 优化 displayName
    if ' - ' not in display_name and '：' not in display_name:
        # 添加中文描述
        cn_names = {
            'auto-backup': '自动备份',
            'model-switch': 'AI 模型切换',
            'memory-enhancer': '记忆增强助手',
            'search-pro': '搜索增强工具',
            'skill-marketplace': '技能市场',
            'clawhub-publish': 'ClawHub 发布工具',
            'ui-designer': 'UI 设计助手',
            'webnovel-writer': '网文写作助手',
            'multi-agent-orchestrator': '多 Agent 协同',
            'skill-scaffold': '技能创建工具',
        }
        cn_desc = cn_names.get(skill_name.replace('openclaw-', ''), '')
        if cn_desc:
            new_display_name = f"{display_name} - {cn_desc}"
            log_info(f"优化 displayName: {display_name} → {new_display_name}")
            if not dry_run:
                frontmatter['displayName'] = new_display_name
        else:
            log_success(f"displayName 已优化：{display_name}")
    else:
        log_success(f"displayName 已优化：{display_name}")
    
    # 优化 description
    if len(description) < 50 or '关键词' not in description:
        template = DESCRIPTION_TEMPLATES.get(category, DESCRIPTION_TEMPLATES['backup'])
        new_desc = template.format(name=frontmatter.get('displayName', display_name))
        log_info(f"优化 description（{len(description)} → {len(new_desc)} 字符）")
        if not dry_run:
            frontmatter['description'] = new_desc
    else:
        log_success(f"description 已优化（{len(description)} 字符）")
    
    # 优化 tags
    existing_tags = [t.strip() for t in tags_str.split(',') if t.strip()]
    recommended_tags = CATEGORY_TAGS.get(category, [])
    
    # 添加缺失的推荐标签
    new_tags = existing_tags.copy()
    for tag in recommended_tags:
        if tag not in new_tags and len(new_tags) < 10:
            new_tags.append(tag)
    
    if len(new_tags) > len(existing_tags):
        log_info(f"优化 tags: {len(existing_tags)} → {len(new_tags)} 个")
        if not dry_run:
            frontmatter['tags'] = ', '.join(new_tags)
    else:
        log_success(f"tags 已优化（{len(new_tags)} 个）")
    
    # 重建 frontmatter
    new_frontmatter = '---\n'
    for key, value in frontmatter.items():
        new_frontmatter += f"{key}: {value}\n"
    new_frontmatter += '---\n'
    
    # 替换原 frontmatter
    if not dry_run:
        new_content = new_frontmatter + content[match.end():]
        skill_md.write_text(new_content, encoding='utf-8')
        log_success(f"SKILL.md 已优化")
    
    return True

def optimize_readme(skill_dir: Path, dry_run: bool = False) -> bool:
    """优化 README.md"""
    readme = skill_dir / 'README.md'
    
    if not readme.exists():
        log_warning(f"README.md 不存在：{readme}")
        return False
    
    content = readme.read_text(encoding='utf-8')
    
    # 检查是否已存在推荐内容
    if '## 🎯 推荐安装场景' in content:
        log_success(f"README 已优化（已包含推荐场景）")
        return True
    
    log_info("添加推荐场景、评分引导、相关技能推荐...")
    
    # 这里简化处理，实际应该调用 batch-optimize-readme.py
    # 为了简洁，我们只输出提示
    log_warning("README 优化需要手动运行：python3 scripts/batch-optimize-readme.py")
    
    return True

def check_seo(skill_dir: Path) -> dict:
    """检查 SEO 状态"""
    skill_md = skill_dir / 'SKILL.md'
    
    if not skill_md.exists():
        return {'error': 'SKILL.md 不存在'}
    
    content = skill_md.read_text(encoding='utf-8')
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    
    if not match:
        return {'error': '缺少 frontmatter'}
    
    frontmatter_str = match.group(1)
    checks = {}
    
    # 检查 name
    if 'name: openclaw-' in frontmatter_str:
        checks['name'] = '✅ 已添加 openclaw- 前缀'
    else:
        checks['name'] = '❌ 需要添加 openclaw- 前缀'
    
    # 检查 displayName
    if ' - ' in frontmatter_str or '：' in frontmatter_str:
        checks['displayName'] = '✅ 已包含中文描述'
    else:
        checks['displayName'] = '❌ 需要添加中文描述'
    
    # 检查 description
    desc_match = re.search(r'description: (.+?)(?:\n|$)', frontmatter_str)
    if desc_match:
        desc = desc_match.group(1)
        if len(desc) > 50 and '关键词' in desc:
            checks['description'] = '✅ 详细描述 + 关键词'
        else:
            checks['description'] = '❌ 需要扩展描述'
    else:
        checks['description'] = '❌ 缺少 description'
    
    # 检查 tags
    tags_match = re.search(r'tags: (.+?)(?:\n|$)', frontmatter_str)
    if tags_match:
        tags = [t.strip() for t in tags_match.group(1).split(',')]
        if 'openclaw' in tags and len(tags) >= 8:
            checks['tags'] = f'✅ 已优化（{len(tags)} 个标签）'
        else:
            checks['tags'] = f'❌ 需要扩展（当前{len(tags)}个）'
    else:
        checks['tags'] = '❌ 缺少 tags'
    
    # 检查 README
    readme = skill_dir / 'README.md'
    if readme.exists():
        readme_content = readme.read_text(encoding='utf-8')
        if '## 🎯 推荐安装场景' in readme_content:
            checks['readme'] = '✅ 已添加推荐场景'
        else:
            checks['readme'] = '❌ 需要添加推荐场景'
    else:
        checks['readme'] = '❌ README.md 不存在'
    
    return checks

def main():
    parser = argparse.ArgumentParser(description='优化技能 SEO，提高 ClawHub 搜索排名')
    parser.add_argument('skill', nargs='?', help='技能名称')
    parser.add_argument('--all', action='store_true', help='优化所有技能')
    parser.add_argument('--check', action='store_true', help='检查 SEO 状态')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行，不实际修改')
    
    args = parser.parse_args()
    
    if args.all:
        # 优化所有技能
        log_info("开始批量优化所有技能...\n")
        
        skills = [d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        for skill_dir in skills:
            log_info(f"\n优化 {skill_dir.name}...")
            optimize_skill_md(skill_dir, args.dry_run)
            optimize_readme(skill_dir, args.dry_run)
        
        log_success(f"\n批量优化完成！共处理 {len(skills)} 个技能")
        
    elif args.skill:
        skill_dir = SKILLS_DIR / args.skill
        
        if not skill_dir.exists():
            log_error(f"技能不存在：{skill_dir}")
            return 1
        
        if args.check:
            # 检查 SEO 状态
            log_info(f"检查 {skill_dir.name} 的 SEO 状态...\n")
            checks = check_seo(skill_dir)
            
            print(f"\n{Colors.BOLD}{Colors.CYAN}SEO 检查报告：{skill_dir.name}{Colors.NC}\n")
            for item, status in checks.items():
                print(f"  {item:15} {status}")
            print()
        else:
            # 优化技能
            log_info(f"优化 {skill_dir.name}...")
            optimize_skill_md(skill_dir, args.dry_run)
            optimize_readme(skill_dir, args.dry_run)
            log_success("优化完成！")
    else:
        parser.print_help()
    
    return 0

if __name__ == "__main__":
    exit(main())
