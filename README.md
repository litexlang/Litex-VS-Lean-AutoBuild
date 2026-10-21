# Litex & Lean 自动构建实验系统

本仓库包含两个AI驱动的几何库自动构建实验系统：**LitexGeo**和**LeanGeo**。

## 📊 实验概述

两个系统都旨在通过AI自动生成几何库的定义和定理，并通过各自的编译器进行实时验证。

### 实验任务

| 类型 | 任务描述 | 数量 |
|------|---------|------|
| **Definition** | 定义几何基础函数和谓词 | 39个 |
| **Theorem** | 证明几何定理 | 165个 |

**Definition任务示例**：
- 定义向量运算（vec、dot、det）
- 定义距离和角度函数
- 定义几何对象（line、circle、triangle）
- 定义几何谓词（平行、垂直、共线等）

**Theorem任务示例**：
- 向量运算性质（交换律、分配律）
- 几何关系定理（三角形内角和、勾股定理）
- 点、线、圆的位置关系定理

## 🎯 实验结果

### Litex系统

#### Definition实验

**Litex代码示例**：

```litex
# 定义两点间距离的平方
have fn distance_sq(A, B cart(R, R)) R = 
  let v = vec(A, B) in dot(v, v)

# 定义直线（一般式方程）
have fn line(a, b, c R) set = 
  {p cart(R, R) | a * p[1] + b * p[2] + c = 0}
```

#### Theorem实验

**Litex证明示例**：

```litex
# 向量点积交换律
thm dot_comm(u, v cart(R, R)) : dot(u, v) = dot(v, u)
proof:
  calc:
    dot(u, v)
    = u[1] * v[1] + u[2] * v[2]   by def dot
    = v[1] * u[1] + v[2] * u[2]   by comm_mul
    = dot(v, u)                    by def dot
qed
```

### 

## ⚖️ 系统特性对比

### 编译器和语言

| 特性 | Litex | Lean |
|------|-------|------|
| 编译器 | Litex 0.9.116-beta | Lean 4.35.0 |
| 语言范式 | 声明式，自然语言风格 | 函数式，依赖类型 |
| 证明风格 | calc链式推理 | tactic证明 |

**Litex优势**：
- ✅ **自然语言风格**：语法接近数学教科书，易于理解
- ✅ **简洁的证明**：calc风格直观，适合几何推理
- ✅ **快速原型**：无需复杂类型标注，快速验证想法

### 验证方式

| 特性 | Litex | Lean |
|------|-------|------|
| 验证模式 | Session协议 | REPL（通过lake env） |
| 增量编译 | ✅ 支持 | ✅ 支持 |
| 编译速度 | 快 | 慢（首次需加载Mathlib） |

### 标准库

| 特性 | Litex | Lean |
|------|-------|------|
| 标准库 | 无（从零构建）| Mathlib（~300MB）|
| 实数运算 | 手动定义 | 现成（Real类型）|
| 几何库 | 完全自建 | 部分现成 |

### 开发体验

| 特性 | Litex | Lean |
|------|-------|------|
| 安装 | 下载二进制即用 | 需安装elan + 下载Mathlib |

### 性能对比

#### Definition实验（39个任务）

| 指标 | Litex | Lean |
|------|-------|-------------|
| 总耗时 | 37.8 min | 10.3 min |
| Token消耗 | 0.56M    | 0.44M |
| 成功率 | 100% | 100% |

#### Theorem实验（165个任务）

| 指标 | Litex | Lean |
|------|-------|-------------|
| 总耗时 | 280.8 min | 638.9 min |
| Token消耗 | 11.5M | 10.5M |
| 成功率 | 90.8% | 70% |

### 综合评分

| 维度 | Litex | Lean |
|------|-------|------|
| **易用性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **严谨性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **学习曲线** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **编译速度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **表达能力** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🚀 快速开始

### Litex系统

```bash
# 1. 获取编译器
# 从 https://github.com/litexlang/litex/releases 
# 下载 litex_0.9.116-beta
# 解压到 LitexGeo/golitex/ 目录

# 2. 配置API
cd litex_auto_build_system
cp config/api_config.example.json config/api_config.json
vim config/api_config.json  # 填入API密钥

# 3. 运行实验（测试模式：前3个任务）
bash scripts/run_all_experiments.sh --test

# 4. 完整运行（所有204个任务）
bash scripts/run_all_experiments.sh
```

