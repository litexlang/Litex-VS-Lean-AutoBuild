#!/bin/bash
# LitexGeo 自动构建实验 - 一键运行脚本
#
# 使用方法:
#   ./run_all_experiments.sh              # 运行所有任务
#   ./run_all_experiments.sh --test       # 测试模式（每个实验只运行3个任务）
#   ./run_all_experiments.sh --def-only   # 只运行definition实验
#   ./run_all_experiments.sh --thm-only   # 只运行theorem实验

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 切换到项目根目录（scripts的父目录）
cd "$SCRIPT_DIR/.."

# 解析参数
TEST_MODE=false
DEF_ONLY=false
THM_ONLY=false
TASK_LIMIT=""

for arg in "$@"; do
    case $arg in
        --test)
            TEST_MODE=true
            TASK_LIMIT="3"
            shift
            ;;
        --def-only)
            DEF_ONLY=true
            shift
            ;;
        --thm-only)
            THM_ONLY=true
            shift
            ;;
        *)
            echo -e "${RED}未知参数: $arg${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}LitexGeo 自动构建实验${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

if [ "$TEST_MODE" = true ]; then
    echo -e "${YELLOW}⚠️  测试模式：每个实验只运行前3个任务${NC}"
    echo ""
fi

# 检查Python环境
echo -e "${GREEN}[1/5] 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi
echo -e "   ✅ Python版本: $(python3 --version)"

# 检查依赖库
echo -e "${GREEN}[2/5] 检查依赖库...${NC}"
if ! python3 -c "import openai" 2>/dev/null; then
    echo -e "${RED}❌ openai库未安装${NC}"
    echo -e "${YELLOW}请运行: pip3 install openai${NC}"
    exit 1
fi
echo -e "   ✅ openai库已安装"

# 检查Litex编译器
echo -e "${GREEN}[3/5] 检查Litex编译器...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LITEX_BIN="$PROJECT_ROOT/../LitexGeo/golitex/litex_0.9.116-beta_darwin_arm64/litex"
if [ ! -f "$LITEX_BIN" ]; then
    echo -e "${RED}❌ Litex编译器未找到: $LITEX_BIN${NC}"
    exit 1
fi
echo -e "   ✅ Litex编译器已找到"

# 设置环境变量
export LITEX_BIN="$LITEX_BIN"

# 检查种子文件
echo -e "${GREEN}[4/5] 检查种子文件...${NC}"

# Definition种子
DEF_SEED="database/definition_library_seed.lit"
if [ ! -f "$DEF_SEED" ]; then
    echo -e "${RED}❌ Definition种子文件不存在: $DEF_SEED${NC}"
    exit 1
fi
echo -e "   ✅ Definition种子: database/definition_library_seed.lit"

# Theorem种子
THM_SEED="database/theorem_library_seed.lit"
if [ ! -f "$THM_SEED" ]; then
    echo -e "${RED}❌ Theorem种子文件不存在: $THM_SEED${NC}"
    exit 1
fi
echo -e "   ✅ Theorem种子: database/theorem_library_seed.lit"

echo ""
echo -e "${GREEN}[5/5] 开始运行实验...${NC}"
echo ""

# 运行Definition实验
if [ "$THM_ONLY" = false ]; then
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}运行 Definition 实验${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo -e "种子库: database/definition_library_seed.lit"
    echo -e "任务数: 39个定义任务"
    if [ "$TEST_MODE" = true ]; then
        echo -e "测试模式: 只运行前3个任务"
    fi
    echo ""

    START_TIME=$(date +%s)

    if [ "$TEST_MODE" = true ]; then
        python3 scripts/run_litex_definitions.py 3
    else
        python3 scripts/run_litex_definitions.py
    fi

    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    echo ""
    echo -e "${GREEN}✅ Definition实验完成 (耗时: ${DURATION}秒)${NC}"
    echo ""
fi

# 运行Theorem实验
if [ "$DEF_ONLY" = false ]; then

    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}运行 Theorem 实验${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo -e "种子库: database/theorem_library_seed.lit"
    echo -e "任务数: 165个定理任务"
    if [ "$TEST_MODE" = true ]; then
        echo -e "测试模式: 只运行前3个任务"
    fi
    echo ""

    START_TIME=$(date +%s)

    if [ "$TEST_MODE" = true ]; then
        python3 scripts/run_litex_theorems.py 3
    else
        python3 scripts/run_litex_theorems.py
    fi

    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    echo ""
    echo -e "${GREEN}✅ Theorem实验完成 (耗时: ${DURATION}秒)${NC}"
    echo ""
fi

echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}✅ 所有实验完成！${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "输出目录:"
echo -e "  - Definition: litex_auto_validated_250tasks/run_*/"
echo -e "  - Theorem: litex_auto_validated_250tasks/theorems_only/run_*/"
echo ""
echo -e "查看结果:"
echo -e "  ls -lht litex_auto_validated_250tasks/*/run_*/"
