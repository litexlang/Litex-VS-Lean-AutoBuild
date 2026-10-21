# 实验输出目录

这个目录用于存放你自己运行的实验输出。

## 📁 目录结构

```
litex_auto_validated_250tasks/
├── definitions_only/
│   └── run_YYYYMMDD_HHMMSS/    # 你的Definition实验输出
└── theorems_only/
    └── run_YYYYMMDD_HHMMSS/    # 你的Theorem实验输出
```

## ✅ 特点

- **自动创建**: 运行实验时自动创建带时间戳的目录
- **不会覆盖**: 每次运行创建新目录，旧的运行结果保留
- **完整记录**: 包含日志、状态、尝试记录等所有信息

## 📊 输出文件说明

每个运行目录包含：

| 文件 | 说明 |
|------|------|
| `experiment.log` | 完整的控制台日志 |
| `experiment_log.md` | Markdown格式日志 |
| `state.json` | 实验状态（已完成任务等） |
| `library_final.lit` | 最终生成的完整库 |
| `attempts.json` | 所有尝试的详细记录 |
| `axioms_debt.md` | Axiom债务清单（仅Theorem） |

## 🎯 查看结果

```bash
# 列出所有运行
ls -lt litex_auto_validated_250tasks/*/

# 查看最新的Definition运行
ls -lt litex_auto_validated_250tasks/definitions_only/run_*/

# 查看最新的Theorem运行
ls -lt litex_auto_validated_250tasks/theorems_only/run_*/
```

## 🔄 与示例的区别

- **`examples/`**: 预先提供的示例输出，供参考学习
- **`litex_auto_validated_250tasks/`**: 你自己运行的实际输出

## 🧹 清理

如果需要清理旧的运行结果：

```bash
# 删除所有Definition运行（保留最新的除外）
cd litex_auto_validated_250tasks/definitions_only
ls -t | tail -n +2 | xargs rm -rf

# 删除所有Theorem运行（保留最新的除外）
cd ../theorems_only
ls -t | tail -n +2 | xargs rm -rf
```

**注意**: 删除前请确认不需要这些数据！
