# Claude Code 源码调研提纲

这份提纲服务的目标不是“让听众完整理解 Claude Code 源码”，而是：

> 通过足够的源码理解，帮助用户和团队更好地使用 Claude Code。

因此，这份提纲采用下面的主次关系：

- 源码架构与工作流：前置讲清，但不占过高比重
- 功能、产出、使用方式、开发流程建议：作为主线
- 代码证据：为技巧和判断提供支撑，不单独做代码炫技

推荐总时长：50-65 分钟  
推荐总页数：45-55 页

对应正文：

- [09-Claude Code 源码深度解读-文档.md](/Users/bobo/code/claude-code-source-code/docs/zh/09-Claude%20Code%20源码深度解读-文档.md)

建议最终 PPT 主结构：

1. 总体架构：先讲整体架构，再讲主要子架构和模块
2. 工作流程：先讲总流程，再讲关键步骤和子流程
3. 功能介绍：功能分类列表，主要功能介绍
4. 产出：主要产出，适合的任务
5. 开发流程建议：怎样组织任务、边界、验证和协作
6. 代码走读概略：代码架构、主要模块、建议阅读顺序

这份提纲同时也是一份“逐页脚本版”材料，目标是：

- 提纲里的内容应当足以直接做成 PPT
- 如果一页需要图、代码块或重点说明，提纲里会显式写出
- 调整 PPT 时，应优先删减或重排表达，而不是再回头补内容骨架

每一页在提纲里尽量包含下面这些信息：

- 这一页要回答的问题
- 核心内容
- 必要时的关键代码片段
- 代码理解支撑
- 希望听众带走什么

也就是说，提纲不只是“页标题列表”，而应该已经接近“页面正文”。

## 术语对照

| 英文术语 | 中文对照 |
| --- | --- |
| `terminal agent runtime` | 终端代理运行时 |
| `bootstrap / assembly` | 启动装配 |
| `conversation host` | 会话宿主 |
| `turn loop` | 轮次循环 |
| `runtime kernel` | 运行时内核 |
| `tool pipeline` | 工具执行流水线 |
| `control plane` | 控制面 |
| `capability surface` | 能力面 |
| `prompt stack` | 提示词栈 |
| `context compaction` | 上下文压缩 |
| `transcript / recovery` | 会话记录 / 恢复 |
| `content replacement` | 内容替换 |
| `task runtime` | 任务运行时 |
| `Plan Mode workflow` | 规划模式工作流 |
| `software engineering tasks` | 软件工程任务 |

---

# 第一部分：总体架构（8 页）

## 第 1 页：封面

**标题**
- `Claude Code 源码调研`

**副标题**
- `总体架构、工作流程、功能设计、产出形态与开发流程建议`

**这一页要讲什么**
- 这不是单纯的源码分享。
- 目标是先用源码建立正确心智模型，再把重点落到“怎么更好地用 Claude Code”。

**希望听众带走什么**
- 后面讲代码，不是为了讲代码本身，而是为了推出更有效的使用方式。

## 第 2 页：这次调研真正要解决的问题

**这一页要回答的问题**
- 为什么同样是 Claude Code，有的人越用越顺，有的人越用越乱。

**核心内容**
- 因为 Claude Code 不是自由聊天助手。
- 它更像一套 `terminal agent runtime（终端代理运行时）`。
- 输入方式、任务组织方式、边界表达方式，都会直接影响它的输出质量。

**希望听众带走什么**
- 这场分享的目标不是“理解全部源码”，而是“理解到足够会用”。

## 第 3 页：先给结论：Claude Code 到底是什么

**这一页要回答的问题**
- Claude Code 从工程上应该怎么理解。

**核心内容**
- 它不是普通聊天 CLI。
- 它更像由下面几层组成的 runtime：
  - `main.tsx`：启动装配
  - `QueryEngine.ts`：会话宿主
  - `query.ts`：轮次循环 / 运行时内核
  - `toolExecution.ts`：工具执行流水线
  - settings / auth / policy / prompt：控制面

**代码支撑**
- [src/main.tsx](/Users/bobo/code/claude-code-source-code/src/main.tsx)
- [src/QueryEngine.ts](/Users/bobo/code/claude-code-source-code/src/QueryEngine.ts)
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)
- [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)

