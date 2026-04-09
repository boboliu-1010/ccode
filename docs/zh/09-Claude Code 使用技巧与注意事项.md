# Claude Code 使用技巧与注意事项

这份文档从源码角度总结 Claude Code 的用户侧使用技巧。目标不是重复功能列表，而是回答三个问题：

1. Claude Code 从工程实现上到底是什么
2. 它默认偏好的工作方式是什么
3. 作为使用者，怎样提需求和控制行为会更稳定

相关源码主要来自：

- [src/constants/prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts)
- [src/utils/messages.ts](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts)
- [src/tools/BashTool/prompt.ts](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts)
- [src/main.tsx](/Users/bobo/code/claude-code-source-code/src/main.tsx)
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)
- [src/QueryEngine.ts](/Users/bobo/code/claude-code-source-code/src/QueryEngine.ts)

## 1. 先看源码：Claude Code 到底是什么

如果只从使用者角度看，Claude Code 很像“能改代码的命令行助手”。  
但从源码看，它更准确的定位是一个 **terminal agent runtime（终端代理运行时）**，而不是简单的聊天壳。

它至少同时包含几层：

- **bootstrap / assembly（启动装配）**  
  由 [main.tsx](/Users/bobo/code/claude-code-source-code/src/main.tsx) 负责，把 settings、auth、policy、plugins、skills、MCP、tools 装起来。
- **conversation host（会话宿主）**  
  由 [QueryEngine.ts](/Users/bobo/code/claude-code-source-code/src/QueryEngine.ts) 负责，管理多轮消息、usage、file state、transcript。
- **turn loop（轮次循环） / runtime kernel（运行时内核）**  
  由 [query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts) 负责，真正推进一轮轮 `model -> tool -> model` 闭环。
- **tool pipeline（工具执行流水线）**  
  负责 schema、hooks、permissions、classifier、`tool.call()`、result processing。
- **control plane（控制面）**  
  包括 settings、auth、prompt stack、policy、managed settings。

这直接决定了一个很重要的使用结论：

> Claude Code 默认不是把你的输入当“闲聊”，而是当“软件工程任务”。

## 2. 从源码反推：Claude Code 默认偏好的工作方式

从 [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts) 和 [messages.ts](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts) 看，Claude Code 有几条非常稳定的默认偏好：

- 把用户请求理解成 **software engineering task（软件工程任务）**
- 偏好 **先读代码，再改代码**
- 偏好 **最小必要改动**
- 偏好 **复用已有实现**
- 偏好 **dedicated tools（专用工具）**，而不是默认走 Bash
- 偏好 **验证后如实汇报**
- 对 **高风险动作** 默认要求确认

所以从使用者角度，最重要的不是“写很厉害的 prompt”，而是：

> 让你的输入形式，尽量贴近它源码里默认支持的工作方式。

下面这些技巧，本质上都是从这些默认偏好里推出来的。

这里还需要补一个关键判断：这些偏好并不是“写在文档里好看”，而是直接进入了 Claude Code 的 **prompt stack（提示词栈）** 和 **tool pipeline（工具执行流水线）**。

- 在架构上，`prompts.ts` 定义的是运行时默认行为，不是普通帮助文案。
- 在执行上，`toolExecution.ts` 会把这些偏好变成实际的工具调用边界。
- 在计划场景里，`messages.ts` 又把 Plan Mode 的探索顺序写成显式工作流。

因此，后面每条技巧都可以同时从三层得到支持：

- **架构支撑**：它在系统里属于哪条控制链
- **源码文件**：哪一个文件在声明或强化这个偏好
- **关键代码点**：哪一段具体规则在约束模型行为

## 3. 使用技巧：怎样提需求，Claude Code 会更稳定

## 3.1 任务写成“目标 + 范围 + 约束 + 验证”

推荐写法：

```text
目标：修复/实现……
范围：只改 …… 相关代码
约束：不要做无关重构；不要新增不必要文件
验证：运行 …… 测试，并说明结果
```

为什么有效：

- Claude Code 的默认任务模型是“软件工程任务”，不是自由聊天。
- 明确范围和验证，能减少它在“分析 / 实现 / 顺手优化”之间摇摆。

架构支撑：

- 这条技巧对应的是 **prompt stack（提示词栈）** 里的默认任务定义和验收方式。

源码支撑：

