# LiteX 短指南（LitexGeo 建库用）

## 1. 定义的形式选择

| 用途 | LiteX 形式 |
|------|-----------|
| 属性/关系/条件 | `prop` |
| 命名对象（给定值/类型）| `have` |
| 显式公式的映射 | `have fn` |
| 唯一存在性选择 | `have fn ... by exist!` |

## 2. 函数定义 (have fn)

**基本语法**：
```litex
have fn name(arg1, arg2 Type) ReturnType = expression
```

**示例**：
```litex
have fn vec(A, B cart(R, R)) cart(R, R) = (B[1] - A[1], B[2] - A[2])
have fn dot(u, v cart(R, R)) R = u[1] * v[1] + u[2] * v[2]
have fn distance_sq(A, B cart(R, R)) R = dot(vec(A, B), vec(A, B))
```

**关键规则**：
- 类型标注格式：`(arg Type)` 不用冒号 `:`
- 返回类型直接写，不用箭头 `->`
- 表达式直接写，不用 `return`

### 2.1 返回集合的函数

**返回集合的函数必须使用 `power_set(Type)` 作为返回类型**，不能直接使用 `set`。

**基本语法**：
```litex
have fn name(args Type) power_set(ElementType) = {element ElementType: conditions}
```

**带约束条件的参数**：
```litex
have fn name(arg1, arg2 Type: constraint) power_set(ElementType) = {element ElementType: conditions}
```

**示例**：
```litex
# 直线（一般方程）
have fn line(a, b, c R: a != 0 or b != 0) power_set(cart(R, R)) = 
    {p cart(R, R): a * p[1] + b * p[2] + c = 0}

# 两点确定直线
have fn line_of(a, b cart(R, R): a != b) power_set(cart(R, R)) = 
    {p cart(R, R): det(vec(a, p), vec(a, b)) = 0}

# 圆
have fn circle(o cart(R, R), r R) power_set(cart(R, R)) = 
    {p cart(R, R): distance_sq(o, p) = r * r}
```

**关键规则**：
- ✅ 返回类型用 `power_set(cart(R, R))`
- ❌ **不要用** `set`（会报错"set is not a valid identifier"）
- 约束条件写在参数后：`(a, b Type: constraint)`
- 集合推导式：`{element Type: conditions}`

## 3. 谓词定义 (prop)

**基本语法**：
```litex
prop name(args Type):
    conditions
```

**示例**：
```litex
prop is_collinear(p, q, r cart(R, R)):
    det(vec(p, q), vec(p, r)) = 0

prop is_perpendicular(a, b, c, d cart(R, R)):
    a != b
    c != d
    dot(vec(a, b), vec(c, d)) = 0
```

**关键规则**：
- 用于定义条件、关系、属性
- 可以有多个条件，每行一个
- 先写非零条件，再写主要等式
- **⚠️ 使用小写字母作为参数名**（p, q, r, a, b 等），不要用大写字母（P, Q, R），否则会出现"变量已绑定"错误
- **⚠️ 在定理的条件或结论中使用 prop 时，必须加 `$` 前缀**（见下文"定理证明"）

### 3.1 存在量词 (exist ... st)

在prop中表达"存在"，使用 `exist ... st {...}` 语法：

**基本语法**：
```litex
prop name(args Type):
    exist var1, var2 Type st {condition1, condition2, ...}
```

**示例**：
```litex
# 判断一个集合是否为直线
prop is_line(L power_set(cart(R, R))):
    exist a, b, c R st {a != 0 or b != 0, L = line(a, b, c)}

# 判断四点是否共圆
prop are_concyclic(a, b, c, d cart(R, R)):
    exist o cart(R, R) st {
        distance_sq(o, a) = distance_sq(o, b),
        distance_sq(o, b) = distance_sq(o, c),
        distance_sq(o, c) = distance_sq(o, d)
    }
```