**代码理解支撑**
- 只有当装配、宿主、执行和控制面同时存在时，才更接近 runtime，而不是普通 CLI wrapper。

**希望听众带走什么**
- Claude Code 的使用方式，必须贴合它的运行时结构。

## 第 4 页：总结构图：Claude Code 的主执行链

**这一页要回答的问题**
- 用户输入之后，系统内部到底穿过了哪些层。

**核心内容**
- 用户输入不是直接给模型。
- 会依次穿过：
  - `prompt stack`
  - `QueryEngine`
  - `query.ts turn loop`
  - `tool pipeline`
  - tools / tasks / execution environment
- 旁边持续有：
  - settings / auth / policy
  - transcript / observability

**建议配图**
- 一张总结构图，画出主执行链和控制面。

**代码理解支撑**
- 这条链是由 `main.tsx -> QueryEngine.ts -> query.ts -> toolExecution.ts` 以及外围模块共同构成的。

**希望听众带走什么**
- 后面所有技巧，本质上都是在影响这条主执行链。

## 第 5 页：整体架构中的主要模块

**这一页要回答的问题**
- Claude Code 的整体架构拆开之后，最值得优先认识哪些模块。

**核心内容**
- 启动装配：`main.tsx`
- 会话宿主：`QueryEngine.ts`
- 轮次推进：`query.ts`
- 工具执行链：`toolExecution.ts`
- 控制面：settings / auth / policy / prompt
- 扩展与续航：skills / MCP / plugins / transcript / recovery / tasks

**代码理解支撑**
- 这些模块共同定义了 Claude Code 的真实运行形态，也构成了后面工作流程、功能和使用技巧的代码基础。

**希望听众带走什么**
- 后面的工作流程和主要功能，都会回到这些核心模块上。

## 第 6 页：`main.tsx`、`QueryEngine.ts`、`query.ts` 的分工

**这一页要回答的问题**
- 这三个文件为什么必须区分开理解。

**核心内容**
- `main.tsx`：装配系统
- `QueryEngine.ts`：持有会话状态
- `query.ts`：推进单轮执行

**关键代码片段**

```ts
export class QueryEngine {
  private mutableMessages: Message[]
  private totalUsage: NonNullableUsage
  private readFileState: FileStateCache
}
```

```ts
type State = {
  messages: Message[]
  toolUseContext: ToolUseContext
  turnCount: number
  transition: Continue | undefined
}
```

**代码理解支撑**
- 一个管装配、一个管寿命、一个管推进，这种分工直接决定了 Claude Code 为什么不像“一次性问答器”。

**希望听众带走什么**
- 理解好这三层，后面的工作流和技巧都会更自然。

## 第 7 页：控制面为什么重要

**这一页要回答的问题**
- 为什么 Claude Code 的行为边界不是只由模型决定。

**核心内容**
- 它有完整的 `control plane（控制面）`：
  - settings
  - auth
  - policy limits
  - managed settings
  - prompt stack

**代码支撑**
- [src/utils/settings/settings.ts](/Users/bobo/code/claude-code-source-code/src/utils/settings/settings.ts)
- [src/utils/auth.ts](/Users/bobo/code/claude-code-source-code/src/utils/auth.ts)
- [src/services/policyLimits/index.ts](/Users/bobo/code/claude-code-source-code/src/services/policyLimits/index.ts)
- [src/utils/systemPrompt.ts](/Users/bobo/code/claude-code-source-code/src/utils/systemPrompt.ts)

**代码理解支撑**
- 这些模块都能直接影响工具可用性、组织限制和系统行为，因此“边界”不是口头说说，而是代码里的真实裁决链。

**希望听众带走什么**
- 用 Claude Code 时，很多“为什么它这样做”，其实来自控制面，而不是模型好坏。

## 第 8 页：架构小结

**这一页要回答的问题**
- 为什么前面这部分要先讲。

**核心内容**
- 因为只有先建立：
  - 它是什么
  - 它怎么分层
  - 哪些层在裁决行为
- 后面讲使用技巧才不会变成经验帖。

**希望听众带走什么**
- 源码理解是铺垫，真正目的是服务后面的使用与协作。

---

# 第二部分：工作流程（8 页）

## 第 9 页：一次请求从哪里开始

