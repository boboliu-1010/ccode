# Claude Code 源码调研提纲

这份提纲服务的目标不是“让听众完整理解 Claude Code 源码”，而是：

> 通过足够的源码理解，帮助用户和团队更好地使用 Claude Code。

因此，这份提纲采用下面的主次关系：

- 源码架构与工作流：前置讲清，但不占过高比重
- 功能、产出、使用方式、开发流程建议：作为主线
- 代码证据：为技巧和判断提供支撑，不单独做代码炫技

推荐总时长：45-60 分钟  
推荐总页数：38-42 页

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

# 第一部分：总体架构（6 页）

## 第 1 页：封面

**标题**
- `Claude Code 源码调研`

**副标题**
- `总体架构、工作流程、功能设计、产出形态与开发流程建议`

**这一页要回答的问题**
- 本次调研的价值是什么，它最终要帮助团队解决什么问题。

**核心内容**
- 这不是单纯的源码分享。
- 目标是先用源码建立正确心智模型，再把重点落到“怎么更好地用 Claude Code”。
- 听众不需要记住所有实现细节，但需要建立一套能直接指导使用和协作的理解框架。

**希望听众带走什么**
- 后面讲代码，不是为了讲代码本身，而是为了推出更有效的使用方式。

## 第 2 页：这次调研真正要解决的问题

**这一页要回答的问题**
- 为什么同样是 Claude Code，有的人越用越顺，有的人越用越乱。

**核心内容**
- 因为 Claude Code 不是自由聊天助手。
- 它更像一套 `terminal agent runtime（终端代理运行时）`。
- 输入方式、任务组织方式、边界表达方式，都会直接影响它的输出质量。
- 所以后面不会把重点放在“源码多复杂”，而会放在“什么理解能转化成更好的使用方式”。

**关键代码片段**

```ts
The user will primarily request you to perform software engineering tasks.
```

**代码理解支撑**
- 从默认 prompt 开始，Claude Code 就已经把用户任务当作软件工程任务来理解，因此用法是否贴合这个前提，会直接影响表现。

**希望听众带走什么**
- 本次调研不追求覆盖全部源码，而是提炼到足够指导使用的理解。

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

**关键代码片段**

```ts
export class QueryEngine {
  private mutableMessages: Message[]
  private totalUsage: NonNullableUsage
}

type State = {
  messages: Message[]
  toolUseContext: ToolUseContext
  transition: Continue | undefined
}
```

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

## 第 5 页：整体架构中的主要模块与分工

**这一页要回答的问题**
- Claude Code 的整体架构拆开之后，最值得优先认识哪些模块，它们的分工是什么。

**核心内容**
- 启动装配：`main.tsx`
- 会话宿主：`QueryEngine.ts`
- 轮次推进：`query.ts`
- 工具执行链：`toolExecution.ts`
- 控制面：settings / auth / policy / prompt
- 扩展与续航：skills / MCP / plugins / transcript / recovery / tasks
- 核心分工可以概括为：
  - `main.tsx` 管装配
  - `QueryEngine.ts` 管寿命
  - `query.ts` 管推进

**关键代码片段**

```ts
export class QueryEngine {
  private mutableMessages: Message[]
  private totalUsage: NonNullableUsage
  private readFileState: FileStateCache
}

type State = {
  messages: Message[]
  toolUseContext: ToolUseContext
  turnCount: number
  transition: Continue | undefined
}
```

**代码理解支撑**
- 这些模块共同定义了 Claude Code 的真实运行形态；尤其是装配、宿主、执行三层拆开之后，后面的工作流程和功能就都能落位。

**希望听众带走什么**
- 后面的工作流程和主要功能，都会回到这些核心模块上。

## 第 6 页：控制面为什么重要

**这一页要回答的问题**
- 为什么 Claude Code 的行为边界不是只由模型决定。

**核心内容**
- 它有完整的 `control plane（控制面）`：
  - settings
  - auth
  - policy limits
  - managed settings
  - prompt stack
- 这些模块共同决定：
  - 哪些工具可用
  - 哪些组织限制生效
  - 当前任务会被怎样解释

**代码支撑**
- [src/utils/settings/settings.ts](/Users/bobo/code/claude-code-source-code/src/utils/settings/settings.ts)
- [src/utils/auth.ts](/Users/bobo/code/claude-code-source-code/src/utils/auth.ts)
- [src/services/policyLimits/index.ts](/Users/bobo/code/claude-code-source-code/src/services/policyLimits/index.ts)
- [src/utils/systemPrompt.ts](/Users/bobo/code/claude-code-source-code/src/utils/systemPrompt.ts)

**关键代码片段**

```ts
export function buildEffectiveSystemPrompt({
  customSystemPrompt,
  defaultSystemPrompt,
  appendSystemPrompt,
  overrideSystemPrompt,
}: ...): SystemPrompt
```

**代码理解支撑**
- 这些模块都能直接影响工具可用性、组织限制和系统行为，因此“边界”不是口头说说，而是代码里的真实裁决链。

**希望听众带走什么**
- 用 Claude Code 时，很多“为什么它这样做”，其实来自控制面，而不是模型好坏。

---

# 第二部分：工作流程（6 页）

## 第 7 页：一次请求从哪里开始

**这一页要回答的问题**
- 用户输入之后，第一步发生了什么。

**核心内容**
- 输入进入 CLI / REPL。
- 先过 settings / auth / policy。
- 构造 tools / commands / app state。
- 然后才进入 `QueryEngine` 和 `query.ts`。

**关键代码片段**

```ts
// Persist the user's message(s) to transcript BEFORE entering the query loop.
if (persistSession && messagesFromUserInput.length > 0) {
  const transcriptPromise = recordTranscript(messages)
  ...
}
```

**代码理解支撑**
- 在 `main.tsx` 和 `QueryEngine.ts` 里，请求处理明显早于模型调用就已经开始。

**希望听众带走什么**
- 这解释了为什么相同提示词在不同环境下可能表现不同。

## 第 8 页：工作流程总图

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

## 第 9 页：`turn loop（轮次循环）` 如何推进

**这一页要回答的问题**
- 一轮 loop 的基本闭环是什么，它为什么不像普通流水线。