**关键规则**：
- ✅ 使用 `exist ... st {...}` 
- ❌ **不要用** `exists ... :` 或 `exist ... :` （会报错"Expected operator or $prop in fact"）
- `st` 后面的条件用大括号 `{...}` 包裹
- 多个条件用逗号分隔

### 3.2 集合成员关系 ($in)

判断元素是否属于集合，使用 `$in` 运算符：

**基本语法**：
```litex
prop name(element, set):
    element $in set
```

**示例**：
```litex
# 判断点是否在直线上
prop is_on_line(p, a, b cart(R, R)):
    a != b
    p $in line_of(a, b)

# 判断点是否在圆上
prop is_on_circle(p, o cart(R, R), r R):
    p $in circle(o, r)
```

**关键规则**：
- ✅ 使用 `$in` 
- ❌ **不要用** `in` （会报错"Expected operator or $prop in fact"）
- `$in` 前面必须加美元符号 `$`

## 4. 定理证明 (thm)

**基本语法**（无条件）：
```litex
thm name:
    ? forall x, y Type:
        conclusion
    proof_body (等式链)
```

**基本语法**（有条件，使用等式作为条件）：
```litex
thm name:
    ? forall x, y Type:
        condition1,        # ← 多个条件用逗号分隔
        condition2,        # ← 逗号
        condition3         # ← 最后一个条件不加逗号
        =>:
            conclusion
    proof_body (等式链)
```

**基本语法**（有条件，使用 prop 谓词作为条件）：
```litex
thm name:
    ? forall x, y Type:
        $prop_name(args),  # ← prop 需要 $ 前缀，多个条件用逗号
        $prop_name(args)   # ← 最后一个不加逗号
        =>:
            $prop_name(args)  # ← 结论中也需要 $
    proof_body (等式链)
```

**⚠️ 重要：多个条件必须用逗号分隔！**
- ✅ `condition1, condition2 =>:`
- ❌ `condition1 condition2 =>:` （会导致 ParseError）

**示例**（等式条件）：
```litex
thm addition_cancel:
    ? forall a, b, c R:
        a + c = b + c
        =>:
            a = b
    a = (a + c) - c = (b + c) - c = b

thm addition_cancel_left:
    ? forall a, b, c R:
        c + a = c + b
        =>:
            a = b
    c + a = a + c
    c + b = b + c
    by thm addition_cancel(a, b, c)
```

**示例**（prop 谓词条件）：
```litex
# 已定义：prop is_collinear(p, q, r): det(vec(p, q), vec(p, r)) = 0

thm collinear_symmetric:
    ? forall p, q, r cart(R, R):
        $is_collinear(p, q, r)    # ← 使用 prop 需要 $ 前缀
        =>:
            $is_collinear(p, r, q)  # ← 结论中也需要 $
    det(vec(p, r), vec(p, q)) = -det(vec(p, q), vec(p, r))
    -det(vec(p, q), vec(p, r)) = -0
    -0 = 0
```

**示例**（多个条件，用逗号分隔）：
```litex
# 已定义：prop are_segments_congruent(a, b, c, d): distance_sq(a, b) = distance_sq(c, d)

thm segments_congruent_transitive:
    ? forall a, b, c, d, e, f cart(R, R):
        $are_segments_congruent(a, b, c, d),    # ← 条件1，逗号
        $are_segments_congruent(c, d, e, f)     # ← 条件2，最后一个不加逗号
        =>:
            $are_segments_congruent(a, b, e, f)
    distance_sq(a, b) = distance_sq(c, d)
    distance_sq(c, d) = distance_sq(e, f)
    distance_sq(a, b) = distance_sq(e, f)
```

**关键：prop 谓词在条件和结论中必须用 `$` 前缀！**
- ✅ `$is_collinear(p, q, r)`
- ❌ `is_collinear(p, q, r)` （会导致 ParseError）