**这一页要回答的问题**
- 用户输入之后，第一步发生了什么。

**核心内容**
- 输入进入 CLI / REPL
- 先过 settings / auth / policy
- 构造 tools / commands / app state
- 然后才进入 `QueryEngine` 和 `query.ts`

**代码理解支撑**
- 在 `main.tsx` 和 `QueryEngine.ts` 里，请求处理明显早于模型调用就已经开始。

**希望听众带走什么**
- 这解释了为什么相同提示词在不同环境下可能表现不同。

## 第 10 页：工作流程总图

**这一页要回答的问题**
- 一次完整请求的主链是什么。

**核心内容**
- 上下文整理
- 模型采样
- 工具执行
- 结果回灌
- 继续推进 / 停止 / 压缩 / 恢复

**建议配图**
- 一张总流程图。

**代码理解支撑**
- 这不是概念图，而是对 `query.ts` 主循环和 `toolExecution.ts` 执行链的压缩表达。

**希望听众带走什么**
- Claude Code 的工作流天然就是多轮的。

## 第 11 页：`turn loop（轮次循环）` 的基本闭环

**这一页要回答的问题**
- 一轮 loop 的最基本闭环是什么。

**核心内容**
- 当前 messages
- context shaping
- API request
- assistant / tool_use
- tool_result 回灌
- next turn

**代码支撑**
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)

**代码理解支撑**
- `query.ts` 反复围绕 messages、tool context、transition 推进，因此 loop 是文件真实形态，不是分析者措辞。

**希望听众带走什么**
- Claude Code 的强项不是“回答”，而是“推进”。

## 第 12 页：为什么它不是线性流水线

**这一页要回答的问题**
- 为什么不能把它当普通“工具调用链”看。

**核心内容**
- 主流程中途要处理：
  - `prompt_too_long`
  - `max_output_tokens`
  - continuation
  - stop hook
  - reactive compact

**代码理解支撑**
- 这些迁移分支都在 `query.ts` 的状态推进逻辑里，是正向路径的一部分。

**希望听众带走什么**
- Claude Code 更像 `recovery graph（恢复图）`，不是简单 pipeline。

## 第 13 页：context shaping（上下文整理）是怎么发生的

**这一页要回答的问题**
- 模型每轮到底看到了什么。

**核心内容**
- 模型看到的不是静态聊天记录，而是动态构造的工作面：
  - prompt stack
  - attachments
  - relevant memories
  - invoked skills
  - system reminders

**代码支撑**
- [src/utils/attachments.ts](/Users/bobo/code/claude-code-source-code/src/utils/attachments.ts)
- [src/utils/systemPrompt.ts](/Users/bobo/code/claude-code-source-code/src/utils/systemPrompt.ts)

**代码理解支撑**
- attachments 和 system prompt sections 都是按 turn 重新拼接的，这直接解释了为什么 Claude Code 的上下文表现和普通聊天工具不同。

**希望听众带走什么**
- 用户写 prompt，不是在给一个静态聊天机器人发消息，而是在参与当前轮工作面的构造。

## 第 14 页：tool pipeline（工具执行流水线）如何推进

**这一页要回答的问题**
- 工具调用为什么不是直接 `tool.call()`。

**核心内容**
- 工具调用会经过：
  - input parse
  - validate
  - hooks
  - permissions / classifier
  - `tool.call()`
  - post process

**代码支撑**
- [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)

**代码理解支撑**
- 这条链说明 Claude Code 最在意的是“动作如何被审查和约束”，而不是最快把命令打出去。

**希望听众带走什么**
- 用户把边界写清楚，能直接帮助这条执行链更稳定工作。

## 第 15 页：transcript / recovery / compact 在流程里的位置

**这一页要回答的问题**
- 为什么长会话能继续，为什么中断后能恢复。

**核心内容**
- transcript 保存的是可恢复消息链
- recovery 的目标是回到 API 可继续状态
- compact 的目标是重建还能工作的最小 context

**代码支撑**
- [src/utils/sessionStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/sessionStorage.ts)
- [src/utils/conversationRecovery.ts](/Users/bobo/code/claude-code-source-code/src/utils/conversationRecovery.ts)
- [src/services/compact/compact.ts](/Users/bobo/code/claude-code-source-code/src/services/compact/compact.ts)

