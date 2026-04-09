# 走读附录：Claude Code 使用技巧

这一份不是源码模块走读，而是把前面分析里能稳定复用的方法提炼成实际使用建议。这里的每条技巧都尽量回答三个问题：

- 该怎么写
- 为什么这样更有效
- 参考的是源码里的哪一段

对应主稿：
- [00-代码总览与运行时走读.md](/Users/bobo/code/claude-code-source-code/docs/zh/00-代码总览与运行时走读.md)

主要参考代码：

- [src/constants/prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts)
- [src/utils/messages.ts](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts)
- [src/tools/BashTool/prompt.ts](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts)

## 1. 高质量任务描述模板

从系统 prompt 的风格看，一个高质量任务描述应尽量包含四部分：

- 目标
- 范围
- 约束
- 验证

推荐模板：

```text
目标：修复/实现……
范围：只改 …… 相关代码，优先复用现有实现，不要扩散修改
约束：不要做无关重构；不要新增不必要文件；不要提交 commit
验证：运行 …… 测试/命令，并说明结果
如果发现我的判断有误，直接指出
```

为什么这样更有效：

- Claude Code 的默认任务假设就是“软件工程任务”，不是纯文本问答，所以它更擅长处理“目标 + 范围 + 约束 + 验证”这种工程化输入。
- 这能直接减少 runtime 在“到底该分析、实现、还是重构”之间的歧义，也更符合它内部的 `tool execution` 和验证链路。

源码依据：

- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L221) 明确把用户请求理解为软件工程任务
- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L230) 强调先读代码再提改动
- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L240) 强调如实报告验证结果

## 2. 最值得长期使用的几条提示

### 2.1 明确限制范围

```text
只修这个问题，不做顺手重构，不改无关逻辑。
```

为什么这样更有效：

- Claude Code 的默认倾向是“完成任务”，如果范围不清，它有时会顺手清理周边代码。
- 源码里的系统提示明确要求不要做额外 feature、重构和“improvements（顺手优化）”，所以把范围写死，会让它更贴近最小修改路径。

源码依据：

- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L200)
- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L203)

### 2.2 明确要求先读代码

```text
先看 src/foo.ts 和 src/bar.ts，再决定改法。
```

为什么这样更有效：

- 这套系统明确偏好“先理解现有实现，再修改”，而不是凭需求直接猜改法。
- 你提前点名关键文件，相当于替 runtime 缩小探索范围，减少无关搜索和上下文噪音。

源码依据：

- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L230)
- [messages.ts](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3344)

### 2.3 明确优先复用

```text
优先复用现有函数、工具或模式，不要新造一套抽象。
```

为什么这样更有效：

- Claude Code 的系统提示对“过早抽象（premature abstraction）”和“一次性 helper”是明显负向约束。
- 这意味着你显式要求复用现有实现时，它更容易顺着仓库已有结构走，而不是新开一层抽象。

源码依据：

- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L203)
- [messages.ts](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3344)

### 2.4 明确不要新建文件

```text
除非绝对必要，不要新建文件。
```

为什么这样更有效：

- 系统提示里明确把“尽量编辑已有文件，避免 file bloat（文件膨胀）”作为默认偏好。
- 对小改动尤其有效，因为它能防止模型通过新增 helper / doc / temp file 来绕开原有结构。

源码依据：

- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L231)

### 2.5 明确验证要求

```text
改完后跑相关测试，并如实说明通过/失败情况。
```

为什么这样更有效：

- Claude Code 的系统提示对“未验证却声称完成”是强约束。
- 你把验证要求写进 prompt，会让它更倾向于真的执行测试或明确声明“没跑”。

源码依据：

- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L211)
- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L240)

## 3. 面向不同任务的推荐 prompt

### Bug 修复

```text
定位并修复这个问题：……
要求最小改动，优先复用现有逻辑，不要重构无关代码。
修完后运行相关测试并说明结果。
```

为什么这样更有效：

- Bug 修复任务最怕范围漂移。把“最小改动 + 验证结果”写清楚，能压住它的重构冲动。

源码依据：

- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L200)
- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L240)

### 新功能实现

```text
实现这个功能：……
先看现有相关模块，尽量沿用已有模式。
只改必要文件，不要额外加抽象层。
最后告诉我改动点和验证方式。
```

为什么这样更有效：

- 新功能比 bug 修复更容易触发“顺手设计一整套”的倾向，所以要显式强调沿用已有模式和最小必要抽象。

