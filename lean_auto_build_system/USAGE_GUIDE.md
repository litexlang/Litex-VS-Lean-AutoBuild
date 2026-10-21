# LeanGeo 自动构建实验系统 - 使用指南

## 📋 目录

1. [环境准备](#环境准备)
2. [首次配置](#首次配置)
3. [运行实验](#运行实验)
4. [查看结果](#查看结果)
5. [常见问题](#常见问题)

---

## 环境准备

### 1. 安装Lean 4和Lake

**重要**：Lean 4编译器和Lake构建工具未包含在git仓库中，需要先安装。

#### macOS/Linux安装

```bash
# 安装elan（Lean版本管理器）
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# 重启终端或刷新环境
source ~/.zshrc  # 如果使用zsh
# 或
source ~/.bashrc  # 如果使用bash

# 验证安装
elan --version    # 应该显示版本号
lean --version    # 应该显示 Lean (version 4.x.x, ...)
lake --version    # 应该显示版本号
```

#### Windows安装

1. 下载并安装：https://github.com/leanprover/elan/releases
2. 或参考官方文档：https://leanprover-community.github.io/install/windows.html

#### 安装位置

- **Lean编译器**：`~/.elan/toolchains/leanprover--lean4---v4.35.0/`
- **Mathlib库**：项目的 `LeanGeo/.lake/packages/` 目录
- **全局工具**：所有Lean项目共用同一个编译器

### 2. 构建Lean项目（下载Mathlib）

```bash
# 进入LeanGeo目录
cd /path/to/auto-build/LeanGeo

# 构建项目（首次运行会下载Mathlib，约300MB）
lake build
```

**注意**：
- 首次运行需要5-10分钟下载Mathlib
- 需要稳定的网络连接
- 下载完成后会自动编译，总共约10-15分钟

---

## 首次配置

### 1. 配置API密钥

**必须在首次运行前完成！**

```bash
# 进入项目目录
cd /path/to/auto-build/lean_auto_build_system

# 复制配置模板
cp config/api_config.example.json config/api_config.json

# 编辑配置文件
vim config/api_config.json
# 或使用其他编辑器：code config/api_config.json
```

配置文件内容：
```json
{
  "api_key": "sk-你的实际密钥",
  "base_url": "https://api.deepseek.com",
  "model": "deepseek-chat"
}
```

**安全提示**：
- ✅ `api_config.json` 已被 `.gitignore` 忽略
- ✅ 不会被提交到git仓库
- ⚠️ 不要将此文件分享给他人

详细配置说明：[config/README.md](config/README.md)

---

## 运行实验

### 方式1：一键运行脚本（推荐）

#### 测试模式（推荐首次运行）
```bash
bash scripts/run_all_experiments.sh --test
```
- 每个实验只运行3个任务
- 预计耗时：20-30分钟
- 适合验证系统是否正常工作

#### 完整运行
```bash
bash scripts/run_all_experiments.sh
```
- Definition实验：39个任务
- Theorem实验：165个任务
- 预计耗时：6-10小时

#### 单独运行
```bash
# 只运行Definition实验
bash scripts/run_all_experiments.sh --def-only

# 只运行Theorem实验
bash scripts/run_all_experiments.sh --thm-only
```

### 方式2：直接运行Python脚本

#### 测试模式
```bash
# Definition实验（5个任务）
python3 scripts/run_lean_definitions.py 5

# Theorem实验（5个任务）
python3 scripts/run_lean_theorems.py 5
```

#### 完整运行
```bash
# Definition实验（所有39个任务）
python3 scripts/run_lean_definitions.py

# Theorem实验（所有165个任务）
python3 scripts/run_lean_theorems.py
```

### 方式3：并行运行

Definition和Theorem实验使用独立的种子库，可以并行运行以节省时间：

```bash
# 并行运行测试（5个任务）
python3 scripts/run_lean_definitions.py 5 & python3 scripts/run_lean_theorems.py 5 & wait

# 并行完整运行
python3 scripts/run_lean_definitions.py & python3 scripts/run_lean_theorems.py & wait
```

**优点**：
- ✅ 节省时间，两个实验同时进行
- ✅ 独立种子库，互不影响
- ✅ 自动等待两个实验都完成

**注意**：并行运行时，控制台日志会交织在一起。如需查看单独的日志，请查看输出目录中的 `experiment.log` 文件。

---

## 查看结果

### 输出目录结构

```
lean_auto_validated_250tasks/
├── definitions_only/
│   └── run_20261021_230000/    # 时间戳目录
│       ├── experiment.log      # 完整日志
│       ├── library_final.lean  # 最终生成的库
│       ├── state.json          # 实验状态
│       └── attempts.json       # 所有尝试记录
└── theorems_only/
    └── run_20261021_230000/
        ├── experiment.log
        ├── library_final.lean
        ├── state.json
        ├── attempts.json
        └── axioms_debt.md      # Axiom债务清单
```

### 查看命令

```bash
# 列出所有运行
ls -lt lean_auto_validated_250tasks/definitions_only/
ls -lt lean_auto_validated_250tasks/theorems_only/

# 查看最新的Definition实验日志
tail -f lean_auto_validated_250tasks/definitions_only/run_*/experiment.log

# 查看最新的Theorem实验日志
tail -f lean_auto_validated_250tasks/theorems_only/run_*/experiment.log

# 查看生成的库
cat lean_auto_validated_250tasks/definitions_only/run_*/library_final.lean
cat lean_auto_validated_250tasks/theorems_only/run_*/library_final.lean
```

### 输出文件说明

| 文件 | 说明 |
|------|------|
| `experiment.log` | 完整的控制台日志 |
| `experiment_log.md` | Markdown格式日志 |
| `state.json` | 实验状态（已完成任务等） |
| `library_final.lean` | 最终生成的完整库 |
| `attempts.json` | 所有尝试的详细记录（包含token统计） |
| `axioms_debt.md` | Axiom债务清单（仅Theorem实验） |

---

## 常见问题

### Q1: 提示 "lean: command not found"

**原因**：未安装Lean或环境变量未配置

**解决**：
```bash
# 安装elan和Lean
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# 刷新环境
source ~/.zshrc  # 或 source ~/.bashrc

# 验证安装
lean --version
```

### Q2: 提示 "API配置文件不存在"

**原因**：未创建 `config/api_config.json`

**解决**：
```bash
cp config/api_config.example.json config/api_config.json
# 然后编辑文件填入API密钥
```

### Q3: 提示 "请配置API密钥"

**原因**：`api_config.json` 中的 `api_key` 仍然是 `"your-api-key-here"`

**解决**：编辑 `config/api_config.json`，填入真实的API密钥

### Q4: 提示 "Unknown identifier `dot`"

**原因**：种子库未正确加载

**检查**：
```bash
# 确认种子库存在
ls -la ../LeanGeo/LeanGeoCore/theorem_library_seed.lean

# 确认种子库内容正确（应该包含vec、dot、det定义）
head -20 ../LeanGeo/LeanGeoCore/theorem_library_seed.lean
```

### Q5: Mathlib下载失败或超时

**原因**：网络问题或GitHub连接不稳定

**解决**：
```bash
cd ../LeanGeo

# 清理缓存重试
rm -rf .lake
lake build

# 或使用国内镜像（如果可用）
# 具体配置请参考Lean社区文档
```

### Q6: 想换用OpenAI API

**解决**：编辑 `config/api_config.json`：
```json
{
  "api_key": "sk-你的OpenAI密钥",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4"
}
```

### Q7: 实验运行中断了怎么办？

**说明**：每次运行都会创建新的时间戳目录，可以直接重新运行，不会覆盖之前的结果。

实验会自动跳过种子库中已有的定义，继续处理后续任务。

**建议**：
- 如果是网络问题导致中断，直接重新运行即可
- 如果是代码错误，检查日志文件了解失败原因
- 每次运行的完整日志都保存在 `experiment.log` 中

### Q8: 如何查看token使用统计？

**解决**：查看 `attempts.json` 文件：
```bash
# 需要安装jq工具
cat lean_auto_validated_250tasks/definitions_only/run_*/attempts.json | jq '.[] | {task_id, total_tokens}'
```

### Q9: Lean编译很慢怎么办？

**说明**：首次构建Mathlib确实需要10-15分钟，这是正常的。

**优化**：
```bash
# 使用多核编译（例如8核）
cd ../LeanGeo
lake build -j8
```

### Q10: 想清理旧的运行结果

**解决**：
```bash
# 只保留最新的Definition运行
cd lean_auto_validated_250tasks/definitions_only
ls -t | tail -n +2 | xargs rm -rf

# 只保留最新的Theorem运行
cd ../theorems_only
ls -t | tail -n +2 | xargs rm -rf
```

**警告**：删除前请确认不需要这些数据！

---

## 🔧 系统工作原理

1. **任务分配**: 从预定义的任务列表中逐个处理
2. **语法指导**: 每次任务都包含完整的Lean 4语法指南
3. **代码生成**: AI根据任务描述和语法指南生成代码
4. **实时验证**: Lean REPL验证生成的代码
5. **错误反馈**: 编译错误自动反馈给AI（最多5次重试）
6. **增量累积**: 验证通过的代码提交到session，供后续任务使用
7. **完整记录**: 所有尝试、错误、token使用等信息都被记录

这个闭环系统能够自动修正错误，持续改进代码质量。

---

## 🎯 快速参考

```bash
# 完整流程（首次运行）
# 1. 安装Lean
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
source ~/.zshrc

# 2. 构建项目
cd /path/to/auto-build/LeanGeo
lake build

# 3. 配置API
cd ../lean_auto_build_system
cp config/api_config.example.json config/api_config.json
vim config/api_config.json  # 填入API密钥

# 4. 测试运行
bash scripts/run_all_experiments.sh --test

# 完整流程（已配置）
bash scripts/run_all_experiments.sh
```

---

## 📚 更多文档

- **系统架构**: [README.md](README.md) - 系统概述和目录结构
- **API配置**: [config/README.md](config/README.md) - 详细配置选项
- **Lean语法**: [prompts/lean_short_guide.md](prompts/lean_short_guide.md) - 完整语法指南
- **示例输出**: [examples/README.md](examples/README.md) - 示例运行结果
- **Lean官方文档**: https://leanprover.github.io/
- **Mathlib文档**: https://leanprover-community.github.io/mathlib4_docs/