**代码理解支撑**
- 这些模块不是边缘工具，而是主流程续航机制，因此 Claude Code 才能支持长任务和断点续做。

**希望听众带走什么**
- “长期工作”是这套系统的显式设计目标。

## 第 16 页：工作流程小结

**这一页要回答的问题**
- 为什么理解工作流对使用方式有帮助。

**核心内容**
- 因为 Claude Code 不是把一句话直接变成一句话。
- 它要把请求变成一个可以持续推进、可约束、可恢复的工作过程。

**希望听众带走什么**
- 用户越理解这套工作流，越知道什么样的任务组织方式更有效。

---

# 第三部分：功能介绍（功能分类列表 + 主要功能）

## 第 17 页：Claude Code 有哪些功能面

**这一页要回答的问题**
- Claude Code 的能力应该怎么分类理解。

**核心内容**
- 交互
- 执行
- 扩展
- 控制
- 续航
- 可观测性

**代码理解支撑**
- 这些功能面都能直接回到 commands、tools、MCP、policy、recovery、profiling 等模块，不是随意分类。

**希望听众带走什么**
- 功能多本身不重要，关键是这些能力能围绕主执行链协同。

## 第 18 页：功能分类小结

**这一页要回答的问题**
- 为什么要先按功能面理解 Claude Code，而不是直接按目录或文件讲。

**核心内容**
- 因为功能面更接近用户会感知到的能力：
  - 交互
  - 执行
  - 扩展
  - 控制
  - 续航
  - 可观测性

**代码理解支撑**
- 这些功能面都可以回到 commands、tools、MCP、policy、recovery、profiling 等模块，不是随意分类。

**希望听众带走什么**
- 先理解功能面，再理解主要功能，后面讲产出和建议时会更自然。

---

# 第三部分续：主要功能介绍

## 第 23 页：Prompt Stack（提示词栈）

**功能**
- 定义系统默认行为与角色

**实现原理**
- default prompt、override prompt、agent prompt、dynamic sections 叠加

**关键代码片段**

```ts
The user will primarily request you to perform software engineering tasks.
```

**代码支撑**
- [src/utils/systemPrompt.ts](/Users/bobo/code/claude-code-source-code/src/utils/systemPrompt.ts)
- [src/constants/prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts)

**使用技巧**
- 任务表达越工程化越好
- 范围、约束、验证越明确越好

**代码理解支撑**
- 默认 system prompt 直接把用户请求定义成软件工程任务，因此“工程化表达更稳”不是经验，而是系统默认角色的直接结果。

## 第 24 页：Turn Loop（轮次循环）

**功能**
- 推进一轮轮 agent 执行

**实现原理**
- 维护 state、transition、toolUseContext、recovery 分支

**关键代码片段**

```ts
type State = {
  messages: Message[]
  toolUseContext: ToolUseContext
  pendingToolUseSummary: Promise<ToolUseSummaryMessage | null> | undefined
  stopHookActive: boolean | undefined
  turnCount: number
  transition: Continue | undefined
}
```

**代码支撑**
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)

**使用技巧**
- 大任务要拆阶段
- 输入要清楚到足以支持持续推进

**代码理解支撑**
- `State` 里保存的是跨轮迁移状态，不只是消息，因此 Claude Code 天然更适合可继续推进的任务，而不是模糊一次性请求。

## 第 25 页：Tool Pipeline（工具执行流水线）

**功能**
- 把工具能力放进可约束的执行链

**实现原理**
- schema parse -> validate -> hooks -> permissions -> call -> post process

**关键代码片段**

```ts
const parsedInput = tool.inputSchema.safeParse(input)
...
runPreToolUseHooks(...)
...
resolveHookPermissionDecision(...)
...
tool.call(...)
```

**代码支撑**
- [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)

**使用技巧**
- 能用专用工具就别默认 Bash
- 高风险动作要写清确认方式

**代码理解支撑**
- 工具调用先经过 parse、hooks、permissions、classifier，再到真正执行，因此边界写清楚，会直接帮助执行链更稳定。

## 第 26 页：BashTool

**功能**
- 提供最强但风险最高的执行能力

**实现原理**
- sandbox、只读识别、路径校验、破坏性判断、长输出处理

