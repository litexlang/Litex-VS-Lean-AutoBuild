# Lean 4 短指南（几何建库用）

本指南涵盖在 Lean 4 中构建几何定理库所需的语法、策略，以及与 Litex 短指南对齐的作战经验（证明风格见 §12.5，**勿照搬 Litex 的 fact-oriented 写法**）。

## ⚠️ 重要规则

### 🚫 不要包含 import 语句
**种子库已经包含了所有必要的 import，你的代码中不要再写 import！**

```lean
-- ❌ 错误 - 不要写 import
import Mathlib.Data.Real.Basic

def distance_sq ...

-- ✅ 正确 - 直接写定义和定理
def distance_sq (A B : Point) : ℝ := dot (vec A B) (vec A B)
```

**记住：种子库已经有了 `import Mathlib.Data.Real.Basic`，你只需要写定义和定理！**

## 1. 基础类型和定义

### 1.1 实数类型
```lean
-- ⚠️ 注意：不要写 import 语句！种子库已经包含了！

-- ℝ 是实数类型（已经在种子库中定义）
-- ℝ × ℝ 是实数对（点类型）
-- Point 已经定义为 ℝ × ℝ
```

### 1.2 定义函数
```lean
-- 定义函数使用 def
def vec (A B : Point) : Point := (B.1 - A.1, B.2 - A.2)

-- 参数类型注解
def dot (u v : Point) : ℝ := u.1 * v.1 + u.2 * v.2

-- 返回类型必须明确
def det (u v : Point) : ℝ := u.1 * v.2 - u.2 * v.1
```

### 1.3 定义谓词（命题）
```lean
-- 谓词返回类型是 Prop
def is_collinear (p q r : Point) : Prop := 
  det (vec p q) (vec p r) = 0

-- 可以有多个条件
def is_parallel (a b c d : Point) : Prop :=
  a ≠ b ∧ c ≠ d ∧ det (vec a b) (vec c d) = 0
```

## 2. 定理证明

### 2.1 定理声明
```lean
-- 使用 theorem 关键字
theorem distance_sq_symm : ∀ (A B : Point), 
  distance_sq A B = distance_sq B A := by
  -- 证明在这里
```

### 2.2 全称量词 (∀)
```lean
-- ∀ 表示"对所有"
theorem example1 : ∀ (x : ℝ), x + 0 = x := by
  intro x
  ring
```

### 2.3 存在量词 (∃)
```lean
-- ∃ 表示"存在"
theorem example2 : ∃ (x : ℝ), x + 1 = 2 := by
  use 1
  ring
```

### 2.4 逻辑连接词
```lean
-- ∧ : 且 (and)
-- ∨ : 或 (or)  
-- ¬ : 非 (not)
-- → : 蕴含 (implies)
-- ↔ : 当且仅当 (iff)

def example_prop (a b : Point) : Prop :=
  a ≠ b ∧ (a.1 = 0 ∨ a.2 = 0)
```

## 3. 证明策略 (Tactics)

### 3.1 intro - 引入变量
```lean
theorem example : ∀ (x y : ℝ), x = y → x + 1 = y + 1 := by
  intro x y h  -- 引入 x, y, 和假设 h : x = y
  rw [h]       -- 重写
  rfl          -- 反射性
```

### 3.2 rfl - 反射性
```lean
-- 用于证明两边完全相同的等式
theorem example : 5 = 5 := by
  rfl
```

### 3.3 rw - 重写
```lean
-- 使用等式进行重写
theorem example : ∀ (x y : ℝ), x = y → x + 1 = y + 1 := by
  intro x y h
  rw [h]  -- 将左边的 x 替换为 y
  rfl
```

### 3.4 simp - 简化
```lean
-- 使用简化规则自动简化表达式
theorem example : ∀ (x : ℝ), x + 0 = x := by
  intro x
  simp
```

### 3.5 ring - 环论求解器
```lean
-- 自动证明环论中的恒等式
theorem example : ∀ (x y : ℝ), (x + y)^2 = x^2 + 2*x*y + y^2 := by
  intro x y
  ring
```