**关键：多个条件必须用逗号分隔！**
- ✅ `condition1, condition2 =>:`
- ❌ `condition1 condition2 =>:` （会导致 ParseError）


**关键规则**：
- 用 `?` 开始 goal block，不用 `prove:`
- 条件和结论用 `=>:` 分隔
- 证明体是**等式链**，不是 tactic 风格（no `proof...end`）
- 可以引用其他定理：`by thm name(args)`
- **定理必须有证明体**，不能只写声明
- **⚠️ 使用函数定义前必须先声明展开形式**（见下文"使用函数定义"）
- **⚠️ 避免变量名冲突**：如果 P, Q, R 已在条件中使用，证明中不要重复绑定这些变量
- **⚠️ 不要在证明中重复声明条件**（见下文"使用条件"）

## 4.1 使用条件（假设）

在带条件的定理中，条件通过 `prop` 定义隐含了某些等式，你可以在证明中直接使用这些等式。

**❌ 错误：重复声明条件**：
```litex
# 已知：prop is_collinear(p, q, r): det(vec(p, q), vec(p, r)) = 0

thm is_collinear_symmetric:
    ? forall p, q, r cart(R, R):
        is_collinear(p, q, r)        # 条件
        =>:
            is_collinear(p, r, q)
    det(vec(p, q), vec(p, r)) = 0    # ❌ 错误！这是在重复声明条件
    det(vec(p, r), vec(p, q)) = -det(vec(p, q), vec(p, r))
    ...
```
这会导致 `Expected operator or $prop in fact` 错误。

**✅ 正确：直接使用条件隐含的等式**：
```litex
thm is_collinear_symmetric:
    ? forall p, q, r cart(R, R):
        is_collinear(p, q, r)        # 条件隐含：det(vec(p, q), vec(p, r)) = 0
        =>:
            is_collinear(p, r, q)
    det(vec(p, r), vec(p, q)) = -det(vec(p, q), vec(p, r))  # 直接开始证明
    -det(vec(p, q), vec(p, r)) = -0   # 使用条件：det(vec(p, q), vec(p, r)) = 0
    -0 = 0
```

**原理：**
- 条件 `is_collinear(p, q, r)` 的定义是 `det(vec(p, q), vec(p, r)) = 0`
- 在证明中，你可以把 `det(vec(p, q), vec(p, r))` 替换为 `0`
- 但**不要**在证明开始时重新声明 `det(vec(p, q), vec(p, r)) = 0`，这会被视为语法错误

**另一个例子：**
```litex
# 已知：prop is_perpendicular(a, b, c, d): 
#           a != b
#           c != d  
#           dot(vec(a, b), vec(c, d)) = 0

thm perpendicular_symmetric:
    ? forall a, b, c, d cart(R, R):
        is_perpendicular(a, b, c, d)
        =>:
            is_perpendicular(c, d, a, b)
    dot(vec(c, d), vec(a, b)) = dot(vec(a, b), vec(c, d))  # 点积交换律
    dot(vec(a, b), vec(c, d)) = 0   # 使用条件
    0 = 0
```

关键：条件给出的等式是**可用的知识**，直接在等式链中使用，不要重复声明。

## 5. 等式链证明

**连续等式**（推荐，简洁）：
```litex
a = (a + c) - c = (b + c) - c = b
```

**分步等式**（每行必须是完整等式，左边 = 右边）：
```litex
a = (a + c) - c
(a + c) - c = (b + c) - c
(b + c) - c = b
```

**❌ 错误1：不能单独写左边**：
```litex
a           # 错误！Expected operator or $prop in fact
= (a + c) - c
= (b + c) - c
```

**❌ 错误2：不要重复中间项**：
```litex
a = (a + c) - c
(a + c) - c              # 错误！不要重复
= (b + c) - c
(b + c) - c              # 错误！不要重复
= b
```