**代码支撑**
- [src/tools/BashTool/BashTool.tsx](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/BashTool.tsx)
- [src/tools/BashTool/prompt.ts](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts)

**使用技巧**
- 不要把 Bash 当默认第一选择
- 破坏性操作一定要单独写明

**代码理解支撑**
- BashTool 周围专门拆出安全子模块，说明它在系统里被视为高能力高风险工具，而不是普通执行路径。

## 第 27 页：Compact（上下文压缩）

**功能**
- 控制长会话上下文体积

**实现原理**
- microcompact、autocompact、reactive compact、summary + attachments 重建工作面

**代码支撑**
- [src/services/compact/compact.ts](/Users/bobo/code/claude-code-source-code/src/services/compact/compact.ts)
- [src/services/compact/microCompact.ts](/Users/bobo/code/claude-code-source-code/src/services/compact/microCompact.ts)

**使用技巧**
- 长任务要接受上下文会被重构
- 不要假设模型永远保留全部细节

**代码理解支撑**
- compact 保留的不只是 summary，还有 boundary、tail messages、attachments，这说明它在重建工作面，而不是简单摘要。

## 第 28 页：Transcript / Recovery

**功能**
- 保证会话可以恢复

**实现原理**
- transcript 链、parentUuid、orphan recovery、synthetic continuation

**关键代码片段**

```ts
const filteredToolUses = filterUnresolvedToolUses(migratedMessages)
const filteredThinking =
  filterOrphanedThinkingOnlyMessages(filteredToolUses)
```

**代码支撑**
- [src/utils/sessionStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/sessionStorage.ts)
- [src/utils/conversationRecovery.ts](/Users/bobo/code/claude-code-source-code/src/utils/conversationRecovery.ts)

**使用技巧**
- 长任务和断点续做是 Claude Code 的强项之一
- 可以放心把它用于需要多轮推进的任务

**代码理解支撑**
- recovery 会主动修复 unresolved tool use、thinking、continuation 等状态，这种深度说明“继续工作”是底层能力。

## 第 29 页：Content Replacement（内容替换）

**功能**
- 控制大工具输出，不让上下文失控

**实现原理**
- 大结果落盘、preview replacement、fate freezing、resume replay

**关键代码片段**

```ts
export type ContentReplacementState = {
  seenIds: Set<string>
  replacements: Map<string, string>
}
```

**代码支撑**
- [src/utils/toolResultStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/toolResultStorage.ts)
- [src/services/compact/microCompact.ts](/Users/bobo/code/claude-code-source-code/src/services/compact/microCompact.ts)

**使用技巧**
- 不要要求模型永远在上下文里保留完整大输出
- 更关注最终结果，而不是每一轮完整原文

**代码理解支撑**
- replacement state 显式记录 `seenIds` 和 `replacements`，说明系统在维护“看过的前缀不能漂”，因此输出治理是运行时核心约束。

## 第 30 页：Skills（技能）

**功能**
- 把提示词能力做成条件激活 artifact

**实现原理**
- `loadSkillsDir.ts` 载入，按路径或上下文激活，compact 后保留 invoked skills

**代码支撑**
- [src/utils/skills/loadSkillsDir.ts](/Users/bobo/code/claude-code-source-code/src/utils/skills/loadSkillsDir.ts)
- [src/utils/attachments.ts](/Users/bobo/code/claude-code-source-code/src/utils/attachments.ts)

**使用技巧**
- skill 更适合用于有明显任务边界的场景
- 它不是一段“快捷短语”，而是一种能力面提示

**代码理解支撑**
- skills 会被按路径、上下文和 compact 结果激活与保留，这说明它们是运行时能力对象，而不是静态 prompt 模板。

## 第 31 页：Attachments（上下文附件）

**功能**
- 动态组装当前轮上下文

**实现原理**
- relevant memories、skill delta、system reminders、task messages、file attachments

**代码支撑**
- [src/utils/attachments.ts](/Users/bobo/code/claude-code-source-code/src/utils/attachments.ts)

**使用技巧**
- 不要把 Claude Code 当“只看聊天记录”的系统
- 当前轮的任务组织方式会直接影响它看到的上下文

**代码理解支撑**
- attachments 会注入 memories、skill delta、task messages、system reminders，说明上下文是逐轮构造的工作面。