### 3.6 field_simp - 域简化
```lean
-- 处理分数和除法
theorem example : ∀ (x : ℝ), x ≠ 0 → x / x = 1 := by
  intro x h
  field_simp
```

### 3.7 unfold - 展开定义
```lean
-- 展开函数或谓词的定义
theorem example : ∀ (A B : Point), vec A B = (B.1 - A.1, B.2 - A.2) := by
  intro A B
  unfold vec  -- 展开 vec 的定义
  rfl
```

### 3.8 calc - 计算式证明
```lean
-- 用于多步等式推导
theorem example : ∀ (x y : ℝ), x = y → x + 1 = y + 1 := by
  intro x y h
  calc x + 1 = y + 1 := by rw [h]
```

### 3.9 apply - 应用定理
```lean
-- 应用已知定理或假设
theorem example : ∀ (x : ℝ), x = x := by
  intro x
  apply Eq.refl  -- 应用反射性定理
```

### 3.10 have - 添加中间结论
```lean
theorem example : ∀ (x : ℝ), x + 0 = x := by
  intro x
  have h : 0 + x = x := by simp
  simp
```

## 4. 结构和模式

### 4.1 访问元组元素
```lean
-- Point = ℝ × ℝ
-- 使用 .1 和 .2 访问元素
def first_coord (p : Point) : ℝ := p.1
def second_coord (p : Point) : ℝ := p.2
```

### 4.2 模式匹配
```lean
-- 可以直接解构元组
def example (p : Point) : ℝ := 
  let (x, y) := p
  x + y
```

### 4.3 条件语句
```lean
-- 使用 if-then-else
def abs (x : ℝ) : ℝ :=
  if x ≥ 0 then x else -x
```

## 5. 常见证明模式

### 5.1 证明对称性
```lean
theorem distance_sq_symm : ∀ (A B : Point), 
  distance_sq A B = distance_sq B A := by
  intro A B
  unfold distance_sq
  unfold dot
  unfold vec
  ring  -- 代数化简
```

### 5.2 证明传递性
```lean
theorem example_trans : ∀ (a b c d e f : Point),
  are_segments_congruent a b c d →
  are_segments_congruent c d e f →
  are_segments_congruent a b e f := by
  intro a b c d e f h1 h2
  unfold are_segments_congruent at *
  calc distance_sq a b = distance_sq c d := h1
    _ = distance_sq e f := h2
```

### 5.3 展开定义后化简
```lean
theorem example : ∀ (p q r : Point),
  is_collinear p q r → det (vec p q) (vec p r) = 0 := by
  intro p q r h
  unfold is_collinear at h
  exact h  -- h 已经是我们需要的结论
```

## 6. 类型和证明

### 6.1 命题即类型
```lean
-- Prop 是命题类型
-- 证明是该命题类型的元素
def example_prop : Prop := 1 + 1 = 2
def example_proof : example_prop := by rfl
```

### 6.2 依赖类型
```lean
-- 类型可以依赖于值
def example (n : ℕ) : n + 0 = n := by simp
```

## 7. 常见错误和解决方法

### 7.1 类型不匹配
```
error: type mismatch
  ℝ
has type
  Type
but is expected to have type
  Prop
```
**解决**：检查定义的返回类型，谓词应该返回 `Prop`，函数应该返回具体类型（如 `ℝ`）。

### 7.2 策略失败
```
error: tactic 'rfl' failed, the left-hand side
  x + 1
is not definitionally equal to the right-hand side
  x + 2
```
**解决**：`rfl` 只能证明定义上相等的式子。使用 `ring` 或其他策略处理需要计算的等式。

### 7.3 未解决的目标
```
error: unsolved goals
x : ℝ
⊢ x + 0 = x
```
**解决**：证明不完整，需要添加策略完成证明（如 `simp` 或 `ring`）。

### 7.4 未知标识符
```
error: unknown identifier 'distance_sq'
```
**解决**：确保函数已经定义，或者需要先定义它。

## 8. 最佳实践

