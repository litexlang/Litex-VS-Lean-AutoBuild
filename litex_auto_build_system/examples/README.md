# 示例输出

这个目录包含完整的实验运行示例，供参考和学习使用。

## 📁 目录结构

```
examples/
├── definitions_only/
│   └── run_20260920_145809/    # Definition实验示例
│       ├── experiment.log       # 完整日志
│       ├── library_final.lit    # 最终生成的定义库
│       ├── state.json           # 实验状态
│       └── attempts.json        # 所有尝试记录
└── theorems_only/
    └── run_20260928_153815/    # Theorem实验示例
        ├── experiment.log       # 完整日志
        ├── library_final.lit    # 最终生成的定理库
        ├── state.json           # 实验状态
        ├── attempts.json        # 所有尝试记录
        └── axioms_debt.md       # Axiom债务清单
```

## 📊 示例统计

### Definition实验示例 (run_20260920_145809)
- **完成任务**: 36个定义
- **成功率**: 高
- **输出**: 完整的几何定义库

### Theorem实验示例 (run_20260928_153815)
- **完成任务**: 多个定理证明
- **成功率**: 高
- **输出**: 包含定理证明的完整库

## 🎯 用途

1. **参考示例**: 查看实验输出的格式和内容
2. **学习材料**: 了解如何编写Litex代码
3. **对比验证**: 检查自己的运行结果是否正常

## ⚠️ 注意

- ✅ 这些是**示例输出**，不会被新的实验覆盖
- ✅ 实际运行的输出会保存到 `../litex_auto_validated_250tasks/`
- ✅ 可以安全地参考和学习这些示例

## 🔍 查看示例

```bash
# 查看Definition示例日志
cat examples/definitions_only/run_20260920_145809/experiment.log

# 查看Theorem示例日志
cat examples/theorems_only/run_20260928_153815/experiment.log

# 查看生成的库
cat examples/definitions_only/run_20260920_145809/library_final.lit
cat examples/theorems_only/run_20260928_153815/library_final.lit
```