**核心内容**
- 当前 messages
- context shaping
- API request
- assistant / tool_use
- tool_result 回灌
- next turn
- 但中途还要处理：
  - `prompt_too_long`
  - `max_output_tokens`
  - continuation
  - stop hook
  - reactive compact

**代码支撑**
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)

**关键代码片段**

```ts
type State = {
  messages: Message[]
  toolUseContext: ToolUseContext
  hasAttemptedReactiveCompact: boolean
  maxOutputTokensRecoveryCount: number
  stopHookActive: boolean | undefined
  transition: Continue | undefined
}
```

**代码理解支撑**
- `query.ts` 反复围绕 messages、tool context、transition 推进，而且 continuation、compact、recovery 都在主路径里，所以 Claude Code 更像 `recovery graph（恢复图）`，不是简单 pipeline。

**希望听众带走什么**
- Claude Code 的强项不是“回答”，而是“推进”。

## 第 10 页：context shaping 与 tool pipeline

**这一页要回答的问题**
- 模型每轮到底看到了什么，工具调用又是怎样被执行的。

**核心内容**
- 模型看到的不是静态聊天记录，而是动态构造的工作面：
  - prompt stack
  - attachments
  - relevant memories
  - invoked skills
  - system reminders
- 工具调用不是直接 `tool.call()`，而是会经过：
  - input parse
  - validate
  - hooks
  - permissions / classifier
  - `tool.call()`
  - post process

**代码支撑**
- [src/utils/attachments.ts](/Users/bobo/code/claude-code-source-code/src/utils/attachments.ts)
- [src/utils/systemPrompt.ts](/Users/bobo/code/claude-code-source-code/src/utils/systemPrompt.ts)
- [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)

**关键代码片段**

```ts
function getCriticalSystemReminderAttachment(...) {
  ...
  return [{ type: 'critical_system_reminder', content: reminder }]
}

const parsedInput = tool.inputSchema.safeParse(input)
...
runPreToolUseHooks(...)
...
resolveHookPermissionDecision(...)
...
tool.call(...)
```

**代码理解支撑**
- attachments 和 system prompt sections 都是按 turn 重新拼接的，而工具执行链又天然带约束和审查，所以用户的上下文组织方式与边界表达会直接影响执行稳定性。

**希望听众带走什么**
- 用户不是在给静态聊天机器人发消息，而是在参与当前轮工作面的构造和动作边界的定义。

## 第 11 页：transcript / recovery / compact 在流程里的位置

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

**关键代码片段**

```ts
const filteredToolUses = filterUnresolvedToolUses(migratedMessages)
const filteredThinking =
  filterOrphanedThinkingOnlyMessages(filteredToolUses)
const filteredMessages =
  filterWhitespaceOnlyAssistantMessages(filteredThinking)
```

**代码理解支撑**
- 这些模块不是边缘工具，而是主流程续航机制，因此 Claude Code 才能支持长任务和断点续做。

**希望听众带走什么**
- “长期工作”是这套系统的显式设计目标。

## 第 12 页：工作流程小结

**这一页要回答的问题**
- 为什么理解工作流对使用方式有帮助。

**核心内容**
- Claude Code 不是把一句话直接变成一句话。
- 它要把请求变成一个可以持续推进、可约束、可恢复的工作过程。
- 所以后面的功能、产出和建议，本质上都是对这套工作流的利用方式。
- 从使用角度看，这条工作流还直接决定了三件事：
  - 复杂任务为什么应该拆阶段，而不是一口气塞进一个模糊请求
  - 为什么验证、确认、继续推进这些动作要单独明确表达
  - 为什么带工具、可恢复、可续做的任务，比纯自由聊天更适合 Claude Code

**希望听众带走什么**
- 用户越理解这套工作流，越知道什么样的任务组织方式更有效。

---

# 第三部分：功能介绍（功能分类列表 + 主要功能，15 页）

## 第 13 页：Claude Code 有哪些功能面

**这一页要回答的问题**
- Claude Code 的能力应该怎么分类理解。

**核心内容**
- 从用户可感知的能力看，Claude Code 的主要功能面可以分成六类：
  - 交互：REPL、commands、结构化输出
  - 执行：Read / Edit / Bash / task runtime
  - 扩展：skills、MCP、plugins、remote capability
  - 控制：prompt stack、permissions、hooks、policy、managed settings
  - 续航：transcript、recovery、compact、content replacement
  - 可观测性：query profiler、context analysis、prompt cache 诊断
- 这些能力面比“按目录讲”更接近最终用户会感知到的系统能力。
- 如果进一步按“用户能直接感知到什么”来拆，还可以把每类能力对应成更具体的问题：
  - 交互：我怎么和 Claude Code 对话、切模式、拿结构化结果
  - 执行：它能直接读什么、改什么、跑什么
  - 扩展：它能接入哪些外部能力和上下文
  - 控制：什么决定了它此刻能做什么、不能做什么
  - 续航：长任务为什么不会一长就崩
  - 可观测性：当结果变差、变慢、变贵时，怎么查原因

**代码支撑**
- [src/commands.ts](/Users/bobo/code/claude-code-source-code/src/commands.ts)
- [src/tools.ts](/Users/bobo/code/claude-code-source-code/src/tools.ts)
- [src/services/mcp/client.ts](/Users/bobo/code/claude-code-source-code/src/services/mcp/client.ts)
- [src/utils/sessionStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/sessionStorage.ts)

**关键代码片段**

```ts
export function getAllBaseTools(): Tools {
  return [
    AgentTool,
    TaskOutputTool,
    BashTool,
    ...(hasEmbeddedSearchTools() ? [] : [GlobTool, GrepTool]),
    ExitPlanModeV2Tool,
    FileReadTool,
    FileEditTool,
    FileWriteTool,
    ...
  ]
}
```

```ts
return uniqBy(
  [...builtInTools].sort(byName).concat(allowedMcpTools.sort(byName)),
  'name',
)
```

**代码理解支撑**
- commands、tools、MCP、policy、recovery、profiling 分布在不同模块里，但它们共同服务的是一条主执行链，因此从功能面而不是目录切入，更能帮助用户理解“Claude Code 到底能帮我完成什么”。

**希望听众带走什么**
- 理解 Claude Code，先看功能面，再看具体模块，会更容易和后面的使用方式对应起来。