### Lean系统

```bash
# 1. 安装Lean
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
source ~/.zshrc

# 2. 构建项目（下载Mathlib，首次需5-10分钟）
cd LeanGeo
lake build

# 3. 配置API
cd ../lean_auto_build_system
cp config/api_config.example.json config/api_config.json
vim config/api_config.json  # 填入API密钥

# 4. 运行实验（测试模式：前3个任务）
bash scripts/run_all_experiments.sh --test

# 5. 完整运行（所有204个任务）
bash scripts/run_all_experiments.sh
```

## 📁 目录结构

```
auto-build/
│
├── README.md                          # 本文件
│
├── litex_auto_build_system/          # Litex实验系统
│   ├── scripts/                      # 实验脚本
│   ├── config/                       # API配置
│   ├── database/                     # 种子库
│   ├── README.md                     # 详细说明
│   └── USAGE_GUIDE.md               # 使用指南
│
├── lean_auto_build_system/           # Lean实验系统
│   ├── scripts/                      # 实验脚本
│   ├── config/                       # API配置
│   ├── prompts/                      # 语法指南
│   ├── README.md                     # 详细说明
│   └── USAGE_GUIDE.md               # 使用指南
│
├── LitexGeo/                         # Litex编译器目录（需单独获取）
│   └── README.md                     # 获取说明
│
└── LeanGeo/                          # Lean项目目录（需单独构建）
    └── README.md                     # 构建说明
```

## ⚠️ 首次克隆后需要

### 1. 获取Litex编译器（未包含在仓库中）
- 从 https://github.com/litexlang/litex/releases 下载
- 版本：`litex_0.9.116-beta`
- 放置在：`LitexGeo/golitex/litex_0.9.116-beta_<platform>/litex`

### 2. 安装Lean环境（未包含在仓库中）
```bash
# 安装Lean
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# 构建项目（下载Mathlib）
cd LeanGeo && lake build
```

### 3. 配置API密钥
两个系统都需要：
```bash
# 进入对应系统目录
cd litex_auto_build_system  # 或 lean_auto_build_system

# 复制配置模板
cp config/api_config.example.json config/api_config.json

# 编辑配置，填入API密钥
vim config/api_config.json
```

配置格式：
```json
{
  "api_key": "your-actual-api-key",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4"
}
```

## 📊 实验输出

运行后会在各自系统的输出目录生成：

```
*_auto_validated_250tasks/
├── definitions_only/
│   └── run_YYYYMMDD_HHMMSS/
│       ├── experiment.log           # 完整运行日志
│       ├── library_final.*          # 生成的完整库
│       ├── attempts.json            # 所有尝试记录
│       └── state.json               # 实验状态
│
└── theorems_only/
    └── run_YYYYMMDD_HHMMSS/
        ├── experiment.log
        ├── library_final.*
        ├── attempts.json
        ├── axioms_debt.md           # Axiom债务清单
        └── state.json
```

## 🎯 运行选项

### 测试模式
```bash
bash scripts/run_all_experiments.sh --test
# 每个实验只运行前3个任务，快速验证环境
```

### 完整模式
```bash
bash scripts/run_all_experiments.sh
# 运行所有任务（Definition: 39个 + Theorem: 165个）
```

### 单独运行
```bash
# 只运行Definition实验
python3 scripts/run_*_definitions.py --max-tasks 10

# 只运行Theorem实验  
python3 scripts/run_*_theorems.py --max-tasks 10
```

## 📖 文档索引

- **[litex_auto_build_system/README.md](litex_auto_build_system/README.md)** - Litex系统详细说明
- **[litex_auto_build_system/USAGE_GUIDE.md](litex_auto_build_system/USAGE_GUIDE.md)** - Litex使用指南
- **[lean_auto_build_system/README.md](lean_auto_build_system/README.md)** - Lean系统详细说明
- **[lean_auto_build_system/USAGE_GUIDE.md](lean_auto_build_system/USAGE_GUIDE.md)** - Lean使用指南

## 🔗 相关链接

- **Litex**: https://github.com/litexlang/litex
- **Lean**: https://leanprover.github.io/
- **Mathlib**: https://leanprover-community.github.io/mathlib4_docs/

## 📝 许可证

请遵守各自编译器和库的许可证要求。

---

**更新日期**: 2026-10-22  
**系统版本**: Litex 0.9.116-beta, Lean 4.35.0

