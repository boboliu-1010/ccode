# Claude Code 源码深度解读：分享提纲

这份提纲用于支撑一场 40-50 页的正式分享。目标不是只讲使用技巧，而是系统回答五个问题：

1. Claude Code 的总体架构是什么
2. 它的一次工作流程如何推进
3. 它有哪些功能面与控制面
4. 哪些重要功能最值得展开讲清楚
5. 从源码看，哪些理解与借鉴边界最值得注意

对应主稿与补充材料：

- [00-代码总览与运行时走读.md](/Users/bobo/code/claude-code-source-code/docs/zh/00-代码总览与运行时走读.md)
- [06-走读附录：长会话与恢复机制.md](/Users/bobo/code/claude-code-source-code/docs/zh/06-走读附录：长会话与恢复机制.md)
- [07-走读附录：配置、认证与扩展系统.md](/Users/bobo/code/claude-code-source-code/docs/zh/07-走读附录：配置、认证与扩展系统.md)
- [08-走读附录：Claude Code 使用技巧.md](/Users/bobo/code/claude-code-source-code/docs/zh/08-走读附录：Claude%20Code%20使用技巧.md)
- [09-Claude Code 使用技巧与注意事项.md](/Users/bobo/code/claude-code-source-code/docs/zh/09-Claude%20Code%20使用技巧与注意事项.md)

## 分享总体建议

- 推荐总页数：45 页左右
- 推荐时长：45-60 分钟
- 推荐节奏：先立模型，再讲主链路，再拆功能面，最后收束到理解边界与借鉴点
- 如果现场时间有限，可以优先保留：第 1、2、4、5 部分

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

# 第一部分：开场与整体定位（6 页）

## 第 1 页：封面

页标题：
- `Claude Code 源码深度解读`

副标题：
- `总体架构、工作流程、功能设计与理解边界`

这一页讲什么：
- 这不是产品测评，也不是功能演示
- 重点是从源码层面解释 Claude Code 为什么能长期工作
- 分享目标是建立一套可复用的 agent runtime 分析框架

## 第 2 页：为什么值得讲这份源码

本页一句话：
- Claude Code 值得研究，不是因为它工具多，而是因为它已经为长时间工作的 agent runtime 付过工程账。

核心讲点：
- 它不是 demo agent
- 它已经处理了长会话、恢复、压缩、权限、任务系统、扩展生态
- 它能帮助理解生产级 agent runtime 和玩具框架的差别

## 第 3 页：先给结论：Claude Code 到底是什么

本页一句话：
- Claude Code 更像一个 `terminal agent runtime（终端代理运行时）`，不是普通聊天 CLI。

核心讲点：
- 不是单纯 CLI 包壳
- 不是简单模型 SDK demo
- 是 conversation host + turn loop + tool pipeline + control plane 的组合

源码依据：
- [src/main.tsx](/Users/bobo/code/claude-code-source-code/src/main.tsx)
- [src/QueryEngine.ts](/Users/bobo/code/claude-code-source-code/src/QueryEngine.ts)
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)

## 第 4 页：总结构图：Claude Code 的主执行链

本页一句话：
- Claude Code 的核心不是“问模型一次”，而是 `prompt stack -> turn loop -> tool pipeline` 的持续闭环。

建议配图：
- 一张总结构图，展示用户输入、prompt stack、QueryEngine、query.ts、tool pipeline、tools/tasks、control plane、observability

讲点：
- 用户输入会穿过多层运行时
- tools 和 tasks 是执行面
- settings / auth / policy 是控制面

## 第 5 页：模块分层图：从入口到执行环境

本页一句话：
- 这套系统是分层的，但真正的复杂度来自跨层协同。

讲点：
- `main.tsx`：启动装配
- `QueryEngine.ts`：会话宿主
- `query.ts`：轮次循环
- `services/tools/*`：工具执行
- `services/api/*`：模型接口
- `utils/*` / `services/*`：配置、恢复、扩展、策略

## 第 6 页：这场分享的主线

本页一句话：
- 全文围绕五个问题展开：架构、流程、功能、重点功能、理解边界。