## 第 14 页：交互、执行、扩展与控制功能

**这一页要回答的问题**
- 在所有功能面里，哪些最直接决定用户能做什么、系统能放开到哪一步。

**核心内容**
- 交互面：
  - REPL 输入与多轮对话
  - slash commands
  - structured output
  - progress / system / compact 边界消息
- 执行面：
  - 读文件、改文件、查文件
  - Bash 与命令执行
  - 任务与子代理
- 扩展与控制面：
  - skills
  - MCP
  - plugins
  - prompt stack
  - settings / auth / permissions / policy
- 如果按用户一天中的真实使用动作来理解，这些能力大致对应：
  - 先通过 REPL / commands 进入任务
  - 再用读写文件、Bash、任务系统推进执行
  - 在复杂任务中通过 skills / MCP / plugins 扩展能力上限
  - 在整个过程中持续受到 prompt、权限、策略和配置的约束

**代码支撑**
- [src/commands.ts](/Users/bobo/code/claude-code-source-code/src/commands.ts)
- [src/tools.ts](/Users/bobo/code/claude-code-source-code/src/tools.ts)
- [src/QueryEngine.ts](/Users/bobo/code/claude-code-source-code/src/QueryEngine.ts)
- [src/utils/systemPrompt.ts](/Users/bobo/code/claude-code-source-code/src/utils/systemPrompt.ts)

**关键代码片段**

```ts
const COMMANDS = memoize((): Command[] => [
  addDir,
  advisor,
  clear,
  compact,
  config,
  context,
  diff,
  help,
  login,
  mcp,
  plan,
  plugin,
  resume,
  review,
  tasks,
  ...
])
```

```ts
case 'assistant':
  this.mutableMessages.push(message)
  yield* normalizeMessage(message)
  break
case 'progress':
  this.mutableMessages.push(message)
  ...
  yield* normalizeMessage(message)
  break
```

**代码理解支撑**
- Claude Code 不只处理普通对话消息，还处理 progress、system、compact 边界等运行时消息；同时扩展和控制模块又分离存在，这说明它从交互层开始就已经是一个工作流系统，而不是自由聊天窗口。

**希望听众带走什么**
- Claude Code 的上限由扩展面决定，下限由控制面决定。

## 第 15 页：续航与可观测性功能

**这一页要回答的问题**
- Claude Code 为什么能支持长任务、恢复和持续诊断。

**核心内容**
- 续航能力：
  - transcript
  - recovery
  - compact
  - content replacement
  - session / task memory
- 可观测性能力：
  - query profiler
  - prompt cache 诊断
  - context analysis
- 这些能力让系统不仅“能跑”，还能“长时间跑”和“知道自己哪里跑坏了”。
- 从用户结果看，这部分能力直接对应：
  - 长任务可以续做
  - 中断后可以 resume
  - 大输出不会直接把上下文拖爆
  - 性能、上下文和缓存问题可以被定位，而不是只能猜

**代码支撑**
- [src/utils/sessionStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/sessionStorage.ts)
- [src/utils/conversationRecovery.ts](/Users/bobo/code/claude-code-source-code/src/utils/conversationRecovery.ts)
- [src/utils/queryProfiler.ts](/Users/bobo/code/claude-code-source-code/src/utils/queryProfiler.ts)
- [src/utils/analyzeContext.ts](/Users/bobo/code/claude-code-source-code/src/utils/analyzeContext.ts)

**关键代码片段**

```ts
const filteredToolUses = filterUnresolvedToolUses(migratedMessages)
const filteredThinking =
  filterOrphanedThinkingOnlyMessages(filteredToolUses)
const filteredMessages =
  filterWhitespaceOnlyAssistantMessages(filteredThinking)
```

```ts
 * - query_context_loading_start/end
 * - query_microcompact_start/end
 * - query_autocompact_start/end
 * - query_tool_schema_build_start/end
 * - query_api_request_sent
 * - query_first_chunk_received
 * - query_tool_execution_start/end
```

**代码理解支撑**
- 这些模块单独存在，说明 Claude Code 把“长任务续航”和“运行时诊断”视作一等能力，而不是出现问题后的补丁。

**希望听众带走什么**
- Claude Code 真正拉开差距的地方，不是功能数量，而是续航和诊断能力。

## 第 16 页：Prompt Stack（提示词栈）

**这一页要回答的问题**
- Claude Code 的默认角色和行为边界，是怎么在系统里被定义出来的。

**功能**
- 定义系统默认行为、角色和输出风格。

**实现原理**
- 由 default prompt、override prompt、agent prompt、dynamic sections 叠加而成。
- 一部分内容可以 cache，一部分内容按会话动态拼接。

**关键代码片段**

```ts
export function buildEffectiveSystemPrompt({
  customSystemPrompt,
  defaultSystemPrompt,
  appendSystemPrompt,
  overrideSystemPrompt,
}: ...): SystemPrompt
```

```ts
The user will primarily request you to perform software engineering tasks.
```

**代码支撑**
- [src/utils/systemPrompt.ts](/Users/bobo/code/claude-code-source-code/src/utils/systemPrompt.ts)
- [src/constants/prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts)

**使用技巧**
- 任务表达越工程化越好。
- 范围、约束、验证越明确越好。

**代码理解支撑**
- 默认 system prompt 直接把用户请求定义成软件工程任务，因此“工程化表达更稳”不是经验，而是系统默认角色的直接结果。

**希望听众带走什么**
- 使用 Claude Code，第一步不是“会不会提 prompt”，而是“会不会用它默认理解的任务语言说话”。

## 第 17 页：Turn Loop（轮次循环）

**这一页要回答的问题**
- Claude Code 为什么更像一个会持续推进的执行系统，而不是一问一答。

**功能**
- 推进一轮轮 agent 执行。

**实现原理**
- 维护 state、transition、toolUseContext、compact / recovery 分支。
- 在一轮 assistant 结果和下一轮工具/续写之间维持连续性。

**关键代码片段**

```ts
type State = {
  messages: Message[]
  toolUseContext: ToolUseContext
  autoCompactTracking: AutoCompactTrackingState | undefined
  maxOutputTokensRecoveryCount: number
  pendingToolUseSummary: Promise<ToolUseSummaryMessage | null> | undefined
  stopHookActive: boolean | undefined
  turnCount: number
  transition: Continue | undefined
}
```