**✅ 正确：前一行的右边 = 下一行的左边**：
```litex
a = (a + c) - c          # a 到 (a + c) - c
(a + c) - c = (b + c) - c    # (a + c) - c 到 (b + c) - c
(b + c) - c = b          # (b + c) - c 到 b
```

**引用定理**：
```litex
by thm theorem_name(arg1, arg2, arg3)
```

**重要规则**：
- 每个等式必须有左边和右边：`left = right`
- 分步等式：前一行的右边应该等于下一行的左边
- 不要把右边单独写成下一行

**重要技巧：避免大跳跃**

当两个表达式之间的关系不明显时，不要直接写 `A = B`。应该使用等式链展开中间步骤：

**❌ 错误：跳跃太大**：
```litex
det(vec(p, r), vec(p, q)) = -det(vec(p, q), vec(p, r))  # litex 无法验证
```

**✅ 正确：使用等式链展开**：
```litex
# 先展开两个 det 的定义
det(vec(p, r), vec(p, q)) = vec(p, r)[1] * vec(p, q)[2] - vec(p, r)[2] * vec(p, q)[1]
det(vec(p, q), vec(p, r)) = vec(p, q)[1] * vec(p, r)[2] - vec(p, q)[2] * vec(p, r)[1]

# 然后用等式链连接（在一行中完成多步推理）
det(vec(p, r), vec(p, q)) = vec(p, r)[1] * vec(p, q)[2] - vec(p, r)[2] * vec(p, q)[1] = -(vec(p, q)[1] * vec(p, r)[2] - vec(p, q)[2] * vec(p, r)[1]) = -det(vec(p, q), vec(p, r))
```

**等式链中的多步连接**：
在一行中可以使用多个 `=` 连接中间步骤，只要每一步都能被 litex 验证：
```litex
A = B = C = D = E
```
等价于：
```litex
A = B
B = C
C = D
D = E
```

## 6. 使用函数定义

**关键规则：在证明中使用函数定义时，必须先声明该定义的展开形式。**

LiteX 不会自动展开 `have fn` 定义的函数。如果你想在证明中使用函数的具体形式，必须先把展开式写成等式。

**❌ 错误：直接使用函数定义**：
```litex
# 种子库中有：have fn vec(A, B cart(R, R)) cart(R, R) = (B[1] - A[1], B[2] - A[2])

thm my_theorem:
    ? forall A, B cart(R, R):
        ...
    distance_sq(A, B) = dot(vec(A, B), vec(A, B))
    dot(vec(A, B), vec(A, B)) = (B[1] - A[1]) * (B[1] - A[1]) + ...  # ❌ 错误！
    # LiteX 不知道 vec(A, B) = (B[1] - A[1], B[2] - A[2])
```

**✅ 正确：先声明定义，再使用**：
```litex
thm my_theorem:
    ? forall A, B cart(R, R):
        ...
    vec(A, B) = (B[1] - A[1], B[2] - A[2])              # ← 先声明展开
    vec(B, A) = (A[1] - B[1], A[2] - B[2])              # ← 如果需要另一个也声明
    distance_sq(A, B) = dot(vec(A, B), vec(A, B))
    dot(vec(A, B), vec(A, B)) = dot((B[1] - A[1], B[2] - A[2]), (B[1] - A[1], B[2] - A[2]))
    dot((B[1] - A[1], B[2] - A[2]), (B[1] - A[1], B[2] - A[2])) = (B[1] - A[1]) * (B[1] - A[1]) + ...
```

**另一个例子：**
```litex
# 种子库中有：have fn det(u, v cart(R, R)) R = u[1] * v[2] - u[2] * v[1]

thm det_antisymmetric:
    ? forall u, v cart(R, R):
        det(v, u) = -det(u, v)
    det(u, v) = u[1] * v[2] - u[2] * v[1]    # ← 先声明 det 的定义
    det(v, u) = v[1] * u[2] - v[2] * u[1]    # ← 也声明反过来的形式
    v[1] * u[2] - v[2] * u[1] = -(u[1] * v[2] - u[2] * v[1])
    -(u[1] * v[2] - u[2] * v[1]) = -det(u, v)
```

