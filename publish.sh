#!/bin/bash
#
# ClawHub Publish Helper
# Usage: ./publish.sh <skill-folder> [--dry-run]
#
# Features:
# - Validates skill structure
# - Checks for required files
# - Handles rate limiting with exponential backoff
# - Logs output to publish-log.md
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/skills/clawhub-publish/publish-log.md"

# Counters
ATTEMPTS=0
MAX_ATTEMPTS=5
BASE_WAIT=300  # 5 minutes in seconds

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Initialize log file
init_log() {
    cat > "$LOG_FILE" << EOF
# ClawHub Publish Log

**Started:** $(date -Iseconds)

---

## Publish Attempts

EOF
}

# Append to log
log_to_file() {
    echo "$1" >> "$LOG_FILE"
}

# Validate skill structure
validate_skill() {
    local skill_dir="$1"
    local errors=0
    
    log_info "验证技能结构：$skill_dir"
    
    # Check if directory exists
    if [ ! -d "$skill_dir" ]; then
        log_error "技能目录不存在：$skill_dir"
        return 1
    fi
    
    # Run comprehensive pre-publish check
    log_info "运行 ClawHub 发布前检查..."
    if [ -f "$SCRIPT_DIR/scripts/pre-publish-check.py" ]; then
        if ! python3 "$SCRIPT_DIR/scripts/pre-publish-check.py" "$skill_dir"; then
            log_error "发布前检查失败，请修复问题后再发布"
            return 1
        fi
    else
        log_warning "pre-publish-check.py 不存在，使用基础验证"
        
        # Check for SKILL.md
        if [ ! -f "$skill_dir/SKILL.md" ]; then
            log_error "缺少必需文件：SKILL.md"
            ((errors++))
        else
            log_success "✓ SKILL.md 存在"
        fi
        
        # Check for scripts directory (if it's a script-based skill)
        if [ -d "$skill_dir/scripts" ]; then
            log_success "✓ scripts/ 目录存在"
            
            # Check for at least one Python or shell script
            if ! ls "$skill_dir/scripts/"*.py "$skill_dir/scripts/"*.sh 1> /dev/null 2>&1; then
                log_warning "scripts/ 目录中没有 .py 或 .sh 文件"
            fi
        fi
        
        # Check for config directory (optional)
        if [ -d "$skill_dir/config" ]; then
            log_success "✓ config/ 目录存在"
        fi
        
        # Check for README.md (recommended)
        if [ -f "$skill_dir/README.md" ]; then
            log_success "✓ README.md 存在"
        else
            log_warning "缺少推荐文件：README.md"
        fi
        
        if [ $errors -gt 0 ]; then
            log_error "验证失败：发现 $errors 个错误"
            return 1
        fi
    fi
    
    log_success "技能结构验证通过"
    return 0
}

# Get skill slug from directory name
get_skill_slug() {
    local skill_dir="$1"
    basename "$skill_dir"
}

# Publish with retry logic
publish_with_retry() {
    local skill_dir="$1"
    local dry_run="$2"
    local slug=$(get_skill_slug "$skill_dir")
    
    while [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
        ((ATTEMPTS++))
        
        log_info "发布尝试 #${ATTEMPTS}/${MAX_ATTEMPTS}"
        log_to_file "### Attempt ${ATTEMPTS} - $(date -Iseconds)"
        
        if [ "$dry_run" == "--dry-run" ]; then
            log_warning "[模拟] 将发布技能：$slug"
            log_to_file "**Dry run** - Would publish: $slug"
            return 0
        fi
        
        # Try to publish
        cd "$WORKSPACE/skills"
        
        if npx clawhub publish "$slug" 2>&1 | tee -a "$LOG_FILE"; then
            log_success "发布成功：$slug"
            log_to_file "**SUCCESS** - Published: $slug at $(date -Iseconds)"
            return 0
        else
            local exit_code=$?
            log_error "发布失败 (退出码：$exit_code)"
            log_to_file "**FAILED** - Exit code: $exit_code"
            
            # Check for rate limit error
            if npx clawhub publish "$slug" 2>&1 | grep -q "Rate limit"; then
                log_warning "检测到限率错误"
                log_to_file "**Rate limit detected**"
                
                if [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; then
                    local wait_time=$((BASE_WAIT * ATTEMPTS))
                    log_info "等待 ${wait_time} 秒后重试..."
                    log_to_file "**Waiting** ${wait_time}s before retry..."
                    sleep $wait_time
                fi
            else
                # Unknown error, don't retry
                log_error "未知错误，不重试"
                log_to_file "**Unknown error** - Not retrying"
                return 1
            fi
        fi
    done
    
    log_error "达到最大重试次数，发布失败"
    log_to_file "**FAILED** - Max attempts reached"
    return 1
}

# Show usage
show_usage() {
    echo "用法：$0 <skill-folder> [--dry-run]"
    echo ""
    echo "参数:"
    echo "  skill-folder  技能目录名称（在 workspace/skills/ 下）"
    echo "  --dry-run     模拟运行，不实际发布"
    echo ""
    echo "示例:"
    echo "  $0 model-switch"
    echo "  $0 auto-backup --dry-run"
    echo ""
    echo "可用技能:"
    ls -1 "$WORKSPACE/skills/" | while read skill; do
        echo "  - $skill"
    done
}

# Main
main() {
    if [ -z "$1" ] || [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
        show_usage
        exit 0
    fi
    
    local skill_name="$1"
    local dry_run="$2"
    local skill_dir="$WORKSPACE/skills/$skill_name"
    
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}              🦞 ClawHub Publish Helper                     ${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
    
    # Initialize log
    init_log
    log_to_file "## Publishing: $skill_name"
    log_to_file "**Dry run:** $dry_run"
    log_to_file ""
    
    # Validate skill
    if ! validate_skill "$skill_dir"; then
        log_error "技能验证失败，请修复后重试"
        log_to_file "**VALIDATION FAILED**"
        exit 1
    fi
    
    log_to_file "**VALIDATION PASSED**"
    echo ""
    
    # Publish with retry
    if publish_with_retry "$skill_dir" "$dry_run"; then
        log_success "发布流程完成"
        log_to_file ""
        log_to_file "**PUBLISH FLOW COMPLETED**"
        echo ""
        echo -e "${GREEN}============================================================${NC}"
        echo -e "${GREEN}  ✅ 发布成功！${NC}"
        echo -e "${GREEN}============================================================${NC}"
        echo ""
        echo "日志文件：$LOG_FILE"
        exit 0
    else
        log_error "发布流程失败"
        log_to_file ""
        log_to_file "**PUBLISH FLOW FAILED**"
        echo ""
        echo -e "${RED}============================================================${NC}"
        echo -e "${RED}  ❌ 发布失败${NC}"
        echo -e "${RED}============================================================${NC}"
        echo ""
        echo "日志文件：$LOG_FILE"
        exit 1
    fi
}

main "$@"