**代码支撑**
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)

**使用技巧**
- 大任务要拆阶段。
- 输入要清楚到足以支持持续推进。
- 复杂任务不要指望“一轮说清一切”。

**代码理解支撑**
- `State` 里保存的是跨轮迁移状态，不只是消息，因此 Claude Code 天然更适合可继续推进的任务，而不是模糊一次性请求。

**希望听众带走什么**
- Claude Code 的强项不是“回答”，而是“推进”。

## 第 18 页：Tool Pipeline 与 BashTool

**这一页要回答的问题**
- 为什么工具调用有完整执行链，Bash 又为什么需要被单独看待。

**功能**
- 把工具能力放进可约束的执行链，同时提供最强但风险最高的 Bash 能力。

**实现原理**
- Tool Pipeline：schema parse -> validate -> hooks -> permissions -> call -> post process。
- BashTool：sandbox、只读识别、路径校验、破坏性判断、长输出处理。

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

```ts
const TOOL_DEFAULTS = {
  isConcurrencySafe: (_input?: unknown) => false,
  isReadOnly: (_input?: unknown) => false,
  isDestructive: (_input?: unknown) => false,
  checkPermissions: (...) =>
    Promise.resolve({ behavior: 'allow', updatedInput: input }),
}
```

```ts
Do NOT use the Bash tool when a relevant dedicated tool is provided.
```

**代码支撑**
- [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)
- [src/tools/BashTool/BashTool.tsx](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/BashTool.tsx)
- [src/tools/BashTool/prompt.ts](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts)

**使用技巧**
- 能用专用工具就别默认 Bash。
- 高风险动作要写清确认方式。
- Bash 更适合兜底，不适合当常规主路径。

**代码理解支撑**
- 工具调用先经过 parse、hooks、permissions、classifier，再到真正执行；而 BashTool 周围又专门拆出安全子模块，这说明 Claude Code 鼓励的是可审查的执行路径，而不是随时走 shell。

**希望听众带走什么**
- 工具不是“能力列表”，而是一条带审查和边界的执行链。

## 第 19 页：Compact、Transcript / Recovery、Content Replacement

**这一页要回答的问题**
- 长会话为什么不会膨胀失控，中断之后又为什么还能续做。

**功能**
- 控制长会话上下文体积，保证消息链可恢复，并治理大工具输出。

**实现原理**
- compact：microcompact、autocompact、reactive compact，重建工作面。
- recovery：修 unresolved tool use、thinking、continuation，回到 API 可继续状态。
- content replacement：大结果落盘、preview replacement、resume replay，保证看过的前缀不漂。

**关键代码片段**

```ts
const filteredToolUses = filterUnresolvedToolUses(migratedMessages)
const filteredThinking =
  filterOrphanedThinkingOnlyMessages(filteredToolUses)
```

```ts
export type ContentReplacementState = {
  seenIds: Set<string>
  replacements: Map<string, string>
}
```

```ts
// Once seen, a result's fate is frozen for the conversation.
export type ContentReplacementRecord = {
  kind: 'tool-result'
  toolUseId: string
  replacement: string
}
```

**代码支撑**
- [src/utils/sessionStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/sessionStorage.ts)
- [src/utils/conversationRecovery.ts](/Users/bobo/code/claude-code-source-code/src/utils/conversationRecovery.ts)
- [src/services/compact/compact.ts](/Users/bobo/code/claude-code-source-code/src/services/compact/compact.ts)
- [src/utils/toolResultStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/toolResultStorage.ts)

**使用技巧**
- 长任务和断点续做是 Claude Code 的强项之一。
- 不要要求模型永远在上下文里保留完整大输出。
- 对复杂任务，不必强迫一轮做完。

**代码理解支撑**
- compact、recovery 和 replacement 共同维护的是“可持续工作”和“前缀稳定性”，这说明 Claude Code 的续航能力不是附加特性，而是底层设计目标。

**希望听众带走什么**
- Claude Code 的长期工作能力，是运行时设计出来的，不是偶然效果。

## 第 20 页：Skills 与 Attachments

**这一页要回答的问题**
- Claude Code 的上下文为什么是动态构造的，skill 又为什么不是简单模板。

**功能**
- 用 skills 打开条件激活的能力面；用 attachments 动态组装当前轮上下文。

**实现原理**
- skills 的加载分成四层：
  - **启动时肯定加载**：
    - `bundled skills`
    - 当前可读到的 `managed / user / project / --add-dir` 下的普通 skills
    - 已启用插件提供的 `plugin skills`
  - **启动时只登记、不立即激活**：
    - 带 `paths` frontmatter 的 `conditional skills`
  - **运行时可能动态加载**：
    - 随文件操作发现的 nested `.claude/skills`
    - MCP 提供的 skills
  - **真正进入 prompt/context**：
    - 只有在 skill 被选中或调用时，`getPromptForCommand()` 才把 skill 文本真正注入当前轮
- attachments 的加载更偏 `turn-scoped`：
  - **每轮都会重算的**：
    - system reminders
    - plan / task / todo / IDE 相关 attachment
    - 可用 skill / MCP / agent delta
  - **条件成立时才会注入的**：
    - relevant memories
    - conditional rules / nested memory
    - teammate mailbox messages
    - pending task messages
  - **下一轮可能自动消失的**：
    - 只在当前 turn 成立的 reminder、memory、task attachment
- 换句话说：
  - skills 更像“能力先注册，再按时机激活”
  - attachments 更像“每轮临时拼装当前工作面”

**关键代码片段**

```ts
export const getSkillDirCommands = memoize(
  async (cwd: string): Promise<Command[]> => {
    const userSkillsDir = join(getClaudeConfigHomeDir(), 'skills')
    const managedSkillsDir = join(getManagedFilePath(), '.claude', 'skills')
    const projectSkillsDirs = getProjectDirsUpToHome('skills', cwd)
    ...
  },
)
```

```ts
for (const skill of deduplicatedSkills) {
  if (
    skill.type === 'prompt' &&
    skill.paths &&
    skill.paths.length > 0 &&
    !activatedConditionalSkillNames.has(skill.name)
  ) {
    newConditionalSkills.push(skill)
  } else {
    unconditionalSkills.push(skill)
  }
}
```