**原因：**
`have fn` 只是给出定义，但 LiteX 不会在证明中自动替换。你需要明确写出等式，LiteX 才认为这是一个可用的事实。

## 7. 变量命名规则

**避免变量名冲突：**

在 `forall` 中绑定的变量在整个定理作用域内有效。不要在证明中重复绑定相同的变量名。

**❌ 错误：变量名冲突**：
```litex
thm is_collinear_symmetric:
    ? forall P, Q, R cart(R, R):          # P, Q, R 已绑定
        is_collinear(P, Q, R)
        =>:
            is_collinear(P, R, Q)
    forall P, Q, R cart(R, R):            # ❌ 错误！P, Q, R 已经存在
        det(vec(P, R), vec(P, Q)) = 0
```

错误信息：`name 'Q' is already active in this scope and cannot be rebound`

**✅ 正确：直接使用已绑定的变量**：
```litex
thm is_collinear_symmetric:
    ? forall P, Q, R cart(R, R):          # P, Q, R 已绑定
        is_collinear(P, Q, R)
        =>:
            is_collinear(P, R, Q)
    det(vec(P, Q), vec(P, R)) = 0         # ✅ 直接使用 P, Q, R
    det(vec(P, R), vec(P, Q)) = -det(vec(P, Q), vec(P, R))
    -det(vec(P, Q), vec(P, R)) = -0
    -0 = 0
```

**✅ 或者使用不同的变量名**：
```litex
thm is_collinear_symmetric:
    ? forall A, B, C cart(R, R):          # 使用 A, B, C
        is_collinear(A, B, C)
        =>:
            is_collinear(A, C, B)
    det(vec(A, B), vec(A, C)) = 0
    det(vec(A, C), vec(A, B)) = -det(vec(A, B), vec(A, C))
    -det(vec(A, B), vec(A, C)) = -0
    -0 = 0
```

## 8. 常见错误

### 8.1 语法错误

❌ 不要用 Python/Lean 风格：
```litex
def vec(A, B: cart(R, R)) -> cart(R, R):  # 错误！
    return (B[1] - A[1], B[2] - A[2])
```

❌ 不要用 tactic 风格证明：
```litex
thm name: ? goal
proof
    unfold definition
    apply lemma
end
```

❌ 不要用 prove: 关键字：
```litex
thm name:
    prove:  # 错误！应该用 ?
        forall x. P(x)
```

❌ 不要只写定理声明不写证明：
```litex
thm name: ? forall x. P(x)  # 错误！必须有证明体
```

✅ 正确的 LiteX 风格：
```litex
have fn vec(A, B cart(R, R)) cart(R, R) = (B[1] - A[1], B[2] - A[2])

thm name:
    ? forall x Type:
        P(x)
    proof_steps_here
```

### 8.2 验证错误及解决方法

当编译器返回验证错误时，理解错误类型可以帮助你找到正确的解决方案：

#### VerifyError: atomic fact unknown
**含义**：你直接断言了一个等式（原子事实），但验证器无法判断它为什么成立。

**示例**：
```litex
thm parallel_transitive:
    ? forall a, b, c, d, f, g cart(R, R):
        $is_parallel(a, b, c, d),
        $is_parallel(c, d, f, g)
        =>:
            $is_parallel(a, b, f, g)
    det(vec(a, b), vec(f, g)) = 0  # ❌ atomic fact unknown
```

**原因**：
- 前提：`det(vec(a, b), vec(c, d)) = 0` 和 `det(vec(c, d), vec(f, g)) = 0`
- 结论：`det(vec(a, b), vec(f, g)) = 0`
- 这**不是简单的代数恒等式**，需要复杂的证明

