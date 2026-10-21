# LitexGeo 自动构建实验系统 - 使用指南

## 📋 目录

1. [环境准备](#环境准备)
2. [首次配置](#首次配置)
3. [验证环境](#验证环境)
4. [运行实验](#运行实验)
5. [查看结果](#查看结果)
6. [常见问题](#常见问题)

---

## 环境准备

### 获取Litex编译器

**重要**：本项目使用Litex 0.9.116-beta编译器。由于编译器体积较大，未包含在git仓库中，需要单独获取。

#### 获取方式

**方式1：从Litex官方仓库获取**
```bash
# 访问Litex官方仓库获取最新版本
# https://github.com/litexlang/litex/releases
# 下载适合你平台的版本（darwin_arm64/darwin_amd64/linux/windows）
```

**方式2：验证项目内版本（如果已下载）**
```bash
# 检查编译器是否存在
ls -lh /path/to/auto-build/LitexGeo/golitex/litex_0.9.116-beta_darwin_arm64/litex

# 测试编译器
/path/to/auto-build/LitexGeo/golitex/litex_0.9.116-beta_darwin_arm64/litex --version
# 应该显示：Litex 0.9.116-beta
```

**编译器位置**：
- 本项目使用：`../LitexGeo/golitex/litex_0.9.116-beta_darwin_arm64/litex`
- macOS M1/M2: `darwin_arm64`
- macOS Intel: `darwin_amd64`
- 其他平台请选择对应版本

---

## 首次配置

### 1. 配置API密钥

**必须在首次运行前完成！**

```bash
# 进入项目目录
cd cd litex_auto_build_system

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

## 验证环境

运行验证脚本确认所有配置正确：

```bash
python3 scripts/final_verification.py
```

**检查项目**：
- ✅ Python环境和版本
- ✅ openai库是否安装
- ✅ Litex编译器是否存在且支持session模式
- ✅ 种子库文件是否完整
- ✅ 实验脚本是否可以导入
- ✅ 验证器是否能正常工作
- ✅ Litex语法指南是否存在

如果所有检查都显示 ✅，说明环境配置正确，可以开始运行实验。

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
python3 scripts/run_litex_definitions.py 5

# Theorem实验（5个任务）
python3 scripts/run_litex_theorems.py 5
```

#### 完整运行
```bash
# Definition实验（所有39个任务）
python3 scripts/run_litex_definitions.py

# Theorem实验（所有165个任务）
python3 scripts/run_litex_theorems.py
```

### 方式3：并行运行

Definition和Theorem实验使用独立的种子库，可以并行运行以节省时间：

```bash
# 设置环境变量
export LITEX_BIN="../LitexGeo/golitex/litex_0.9.116-beta_darwin_arm64/litex"

# 并行运行测试（5个任务）
python3 scripts/run_litex_definitions.py 5 & python3 scripts/run_litex_theorems.py 5 & wait

# 并行完整运行
python3 scripts/run_litex_definitions.py & python3 scripts/run_litex_theorems.py & wait
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
litex_auto_validated_250tasks/
├── definitions_only/
│   └── run_20261021_210000/    # 时间戳目录
│       ├── experiment.log      # 完整日志
│       ├── library_final.lit   # 最终生成的库
│       ├── state.json          # 实验状态
│       └── attempts.json       # 所有尝试记录
└── theorems_only/
    └── run_20261021_210000/
        ├── experiment.log
        ├── library_final.lit
        ├── state.json
        ├── attempts.json
        └── axioms_debt.md      # Axiom债务清单
```

### 查看命令

```bash
# 列出所有运行
ls -lt litex_auto_validated_250tasks/definitions_only/
ls -lt litex_auto_validated_250tasks/theorems_only/

# 查看最新的Definition实验日志
tail -f litex_auto_validated_250tasks/definitions_only/run_*/experiment.log

# 查看最新的Theorem实验日志
tail -f litex_auto_validated_250tasks/theorems_only/run_*/experiment.log

# 查看生成的库
cat litex_auto_validated_250tasks/definitions_only/run_*/library_final.lit
cat litex_auto_validated_250tasks/theorems_only/run_*/library_final.lit
```

### 输出文件说明

| 文件 | 说明 |
|------|------|
| `experiment.log` | 完整的控制台日志 |
| `experiment_log.md` | Markdown格式日志 |
| `state.json` | 实验状态（已完成任务等） |
| `library_final.lit` | 最终生成的完整库 |
| `attempts.json` | 所有尝试的详细记录（包含token统计） |
| `axioms_debt.md` | Axiom债务清单（仅Theorem实验） |

---

## 常见问题

### Q1: 提示 "API配置文件不存在"

**原因**：未创建 `config/api_config.json`

**解决**：
```bash
cp config/api_config.example.json config/api_config.json
# 然后编辑文件填入API密钥
```

### Q2: 提示 "请配置API密钥"

**原因**：`api_config.json` 中的 `api_key` 仍然是 `"your-api-key-here"`

**解决**：编辑 `config/api_config.json`，填入真实的API密钥

### Q3: 提示 "Litex编译器未找到" 或 "litex: command not found"

**原因**：Litex编译器不存在或路径不正确

**解决**：
```bash
# 1. 检查编译器文件是否存在
ls -lh ../LitexGeo/golitex/litex_0.9.116-beta_darwin_arm64/litex

# 2. 如果不存在，需要从Litex官方仓库获取
# https://github.com/litexlang/litex/releases
# 下载 litex_0.9.116-beta 对应平台的版本

# 3. 设置环境变量指向正确路径
export LITEX_BIN="/path/to/LitexGeo/golitex/litex_0.9.116-beta_darwin_arm64/litex"

# 4. 测试编译器
$LITEX_BIN --version  # 应该显示 Litex 0.9.116-beta
```

**注意**：不同平台使用不同版本：
- macOS M1/M2: `litex_0.9.116-beta_darwin_arm64`
- macOS Intel: `litex_0.9.116-beta_darwin_amd64`
- Linux: `litex_0.9.116-beta_linux_*`
- Windows: `litex_0.9.116-beta_windows_*`

### Q4: 想换用OpenAI API

**解决**：编辑 `config/api_config.json`：
```json
{
  "api_key": "sk-你的OpenAI密钥",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4"
}
```

### Q5: 实验运行中断了怎么办？

**说明**：每次运行都会创建新的时间戳目录，可以直接重新运行，不会覆盖之前的结果。

实验会自动跳过种子库中已有的定义，继续处理后续任务。

**建议**：
- 如果是网络问题导致中断，直接重新运行即可
- 如果是代码错误，检查日志文件了解失败原因
- 每次运行的完整日志都保存在 `experiment.log` 中

### Q6: 如何查看token使用统计？

**解决**：查看 `attempts.json` 文件：
```bash
cat litex_auto_validated_250tasks/definitions_only/run_*/attempts.json | jq '.[] | {task_id, total_tokens}'
```

### Q7: 想清理旧的运行结果

**解决**：
```bash
# 只保留最新的Definition运行
cd litex_auto_validated_250tasks/definitions_only
ls -t | tail -n +2 | xargs rm -rf

# 只保留最新的Theorem运行
cd ../theorems_only
ls -t | tail -n +2 | xargs rm -rf
```

**警告**：删除前请确认不需要这些数据！

---

## 📚 更多文档

- **系统架构**: [README.md](README.md) - 系统概述和目录结构
- **API配置**: [config/README.md](config/README.md) - 详细配置选项
- **脚本说明**: [SCRIPTS_EXPLANATION.md](SCRIPTS_EXPLANATION.md) - 各脚本功能说明
- **Litex语法**: [prompts/litex_short_guide.md](prompts/litex_short_guide.md) - 25KB完整语法指南
- **示例输出**: [examples/README.md](examples/README.md) - 示例运行结果

---

## 🔧 系统工作原理

1. **任务分配**: 从预定义的任务列表中逐个处理
2. **语法指导**: 每次任务都包含完整的Litex语法指南（25KB）
3. **代码生成**: AI根据任务描述和语法指南生成代码
4. **实时验证**: Litex编译器在session模式下验证生成的代码
5. **错误反馈**: 编译错误自动格式化并反馈给AI（最多5次重试）
6. **增量累积**: 验证通过的代码提交到session，供后续任务使用
7. **完整记录**: 所有尝试、错误、token使用等信息都被记录

这个闭环系统能够自动修正错误，持续改进代码质量。

---

## 🎯 快速参考

```bash
# 完整流程（首次运行）
# 1. 获取Litex编译器（如果还没有）
# 从 https://github.com/litexlang/litex/releases 下载 litex_0.9.116-beta

# 2. 验证编译器
ls -lh ../LitexGeo/golitex/litex_0.9.116-beta_darwin_arm64/litex

# 3. 配置API
cp config/api_config.example.json config/api_config.json
vim config/api_config.json                    # 填入API密钥

# 4. 验证环境
python3 scripts/final_verification.py

# 5. 测试运行
bash scripts/run_all_experiments.sh --test

# 完整流程（已配置）
python3 scripts/final_verification.py         # 验证环境
bash scripts/run_all_experiments.sh           # 完整运行
```