```ts
if (skillIgnore.ignores(relativePath)) {
  dynamicSkills.set(name, skill)
  conditionalSkills.delete(name)
  activatedConditionalSkillNames.add(name)
}
```

```ts
export function createSkillCommand({...}): Command {
  return {
    type: 'prompt',
    name: skillName,
    allowedTools,
    whenToUse,
    model,
    effort,
  }
}
```

```ts
return [{ type: 'relevant_memories' as const, memories }]
```

```ts
function getCriticalSystemReminderAttachment(
  toolUseContext: ToolUseContext,
): Attachment[] {
  const reminder = toolUseContext.criticalSystemReminder_EXPERIMENTAL
  if (!reminder) return []
  return [{ type: 'critical_system_reminder', content: reminder }]
}
```

**代码支撑**
- [src/utils/skills/loadSkillsDir.ts](/Users/bobo/code/claude-code-source-code/src/utils/skills/loadSkillsDir.ts)
- [src/utils/attachments.ts](/Users/bobo/code/claude-code-source-code/src/utils/attachments.ts)
- [src/commands.ts](/Users/bobo/code/claude-code-source-code/src/commands.ts)

**使用技巧**
- skill 更适合用于有明显任务边界的场景。
- 当前轮的任务组织方式会直接影响 Claude Code 看到的上下文。
- 任务阶段、文件范围和关键提醒，最好显式表达。
- 如果希望某类 skill 更容易被激活，最好显式给出：
  - 当前涉及的目录或文件
  - 当前任务属于哪个阶段
  - 当前最重要的约束和输出目标
- 如果任务依赖 memory / task / reminder 一类 attachment，就不要假设它们会永久常驻；它们更像当前轮按条件拼进来的工作材料。

**代码理解支撑**
- `getSkillDirCommands()` 说明普通 skills 会在启动构建 commands 时批量加载，但 `conditional skills` 会先放进待激活集合，不会立即加入可见能力面。
- `activateConditionalSkillsForPaths()` 说明带 `paths` 的 skill 只有在命中文件路径后才会进入 `dynamicSkills`。
- `createSkillCommand()` 说明 skill 的 markdown 不是启动时就直接进 prompt，而是先编译成 `prompt command`，等真正调用时才注入当前轮。
- attachments 这一侧则完全是 turn-scoped 的：每轮根据 memory、task、rules、mailbox、system reminder 等条件重新构造，所以 Claude Code 当前轮看到的上下文，本质上是“运行时临时工作面”，不是静态对话历史。

**希望听众带走什么**
- 会组织文件范围、任务阶段和当前约束，就更容易让正确的 skills 被激活、让正确的 attachments 出现在当前轮。

## 第 21 页：Permissions / Hooks / Classifier

**这一页要回答的问题**
- Claude Code 的行动边界，到底是怎么落在系统里的。

**功能**
- 决定模型能否继续代表用户行动。

**实现原理**
- allow / ask / deny、hook pre/post、classifier 决策链、auto mode。
- 工具执行不是“能调就调”，而是被运行时裁决。

**关键代码片段**

```ts
if (appState.toolPermissionContext.mode === 'auto') {
  ...
  classifierResult = await classifyYoloAction(...)
}
```

```ts
export function syncPermissionRulesFromDisk(
  toolPermissionContext: ToolPermissionContext,
  rules: PermissionRule[],
): ToolPermissionContext {
  ...
  const updates = convertRulesToUpdates(rules, 'replaceRules')
  return applyPermissionUpdates(context, updates)
}
```

**代码支撑**
- [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)
- [src/utils/permissions/permissions.ts](/Users/bobo/code/claude-code-source-code/src/utils/permissions/permissions.ts)

**使用技巧**
- 高风险动作要写清楚。
- 模糊授权会显著放大不确定性。
- 团队协作时，责任边界要显式表达。

**代码理解支撑**
- permissions、hooks、classifier 都位于工具执行链中，说明真正的自主边界在 runtime 内部，而不是口头提醒。

**希望听众带走什么**
- Claude Code 并不是“模型想到什么就去做什么”，真正的边界在执行链里。

## 第 22 页：Tasks / Subagents / Mailbox 与 MCP / Plugins

**这一页要回答的问题**
- Claude Code 为什么适合处理阶段性任务和多执行体协作，同时又能不断扩展上限。

**功能**
- 把异步执行体变成一等对象，并通过 MCP / plugins / remote capability 扩展能力上限。

**实现原理**
- task registry、local/remote agent、sidechain transcript、mailbox protocol。
- MCP client、plugin loader、remote session / remote agent。

**关键代码片段**

```ts
export function registerTask(task: TaskState, setAppState: SetAppState): void {
  ...
  enqueueSdkEvent({
    type: 'system',
    subtype: 'task_started',
    task_id: task.id,
  })
}
```

```ts
 * Workers send permission requests to the leader's mailbox
 * Leaders send permission responses to the worker's mailbox
```

**代码支撑**
- [src/Task.ts](/Users/bobo/code/claude-code-source-code/src/Task.ts)
- [src/utils/task/framework.ts](/Users/bobo/code/claude-code-source-code/src/utils/task/framework.ts)
- [src/tools/AgentTool/runAgent.ts](/Users/bobo/code/claude-code-source-code/src/tools/AgentTool/runAgent.ts)
- [src/services/mcp/client.ts](/Users/bobo/code/claude-code-source-code/src/services/mcp/client.ts)
- [src/utils/plugins/pluginLoader.ts](/Users/bobo/code/claude-code-source-code/src/utils/plugins/pluginLoader.ts)

**使用技巧**
- 复杂任务适合拆成阶段或子任务。
- 需要并行探索时，要显式定义子任务边界。
- Claude Code 的上限不仅取决于模型，也取决于能接入哪些能力面。

**代码理解支撑**
- task registry、mailbox、sidechain transcript 和 MCP / plugins 同时存在，说明 Claude Code 已经有多执行体 runtime 和能力枢纽的雏形。

**希望听众带走什么**
- 按任务系统思维组织复杂工作，并主动扩展能力面，会比把所有事都塞进一个 prompt 更稳。

## 第 23 页：重要功能小结