**解决方法**：
1. **提供完整的证明链**：展开所有中间步骤，不要跳跃
2. **使用辅助构造**：通过乘以非零项来构造可验证的等式
3. **添加额外前提**：某些定理需要额外的非零条件

**正确的证明策略**：
```litex
thm parallel_transitive:
    ? forall a, b, c, d, x, y cart(R, R):
        $is_parallel(a, b, c, d),
        $is_parallel(c, d, x, y),
        distance_sq(c, d) != 0           # ← 添加额外前提
        =>:
            $is_parallel(a, b, x, y)
    # 展开所有定义
    vec(a, b) = (b[1] - a[1], b[2] - a[2])
    vec(c, d) = (d[1] - c[1], d[2] - c[2])
    vec(x, y) = (y[1] - x[1], y[2] - x[2])
    
    # 构造辅助项：det * distance_sq（可以通过代数展开）
    det(vec(a, b), vec(x, y)) * distance_sq(c, d) = ...（一长串代数展开）...
    
    # 证明辅助项等于0
    ...（更多步骤）... = 0
    
    # 最后通过除法得出结论
    det(vec(a, b), vec(x, y)) = 0
```

#### VerifyError: chain fact unknown
**含义**：等式链中某一步跳跃太大，验证器无法理解中间的推导。

**示例**：
```litex
det(vec(p, r), vec(p, q)) = -det(vec(p, q), vec(p, r))  # ❌ chain fact unknown
```

**解决方法**：将大步骤拆分为更小的步骤，明确展开中间的代数运算：
```litex
det(vec(p, r), vec(p, q)) = vec(p, r)[1] * vec(p, q)[2] - vec(p, r)[2] * vec(p, q)[1]
vec(p, r)[1] * vec(p, q)[2] - vec(p, r)[2] * vec(p, q)[1] = -(vec(p, q)[1] * vec(p, r)[2] - vec(p, q)[2] * vec(p, r)[1])
-(vec(p, q)[1] * vec(p, r)[2] - vec(p, q)[2] * vec(p, r)[1]) = -det(vec(p, q), vec(p, r))
```

#### ParseError: name already active
**含义**：你在同一作用域中重复绑定了同一个变量名。

**解决方法**：使用不同的变量名，或者直接使用已绑定的变量（见第7节）。

#### TypeError: type mismatch
**含义**：表达式的类型不匹配，例如将点当作向量使用。

**解决方法**：检查每个表达式的类型，确保函数参数类型正确。

### 8.3 证明策略提示

对于复杂的传递性定理（如平行传递性、全等传递性），常用的证明技巧：

1. **乘以辅助非零项**：将目标 `A = 0` 转化为 `A * B = 0`，其中 `B != 0` 是已知的
2. **添加非零前提**：如 `distance_sq(c, d) != 0` 来允许除法
3. **完整展开代数**：将所有函数定义展开为坐标形式，然后用代数恒等式连接
4. **使用中间引理**：先证明辅助引理，再在主定理中引用

## 9. 常见技巧（作战经验）

### 9.1 先自然语言拆解，再写 Litex

做题前先用自然语言写清思路，再映射成代码。建议把**简略自然语言过程**放在代码最前面当注释，当作证明提纲：

```litex
# 思路：角全等 ⇒ cos 分子成比例；两边同乘 den 后交叉；
#       再用 |u|^2|v|^2 - (u·v)^2 = det^2 两边替换即得
thm angle_congruence_det_ratio:
    ? forall ...
```

提纲里写清：

1. **已知** / **目标**
2. **第一思路**怎么算（对纯计算题，往往就是展开 + 代数恒等式，不必绕引理）
3. 再落到 Litex 行

不要一上来就堆 `by thm`。

### 9.2 定义追求简便，第一反应未必最好

同一个几何概念，选**后续最好证**的定义。

`is_midpoint` 经典对比：