讲点：
- 先讲总体架构
- 再讲工作流程
- 再讲功能列表
- 再讲重要功能细节
- 最后讲理解边界与借鉴点

---

# 第二部分：总体架构（9 页）

## 第 7 页：启动层：`main.tsx` 在做什么

本页一句话：
- `main.tsx` 是 `bootstrap / assembly（启动装配）`，不是智能内核。

讲点：
- 读取 settings / auth / policy
- 初始化 commands / tools / plugins / skills / MCP
- 进入 REPL 或 headless 模式

源码依据：
- [src/main.tsx](/Users/bobo/code/claude-code-source-code/src/main.tsx)

## 第 8 页：会话层：`QueryEngine.ts` 为什么重要

本页一句话：
- `QueryEngine.ts` 负责会话寿命，而不是单轮推理。

讲点：
- 持有 `mutableMessages`
- usage 聚合
- transcript 预落盘
- file state 持有
- SDK / headless 投影

关键代码片段：

```ts
export class QueryEngine {
  private mutableMessages: Message[]
  private totalUsage: NonNullableUsage
  private readFileState: FileStateCache
}
```

源码依据：
- [src/QueryEngine.ts](/Users/bobo/code/claude-code-source-code/src/QueryEngine.ts)

## 第 9 页：执行层：`query.ts` 为什么是核心

本页一句话：
- `query.ts` 是 Claude Code 的 `runtime kernel（运行时内核）`。

讲点：
- 组装当前上下文
- 发起模型请求
- 处理 streaming 输出
- 接管 tool use / tool result
- 处理 retry / continue / compact / recovery

关键代码片段：

```ts
type State = {
  messages: Message[]
  toolUseContext: ToolUseContext
  turnCount: number
  transition: Continue | undefined
}
```

源码依据：
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)

## 第 10 页：能力层：Tool System 是怎么组织的

本页一句话：
- Claude Code 把工具建模成能力契约，而不是函数集合。

讲点：
- `Tool.ts` 定义工具协议
- `tools.ts` 负责注册和裁剪工具
- tools 既受 feature 控制，也受权限和上下文控制

源码依据：
- [src/Tool.ts](/Users/bobo/code/claude-code-source-code/src/Tool.ts)
- [src/tools.ts](/Users/bobo/code/claude-code-source-code/src/tools.ts)

## 第 11 页：控制面：settings / auth / policy / prompt stack

本页一句话：
- Claude Code 的行为边界由控制面决定，而不只由模型决定。

讲点：
- settings 叠加与 managed settings
- auth 与 token source
- policy limits
- prompt stack

源码依据：
- [src/utils/settings/settings.ts](/Users/bobo/code/claude-code-source-code/src/utils/settings/settings.ts)
- [src/utils/auth.ts](/Users/bobo/code/claude-code-source-code/src/utils/auth.ts)
- [src/services/policyLimits/index.ts](/Users/bobo/code/claude-code-source-code/src/services/policyLimits/index.ts)
- [src/utils/systemPrompt.ts](/Users/bobo/code/claude-code-source-code/src/utils/systemPrompt.ts)

## 第 12 页：扩展层：MCP / plugins / skills

本页一句话：
- Claude Code 的扩展不是附加功能，而是能力面治理的一部分。

讲点：
- MCP：外部工具与资源协议
- plugins：本地插件系统
- skills：提示词级能力 artifact

源码依据：
- [src/services/mcp/client.ts](/Users/bobo/code/claude-code-source-code/src/services/mcp/client.ts)
- [src/utils/plugins/pluginLoader.ts](/Users/bobo/code/claude-code-source-code/src/utils/plugins/pluginLoader.ts)
- [src/utils/skills/loadSkillsDir.ts](/Users/bobo/code/claude-code-source-code/src/utils/skills/loadSkillsDir.ts)

## 第 13 页：执行底座：tasks / subagents / mailbox

本页一句话：
- Claude Code 已经不仅是单轮对话系统，而是有异步执行体的 runtime。

讲点：
- task framework
- local agent / remote agent / teammate
- mailbox 协议
- sidechain transcript