**这一页要回答的问题**
- 为什么前面这些功能值得逐个讲，而且必须和使用方式联系起来。

**核心内容**
- 因为它们共同决定了：
  - 系统如何继续工作
  - 用户如何更稳地使用它
  - 哪些边界必须显式表达
  - Claude Code 更适合什么样的工程任务
- 真正有价值的不是“记住功能名”，而是知道：
  - 哪个功能解决哪个问题
  - 它会导出怎样的使用方式
- 如果把前面的重点功能压成用户最需要记住的五个点，大致就是：
  - Claude Code 的默认角色是工程任务执行体，而不是自由聊天角色
  - 它擅长推进任务，不擅长在模糊目标下自由发挥
  - 它的工具执行是带边界和审查的，不是直接替用户乱做事
  - 它有长任务续航机制，所以复杂任务不必强行压成一轮
  - 它的上下文是动态构造的，所以任务组织方式本身会改变结果质量

**代码理解支撑**
- Prompt Stack、Turn Loop、Tool Pipeline、Compact、Recovery、Tasks 都直接对应一类真实运行时问题，因此“技巧”必须回到这些机制上理解。

**希望听众带走什么**
- 真正的“使用技巧”，必须回到运行时机制上理解。

---

# 第四部分：产出（主要产出 + 适合的任务，4 页）

## 第 24 页：从用户视角看，Claude Code 最典型的产出是什么

**这一页要回答的问题**
- Claude Code 最擅长产出什么结果。

**核心内容**
- 代码修改
- 代码解释与定位结论
- 调试与排障结论
- 命令执行与验证结果
- 计划、任务拆解、review 结论
- 结构化输出与工作卡
- 这些结果共同特点是：
  - 可执行
  - 可验证
  - 可继续推进

**关键代码片段**

```ts
addFunctionHook(
  setAppState,
  sessionId,
  'Stop',
  '',
  messages => hasSuccessfulToolCall(messages, SYNTHETIC_OUTPUT_TOOL_NAME),
  `You MUST call the ${SYNTHETIC_OUTPUT_TOOL_NAME} tool to complete this request. Call this tool now.`,
)
```

**代码理解支撑**
- commands、Edit/Read/Bash、structured output、Plan Mode、task runtime 在代码里都明确存在，说明它默认就围绕工程结果设计。

**希望听众带走什么**
- Claude Code 最适合被当作工程产出生成器，而不是意见生成器。

## 第 25 页：哪些任务适合 / 不适合 Claude Code

**这一页要回答的问题**
- 哪类任务最能发挥这套系统的优势，哪类任务会让它失稳。

**核心内容**
- 适合：
  - 局部修复与重构
  - 多文件追踪与定位
  - 命令执行与验证
  - 需要拆阶段推进的任务
  - 需要形成“代码 + 解释 + 验证”的任务
- 不适合直接硬做：
  - 目标极度模糊
  - 范围完全不受限
  - 对输出形式没有约束
  - 高风险动作但没给确认规则
  - 完全依赖口头背景、缺少可见材料的任务

**代码理解支撑**
- 适合的任务天然贴合 `tool pipeline + plan + task runtime + recovery` 这几条主能力链；不适合的任务则会同时让 prompt stack、工具执行链和权限链进入不稳定状态。

**希望听众带走什么**
- 不是所有任务都该交给 Claude Code，任务筛选本身就是能力的一部分。

## 第 26 页：为什么它能稳定地产出这些结果

**这一页要回答的问题**
- Claude Code 为什么比普通聊天系统更容易产出稳定工程结果。

**核心内容**
- 默认角色是工程代理
- 工具执行受约束
- 结果可进入 transcript / compact / recovery
- plan、task、memory 支持多阶段工作
- 输出不是“一轮完成”，而是可继续推进的工作过程

**代码支撑**
- [src/constants/prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts)
- [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)
- [src/utils/sessionStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/sessionStorage.ts)
- [src/utils/messages.ts](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts)

**关键代码片段**

```ts
The user will primarily request you to perform software engineering tasks.
...
Report outcomes faithfully...
```

**代码理解支撑**
- 角色定义、执行链、续航链和任务链一起存在，决定了 Claude Code 更容易产出“工作结果”，而不是发散回答。

**希望听众带走什么**
- 稳定产出来自运行时结构，不只是模型强。

## 第 27 页：产出小结

**这一页要回答的问题**
- 从用户视角，前面这些产出和适用任务能压成什么结论。

**核心内容**
- Claude Code 最适合用来推进工程任务。
- 它特别适合产出“代码 + 解释 + 验证 + 计划”。
- 它不适合完全模糊、完全无边界的自由发挥。
- 任务是否适合 Claude Code，本质上取决于：
  - 是否能定义清楚目标
  - 是否能给出边界和验证
  - 是否允许分阶段推进
- 在任务筛选上，可以优先把它放到这些场景：
  - 有明确目标、范围和完成标准的编码任务
  - 需要查代码、改代码、跑命令、回写结果的串联任务
  - 可以分阶段推进、允许中途继续或补充信息的复杂任务
- 相对不适合的，是纯开放式脑暴、目标频繁变化、边界极不清晰的自由讨论型任务

**希望听众带走什么**
- 先理解产出形态，再谈技巧，效果会更稳。

---

# 第五部分：开发流程建议（8 页）

## 第 28 页：为什么要单独讲“开发流程建议”

**这一页要回答的问题**
- 为什么最后还要讲“建议”，而不是停在架构和功能。

**核心内容**
- 因为 Claude Code 最终是用来协作和产出的。
- 只有把前面的 runtime 逻辑翻译成工作流建议，分享才真正落地。
- 这里的建议不是经验帖，而是从系统默认行为和执行链约束反推出来的工作方式。
- 更具体地说，推荐的开发流程可以压成四步：
  - 先定义目标、范围、边界和验证方式
  - 再决定是否需要先读代码、先 plan、先拆子任务
  - 再让 Claude Code 进入执行、验证和继续推进阶段
  - 对高风险动作、复杂协作和长任务，显式补足边界条件
- 这样做的意义不只是“更安全”，而是能显著降低范围漂移、误解任务和跳过验证的概率。

**希望听众带走什么**
- 这一部分不是“经验汇总”，而是从源码约束倒推出的协作方式。