```litex
# ❌ 偏重：共线 + 等距（后面定理很重）
prop is_midpoint(p, a, b cart(R, R)):
    $is_collinear(a, p, b)
    distance_sq(a, p) = distance_sq(p, b)

# ✅ 简便：坐标平均（展开即代数）
prop is_midpoint(p, a, b cart(R, R)):
    p[1] = (a[1] + b[1]) / 2
    p[2] = (a[2] + b[2]) / 2
```

原则：定义要服务后面的推理，不只是「几何上听起来对」。

### 9.3 卡在哪改哪；改不动就换路

- 验证失败时：只修**第一条**报错或等式链断点，不要整段重写。
- 仍卡住：换路，例如
  - 换定义形状（包装层 `dot(vec(...))` → 直接坐标）
  - 换证明策略（正向连等 → `by contra`）
  - 对准 Builtin 形状（见第 11 节），而不是猜规则名

典型坑（`point_difference_norm_pos`）：

```litex
# ❌ 一步里混 = 和 >，且跳跃太大
dot(vec(a, b), vec(a, b)) = (b[1]-a[1])*(b[1]-a[1]) + (b[2]-a[2])*(b[2]-a[2]) > 0

# ✅ 先连等展开，正性另写，对准 x^2 / 平方和
#    目标写成 (b[1]-a[1])^2 + (b[2]-a[2])^2 > 0 往往更顺
```

### 9.4 先建框架，卡住就 axiom，再慢慢填

建库追求：**先把接口和依赖骨架立住，再填补证明细节**。

若某条 `thm` 反复证不出来，又会被后面用到：不要空着跳过（后面 `by thm ...` 会找不到），先写成同名同陈述的 `axiom`，让库继续往下长：

```litex
# 证不出时先顶上；债务 = 库里还剩多少条这类 axiom
axiom point_difference_norm_pos:
    ? forall a, b cart(R, R):
        a != b
        =>:
            (b[1] - a[1])^2 + (b[2] - a[2])^2 > 0
```

原则：

- axiom 必须是**你认为真**的陈述，只是暂时没证
- 每条 axiom 记一笔信任债，以后再改回 `thm` + 证明
- 这是推进手段，不是终点：骨架先通，细节后补
- 自动实验 runner 已用 `litex -session` + `try` 增量验证；定理多次失败后会自动 axiom 顶库

### 9.5 Litex 是 fact-oriented：少 `by thm`，多写「要成立的事实」

**Litex 本质上是 fact-oriented 的语言。** 鼓励的代码格式是把 **what to prove**（要成立的等式/条件）直接写出来，而不是堆一串 **how to prove** 的引用步骤。

对 `have fn` / `prop` 的展开，**直接写等式往往更短、更好读**（见第 6 节）。验证器认的是事实形状，不是「你引用了哪个名字」。

因此：**不要写成 Lean 风格**——一排 `by thm xxx` 只声明“用了某引理”，却不把中间事实摊开。

**纯计算 / 恒等式题**：自然语言第一思路通常就是「展开定义 → 代数变形」。那就**按这个思路直接算**，不要为了「用库」硬塞一排 `by thm`。

```litex
# ❌ how-to 堆砌：简单交叉乘法却先 by thm 一堆
by thm dot_det_eliminate(...)
by thm vec_dot_self_is_distance(...)
...

# ✅ what-to-prove：注释里写清思路，正文直接写要成立的事实
# 思路：两边 |u×v|^2 * den' = ...；用 |u|^2|v|^2-(u·v)^2 替换
angle_cos_num(a, b, c) = dot(vec(b, a), vec(b, c))
...
det(...) * det(...) * angle_cos_den(...) = ... = ...
```

何时才 `by thm`：

- **大定理 / 非平凡推理**（传递、辅助构造、contra 结论），不是单纯展开或小学代数
- 或同一非平凡步骤要复用很多次

口令：**源代码写 what to prove；`by thm` 留给大定理。能写清的事实就写事实。**

### 9.6 每写一行，先问：它的来源成立了吗？

