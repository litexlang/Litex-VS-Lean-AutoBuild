#!/bin/bash

# LeanGeo 自动构建实验 - 一键运行脚本
# 支持运行Definition和Theorem两个实验

set -e  # 遇到错误立即退出

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印使用说明
print_usage() {
    cat << EOF
使用方法: $0 [选项]

选项:
    --test         测试模式（每个实验只运行3个任务）
    --def-only     只运行Definition实验
    --thm-only     只运行Theorem实验
    --help         显示此帮助信息

示例:
    $0                    # 完整运行（所有任务）
    $0 --test            # 测试模式
    $0 --def-only        # 只运行Definition
    $0 --thm-only        # 只运行Theorem
EOF
}

# 解析命令行参数
TEST_MODE=0
DEF_ONLY=0
THM_ONLY=0

for arg in "$@"; do
    case $arg in
        --test)
            TEST_MODE=1
            shift
            ;;
        --def-only)
            DEF_ONLY=1
            shift
            ;;
        --thm-only)
            THM_ONLY=1
            shift
            ;;
        --help)
            print_usage
            exit 0
            ;;
        *)
            print_error "未知参数: $arg"
            print_usage
            exit 1
            ;;
    esac
done

# 检查Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 未安装"
    exit 1
fi

# 检查Lean
if ! command -v lean &> /dev/null; then
    print_error "Lean 未安装，请先运行: curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh"
    exit 1
fi

# 检查API配置
API_CONFIG="$PROJECT_ROOT/config/api_config.json"
if [ ! -f "$API_CONFIG" ]; then
    print_error "API配置文件不存在: $API_CONFIG"
    print_info "请运行: cp config/api_config.example.json config/api_config.json"
    exit 1
fi

# 检查种子库
SEED_FILE="$PROJECT_ROOT/../LeanGeo/LeanGeoCore/theorem_library_seed.lean"
if [ ! -f "$SEED_FILE" ]; then
    print_error "种子库文件不存在: $SEED_FILE"
    exit 1
fi

# 打印配置信息
print_info "========================================="
print_info "LeanGeo 自动构建实验系统"
print_info "========================================="
print_info "项目目录: $PROJECT_ROOT"
print_info "Python版本: $(python3 --version)"
print_info "Lean版本: $(lean --version | head -1)"

if [ $TEST_MODE -eq 1 ]; then
    print_warning "测试模式: 每个实验只运行3个任务"
    TASK_LIMIT=3
else
    print_info "完整模式: 运行所有任务"
    TASK_LIMIT=""
fi

# 记录开始时间
START_TIME=$(date +%s)

# 运行Definition实验
if [ $THM_ONLY -eq 0 ]; then
    print_info ""
    print_info "========================================="
    print_info "1. 运行 Definition 实验"
    print_info "========================================="
    
    if [ $TEST_MODE -eq 1 ]; then
        python3 "$SCRIPT_DIR/run_lean_definitions.py" $TASK_LIMIT
    else
        python3 "$SCRIPT_DIR/run_lean_definitions.py"
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Definition 实验完成"
    else
        print_error "Definition 实验失败"
        exit 1
    fi
fi

# 运行Theorem实验
if [ $DEF_ONLY -eq 0 ]; then
    print_info ""
    print_info "========================================="
    print_info "2. 运行 Theorem 实验"
    print_info "========================================="
    
    if [ $TEST_MODE -eq 1 ]; then
        python3 "$SCRIPT_DIR/run_lean_theorems.py" $TASK_LIMIT
    else
        python3 "$SCRIPT_DIR/run_lean_theorems.py"
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Theorem 实验完成"
    else
        print_error "Theorem 实验失败"
        exit 1
    fi
fi

# 计算总耗时
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
ELAPSED_MIN=$((ELAPSED / 60))
ELAPSED_SEC=$((ELAPSED % 60))

# 打印总结
print_info ""
print_info "========================================="
print_success "所有实验完成！"
print_info "========================================="
print_info "总耗时: ${ELAPSED_MIN}分${ELAPSED_SEC}秒"
print_info ""
print_info "输出目录:"
if [ $THM_ONLY -eq 0 ]; then
    LATEST_DEF=$(ls -t "$PROJECT_ROOT/lean_auto_validated_250tasks/definitions_only" 2>/dev/null | head -1)
    if [ -n "$LATEST_DEF" ]; then
        print_info "  Definition: lean_auto_validated_250tasks/definitions_only/$LATEST_DEF"
    fi
fi
if [ $DEF_ONLY -eq 0 ]; then
    LATEST_THM=$(ls -t "$PROJECT_ROOT/lean_auto_validated_250tasks/theorems_only" 2>/dev/null | head -1)
    if [ -n "$LATEST_THM" ]; then
        print_info "  Theorem: lean_auto_validated_250tasks/theorems_only/$LATEST_THM"
    fi
fi