## 第 29 页：建议一：把任务组织成工程任务，而不是聊天请求

**这一页要回答的问题**
- 什么样的任务表达方式最贴近 Claude Code 的默认角色。

**核心内容**
- 把任务写成：目标、范围、约束、验证。
- 避免模糊话术和隐藏边界。
- 尽量把任务写成 Claude Code 可以持续推进的工程工作，而不是抽象愿望。

**关键代码片段**

```ts
The user will primarily request you to perform software engineering tasks.
```

**代码理解支撑**
- system prompt 已经把用户请求定义成工程任务，因此任务表达越工程化，Claude Code 越接近默认最佳状态。

**希望听众带走什么**
- 想用稳 Claude Code，先把任务写得像工程任务。

## 第 30 页：建议二：先读代码，再改代码

**这一页要回答的问题**
- 为什么“先读代码”必须显式写出来，而不是默认它自然会做。

**核心内容**
- 明确要求先读关键文件。
- 不要一上来就让它直接改。
- 给出阅读入口，会减少无关探索和错误改动。

**关键代码片段**

```ts
In general, do not propose changes to code you haven't read.
```

**代码理解支撑**
- 这不是使用习惯，而是 prompt stack 明确写出的默认行为。

**希望听众带走什么**
- 想要稳定质量，先让 Claude Code 建立正确上下文。

## 第 31 页：建议三：最小改动，优先复用；专用工具优先，Bash 后置

**这一页要回答的问题**
- 为什么“最小改动、优先复用”和“专用工具优先”常常要一起强调。

**核心内容**
- 明确要求最小必要改动。
- 优先复用现有模式。
- 不要默认允许顺手抽象。
- 有 dedicated tools 时优先 dedicated tools。
- Bash 是高能力、高风险通道。

**关键代码片段**

```ts
Don't create helpers, utilities, or abstractions for one-time operations.
```

```ts
Do NOT use the Bash tool when a relevant dedicated tool is provided.
```

**代码理解支撑**
- Claude Code 默认就反对无边界“优化”和一锤子抽象，同时工具执行链与 BashTool 安全层也共同说明：系统鼓励可审查的执行路径，而不是随时走 shell。

**希望听众带走什么**
- 先把问题修好，再考虑抽象；先走专用工具，再考虑 Bash。

## 第 32 页：建议四：验证要单独要求；高风险动作要写清确认规则

**这一页要回答的问题**
- 为什么“验证”和“风险边界”必须被单独写出来。

**核心内容**
- 验证不是默认一定会发生。
- 验证结果要显式回报。
- 删除、覆盖、push、外发等动作要明确确认。
- 不要给模糊授权。

**关键代码片段**

```ts
Report outcomes faithfully...
```

```ts
Carefully consider the reversibility and blast radius of actions.
```

**代码理解支撑**
- 默认 prompt 会直接约束结果汇报，而 BashTool prompt、tool pipeline、permissions 又都把高风险动作当成单独路径，因此“验证”和“确认规则”都不该省略。

**希望听众带走什么**
- Claude Code 能帮你执行和验证，但前提是你把风险边界和验证条件一开始就写清楚。

## 第 33 页：建议五：复杂任务先走 Plan Mode；独立查询允许并行，长任务允许分阶段推进

**这一页要回答的问题**
- 复杂任务为什么要先规划，长任务为什么要按阶段推进。

**核心内容**
- 先探索、再计划、后实现。
- 不要在需求不清时直接让它开干。
- 独立查询可以 parallel。
- 长任务适合拆阶段、拆子任务。
- 对并行探索，最好先定义每个子任务的范围和输出要求。

**代码支撑**
- [src/utils/messages.ts](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts)
- [src/utils/task/framework.ts](/Users/bobo/code/claude-code-source-code/src/utils/task/framework.ts)

**关键代码片段**

```ts
Explore — Use the tools available to you to learn about the codebase...
Update the plan file with a clear plan.
Ask the user questions, but only if necessary.
```

```ts
You can call multiple tools in a single response.
If you intend to call multiple tools and there are no dependencies between them,
make all independent tool calls in parallel.
```

**代码理解支撑**
- Plan workflow 明确把“探索现有实现、更新计划、再问缺失信息”做成了独立流程；并行工具调用和 task runtime 又是系统一级能力，因此复杂任务和长任务都应该按阶段设计。

**希望听众带走什么**
- 对复杂任务，先让 Claude Code 帮你把问题讲清楚；对长任务，按阶段组织它。

## 第 34 页：建议六：哪些任务最适合直接交给 Claude Code

**这一页要回答的问题**
- 如果要把任务直接扔给 Claude Code，哪类最值得优先尝试。

**核心内容**
- 局部修复
- 代码理解与定位
- 需要命令验证的任务
- 可分阶段推进的任务
- 需要“代码 + 解释 + 验证结果”的任务

**代码理解支撑**
- 这些任务正好贴合 prompt stack、tool pipeline、task runtime 和 recovery 的优势区间。

**希望听众带走什么**
- 优先把适合的任务交给 Claude Code，才能快速建立正确使用感。

## 第 35 页：建议七：哪些任务要谨慎交给 Claude Code

**这一页要回答的问题**
- 哪些任务最容易把 Claude Code 带离稳定区间。

**核心内容**
- 完全模糊的探索
- 范围极大的全局变更
- 高风险但边界不清的动作
- 需要大量隐性业务背景的任务
- 既没有验证条件，又没有结果格式要求的任务

**代码理解支撑**
- Claude Code 不是不能做，而是这类任务更容易让 prompt stack、tool pipeline 和权限链都处在不稳定状态。

**希望听众带走什么**
- 不是所有任务都该交给 Claude Code，任务筛选本身就是能力的一部分。

## 第 36 页：团队协作时，应该把 Claude Code 当成什么角色

**这一页要回答的问题**
- 在团队里，Claude Code 最适合作为什么样的协作对象存在。

**核心内容**
- 工程代理
- 多阶段任务推进器
- 带工具的验证者
- 文档、代码、验证结果的联合产出器
- 而不是“替代所有人判断”的黑盒执行者

**关键代码片段**

```ts
Just writing a response in text is not visible to others on your team -
you MUST use the SendMessage tool.
```