### 8.1 命名规范
- 类型名：大写开头（`Point`, `Line`）
- 函数名：小写下划线分隔（`distance_sq`, `vec`）
- 定理名：小写下划线分隔（`distance_sq_symm`, `collinear_symm`）
- 谓词名：`is_` 或 `are_` 开头（`is_collinear`, `are_congruent`）

### 8.2 证明结构
```lean
theorem theorem_name : statement := by
  intro ...           -- 引入变量
  unfold ...          -- 展开定义
  have ... := ...     -- 中间步骤
  calc ...            -- 计算链（如果需要）
  ring / simp / ...   -- 最终化简
```

### 8.3 注释
```lean
-- 单行注释使用 --

/- 
  多行注释
  使用 /- ... -/
-/

/-- 
  文档注释（显示在hover中）
  使用 /-- ... -/
-/
def documented_function : ℝ := 42
```

## 9. 常用策略组合

### 9.1 展开并化简
```lean
by
  intro x y
  unfold distance_sq dot vec
  ring
```

### 9.2 使用假设重写
```lean
by
  intro x y h
  rw [h]
  rfl
```

### 9.3 分解AND条件
```lean
by
  intro h
  obtain ⟨h1, h2⟩ := h  -- 分解 h : A ∧ B 为 h1 : A 和 h2 : B
  ...
```

## 10. 数学符号

| 符号 | 输入 | 含义 |
|------|------|------|
| `ℝ` | `\R` 或 `\real` | 实数 |
| `×` | `\times` | 笛卡尔积 |
| `∀` | `\forall` | 全称量词 |
| `∃` | `\exists` | 存在量词 |
| `∧` | `\and` | 逻辑与 |
| `∨` | `\or` | 逻辑或 |
| `¬` | `\not` | 逻辑非 |
| `→` | `\to` | 蕴含 |
| `↔` | `\iff` | 当且仅当 |
| `≠` | `\ne` | 不等于 |
| `≤` | `\le` | 小于等于 |
| `≥` | `\ge` | 大于等于 |

## 11. 示例：完整证明

```lean
-- ⚠️ 不要写 import！种子库已经包含了！

-- 种子库已有：
-- def Point := ℝ × ℝ
-- def vec (A B : Point) : Point := (B.1 - A.1, B.2 - A.2)
-- def dot (u v : Point) : ℝ := u.1 * v.1 + u.2 * v.2

-- 你只需要写新的定义和定理：
def distance_sq (A B : Point) : ℝ := dot (vec A B) (vec A B)

theorem distance_sq_symm : ∀ (A B : Point), 
  distance_sq A B = distance_sq B A := by
  intro A B
  unfold distance_sq
  unfold dot
  unfold vec
  ring
```

这个示例展示了正确的代码结构：**直接写定义和定理，不要包含import语句！**

## 12. 常见技巧（作战经验）

与 Litex 短指南对齐的建库习惯；**证明风格不要照搬 Litex**（见 12.5）。

### 12.1 先自然语言拆解，再写 Lean

做题前先用自然语言写清思路，再映射成代码。建议把**简略自然语言过程**放在证明最前面当注释：

```lean
/-- 思路：展开 distance_sq / dot / vec，坐标上 ring -/
theorem distance_sq_symm : ∀ (A B : Point),
    distance_sq A B = distance_sq B A := by
  intro A B
  unfold distance_sq dot vec
  ring
```

提纲：已知 / 目标 / 第一思路（展开？calc？用哪个 lemma？）。

### 12.2 定义追求简便，第一反应未必最好

同一个几何概念，选**后续最好证**的定义。

```lean
-- ❌ 偏重：共线 + 等距
def is_midpoint (p a b : Point) : Prop :=
  is_collinear a p b ∧ distance_sq a p = distance_sq p b

-- ✅ 简便：坐标平均（后续多为代数）
def is_midpoint (p a b : Point) : Prop :=
  p.1 = (a.1 + b.1) / 2 ∧ p.2 = (a.2 + b.2) / 2
```

原则：定义要服务后面的推理，不只是「几何上听起来对」。