## 第 32 页：Permissions / Hooks / Classifier

**功能**
- 决定模型能否继续代表用户行动

**实现原理**
- allow / ask / deny、hook pre/post、classifier 决策链、auto mode

**代码支撑**
- [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)
- [src/utils/permissions/permissions.ts](/Users/bobo/code/claude-code-source-code/src/utils/permissions/permissions.ts)

**使用技巧**
- 高风险动作要写清楚
- 模糊授权会显著放大不确定性

**代码理解支撑**
- permissions、hooks、classifier 都位于工具执行链中，说明真正的自主边界在 runtime 内部，而不是口头提醒。

## 第 33 页：Tasks / Subagents / Mailbox

**功能**
- 把异步执行体变成一等对象

**实现原理**
- task registry、local/remote agent、sidechain transcript、mailbox protocol

**代码支撑**
- [src/Task.ts](/Users/bobo/code/claude-code-source-code/src/Task.ts)
- [src/utils/task/framework.ts](/Users/bobo/code/claude-code-source-code/src/utils/task/framework.ts)
- [src/tools/AgentTool/runAgent.ts](/Users/bobo/code/claude-code-source-code/src/tools/AgentTool/runAgent.ts)

**使用技巧**
- 复杂任务适合拆成阶段或子任务
- Claude Code 很适合做持续推进，而不是只做一次性答复

**代码理解支撑**
- task registry、agent metadata、mailbox、sidechain transcript 同时存在，说明它已经有多执行体 runtime 的雏形。

## 第 34 页：MCP / Plugins / Remote Capability

**功能**
- 把 Claude Code 扩展成能力枢纽

**实现原理**
- MCP client、plugin loader、remote session / remote agent

**代码支撑**
- [src/services/mcp/client.ts](/Users/bobo/code/claude-code-source-code/src/services/mcp/client.ts)
- [src/utils/plugins/pluginLoader.ts](/Users/bobo/code/claude-code-source-code/src/utils/plugins/pluginLoader.ts)

**使用技巧**
- Claude Code 的上限不仅取决于模型，也取决于能接入哪些能力面

**代码理解支撑**
- MCP、plugins、remote capability 各有接入点，说明扩展能力在系统里是一级设计目标。

## 第 35 页：重要功能小结

**这一页要回答的问题**
- 为什么前面这些功能值得逐个讲。

**核心内容**
- 因为它们共同决定了：
  - 系统如何继续工作
  - 用户如何更稳地使用它
  - 哪些边界必须显式表达

**希望听众带走什么**
- 真正的“使用技巧”，必须回到运行时机制上理解。

---

# 第四部分：产出（主要产出 + 适合的任务）

## 第 36 页：从用户视角看，Claude Code 最典型的产出是什么

**这一页要回答的问题**
- Claude Code 最擅长产出什么结果。

**核心内容**
- 代码修改
- 代码解释与定位结论
- 调试与排障结论
- 命令执行与验证结果
- 计划、任务拆解、review 结论
- 结构化输出与工作卡

**代码理解支撑**
- commands、Edit/Read/Bash、structured output、Plan Mode、task runtime 在代码里都明确存在，说明它默认就围绕工程结果设计。

**希望听众带走什么**
- Claude Code 最适合被当作工程产出生成器。

## 第 37 页：哪些任务特别适合 Claude Code

**这一页要回答的问题**
- 哪类任务最能发挥这套系统的优势。

**核心内容**
- 局部修复与重构
- 多文件追踪与定位
- 命令执行与验证
- 需要拆阶段推进的任务
- 需要形成“代码 + 解释 + 验证”的任务

**代码理解支撑**
- 这些任务之所以适合，是因为它们天然贴合 `tool pipeline + plan + task runtime + recovery` 这几条主能力链。

**希望听众带走什么**
- 越像工程任务，Claude Code 越容易发挥。

## 第 38 页：哪些任务不适合用 Claude Code 直接硬做

**这一页要回答的问题**
- 哪些任务形态会让 Claude Code 失稳。

**核心内容**
- 目标极度模糊
- 范围完全不受限
- 对输出形式没有约束
- 要求它自行理解隐含边界
- 高风险动作但没给确认规则