**代码理解支撑**
- commands、Plan Mode、task runtime、structured output、tool pipeline 都说明它更适合作为“协作型工程执行体”，而不是单纯聊天机器人。

**希望听众带走什么**
- 团队越把 Claude Code 放在正确角色上，它越容易发挥稳定价值。

## 第 37 页：开发流程建议小结

**这一页要回答的问题**
- 前面的建议如果收成一句方法论，应该怎么记。

**核心内容**
- 先用少量源码理解建立正确模型。
- 再把重心放到产出、使用方式和任务组织。
- 所有真正有效的技巧，都可以回到代码机制解释。
- 更好的使用方式，本质上就是更贴近 Claude Code 默认运行方式的协作方式。

**希望听众带走什么**
- Claude Code 最值得学的，不只是它“会什么”，而是你怎样组织任务，才能让它稳定地产出高质量工程结果。

---

# 第六部分：代码走读概略（3 页）

## 第 38 页：代码组织和架构概略

**这一页要回答的问题**
- 如果听众后续要自己读代码，应该先怎么建立代码组织视图。

**核心内容**
- 启动与装配：`main.tsx`
- 会话与执行：`QueryEngine.ts`、`query.ts`
- 工具与命令：`Tool.ts`、`tools.ts`、`commands.ts`
- 续航与恢复：`sessionStorage.ts`、`conversationRecovery.ts`、`compact/*`
- 扩展与控制：settings、auth、policy、MCP、plugins、skills
- 这套代码最适合按“运行链 + 控制链”来阅读。
- 这六层不是教科书式的干净分层，而是阅读源码时最有帮助的拆法：
  - 前三层帮助建立主执行链
  - 中间两层帮助理解边界与控制
  - 最后一层帮助理解为什么它能长期工作和持续扩展

**建议配图**
- 一张“代码结构关系图”，至少画出：
  - `main.tsx -> QueryEngine.ts -> query.ts`
  - `query.ts -> toolExecution.ts`
  - `query.ts -> compact / recovery`
  - `main.tsx -> settings / auth / policy / prompt`
  - `query.ts / toolExecution.ts -> tasks / MCP / skills`

**关键代码片段**

```ts
export class QueryEngine { ... }
type State = { ... }
export async function executeToolCalls(...) { ... }
```

```ts
const processUserInputContext: ProcessUserInputContext = {
  canUseTool: this.config.canUseTool,
  getUpdatedContext: () => ({
    commands,
    tools,
    agents,
    mcpClients,
  }),
}
```

**代码理解支撑**
- Claude Code 的目录层次和运行时层次不完全一致，因此读代码时要优先遵循执行链，而不是只看文件夹结构。
- 第二段代码说明 `QueryEngine.ts` 并不是单纯消息容器，它会把 commands、tools、agents、MCP clients 一起装配进运行时上下文；这也是为什么代码组织要按“主执行链 + 能力/控制链”来理解。

**希望听众带走什么**
- 先看代码分层，再看实现细节，效率会高很多。

## 第 39 页：建议的代码走读顺序

**这一页要回答的问题**
- 如果只给听众一条阅读路径，应该怎样安排顺序。

**核心内容**
1. `main.tsx`
2. `QueryEngine.ts`
3. `query.ts`
4. `toolExecution.ts`
5. `compact / recovery`
6. `commands / tools / MCP / tasks`
- 这条顺序可以先建立最小完整模型，再逐步钻进细节。
- 如果时间更紧，可以进一步压成“两遍阅读”：
  - 第一遍只看 `main.tsx -> QueryEngine.ts -> query.ts -> toolExecution.ts`
  - 第二遍再补 `compact / recovery / tasks / MCP / skills`
- 这样做的好处是，先建立“系统怎么跑”的心智模型，再看“系统还能做什么、怎么继续工作”，理解会顺很多

**建议配图**
- 一张“代码走读顺序图”：
  - 第一遍阅读：主执行链
  - 第二遍阅读：续航、扩展、控制
- 让听众能一眼看出阅读顺序不是按目录，而是按职责递进。

**关键代码片段**

```ts
// Persist the user's message(s) to transcript BEFORE entering the query loop.
if (persistSession && messagesFromUserInput.length > 0) {
  const transcriptPromise = recordTranscript(messages)
  ...
}
```

```ts
type State = {
  messages: Message[]
  toolUseContext: ToolUseContext
  transition: Continue | undefined
}
```

**代码理解支撑**
- 这条顺序是从装配、宿主、执行、恢复、扩展逐层展开，最容易建立完整心智模型。
- 第一段代码说明 `QueryEngine.ts` 在进入 loop 前就已经处理持久化和宿主状态；第二段代码说明 `query.ts` 的核心不是单次回答，而是维护可迁移状态。这两点决定了阅读顺序必须先“装配/宿主”，再“执行/恢复”。

**希望听众带走什么**
- 代码走读不应该按目录平铺，而应该按运行链和控制链阅读。

## 第 40 页：主要模块与重点文件

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
- 这组文件足以支撑一次从整体到细节的高质量走读。
- 如果只挑最值得反复读的五个入口文件，我会优先选：
  - `src/main.tsx`
  - `src/QueryEngine.ts`
  - `src/query.ts`
  - `src/services/tools/toolExecution.ts`
  - `src/utils/sessionStorage.ts`
- 这五个入口基本已经覆盖了：
  - 系统怎么装起来
  - 会话怎么存在
  - 一轮任务怎么推进
  - 工具怎么被约束执行
  - 长任务和中断怎么继续

**建议配图**
- 一张“重点文件关系图”，建议把五个主入口放在中间，再把：
  - `tools.ts / commands.ts`
  - `compact/*`
  - `conversationRecovery.ts`
  - `BashTool.tsx`
  - `messages.ts`
  作为外围关联模块挂在旁边。

**代码理解支撑**
- 这组文件覆盖了装配、宿主、执行、工具、续航和工作流提示，是 Claude Code 运行时的最小高价值切片。
- 如果听众只打算花有限时间自己读代码，这页给出的文件集合已经足够支撑一次“建立整体模型 -> 跟主流程 -> 理解续航机制”的完整走读。

**希望听众带走什么**
- 这组文件足以支撑一次高质量的 Claude Code 源码走读。