源码依据：
- [src/Task.ts](/Users/bobo/code/claude-code-source-code/src/Task.ts)
- [src/utils/task/framework.ts](/Users/bobo/code/claude-code-source-code/src/utils/task/framework.ts)
- [src/tools/AgentTool/runAgent.ts](/Users/bobo/code/claude-code-source-code/src/tools/AgentTool/runAgent.ts)

## 第 14 页：状态载体总览

本页一句话：
- Claude Code 的连续性不依赖单一消息数组，而依赖多种状态载体协同。

讲点：
- `messages`
- transcript
- `ToolUseContext`
- `AppState`
- attachments
- session memory / sidecar artifacts

## 第 15 页：架构小结

本页一句话：
- Claude Code 的架构价值，不在层数多，而在它把长期工作所需的层都做出来了。

讲点：
- 有主执行链
- 有控制面
- 有扩展面
- 有恢复与可观测性

---

# 第三部分：工作流程（9 页）

## 第 16 页：从用户输入到系统启动

本页一句话：
- 一次请求不是直接发给模型，而是先经过宿主与控制面的装配。

讲点：
- 用户输入 / 命令进入 CLI
- 加载 settings / auth / policy
- 构造 tools / commands / app state
- 进入 QueryEngine 或 REPL

## 第 17 页：工作流程总图

本页一句话：
- Claude Code 的工作流程是“上下文整理 -> 模型采样 -> 工具执行 -> 结果回灌 -> 继续推进”的闭环。

建议配图：
- 一张总流程图，显示主执行链

## 第 18 页：`turn loop（轮次循环）` 的基本闭环

本页一句话：
- `turn loop` 是 `model -> tool -> model` 的循环，不是一次性问答。

讲点：
- 当前 messages
- context shaping
- API request
- assistant / tool_use
- tool_result 回灌
- next turn

源码依据：
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)

## 第 19 页：时序图：一次请求如何流过 Claude Code

本页一句话：
- 用时序视角看，Claude Code 的关键不在“回答”，而在“穿过多层系统后仍可继续”。

建议配图：
- User -> Prompt Stack -> QueryEngine -> query.ts -> Tool Pipeline -> Tools -> transcript

## 第 20 页：context shaping（上下文整理）是怎么发生的

本页一句话：
- 模型每轮看到的 context 不是静态历史，而是动态重建出来的。

讲点：
- prompt stack
- attachments
- relevant memories
- invoked skills
- plan mode / system reminders

源码依据：
- [src/utils/attachments.ts](/Users/bobo/code/claude-code-source-code/src/utils/attachments.ts)
- [src/utils/systemPrompt.ts](/Users/bobo/code/claude-code-source-code/src/utils/systemPrompt.ts)

## 第 21 页：tool pipeline（工具执行流水线）如何推进

本页一句话：
- 工具调用不是直接执行，而是经过一整条校验、权限、钩子和结果处理链。

讲点：
- input parse
- validate
- hooks
- permissions / classifier
- `tool.call()`
- post processing

源码依据：
- [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)

## 第 22 页：为什么它不是 linear pipeline（线性流水线）

本页一句话：
- Claude Code 更像 recovery graph（恢复图），不是简单流水线。

讲点：
- `prompt_too_long`
- `max_output_tokens`
- continuation
- stop hook
- reactive compact

## 第 23 页：transcript / recovery（会话记录 / 恢复）如何工作

本页一句话：
- 恢复的目标不是还原 UI，而是回到 API 可继续运行状态。

讲点：
- `parentUuid` 链
- compact boundary
- orphaned tool result
- synthetic continuation

源码依据：
- [src/utils/sessionStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/sessionStorage.ts)
- [src/utils/conversationRecovery.ts](/Users/bobo/code/claude-code-source-code/src/utils/conversationRecovery.ts)

## 第 24 页：compact（上下文压缩）在流程里的位置

本页一句话：
- compact 不是附属优化，而是长会话主流程的一部分。

讲点：
- microcompact
- snip
- autocompact
- reactive compact
- session memory compact