**代码理解支撑**
- 由于 prompt stack、tool pipeline、permission chain 都期待更明确的任务边界，模糊任务天然更容易产生漂移。

**希望听众带走什么**
- Claude Code 不是不能做难任务，而是难任务更需要结构化地给它。

## 第 39 页：为什么它能稳定地产出这些结果

**这一页要回答的问题**
- Claude Code 为什么比普通聊天系统更容易产出稳定工程结果。

**核心内容**
- 默认角色是工程代理
- 工具执行受约束
- 结果可进入 transcript / compact / recovery
- plan、task、memory 支持多阶段工作

**代码支撑**
- [src/constants/prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts)
- [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)
- [src/utils/sessionStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/sessionStorage.ts)
- [src/utils/messages.ts](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts)

**代码理解支撑**
- 角色定义、执行链、续航链和任务链一起存在，决定了 Claude Code 更容易产出“工作结果”，而不是发散回答。

**希望听众带走什么**
- 稳定产出来自运行时结构，不只是模型强。

## 第 40 页：产出小结

**这一页要回答的问题**
- 从用户视角，前面这些产出和适用任务能压成什么结论。

**核心内容**
- Claude Code 最适合用来推进工程任务
- 它特别适合产出“代码 + 解释 + 验证 + 计划”
- 它不适合完全模糊、完全无边界的自由发挥

**希望听众带走什么**
- 先理解产出形态，再谈技巧，效果会更稳。

---

# 第五部分：开发流程建议

## 第 41 页：为什么要单独讲“开发流程建议”

**这一页要回答的问题**
- 为什么最后还要讲“建议”，而不是停在架构和功能。

**核心内容**
- 因为 Claude Code 最终是用来协作和产出的。
- 只有把前面的 runtime 逻辑翻译成工作流建议，分享才真正落地。

**希望听众带走什么**
- 这一部分不是“经验汇总”，而是从源码约束倒推出的协作方式。

## 第 42 页：建议一：把任务组织成工程任务，而不是聊天请求

**核心内容**
- 把任务写成：目标、范围、约束、验证
- 避免模糊话术和隐藏边界

**关键代码片段**

```ts
The user will primarily request you to perform software engineering tasks.
```

**代码理解支撑**
- system prompt 已经把用户请求定义成工程任务，因此任务表达越工程化，Claude Code 越接近默认最佳状态。

## 第 43 页：建议二：先读代码，再改代码

**核心内容**
- 明确要求先读关键文件
- 不要一上来就让它直接改

**关键代码片段**

```ts
In general, do not propose changes to code you haven't read.
```

**代码理解支撑**
- 这不是使用习惯，而是 prompt stack 明确写出的默认行为。

## 第 44 页：建议三：最小改动，优先复用

**核心内容**
- 明确要求最小必要改动
- 优先复用现有模式
- 不要默认允许顺手抽象

**关键代码片段**

```ts
Don't create helpers, utilities, or abstractions for one-time operations.
```

**代码理解支撑**
- Claude Code 默认就反对无边界“优化”和一锤子抽象，因此这条建议是顺着系统默认行为走。

## 第 45 页：建议四：专用工具优先，Bash 后置

**核心内容**
- 有 dedicated tools 时优先 dedicated tools
- Bash 是高能力、高风险通道

**关键代码片段**

```ts
Do NOT use the Bash tool when a relevant dedicated tool is provided.
```

**代码理解支撑**
- tool pipeline 与 BashTool 安全层共同说明：Claude Code 不是鼓励随时走 shell，而是鼓励可审查的执行路径。

## 第 46 页：建议五：验证要单独要求，而且结果要如实汇报

**核心内容**
- 验证不是默认一定会发生
- 验证结果要显式回报

**关键代码片段**

```ts
Report outcomes faithfully...
```

**代码理解支撑**
- 默认 prompt 直接约束结果汇报，因此“把验证写出来”是利用系统已有规则，而不是额外施压。

## 第 47 页：建议六：高风险动作一定要把确认规则写清楚

**核心内容**
- 删除、覆盖、push、外发等动作要明确确认
- 不要给模糊授权

**关键代码片段**

```ts
Carefully consider the reversibility and blast radius of actions.
```

**代码理解支撑**
- BashTool prompt、tool pipeline、permissions 都表明高风险动作是单独对待的，因此用户必须把这条边界写清。

