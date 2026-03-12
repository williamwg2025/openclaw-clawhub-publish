#!/usr/bin/env python3
"""
ClawHub Publish Pre-Check
发布前自动检查工具，确保技能符合 ClawHub 审查要求

检查项：
1. 必需文件检查 (SKILL.md, scripts/, README.md)
2. SKILL.md frontmatter 验证
3. 脚本文件完整性
4. 配置与代码一致性
5. 路径安全检查
6. 外部依赖检查
7. 安全说明检查
"""

import json
import os
import re
import sys
from pathlib import Path

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

class PreCheck:
    def __init__(self, skill_dir: Path):
        self.skill_dir = skill_dir
        self.errors = 0
        self.warnings = 0
        self.passed = 0
        
    def check_required_files(self) -> bool:
        """检查必需文件"""
        log_info("检查必需文件...")
        
        files = {
            'SKILL.md': '技能元数据和文档',
            'README.md': '使用说明文档',
        }
        
        for file, desc in files.items():
            path = self.skill_dir / file
            if path.exists():
                log_success(f"{file} 存在 - {desc}")
                self.passed += 1
            else:
                log_error(f"{file} 缺失 - {desc}")
                self.errors += 1
        
        # 检查 scripts 目录
        scripts_dir = self.skill_dir / 'scripts'
        if scripts_dir.exists():
            log_success("scripts/ 目录存在")
            self.passed += 1
            
            # 检查是否有脚本文件
            py_files = list(scripts_dir.glob('*.py'))
            sh_files = list(scripts_dir.glob('*.sh'))
            if py_files or sh_files:
                log_success(f"scripts/ 目录中有 {len(py_files) + len(sh_files)} 个脚本文件")
                self.passed += 1
            else:
                log_warning("scripts/ 目录中没有 .py 或 .sh 文件")
                self.warnings += 1
        else:
            log_warning("scripts/ 目录不存在（如果是纯配置技能可忽略）")
            self.warnings += 1
        
        # 检查 config 目录（可选）
        config_dir = self.skill_dir / 'config'
        if config_dir.exists():
            log_success("config/ 目录存在")
            self.passed += 1
        
        return self.errors == 0
    
    def check_skill_frontmatter(self) -> bool:
        """检查 SKILL.md frontmatter"""
        log_info("检查 SKILL.md frontmatter...")
        
        skill_md = self.skill_dir / 'SKILL.md'
        if not skill_md.exists():
            return False
        
        content = skill_md.read_text(encoding='utf-8')
        
        # 提取 frontmatter
        match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if not match:
            log_error("SKILL.md 缺少 frontmatter (--- 包裹的元数据)")
            self.errors += 1
            return False
        
        frontmatter = match.group(1)
        
        # 检查必需字段
        required_fields = {
            'name': '技能名称（kebab-case）',
            'displayName': '显示名称',
            'version': '版本号（semver 格式）',
            'description': '技能描述',
            'license': '许可证',
            'acceptLicenseTerms': '许可证确认（必须为 true）',
        }
        
        for field, desc in required_fields.items():
            pattern = rf'^{field}:\s*(.+)$'
            match = re.search(pattern, frontmatter, re.MULTILINE)
            if match:
                value = match.group(1).strip()
                
                # 特殊验证
                if field == 'version':
                    if not re.match(r'^\d+\.\d+\.\d+', value):
                        log_error(f"version: {value} 不是有效的 semver 格式")
                        self.errors += 1
                        continue
                
                if field == 'acceptLicenseTerms':
                    if value.lower() != 'true':
                        log_error(f"acceptLicenseTerms: {value} 必须为 true")
                        self.errors += 1
                        continue
                
                log_success(f"{field}: {value} - {desc}")
                self.passed += 1
            else:
                log_error(f"{field} 缺失 - {desc}")
                self.errors += 1
        
        # 检查 tags（推荐）
        if 'tags:' in frontmatter:
            log_success("tags: 已设置（推荐字段）")
            self.passed += 1
        else:
            log_warning("tags: 未设置（推荐添加 3-5 个标签）")
            self.warnings += 1
        
        return self.errors == 0
    
    def check_script_mentions(self) -> bool:
        """检查文档中提到的脚本是否都存在"""
        log_info("检查文档中提到的脚本...")
        
        skill_md = self.skill_dir / 'SKILL.md'
        readme_md = self.skill_dir / 'README.md'
        
        mentioned_scripts = set()
        
        # 从文档中提取提到的脚本
        for doc in [skill_md, readme_md]:
            if not doc.exists():
                continue
            
            content = doc.read_text(encoding='utf-8')
            
            # 查找 python3 scripts/xxx.py 模式
            matches = re.findall(r'scripts/(\w+\.py)', content)
            mentioned_scripts.update(matches)
            
            # 查找 ./xxx.sh 或 xxx.sh 模式（根目录的 shell 脚本）
            matches = re.findall(r'(?:\.\/)?(\w+\.sh)', content)
            mentioned_scripts.update(matches)
        
        if not mentioned_scripts:
            log_info("文档中未提到具体脚本文件")
            return True
        
        # 检查提到的脚本是否存在（scripts/ 目录或根目录）
        scripts_dir = self.skill_dir / 'scripts'
        missing_scripts = []
        
        for script in mentioned_scripts:
            # 检查 scripts/ 目录
            if (scripts_dir / script).exists():
                log_success(f"scripts/{script} 存在")
                self.passed += 1
            # 检查根目录
            elif (self.skill_dir / script).exists():
                log_success(f"{script} 存在（根目录）")
                self.passed += 1
            else:
                log_error(f"{script} 缺失（文档中提到但文件不存在）")
                self.errors += 1
                missing_scripts.append(script)
        
        if missing_scripts:
            log_warning(f"缺失的脚本：{', '.join(missing_scripts)}")
        
        return len(missing_scripts) == 0
    
    def check_external_dependencies(self) -> bool:
        """检查外部依赖（git clone 等）"""
        log_info("检查外部依赖...")
        
        skill_md = self.skill_dir / 'SKILL.md'
        readme_md = self.skill_dir / 'README.md'
        
        has_external = False
        
        for doc in [skill_md, readme_md]:
            if not doc.exists():
                continue
            
            content = doc.read_text(encoding='utf-8')
            
            # 检查 git clone 指令
            if 'git clone' in content:
                # 提取 clone 的 URL
                matches = re.findall(r'git clone (https?://\S+)', content)
                for url in matches:
                    # 如果是自己的 GitHub 仓库，警告但不报错
                    if 'github.com' in url:
                        log_warning(f"发现 git clone 指令：{url}")
                        log_warning("  建议：技能应包含所有代码，无需外部克隆")
                        self.warnings += 1
                        has_external = True
        
        if not has_external:
            log_success("无外部 git clone 依赖")
            self.passed += 1
        
        return not has_external
    
    def check_path_security(self) -> bool:
        """检查路径安全性（不使用硬编码的 /root）"""
        log_info("检查路径安全性...")
        
        has_root_path = False
        
        # 检查所有 Python 脚本和配置文件
        for pattern in ['**/*.py', '**/*.json', '**/*.md']:
            for file in self.skill_dir.glob(pattern):
                if file.name.startswith('.'):
                    continue
                
                try:
                    content = file.read_text(encoding='utf-8')
                    if '/root/' in content:
                        log_warning(f"{file.relative_to(self.skill_dir)}: 使用硬编码的 /root 路径")
                        has_root_path = True
                except:
                    pass
        
        if has_root_path:
            log_warning("建议：使用 ~/ 或 Path.home() 替代 /root/")
            self.warnings += 1
        else:
            log_success("路径使用规范（无 /root 硬编码）")
            self.passed += 1
        
        return True
    
    def check_config_consistency(self) -> bool:
        """检查配置文件与代码一致性"""
        log_info("检查配置与代码一致性...")
        
        config_dir = self.skill_dir / 'config'
        if not config_dir.exists():
            log_info("无 config/ 目录，跳过检查")
            return True
        
        # 读取所有配置文件
        config_features = {}
        for config_file in config_dir.glob('*.json'):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    config_features[config_file.name] = config
            except Exception as e:
                log_warning(f"无法读取 {config_file.name}: {e}")
        
        # 检查是否有配置项在代码中未使用
        # 简化检查：只检查明显的功能声明
        for config_name, config in config_features.items():
            # 检查 notify 相关配置
            if 'notifyOnBackup' in config or 'notifyChannel' in config:
                # 检查是否有对应的通知代码
                has_notify_code = False
                for py_file in (self.skill_dir / 'scripts').glob('*.py'):
                    content = py_file.read_text(encoding='utf-8')
                    if 'notify' in content.lower() or 'send_message' in content.lower():
                        has_notify_code = True
                        break
                
                if not has_notify_code:
                    log_warning(f"{config_name}: 声明了通知功能但代码中未实现")
                    log_warning("  建议：移除配置或实现对应功能")
                    self.warnings += 1
        
        log_success("配置与代码基本一致")
        self.passed += 1
        return True
    
    def check_security_notes(self) -> bool:
        """检查安全说明"""
        log_info("检查安全说明...")
        
        skill_md = self.skill_dir / 'SKILL.md'
        if not skill_md.exists():
            return False
        
        content = skill_md.read_text(encoding='utf-8')
        
        # 检查关键安全说明
        security_keywords = {
            '加密': ['加密', 'encrypt', 'encryption'],
            '权限': ['权限', 'permission', 'access'],
            '存储': ['存储', 'storage', 'backup'],
            '网络': ['网络', 'network', '联网'],
        }
        
        found_keywords = []
        missing_keywords = []
        
        for category, keywords in security_keywords.items():
            found = any(kw in content.lower() for kw in keywords)
            if found:
                found_keywords.append(category)
            else:
                missing_keywords.append(category)
        
        if found_keywords:
            log_success(f"包含安全说明：{', '.join(found_keywords)}")
            self.passed += 1
        
        if missing_keywords:
            log_warning(f"建议添加安全说明：{', '.join(missing_keywords)}")
            self.warnings += 1
        
        return True
    
    def run_all_checks(self) -> bool:
        """运行所有检查"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.NC}")
        print(f"{Colors.BOLD}{Colors.CYAN}🔍 ClawHub 发布前检查{Colors.NC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.NC}")
        print(f"\n检查目录：{self.skill_dir}\n")
        
        self.check_required_files()
        print()
        
        self.check_skill_frontmatter()
        print()
        
        self.check_script_mentions()
        print()
        
        self.check_external_dependencies()
        print()
        
        self.check_path_security()
        print()
        
        self.check_config_consistency()
        print()
        
        self.check_security_notes()
        print()
        
        # 打印摘要
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.NC}")
        print(f"{Colors.BOLD}检查摘要:{Colors.NC}")
        print(f"  {Colors.GREEN}通过：{self.passed}{Colors.NC}")
        print(f"  {Colors.YELLOW}警告：{self.warnings}{Colors.NC}")
        print(f"  {Colors.RED}错误：{self.errors}{Colors.NC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.NC}\n")
        
        if self.errors > 0:
            log_error(f"发现 {self.errors} 个错误，请修复后再发布")
            return False
        elif self.warnings > 0:
            log_warning(f"发现 {self.warnings} 个警告，建议修复后发布")
            return True
        else:
            log_success("所有检查通过，可以发布！")
            return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='ClawHub 发布前检查工具')
    parser.add_argument('skill_dir', nargs='?', help='技能目录')
    parser.add_argument('--strict', action='store_true', help='严格模式（警告也视为错误）')
    
    args = parser.parse_args()
    
    if not args.skill_dir:
        args.skill_dir = '.'
    
    skill_dir = Path(args.skill_dir).resolve()
    
    if not skill_dir.exists():
        log_error(f"目录不存在：{skill_dir}")
        sys.exit(1)
    
    checker = PreCheck(skill_dir)
    success = checker.run_all_checks()
    
    if args.strict and checker.warnings > 0:
        success = False
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