## 第 25 页：工作流程小结

本页一句话：
- Claude Code 能长期工作，是因为它把失败、恢复、压缩、续写都纳入了主流程。

---

# 第四部分：功能列表（8 页）

## 第 26 页：功能全景：Claude Code 提供了哪些能力

本页一句话：
- Claude Code 的功能可以按交互、执行、扩展、控制四个维度理解。

讲点：
- 交互能力
- 代码操作能力
- 外部系统接入能力
- 企业与策略能力

## 第 27 页：交互功能列表

讲点：
- CLI / REPL
- commands
- headless / SDK 模式
- plan mode
- structured output

源码依据：
- [src/commands.ts](/Users/bobo/code/claude-code-source-code/src/commands.ts)
- [src/QueryEngine.ts](/Users/bobo/code/claude-code-source-code/src/QueryEngine.ts)

## 第 28 页：代码操作与执行功能列表

讲点：
- Read / Write / Edit / Grep / Glob
- BashTool
- Task / Agent / REPL
- file state / edit safety

## 第 29 页：扩展生态功能列表

讲点：
- MCP
- plugins
- skills
- remote session / remote agent

## 第 30 页：控制与治理功能列表

讲点：
- auth
- policy limits
- managed settings
- permission rules
- hooks / classifier

## 第 31 页：长会话与恢复功能列表

讲点：
- transcript
- recovery
- content replacement
- compact
- session memory

## 第 32 页：可观测性功能列表

讲点：
- query profiler
- prompt cache break detection
- analyzeContext
- telemetry / metadata

## 第 33 页：功能列表小结

本页一句话：
- Claude Code 的功能密度说明，它已经是产品化 runtime，而不只是推理循环。

---

# 第五部分：重要功能详细介绍（15 页）

## 第 34 页：重要功能一：Prompt Stack（提示词栈）

功能：
- 定义系统默认行为与能力边界

实现原理：
- default prompt、override prompt、agent prompt、coordinator prompt、dynamic sections 叠加

使用技巧：
- 用户要把任务写得像工程任务
- 约束要明确写出来

源码依据：
- [src/utils/systemPrompt.ts](/Users/bobo/code/claude-code-source-code/src/utils/systemPrompt.ts)
- [src/constants/prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts)

关键代码片段：

```ts
The user will primarily request you to perform software engineering tasks.
```

## 第 35 页：重要功能二：Turn Loop（轮次循环）

功能：
- 推进一轮轮 agent 执行

实现原理：
- 维护 state、transition、toolUseContext、recovery 分支

使用技巧：
- 输入越清晰，loop 越稳定
- 任务越能被分解成明确工具步骤，效果越好

源码依据：
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)

关键代码片段：

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

## 第 36 页：重要功能三：Tool Pipeline（工具执行流水线）

功能：
- 把工具能力纳入安全、权限和审查链

实现原理：
- schema parse -> validate -> hooks -> permissions -> call -> post process

使用技巧：
- 优先 dedicated tools
- 不要默认让模型走 Bash

源码依据：
- [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)

关键代码片段：

```ts
const parsedInput = tool.inputSchema.safeParse(input)
...
runPreToolUseHooks(...)
...
resolveHookPermissionDecision(...)
...
tool.call(...)
```

## 第 37 页：重要功能四：BashTool

功能：
- 提供最强但风险最高的执行能力

实现原理：
- sandbox、只读识别、路径校验、破坏性判断、长输出处理

使用技巧：
- 能用专用工具就别先走 Bash
- 破坏性操作需要显式确认

源码依据：
- [src/tools/BashTool/BashTool.tsx](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/BashTool.tsx)
- [src/tools/BashTool/prompt.ts](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts)

## 第 38 页：重要功能五：Compact（上下文压缩）

功能：
- 控制长会话上下文体积

实现原理：
- microcompact、autocompact、reactive compact、summary + attachments 重建工作面

使用技巧：
- 理解 compact 后不是“失忆”，而是工作面重建
- 长任务要接受上下文会被重构