输出每一句 Litex 事实前，想清楚这句话**凭什么成立**：

1. **来源是什么**：定义展开？已知前提？前面已写出的等式？某个 `by thm` / Builtin 形状？
2. **来源是否已经在上下文里**：库里有、前提里有、或本证明前面已经写出过
3. **若来源还没有**：先写出/证出来源，再写这一句；不要凭直觉跳一步

口令：**先有来源，再写结论。** 验证器卡 `atomic fact unknown` / `chain fact unknown`，多半是某一行的来源没铺好。

## 10. 从零构建 LitexGeo：三个最小概念

建库顺序：**基底函数 → 关系谓词 → 几何谓词**。后面垂直、全等、平行都叠在这三层上。

### 10.1 基底：vec 与 dot

点是坐标对；`vec` 把两点变成向量；`dot` 把向量变成标量。同层还有 `det`（给共线用）。

```litex
have points set = cart(R, R)

have fn vec(A, B cart(R, R)) cart(R, R) = (B[1] - A[1], B[2] - A[2])
have fn dot(u, v cart(R, R)) R = u[1] * v[1] + u[2] * v[2]
have fn det(u, v cart(R, R)) R = u[1] * v[2] - u[2] * v[1]
```

### 10.2 关系：is_collinear

几何含义：三点共线。用行列式为零，可展开、可验证。

```litex
prop is_collinear(p, q, r cart(R, R)):
    det(vec(p, q), vec(p, r)) = 0
```

### 10.3 几何谓词：is_midpoint

有了共线也不要堆砌；中点用坐标平均（见 9.2）。

```litex
prop is_midpoint(p, a, b cart(R, R)):
    p[1] = (a[1] + b[1]) / 2
    p[2] = (a[2] + b[2]) / 2
```

### 10.4 小结

| 概念 | 形式 | 依赖 | 解锁 |
|------|------|------|------|
| `vec` / `dot`（+`det`） | `have fn` | 坐标 | 长度、垂直、共线计算 |
| `is_collinear` | `prop` | `vec`,`det` | 位置关系 |
| `is_midpoint` | `prop` | 坐标 | 中点相关定理 |

## 11. 常见 Builtin 形状（速查）

Builtin **不是** `by builtin xxx`。你写出匹配形状的事实，验证器自己匹配。卡死时优先**改写形状**。

### 代数与连等

| 形状 | 写法 |
|------|------|
| 多项式恒等 | `(x+1)*(x-1) = x^2 - 1` |
| 差分 | `a = b` ⇒ `a - b = 0`；`a - b != 0` ⇒ `a != b` |

### 平方与正性（几何最常用）

| 形状 | 写法 |
|------|------|
| 平方非负 | `0 <= x^2`（`x * x` 也常认，优先写 `^2`） |
| 底非零 ⇒ 平方正 | 已知 `x != 0` ⇒ `0 < x^2` |
| 平方和非零 | 已知 `a != 0` ⇒ `a^2 + b^2 != 0` |
| 平方和为零 | `a^2 + b^2 = 0` ⇒ `a = 0`、`b = 0` |

口令：正性先展开成 `dx^2 + dy^2`；**不要**把 `=` 和 `>` 写在同一条链里。

### 乘积与消元

| 形状 | 写法 |
|------|------|
| 乘积为零 | `a * b = 0` 且 `a != 0` ⇒ `b = 0` |
| 乘积非零 | `a != 0`，`b != 0` ⇒ `a * b != 0` |
| 除法回乘 | `a / b = c` 且 `b != 0` ⇒ `a = c * b` |

### 序与坐标

| 形状 | 写法 |
|------|------|
| 削弱 | `a < b` ⇒ `a <= b` |
| 非负和 | `0 <= a`，`0 <= b` ⇒ `0 <= a + b` |
| 分量 ⇒ 点相等 | `a[1] = b[1]`，`a[2] = b[2]` ⇒ `a = b` |