## 第 48 页：建议七：复杂任务先走 Plan Mode

**核心内容**
- 先探索、再计划、后实现
- 不要在需求不清时直接让它开干

**代码支撑**
- [src/utils/messages.ts](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts)

**代码理解支撑**
- Plan workflow 明确把“探索现有实现、更新计划、再问缺失信息”做成了独立流程，这正是复杂任务更稳的原因。

## 第 49 页：建议八：独立查询允许并行，长任务允许分阶段推进

**核心内容**
- 独立查询可以 parallel
- 长任务适合拆阶段、拆子任务

**代码支撑**
- [src/utils/messages.ts](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts)
- [src/utils/task/framework.ts](/Users/bobo/code/claude-code-source-code/src/utils/task/framework.ts)

**代码理解支撑**
- 并行工具调用和 task runtime 都是系统一级能力，因此任务节奏设计会直接影响 Claude Code 的发挥。

## 第 50 页：建议九：哪些任务最适合直接交给 Claude Code

**核心内容**
- 局部修复
- 代码理解与定位
- 需要命令验证的任务
- 可分阶段推进的任务

**代码理解支撑**
- 这些任务正好贴合 prompt stack、tool pipeline、task runtime 和 recovery 的优势区间。

## 第 51 页：建议十：哪些任务要谨慎交给 Claude Code

**核心内容**
- 完全模糊的探索
- 范围极大的全局变更
- 高风险但边界不清的动作
- 需要大量隐性业务背景的任务

**代码理解支撑**
- Claude Code 不是不能做，而是这类任务更容易让 prompt stack、tool pipeline 和权限链都处在不稳定状态。

## 第 52 页：团队协作时，应该把 Claude Code 当成什么角色

**核心内容**
- 工程代理
- 多阶段任务推进器
- 带工具的验证者
- 文档、代码、验证结果的联合产出器

**代码理解支撑**
- commands、Plan Mode、task runtime、structured output、tool pipeline 都说明它更适合作为“协作型工程执行体”，而不是单纯聊天机器人。

## 第 53 页：开发流程建议小结

**核心内容**
- 先用少量源码理解建立正确模型
- 再把重心放到产出、使用方式和任务组织
- 所有真正有效的技巧，都可以回到代码机制解释

**希望听众带走什么**
- Claude Code 最值得学的，不只是它“会什么”，而是你怎样组织任务，才能让它稳定地产出高质量工程结果。

---

# 第六部分：代码走读概略

## 第 54 页：代码组织和架构概略

**这一页要回答的问题**
- 如果听众后续要自己读代码，应该先怎么建立代码组织视图。

**核心内容**
- 启动与装配：`main.tsx`
- 会话与执行：`QueryEngine.ts`、`query.ts`
- 工具与命令：`Tool.ts`、`tools.ts`、`commands.ts`
- 续航与恢复：`sessionStorage.ts`、`conversationRecovery.ts`、`compact/*`
- 扩展与控制：settings、auth、policy、MCP、plugins、skills

**希望听众带走什么**
- 先看代码分层，再看实现细节，效率会高很多。

## 第 55 页：建议的代码走读顺序

**这一页要回答的问题**
- 如果只给听众一条阅读路径，应该怎样安排顺序。

**核心内容**
1. `main.tsx`
2. `QueryEngine.ts`
3. `query.ts`
4. `toolExecution.ts`
5. `compact / recovery`
6. `commands / tools / MCP / tasks`

**代码理解支撑**
- 这条顺序是从装配、宿主、执行、恢复、扩展逐层展开，最容易建立完整心智模型。

**希望听众带走什么**
- 代码走读不应该按目录平铺，而应该按运行链和控制链阅读。

## 第 56 页：主要模块与重点文件

**这一页要回答的问题**
- 如果只能记住一组文件，应该记住哪些。

**核心内容**
- `main.tsx`
- `QueryEngine.ts`
- `query.ts`
- `toolExecution.ts`
- `BashTool.tsx`
- `compact.ts` / `microCompact.ts`
- `sessionStorage.ts` / `conversationRecovery.ts`
- `messages.ts`

**希望听众带走什么**
- 这组文件足以支撑一次高质量的 Claude Code 源码走读。