### 12.3 卡在哪改哪；改不动就换路

- 报错时只修**第一个**失败目标，不要整段重写。
- 仍卡住：换路——换定义形状、换 `calc`/`ring`/`linarith`、拆 `have` 中间引理。

### 12.4 先建框架，卡住就 `sorry` / `axiom`，再慢慢填

建库追求：**先把接口和依赖骨架立住，再填补证明细节**。

若某条定理反复证不出又会被后面用到，可先：

```lean
axiom point_difference_norm_pos :
  ∀ (a b : Point), a ≠ b →
    (b.1 - a.1)^2 + (b.2 - a.2)^2 > 0
```

或临时 `sorry`（债务清单同上）。axiom/`sorry` 必须是你认为真的陈述；每条记一笔债，以后再补。

### 12.5 Lean 是 tactic-oriented（与 Litex 不同）

**不要把 Litex 的「少 `by thm`、只写事实」原样搬到 Lean。**

| | Litex | Lean |
|--|-------|------|
| 取向 | **fact-oriented**：正文写 what to prove | **tactic-oriented**：`by` 里写 how to prove |
| 展开定义 | 直接写等式事实 | `unfold` / `rw` / `simp` / `dsimp` |
| 复用结论 | 少用小引理 `by thm`；大定理才引用 | `apply` / `exact` / `have :=` 用库定理是常态 |
| 计算 | 超长连等 | `calc` + `ring` / `field_simp` / `linarith` |

Lean 里鼓励：

- 小步 `have` 把子目标钉住
- 坐标几何优先 `unfold` 后 `ring`
- 该用 Mathlib 引理就用，不必为了「像 Litex」而拒绝 `apply`

口令：**Lean 写清 tactic 路径；Litex 写清事实。两边别混风格。**

### 12.6 每写一步，先问：前提够了吗？

每个 tactic 前想清楚：当前 goal 是什么、需要哪些假设、上一步是否已经提供。`unknown identifier` / `failed to synthesize` / tactic 失败，多半是前提或类型没铺好。

## 13. 从零构建 LitexGeo（Lean）：三个最小概念

建库顺序同样是：**基底函数 → 关系谓词 → 几何谓词**。

### 13.1 基底：vec 与 dot

```lean
-- 种子库通常已有 Point / vec / dot；示意：
def vec (A B : Point) : Point := (B.1 - A.1, B.2 - A.2)
def dot (u v : Point) : ℝ := u.1 * v.1 + u.2 * v.2
def det (u v : Point) : ℝ := u.1 * v.2 - u.2 * v.1
```

### 13.2 关系：is_collinear

```lean
def is_collinear (p q r : Point) : Prop :=
  det (vec p q) (vec p r) = 0
```

### 13.3 几何谓词：is_midpoint

```lean
def is_midpoint (p a b : Point) : Prop :=
  p.1 = (a.1 + b.1) / 2 ∧ p.2 = (a.2 + b.2) / 2
```

### 13.4 小结

| 概念 | 形式 | 依赖 | 解锁 |
|------|------|------|------|
| `vec` / `dot`（+`det`） | `def` | 坐标 | 长度、垂直、共线计算 |
| `is_collinear` | `Prop` | `vec`,`det` | 位置关系 |
| `is_midpoint` | `Prop` | 坐标 | 中点相关定理 |

## 14. 常见 tactic / 求解器形状（速查）

不是 Litex Builtin，而是 Lean 侧「对准什么形状更好证」：

| 目标形状 | 常用手段 |
|----------|----------|
| 多项式 / 坐标恒等 | `unfold` + `ring` |
| 域上分式 | `field_simp` 再 `ring` |
| 线性不等式 | `linarith` / `nlinarith` |
| 定义展开 | `unfold` / `dsimp` / `rw [def]` |
| 等式链 | `calc` |
| 应用已有定理 | `apply` / `exact` / `have :=` |

口令：先把 goal 化成求解器吃得下的形状，再砸 `ring`/`linarith`；大步跳不动就拆 `have`。