- [prompts.ts#L221](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L221)：把用户请求理解成软件工程任务
- [prompts.ts#L230](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L230)：要求先读代码再改
- [prompts.ts#L240](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L240)：要求如实报告验证结果

关键代码点：

- `The user will primarily request you to perform software engineering tasks`
- `do not propose changes to code you haven't read`
- `Report outcomes faithfully`

## 3.2 明确要求“先读代码，再改代码”

推荐写法：

```text
先看 src/foo.ts 和 src/bar.ts，再决定改法。
```

为什么有效：

- 系统提示明确偏好“先理解现有实现，再修改”。
- 直接点名关键文件，可以减少无关探索和上下文噪音。

架构支撑：

- 这条技巧同时受 **prompt stack** 和 **Plan Mode workflow（计划模式工作流）** 约束。

源码支撑：

- [prompts.ts#L230](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L230)：要求先读代码
- [messages.ts#L3344](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3344)：Plan workflow 里先 Explore 现有代码

关键代码点：

- `do not propose changes to code you haven't read`
- `Explore — Use ... to read code`
- `Look for existing functions, utilities, and patterns to reuse`

## 3.3 明确强调“最小改动”和“优先复用”

推荐写法：

```text
做最小必要改动；优先复用现有函数、工具和模式；不要新造一层抽象。
```

为什么有效：

- Claude Code 明确反对 one-time helpers（一锤子 helper）和 premature abstraction（过早抽象）。
- 这会让它更愿意顺着现有结构修改，而不是顺手重构出一套新设计。

架构支撑：

- 这条技巧属于 **默认代码风格约束**，直接影响实现策略而不是输出措辞。

源码支撑：

- [prompts.ts#L200](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L200)：反对额外 feature / refactor / improvements
- [prompts.ts#L203](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L203)：反对 one-time abstraction
- [messages.ts#L3344](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3344)：鼓励寻找现有函数和模式复用

关键代码点：

- `Don't add features, refactor code, or make "improvements" beyond what was asked`
- `Don't create helpers, utilities, or abstractions for one-time operations`
- `Look for existing functions, utilities, and patterns to reuse`

## 3.4 能不新建文件，就不要新建文件

推荐写法：

```text
除非绝对必要，不要新建文件，优先修改现有文件。
```

为什么有效：

- 系统提示明确把“避免 file bloat（文件膨胀）”设成默认偏好。
- 对小改动尤其有效，因为它能减少通过额外 helper / doc / temp file 绕开现有结构的倾向。

架构支撑：

- 这条技巧仍然属于 **默认任务约束**，它控制的是修改范围和落盘方式。

源码支撑：

- [prompts.ts#L231](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L231)：优先编辑已有文件

关键代码点：

- `Do not create files unless they're absolutely necessary`
- `prefer editing an existing file to creating a new one`

## 3.5 优先 dedicated tools，不要默认走 Bash

推荐写法：

```text
优先直接读写文件，不要用 Bash 做本可由专用工具完成的事情。
```

为什么有效：

- 在源码里，Bash 被设定为 fallback tool（兜底工具），不是首选。
- 专用工具更容易被审查、被解释，也更容易受权限系统约束。

架构支撑：

- 这条技巧直接对应 **tool pipeline（工具执行流水线）** 的可审查性和可约束性。

源码支撑：

- [prompts.ts#L301](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L301)：有 dedicated tool 时优先 dedicated tool
- [prompts.ts#L305](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L305)：不要在有专用工具时用 Bash
- [BashTool prompt#L297](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts#L297)：Bash prompt 里也强调并行和正确使用方式

关键代码点：

- `default to using the dedicated tool`
- `Do NOT use the Bash tool when a relevant dedicated tool is provided`
- Bash prompt 明确把多命令并行、顺序和破坏性操作单独拿出来约束

## 3.6 验证要求要写清楚，而且要它如实汇报

推荐写法：

```text
改完后跑相关测试；如果没跑，请明确说明没有跑，不要默认当作成功。
```

为什么有效：

- 源码里对“未验证却宣称完成”是强约束。
- 这能减少“看起来完成了，但其实没验证”的风险。

架构支撑：

- 这条技巧属于 **结果汇报约束**，直接作用在最终答复质量上。

源码支撑：

- [prompts.ts#L211](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L211)：做完前要验证
- [prompts.ts#L240](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L240)：如实报告结果

关键代码点：

- `Before reporting a task complete, verify it actually works`
- `Never claim "all tests pass" when output shows failures`
- `say that rather than implying it succeeded`

## 3.7 独立查询要显式允许 parallel（并行）

推荐写法：

```text
如果这些查询彼此独立，可以并行完成；不要重复做相同搜索。
```

为什么有效：

- Claude Code 的系统提示明确鼓励 independent tool calls（独立工具调用）并行化。
- Bash prompt 和 Plan Mode 相关提示里也都强调能并行就并行。

架构支撑：

- 这条技巧属于 **工具调度策略** 和 **探索工作流策略**。

源码支撑：

- [prompts.ts#L310](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L310)：独立工具调用并行
- [prompts.ts#L319](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L319)：subagent 用于并行和保护上下文
- [messages.ts#L3344](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3344)：Plan workflow 里允许并行探索
- [BashTool prompt#L298](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts#L298)：Bash 提示里强调并行

关键代码点：

- `make all independent tool calls in parallel`
- `parallelize complex searches without filling your context`
- `If the commands are independent and can run in parallel`

## 3.8 高风险动作要显式要求“先确认”

推荐写法：

```text
涉及 push、删除、覆盖、外部发送、破坏性 git 操作时，先告诉我并确认。
```

为什么有效：

- 系统提示对 reversibility（可逆性）和 blast radius（影响范围）非常敏感。
- 只要动作难以回滚，默认就应该确认。

架构支撑：

- 这条技巧属于 **risk control（风险控制）** 和 **execution boundary（执行边界）**。

源码支撑：

- [prompts.ts#L258](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L258)：高风险动作默认先确认
- [BashTool prompt#L304](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts#L304)：破坏性 git 操作优先考虑安全替代方案

关键代码点：

- `Carefully consider the reversibility and blast radius of actions`
- `ask for confirmation before proceeding`
- `Only use destructive operations when they are truly the best approach`

## 3.9 做方案时，先走 Plan Mode 风格

推荐写法：

```text
先不要实现。先快速读关键文件，给我一个可执行计划；只问代码里无法确定的问题。
```

为什么有效：

- 源码里的 Plan Mode 明确规定：先 Explore（探索），再 Update plan（更新计划），最后再问用户代码里解决不了的问题。
- 用这种方式提需求，最接近系统原生的计划工作流。

架构支撑：

- 这条技巧对应 **Plan Mode（计划模式）** 的显式工作流，而不是一般 prompt 风格。

源码支撑：

- [messages.ts#L3336](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3336)：Iterative Planning Workflow
- [messages.ts#L3350](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3350)：First Turn 先扫描关键文件

关键代码点：

- `Explore -> Update the plan file -> Ask the user`
- `Start by quickly scanning a few key files`
- `Never ask what you could find out by reading the code`

## 4. 注意事项：这些误用最容易让 Claude Code 失稳

这部分不是技巧，而是从源码反推出来的常见误区。

### 4.1 不要把 Claude Code 当自由聊天助手来用

原因：

- 它的默认工作方式明显偏工程任务，不是开放式随聊。
- 如果你给的是模糊、无范围、无验证标准的任务，它更容易输出看似合理、但不稳定的结果。

源码支撑：

- [prompts.ts#L221](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L221)

### 4.2 不要一上来就让它“大改一遍”

原因：

- 系统提示明显偏向 minimal change（最小改动）。
- 范围越模糊，它越可能进入顺手重构或过度抽象。

源码支撑：

- [prompts.ts#L200](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L200)
- [prompts.ts#L203](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L203)

### 4.3 不要默认它已经验证过

原因：

- 即使源码里强约束了验证与如实汇报，用户侧仍然应该显式要求验证。
- 否则某些环境受限任务里，它可能会因为无法执行而只给分析结论。

源码支撑：

- [prompts.ts#L211](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L211)
- [prompts.ts#L240](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L240)

### 4.4 不要把高风险授权写得太含糊

原因：

- 源码里对高风险动作的默认策略就是先确认。
- 如果用户授权语句模糊，模型和执行边界都更容易漂。

源码支撑：

- [prompts.ts#L258](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L258)

## 5. 最后压成一个最小使用清单

如果只保留最该记住的 6 条：

1. 用“目标 + 范围 + 约束 + 验证”提任务
2. 明确要求先读代码
3. 明确要求最小改动、优先复用
4. 优先 dedicated tools，不要默认走 Bash
5. 验证结果要如实汇报
6. 高风险动作先确认