源码依据：
- [src/services/compact/compact.ts](/Users/bobo/code/claude-code-source-code/src/services/compact/compact.ts)
- [src/services/compact/microCompact.ts](/Users/bobo/code/claude-code-source-code/src/services/compact/microCompact.ts)

## 第 39 页：重要功能六：Transcript / Recovery

功能：
- 保证会话可以恢复

实现原理：
- transcript 链、parentUuid、orphan recovery、synthetic continuation

使用技巧：
- 长任务和断点续做是被系统认真支持的，不只是 UI 假象

源码依据：
- [src/utils/sessionStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/sessionStorage.ts)
- [src/utils/conversationRecovery.ts](/Users/bobo/code/claude-code-source-code/src/utils/conversationRecovery.ts)

关键代码片段：

```ts
const filteredToolUses = filterUnresolvedToolUses(migratedMessages)
const filteredThinking =
  filterOrphanedThinkingOnlyMessages(filteredToolUses)
```

## 第 40 页：重要功能七：Content Replacement（内容替换）

功能：
- 控制大工具输出，不让上下文失控

实现原理：
- 大结果落盘、preview replacement、fate freezing、resume replay

使用技巧：
- 不要把工具返回当成必须全部保留在上下文里
- Claude Code 的长任务稳定性很大程度依赖这层

源码依据：
- [src/utils/toolResultStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/toolResultStorage.ts)
- [src/services/compact/microCompact.ts](/Users/bobo/code/claude-code-source-code/src/services/compact/microCompact.ts)

关键代码片段：

```ts
export type ContentReplacementState = {
  seenIds: Set<string>
  replacements: Map<string, string>
}
```

## 第 41 页：重要功能八：Skills（技能）

功能：
- 把提示词能力做成条件激活 artifact

实现原理：
- `loadSkillsDir.ts` 载入，按路径或上下文激活，compact 后继续保留 invoked skills

使用技巧：
- skill 不是快捷短语，而是受上下文和任务面控制的能力面

源码依据：
- [src/utils/skills/loadSkillsDir.ts](/Users/bobo/code/claude-code-source-code/src/utils/skills/loadSkillsDir.ts)
- [src/utils/attachments.ts](/Users/bobo/code/claude-code-source-code/src/utils/attachments.ts)

## 第 42 页：重要功能九：Attachments（上下文附件）

功能：
- 动态组装当前轮的工作上下文

实现原理：
- relevant memories、skill delta、system reminders、task messages、file attachments

使用技巧：
- 模型每轮看到的上下文不是固定聊天记录，而是动态构造物

源码依据：
- [src/utils/attachments.ts](/Users/bobo/code/claude-code-source-code/src/utils/attachments.ts)

## 第 43 页：重要功能十：Permissions / Hooks / Classifier

功能：
- 控制模型能否代表用户继续行动

实现原理：
- allow / ask / deny、hook pre/post、classifier 决策链、auto mode

使用技巧：
- 高风险动作写清楚
- 不要给模糊授权

源码依据：
- [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)
- [src/utils/permissions/permissions.ts](/Users/bobo/code/claude-code-source-code/src/utils/permissions/permissions.ts)

## 第 44 页：重要功能十一：Tasks / Subagents / Mailbox

功能：
- 把异步执行体变成一等 runtime 对象

实现原理：
- task registry、local/remote agent、sidechain transcript、mailbox protocol

使用技巧：
- Claude Code 适合做多阶段任务，不只是单轮问答

源码依据：
- [src/Task.ts](/Users/bobo/code/claude-code-source-code/src/Task.ts)
- [src/utils/task/framework.ts](/Users/bobo/code/claude-code-source-code/src/utils/task/framework.ts)
- [src/tools/AgentTool/runAgent.ts](/Users/bobo/code/claude-code-source-code/src/tools/AgentTool/runAgent.ts)

## 第 45 页：重要功能十二：MCP / Plugins / Remote Capability

功能：
- 把 Claude Code 扩展成协议枢纽

实现原理：
- MCP client、plugin loader、remote session / remote agent

使用技巧：
- Claude Code 的上限来自能力面扩展，而不只是模型更强