源码依据：

- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L203)
- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L230)

### 代码分析

```text
先不要改代码。分析这块实现：
- 主调用链
- 关键状态流转
- 风险点
- 如果要改，最小切入点在哪
给我结论导向的分析，不要泛泛而谈。
```

为什么这样更有效：

- 先明确“不要改代码”，可以把行为从 execution mode（执行模式）切到 analysis mode（分析模式）。
- Claude Code 对结论导向分析是有偏好的，但如果不写清楚，它可能会直接进入实现。

源码依据：

- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L221)
- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L230)

### 方案设计

```text
先不要实现。先快速读关键文件，给我一个可执行计划：
- 改哪些文件
- 复用哪些现有函数
- 风险点是什么
- 怎么验证
如果有问题，一次性问我，不要一条条追问。
```

为什么这样更有效：

- 这套 runtime 内部对 Plan Mode（计划模式）有很明确的探索流程：先读代码，再写计划，再只问代码解决不了的问题。
- 按这个模板提需求，最接近源码里原生的 plan workflow（计划工作流）。

源码依据：

- [messages.ts](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3336)
- [messages.ts](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3350)

## 4. 这套源码反映出的使用偏好

从系统提示可以明显看出，它更偏好：

- 结论导向，而不是长篇铺垫
- 任务边界清楚，而不是开放式模糊描述
- 先用专用工具，再用 Bash
- 先定位问题，再决定改法
- 先小范围试探，再扩大修改

所以和它交互时：

- 不要把需求写成口号式指令
- 不要只给模糊目标却不给边界
- 不要把“分析”和“实现”混在一句话里又不说明先后

为什么会形成这些偏好：

- 系统提示把“软件工程任务”设成默认场景
- 明确偏向 dedicated tools（专用工具）而不是 Bash
- 明确偏向“先读代码、再改代码”
- 明确反对“premature abstraction（过早抽象）”

源码依据：

- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L221)
- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L230)
- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L301)
- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L305)

## 5. 针对 Bash / 文件编辑的额外技巧

从 BashTool 的约束看，有几个实用结论：

- 如果希望它少走 shell，明确说“优先直接读写文件，不要用 bash 做文件编辑”
- 如果担心误操作，明确说“不要运行 destructive git commands”
- 如果不希望它提交代码，直接写“不要 commit / push”

推荐附加句：

```text
优先直接读写文件，不要用 bash 做本可由专用工具完成的事情。
不要执行 destructive git 命令，也不要 commit。
```

为什么这样更有效：

- 在源码里，Bash 被明确设定为 fallback tool（兜底工具），不是首选。
- 这不只是风格问题，而是因为 dedicated tools 更容易被审查、被解释、被权限系统约束。
- 对 destructive git commands（破坏性 git 命令），系统提示也明确要求优先考虑更安全替代方案。

源码依据：

- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L301)
- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L305)
- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L310)
- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L258)
- [BashTool prompt](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts#L297)

## 6. 一句通用增强指令

如果只想附一小句，我最推荐这一句：

```text
先读相关代码再改；优先复用现有实现；做最小必要改动；验证后如实汇报。
```

为什么这一句有效：

- 这句话几乎把源码里最稳定的行为约束压成了一句：
  - 先读代码
  - 少做无关改动
  - 少做过早抽象
  - 做完要验证
- 它不会过度限制模型，但能显著减少“改太多、想太多、报太满”这几类常见偏差。

源码依据：

- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L203)
- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L230)
- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L240)

## 7. 额外两条高价值技巧

### 7.1 能并行的查询就明确允许 parallel（并行）

推荐写法：

```text
如果这些查询彼此独立，可以并行完成；不要重复做相同搜索。
```

为什么这样更有效：

- Claude Code 的系统提示明确鼓励 independent tool calls（独立工具调用）并行化。
- 在 Bash prompt 和 agent / plan 提示里，也都强调能并行就并行，避免无谓串行和重复搜索。

源码依据：

- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L310)
- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L319)
- [BashTool prompt](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts#L298)

### 7.2 高风险动作要显式写“先确认”

推荐写法：

```text
涉及 push、删除、覆盖、外部发送、破坏性 git 操作时，先告诉我并确认。
```

为什么这样更有效：

- 系统提示对 reversibility（可逆性）和 blast radius（影响范围）看得很重。
- 这类动作在源码里默认就是需要确认的，除非用户显式授权更高自主性。

源码依据：

- [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L258)