源码依据：
- [src/services/mcp/client.ts](/Users/bobo/code/claude-code-source-code/src/services/mcp/client.ts)
- [src/utils/plugins/pluginLoader.ts](/Users/bobo/code/claude-code-source-code/src/utils/plugins/pluginLoader.ts)

## 第 46 页：重要功能小结

本页一句话：
- 这套系统真正的价值，不在某一个功能点，而在它把这些功能做成了一套长期工作 runtime。

---

# 第六部分：理解边界与借鉴点（6 页）

## 第 47 页：如果你要读这份代码，怎样建立理解顺序

讲点：
- 先读 `main.tsx`
- 再读 `QueryEngine.ts` / `query.ts`
- 再读 tool pipeline
- 再读 compact / recovery
- 最后读 control plane 与扩展系统

源码依据：
- [src/main.tsx](/Users/bobo/code/claude-code-source-code/src/main.tsx)
- [src/QueryEngine.ts](/Users/bobo/code/claude-code-source-code/src/QueryEngine.ts)
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)
- [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)

## 第 48 页：如果你要改这份代码，哪些状态和链路必须先确认

讲点：
- 先确定改动属于哪一层：宿主、loop、tools、control plane、task runtime
- 先确认状态载体
- 先确认 recovery / compact / cache 是否受影响

源码依据：
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)
- [src/utils/sessionStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/sessionStorage.ts)
- [src/services/compact/microCompact.ts](/Users/bobo/code/claude-code-source-code/src/services/compact/microCompact.ts)
- [src/utils/toolResultStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/toolResultStorage.ts)

## 第 49 页：从源码看，哪些设计最值得借鉴

讲点：
- turn loop 的恢复图思路
- transcript / recovery
- tool pipeline 的约束链
- content replacement / compact
- task runtime / mailbox

源码依据：
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)
- [src/utils/conversationRecovery.ts](/Users/bobo/code/claude-code-source-code/src/utils/conversationRecovery.ts)
- [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)
- [src/utils/toolResultStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/toolResultStorage.ts)
- [src/utils/task/framework.ts](/Users/bobo/code/claude-code-source-code/src/utils/task/framework.ts)

## 第 50 页：从源码看，哪些地方体现了明显结构债

讲点：
- God Loop 倾向
- ToolUseContext 过胖
- cache invariants 分散
- continuity surface 太多
- control plane owner 不清

源码依据：
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)
- [src/Tool.ts](/Users/bobo/code/claude-code-source-code/src/Tool.ts)
- [src/utils/toolResultStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/toolResultStorage.ts)
- [src/utils/attachments.ts](/Users/bobo/code/claude-code-source-code/src/utils/attachments.ts)

## 第 51 页：从代码演化角度看，更稳的方向是什么

讲点：
- 先建状态模型，再写实现
- 先把失败路径当一等对象
- 给主流程加 observability
- 不要只优化 happy path

代码理解支撑：
- `query.ts` 已经事实性地表现出状态机形态，只是状态分散
- recovery / compact / permissions / task lifecycle 都说明 failure path 是主路径的一部分
- `queryProfiler.ts`、`promptCacheBreakDetection.ts`、`analyzeContext.ts` 说明 observability 不是附属品

源码依据：
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)
- [src/utils/queryProfiler.ts](/Users/bobo/code/claude-code-source-code/src/utils/queryProfiler.ts)
- [src/services/api/promptCacheBreakDetection.ts](/Users/bobo/code/claude-code-source-code/src/services/api/promptCacheBreakDetection.ts)
- [src/utils/analyzeContext.ts](/Users/bobo/code/claude-code-source-code/src/utils/analyzeContext.ts)

## 第 52 页：总结页

本页一句话：
- Claude Code 最值得学的不是“会调很多工具”，而是它已经把长期工作所需的 runtime 约束做成了系统。

建议收束：
- 它不是聊天壳，而是 agent runtime
- 它的强项是长期工作、恢复、压缩、能力治理
- 它的弱项是结构债已经开始累积
- 真正值得借鉴的是不变量和控制链，而不是今天的文件形状
