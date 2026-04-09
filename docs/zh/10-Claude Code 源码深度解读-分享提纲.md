# Claude Code 源码深度解读：分享提纲

这份提纲面向 45-60 分钟正式分享。目标不是罗列模块，而是把 Claude Code 解释成一套可以长期工作的 `terminal agent runtime（终端代理运行时）`。

这份提纲的写法刻意偏“可直接写成 PPT 页内容”，因此每页都尽量包含：

- 这页要回答什么问题
- 这页真正想让听众记住什么
- 这页依赖哪些代码证据
- 这页和前后页如何衔接

对应正文：

- [09-Claude Code 源码深度解读-文档.md](/Users/bobo/code/claude-code-source-code/docs/zh/09-Claude%20Code%20源码深度解读-文档.md)

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

# 第一部分：为什么这份源码值得看（6 页）

## 第 1 页：封面

**标题**
- `Claude Code 源码深度解读`

**副标题**
- `总体架构、主工作流、关键机制与借鉴边界`

**这一页要讲什么**
- 这不是产品测评，也不是使用教程。
- 目标是解释 Claude Code 为什么不是普通聊天 CLI，而是一套已经相当完整的 agent runtime。
- 这场分享既关注“它做了什么”，更关注“它为什么能长期工作”。

**希望听众带走什么**
- 后面不会按目录照着念，而是按系统问题来讲。
- 这份源码的价值在于 runtime 约束，而不是功能多。

## 第 2 页：为什么值得研究 Claude Code

**这一页要回答的问题**
- 市面上 agent demo 很多，为什么 Claude Code 还值得单独拆开讲。

**核心内容**
- 它已经认真处理了长会话、恢复、压缩、权限、任务系统和扩展生态。
- 这些问题恰好是 demo agent 最容易回避、但生产系统必须面对的。
- 因此它更像一份“生产级样本”，而不是单纯“功能产品”。

**建议页面内容**
- 左侧放“常见 demo agent 的典型缺口”：
  - 没有恢复
  - 没有上下文治理
  - 没有清晰权限链
  - 没有多执行体生命周期
- 右侧放“Claude Code 已经补上的层”：
  - transcript / recovery
  - compact / replacement
  - tool pipeline
  - task runtime

**希望听众带走什么**
- Claude Code 最值得研究的不是“它会什么”，而是“它如何让系统持续工作”。

**代码理解支撑**
- 长会话与恢复不是抽象判断，而是可以直接在 [src/utils/sessionStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/sessionStorage.ts)、[src/utils/conversationRecovery.ts](/Users/bobo/code/claude-code-source-code/src/utils/conversationRecovery.ts) 看到专门实现。
- 工具约束也不是产品层说法，而是 [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts) 里真的有 parse、hook、permission、classifier 的执行链。

## 第 3 页：先给结论：Claude Code 到底是什么

**这一页要回答的问题**
- 这套系统从工程上应该如何命名和理解。

**核心内容**
- Claude Code 更像 `terminal agent runtime（终端代理运行时）`。
- 它不是简单的 CLI wrapper，也不是单纯的模型 SDK。
- 更准确的理解是：
  - 有宿主层
  - 有执行内核
  - 有工具链
  - 有控制面
  - 有任务运行时

**代码支撑**
- [src/main.tsx](/Users/bobo/code/claude-code-source-code/src/main.tsx)
- [src/QueryEngine.ts](/Users/bobo/code/claude-code-source-code/src/QueryEngine.ts)
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)

**代码理解支撑**
- 这个“runtime”判断来自三层职责同时存在：`main.tsx` 负责装配，`QueryEngine.ts` 持有会话状态，`query.ts` 负责单轮推进；如果只是聊天 CLI，通常不会把这三层拆得这么明确。

**希望听众带走什么**
- 从这一页开始，就不要再把它当成“聊天工具增强版”。

## 第 4 页：高层判断：Claude Code 和 demo agent 的本质差别

**这一页要回答的问题**
- 如果只用一句话区分 Claude Code 和普通 agent 框架，差别在哪里。

**核心内容**
- demo agent 的中心往往是“让模型调工具”。
- Claude Code 的中心是“让一条执行轨迹在复杂条件下仍然可持续”。
- 因此它关注的是：
  - 轨迹闭合
  - 上下文收缩
  - 状态恢复
  - 权限裁决
  - 多执行体协同

**页面建议**
- 左边：`demo agent`
- 右边：`Claude Code`
- 中间用 4-5 个关键词对比

**希望听众带走什么**
- Claude Code 的价值主张是 durability（续航）和 controllability（可控性）。

**代码理解支撑**
- `query.ts` 里有 continuation、compact、retry、recovery 相关状态，说明它关心的是轨迹续航。
- `toolExecution.ts`、permissions、hooks、classifier 的存在，说明它关心的是执行可控性，而不是只让模型自由调用工具。

## 第 5 页：总结构图：Claude Code 的主执行链

**这一页要回答的问题**
- 用户输入之后，系统内部到底穿过了哪些层。

**核心内容**
- 用户输入不会直接变成模型回答。
- 它会穿过：
  - `prompt stack`
  - `QueryEngine`
  - `query.ts turn loop`
  - `tool pipeline`
  - tools / tasks / execution environment
- 旁边始终有 `control plane` 和 `observability` 在约束与记录。

**建议配图**
- 一张总结构图，展示：
  - User Prompt
  - Prompt Stack
  - QueryEngine
  - query.ts
  - Tool Pipeline
  - Tools / Tasks
  - Control Plane
  - Transcript / Observability

**希望听众带走什么**
- 后面所有细节都只是把这条主执行链拆开。

**代码理解支撑**
- 这条链不是分析者主观拼出来的，`main.tsx -> QueryEngine.ts -> query.ts -> toolExecution.ts` 在代码里就是主调用链，旁边再叠加 settings / auth / policy / transcript 等外围控制面。

## 第 6 页：这场分享怎么展开

**这一页要回答的问题**
- 为什么这场分享按现在这个顺序讲。

**核心内容**
- 先讲系统定位和总体架构，否则所有机制都会被误读。
- 再讲主工作流程，否则模块间关系无法建立。
- 再讲功能面和重要功能，否则只剩目录感。
- 最后讲借鉴边界，否则容易把现状误当模板。

**希望听众带走什么**
- 这份源码最怕“按目录平读”，最适合“按系统问题读”。

---

# 第二部分：总体架构（9 页）

## 第 7 页：启动层：`main.tsx` 在做什么

**这一页要回答的问题**
- `main.tsx` 在 Claude Code 里到底扮演什么角色。

**核心内容**
- 它不是智能核心，而是 `bootstrap / assembly（启动装配）`。
- 它负责：
  - 读取 settings / auth / policy
  - 初始化 commands / tools / plugins / skills / MCP
  - 配置权限模式和远程设置
  - 进入 REPL 或 headless 模式

**代码支撑**
- [src/main.tsx](/Users/bobo/code/claude-code-source-code/src/main.tsx)

**代码理解支撑**
- `main.tsx` 文件体量很大，而且初始化内容明显跨越配置、认证、策略、扩展、命令和工具注册，这种形态更像 bootstrapper，而不是“开始思考”的地方。

**希望听众带走什么**
- 这类系统的入口文件往往很大，但大的原因是“装配”，不是“推理”。

## 第 8 页：会话层：`QueryEngine.ts` 为什么重要

**这一页要回答的问题**
- 为什么 `QueryEngine.ts` 不是普通包装类。

**核心内容**
- 它是 `conversation host（会话宿主）`。
- 它持有的是跨 turn 的状态，不是一次响应。
- 它承担：
  - mutable messages
  - usage 聚合
  - file state
  - transcript 持久化
  - SDK / headless 投影

**关键代码片段**

```ts
export class QueryEngine {
  private mutableMessages: Message[]
  private totalUsage: NonNullableUsage
  private readFileState: FileStateCache
}
```

**代码支撑**
- [src/QueryEngine.ts](/Users/bobo/code/claude-code-source-code/src/QueryEngine.ts)

**代码理解支撑**
- 这里不是只包一层 `query()` 调用；它持有 `mutableMessages`、usage、file state 等跨轮状态，说明它真正负责的是会话寿命。

**希望听众带走什么**
- Claude Code 把“会话寿命”单独建模了，这和很多直接在 loop 里塞全部状态的系统不一样。

## 第 9 页：执行层：`query.ts` 为什么是核心

**这一页要回答的问题**
- 为什么几乎所有真正值钱的 runtime 逻辑都能回到 `query.ts`。

**核心内容**
- `query.ts` 是 `runtime kernel（运行时内核）`。
- 它负责：
  - 组装当前上下文
  - 发起模型请求
  - 处理流式输出
  - 推进 tool use / tool result
  - 处理 retry / continue / compact / recovery

**关键代码片段**

```ts
type State = {
  messages: Message[]
  toolUseContext: ToolUseContext
  turnCount: number
  transition: Continue | undefined
}
```

**代码支撑**
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)

**代码理解支撑**
- `State` 里除了 `messages` 还有 `toolUseContext`、`transition`、turn 相关状态，说明这个文件关心的是执行推进与迁移，而不是单次 API 调用。

**希望听众带走什么**
- Claude Code 的真正执行秩序，必须从 `query.ts` 理解。

## 第 10 页：能力层：Tool System 是怎么组织的

**这一页要回答的问题**
- Claude Code 是怎样把“工具”变成系统能力的。

**核心内容**
- 它不是简单把若干函数暴露给模型。
- `Tool.ts` 定义能力契约：
  - schema
  - 权限语义
  - 并发语义
  - 结果处理
- `tools.ts` 负责注册、排序、裁剪和 feature gating。

**代码支撑**
- [src/Tool.ts](/Users/bobo/code/claude-code-source-code/src/Tool.ts)
- [src/tools.ts](/Users/bobo/code/claude-code-source-code/src/tools.ts)

**代码理解支撑**
- `Tool.ts` 里不仅有调用接口，还有 schema、权限语义、并发语义等定义；这说明工具在这里是能力契约，不是零散函数。

**希望听众带走什么**
- 工具系统是 Claude Code 的“能力面治理层”，不是工具箱清单。

## 第 11 页：控制面：settings / auth / policy / prompt stack

**这一页要回答的问题**
- 行为边界是由谁决定的。

**核心内容**
- 这套系统不是“模型想做什么就做什么”。
- 真正裁决边界的是控制面：
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
- 这些模块分别决定配置来源、身份来源、组织限制和系统提示，合起来实际上就是行为边界；这也是“control plane（控制面）”这个说法的代码依据。

**希望听众带走什么**
- 控制面是 Claude Code 产品化的关键，不是边缘配置。

## 第 12 页：扩展层：MCP / plugins / skills

**这一页要回答的问题**
- Claude Code 为什么不是封闭能力系统。

**核心内容**
- 它通过三层扩展体系扩展能力面：
  - MCP
  - plugins
  - skills
- 三者并不相同：
  - MCP 偏协议与外部能力
  - plugins 偏本地集成
  - skills 偏提示词 artifact

**代码支撑**
- [src/services/mcp/client.ts](/Users/bobo/code/claude-code-source-code/src/services/mcp/client.ts)
- [src/utils/plugins/pluginLoader.ts](/Users/bobo/code/claude-code-source-code/src/utils/plugins/pluginLoader.ts)
- [src/utils/skills/loadSkillsDir.ts](/Users/bobo/code/claude-code-source-code/src/utils/skills/loadSkillsDir.ts)

**代码理解支撑**
- 三套扩展机制各自有独立入口和生命周期，说明 Claude Code 并不是把所有扩展都混成“额外工具”，而是在治理不同类型的能力面。

**希望听众带走什么**
- Claude Code 的上限，不只是模型强不强，还取决于能力面扩展。

## 第 13 页：执行底座：tasks / subagents / mailbox

**这一页要回答的问题**
- 为什么说 Claude Code 已经进入“多执行体”阶段。

**核心内容**
- 它不只是单 agent 对话。
- 它已经有：
  - task registry
  - local / remote agent
  - teammate / mailbox
  - sidechain transcript

**代码支撑**
- [src/Task.ts](/Users/bobo/code/claude-code-source-code/src/Task.ts)
- [src/utils/task/framework.ts](/Users/bobo/code/claude-code-source-code/src/utils/task/framework.ts)
- [src/tools/AgentTool/runAgent.ts](/Users/bobo/code/claude-code-source-code/src/tools/AgentTool/runAgent.ts)

**代码理解支撑**
- 这里已经有 task state、registry、agent metadata、sidechain transcript，这些都说明它不是“顺手起个子任务”，而是把执行体建模成了一等对象。

**希望听众带走什么**
- 这层是 Claude Code 和普通单循环 agent 的关键分水岭。

## 第 14 页：状态载体总览

**这一页要回答的问题**
- Claude Code 的连续性到底靠什么维持。

**核心内容**
- 不是只靠 `messages`。
- 真正重要的状态载体包括：
  - `messages`
  - transcript
  - `ToolUseContext`
  - `AppState`
  - attachments
  - session memory / sidecar artifacts

**希望听众带走什么**
- 生产级 runtime 的状态往往是多载体协同，而不是单对象真相源。

**代码理解支撑**
- 这不是抽象概括，`messages`、transcript、`ToolUseContext`、`AppState`、attachments 都在不同模块里承担状态职责，状态所有权本身就是系统复杂度来源。

## 第 15 页：总体架构小结

**这一页要回答的问题**
- 为什么架构层值得单独讲这么多。

**核心内容**
- 因为 Claude Code 的关键优势不在单点模块，而在：
  - 有主执行链
  - 有控制面
  - 有扩展面
  - 有恢复和可观测性

**希望听众带走什么**
- 它更像一个完整系统，而不是一组堆叠功能。

---

# 第三部分：主工作流程（10 页）

## 第 16 页：从用户输入到系统启动

**这一页要回答的问题**
- 一次请求最开始是如何进入系统的。

**核心内容**
- 用户输入进入 CLI / REPL
- 读取 settings / auth / policy
- 构造 tools / commands / app state
- 进入 QueryEngine 或 REPL 主路径

**希望听众带走什么**
- 真正的请求处理从进入 loop 之前就开始了。

**代码理解支撑**
- 请求进入系统后先经过 settings / auth / policy / tool assembly，这些在 `main.tsx` 和 `QueryEngine.ts` 里都发生在真正调用模型之前。

## 第 17 页：工作流程总图

**这一页要回答的问题**
- 一次完整请求的主执行链长什么样。

**核心内容**
- 上下文整理
- 模型采样
- 工具执行
- 结果回灌
- 继续推进 / 停止 / 压缩 / 恢复

**建议配图**
- 一张总流程图，展示主闭环。

**希望听众带走什么**
- Claude Code 的工作流天然就是多轮和可恢复的。

**代码理解支撑**
- 主流程里天然存在 tool result 回灌、continue、compact、recovery；这不是报错后的异常支路，而是代码中显式存在的正常迁移。

## 第 18 页：`turn loop（轮次循环）` 的基本闭环

**这一页要回答的问题**
- 一轮 loop 最基本的闭环是什么。

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
- `query.ts` 明确围绕 messages、tool context 和 transition 反复推进，因此“loop”不是比喻，而是文件真正实现的执行形态。

**希望听众带走什么**
- 这不是“先问一次、再问一次”，而是一条持续推进的执行轨迹。

## 第 19 页：时序图：一次请求如何流过 Claude Code

**这一页要回答的问题**
- 从时序视角看，各层如何参与同一次请求。

**核心内容**
- User
- Prompt Stack
- QueryEngine
- query.ts
- Tool Pipeline
- Tools
- transcript / persistence

**建议配图**
- 简化时序图，不追求细节齐全，重点强调层间协作。

**希望听众带走什么**
- “能继续工作”来自跨层协同，而不是某一个类特别聪明。

**代码理解支撑**
- QueryEngine、query、tool pipeline、transcript persistence 各自只负责一部分；系统能力来自它们之间的配合，而不是单文件内部的魔法。

## 第 20 页：context shaping（上下文整理）是怎么发生的

**这一页要回答的问题**
- 模型每轮到底看到了什么。

**核心内容**
- 它看到的不是静态聊天记录，而是动态重建的工作面。
- 这其中包括：
  - prompt stack
  - attachments
  - relevant memories
  - invoked skills
  - plan mode / reminders

**代码支撑**
- [src/utils/attachments.ts](/Users/bobo/code/claude-code-source-code/src/utils/attachments.ts)
- [src/utils/systemPrompt.ts](/Users/bobo/code/claude-code-source-code/src/utils/systemPrompt.ts)

**代码理解支撑**
- attachments、system prompt sections、invoked skills 都是按 turn 重新拼接的，这说明模型看到的是动态构造的工作面，不是简单聊天历史。

**希望听众带走什么**
- Claude Code 的上下文构造能力，是它持续工作的基础之一。

## 第 21 页：tool pipeline（工具执行流水线）如何推进

**这一页要回答的问题**
- 工具调用为什么不是直接 `tool.call()`。

**核心内容**
- 工具调用依次经过：
  - input parse
  - validate
  - hooks
  - permissions / classifier
  - `tool.call()`
  - post process

**代码支撑**
- [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)

**代码理解支撑**
- 工具调用前后被多层包裹，说明 Claude Code 最在意的是“动作如何被审查和约束”，而不是尽快调用完成。

**希望听众带走什么**
- Claude Code 的“可控性”主要就长在这条链上。

## 第 22 页：为什么它不是 linear pipeline（线性流水线）

**这一页要回答的问题**
- 为什么不能把它理解成普通工具循环。

**核心内容**
- 主流程中途要处理：
  - `prompt_too_long`
  - `max_output_tokens`
  - continuation
  - stop hook
  - reactive compact

**希望听众带走什么**
- Claude Code 更像 `recovery graph（恢复图）`，而不是顺序流程图。

**代码理解支撑**
- 只要代码里显式存在 `prompt_too_long`、`max_output_tokens`、continuation、reactive compact 这些迁移分支，就已经说明它不是简单线性链。

## 第 23 页：transcript / recovery（会话记录 / 恢复）如何工作

**这一页要回答的问题**
- 中断后为什么还能继续。

**核心内容**
- transcript 保存的是带 `parentUuid` 的消息链。
- recovery 的目标不是还原 UI，而是修回 API 可继续状态。
- 因此中间要处理：
  - unresolved tool use
  - orphaned tool result
  - compact boundary
  - synthetic continuation

**代码支撑**
- [src/utils/sessionStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/sessionStorage.ts)
- [src/utils/conversationRecovery.ts](/Users/bobo/code/claude-code-source-code/src/utils/conversationRecovery.ts)

**代码理解支撑**
- recovery 阶段不是直接读盘再恢复，而是先过滤 unresolved tool use、orphaned thinking 等残片，这正是“恢复成可运行状态”而不是“还原 UI”的证据。

**希望听众带走什么**
- 恢复在 Claude Code 里是 runtime 能力，不是产品体验幻觉。

## 第 24 页：compact（上下文压缩）在流程里的位置

**这一页要回答的问题**
- compact 为什么不是边缘优化。

**核心内容**
- 它存在于主流程里，而不是辅助流程里。
- 主要形式包括：
  - microcompact
  - snip
  - autocompact
  - reactive compact
  - session memory compact

**希望听众带走什么**
- 长会话能持续，compact 是必要机制，不是锦上添花。

**代码理解支撑**
- compact 在主流程里被反复触发，而且有多种形态，说明它是系统性机制，不是偶尔用的优化开关。

## 第 25 页：工作流程小结

**这一页要回答的问题**
- 为什么主流程讲完后，Claude Code 的价值会更清楚。

**核心内容**
- 它把失败、恢复、压缩、续写都纳入主路径。
- 这就是它更像生产系统而不是 demo 的原因。

**希望听众带走什么**
- 如果只记一件事：Claude Code 最强的不是回答，而是持续推进。

---

# 第四部分：功能面与系统职责（8 页）

## 第 26 页：功能全景：Claude Code 提供了哪些能力

**这一页要回答的问题**
- 从系统职责看，Claude Code 有哪些能力面。

**核心内容**
- 交互
- 执行
- 扩展
- 控制
- 续航
- 可观测性

**希望听众带走什么**
- 功能多本身不重要，形成体系才重要。

**代码理解支撑**
- 这些功能面并不是后期人为分类，而是能直接对应到 commands、tools、MCP、policy、recovery、profiling 等模块分布。

## 第 27 页：交互功能面

**核心内容**
- CLI / REPL
- commands
- headless / SDK
- plan mode
- structured output

**代码支撑**
- [src/commands.ts](/Users/bobo/code/claude-code-source-code/src/commands.ts)
- [src/QueryEngine.ts](/Users/bobo/code/claude-code-source-code/src/QueryEngine.ts)

**希望听众带走什么**
- 交互层不只是 UI，而是宿主能力的一部分。

**代码理解支撑**
- commands、REPL、headless/SDK 投影分别落在命令层和宿主层，说明“交互”在 Claude Code 里本身就是一条系统能力线。

## 第 28 页：代码操作与执行功能面

**核心内容**
- Read / Write / Edit / Grep / Glob
- BashTool
- Task / Agent / REPL
- file state / edit safety

**希望听众带走什么**
- 这层定义了 Claude Code 作为工程代理的直接执行能力。

**代码理解支撑**
- Read/Edit/Grep/Bash/Task 等能力直接决定了模型的行动边界，因此执行层就是 Claude Code 作为工程代理的“手和脚”。

## 第 29 页：扩展生态功能面

**核心内容**
- MCP
- plugins
- skills
- remote session / remote agent

**希望听众带走什么**
- 扩展能力是 Claude Code 上限的重要来源。

**代码理解支撑**
- MCP、plugins、skills 各自有独立入口和生命周期，说明扩展不是附加包袱，而是一级能力设计。

## 第 30 页：控制与治理功能面

**核心内容**
- auth
- policy limits
- managed settings
- permission rules
- hooks / classifier

**希望听众带走什么**
- 没有这层，就没有真正的企业可控性。

**代码理解支撑**
- auth、policy、managed settings、permission rules 都能直接影响执行路径，说明治理层并不是外置说明文档，而是 runtime 的实际约束来源。

## 第 31 页：长会话与恢复功能面

**核心内容**
- transcript
- recovery
- content replacement
- compact
- session memory

**希望听众带走什么**
- 这层是长期工作的真正支柱。

**代码理解支撑**
- transcript、recovery、replacement、compact、session memory 都有专门模块，这说明“续航”是系统显式建模的能力，而不是副产物。

## 第 32 页：可观测性功能面

**核心内容**
- query profiler
- prompt cache break detection
- analyzeContext
- telemetry / metadata

**希望听众带走什么**
- 可观测性不是附属品，而是 runtime 演化能力的一部分。

**代码理解支撑**
- profiler、cache break detection、context analysis 都是为“解释为什么系统变慢、变贵、变坏”服务，这正是成熟 runtime 的标志。

## 第 33 页：功能面小结

**核心内容**
- 从职责上看，Claude Code 已经具备一个产品化 runtime 应有的主要系统面。

**希望听众带走什么**
- 这不是“功能堆叠”，而是系统成形的迹象。

**代码理解支撑**
- 如果只是堆功能，通常看不到这么明确的职责层次和配套的恢复/治理/观测机制；Claude Code 已经具备这些结构特征。

---

# 第五部分：重要功能详细介绍（13 页）

## 第 34 页：Prompt Stack（提示词栈）

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

**实践含义**
- 这解释了为什么 Claude Code 对“工程化任务表达”特别敏感。

**代码理解支撑**
- 默认 system prompt 直接把用户请求定义成软件工程任务，因此“工程化表达更稳”是系统默认角色推出来的，而不是经验心得。

## 第 35 页：Turn Loop（轮次循环）

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

**实践含义**
- 这说明 Claude Code 的内核本质上是一台恢复状态机。

**代码理解支撑**
- `State` 不只保存消息，还保存 transition、stop hook、tool summary 等跨轮状态，这正是状态机而不是线性调用器的特征。

## 第 36 页：Tool Pipeline（工具执行流水线）

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

**实践含义**
- 真正的自主边界长在执行流水线，而不在 UI。

**代码理解支撑**
- 工具调用先经过 parse、hooks、permissions、classifier，再到真正执行，这表明“模型能否行动”是在 runtime 执行链里裁决的。

## 第 37 页：BashTool

**功能**
- 提供最强但风险最高的执行能力

**实现原理**
- sandbox、只读识别、路径校验、破坏性判断、长输出处理

**代码支撑**
- [src/tools/BashTool/BashTool.tsx](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/BashTool.tsx)
- [src/tools/BashTool/prompt.ts](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts)

**实践含义**
- BashTool 的存在说明 Claude Code 有强执行力；围绕它的安全层则说明系统在认真处理 blast radius。

**代码理解支撑**
- BashTool 周围专门拆出了路径校验、只读识别、sandbox 判断等模块，这说明安全和可逆性是设计重点，不是文档提醒。

## 第 38 页：Compact（上下文压缩）

**功能**
- 控制长会话上下文体积

**实现原理**
- microcompact、autocompact、reactive compact、summary + attachments 重建工作面

**代码支撑**
- [src/services/compact/compact.ts](/Users/bobo/code/claude-code-source-code/src/services/compact/compact.ts)
- [src/services/compact/microCompact.ts](/Users/bobo/code/claude-code-source-code/src/services/compact/microCompact.ts)

**实践含义**
- compact 的意义不是总结历史，而是重建一个还能工作的工作面。

**代码理解支撑**
- compact 系列模块除了 summary 还保留 boundary、tail messages、attachments 等信息，说明它在保留“继续工作所需的表面”。

## 第 39 页：Transcript / Recovery

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

**实践含义**
- 中断恢复在这里是 runtime 能力，不是前端补丁。

**代码理解支撑**
- recovery 会主动修复 unresolved tool use、thinking、continuation 等问题，这种深度只能来自运行时语义，而不是前端展示层。

## 第 40 页：Content Replacement（内容替换）

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

**实践含义**
- Claude Code 对“模型已经见过什么”非常认真，这就是它前缀稳定性的来源。

**代码理解支撑**
- replacement state 显式记录 `seenIds` 和 `replacements`，说明系统在维护“看过的前缀不能漂”这一层不变量。

## 第 41 页：Skills（技能）

**功能**
- 把提示词能力做成条件激活 artifact

**实现原理**
- `loadSkillsDir.ts` 载入，按路径或上下文激活，compact 后保留 invoked skills

**代码支撑**
- [src/utils/skills/loadSkillsDir.ts](/Users/bobo/code/claude-code-source-code/src/utils/skills/loadSkillsDir.ts)
- [src/utils/attachments.ts](/Users/bobo/code/claude-code-source-code/src/utils/attachments.ts)

**实践含义**
- skill 不只是模板，而是能力面治理的一部分。

**代码理解支撑**
- skills 会被按路径、上下文和 compact 结果激活与保留，这说明它们是运行时能力对象，而不是静态提示词片段。

## 第 42 页：Attachments（上下文附件）

**功能**
- 动态组装当前轮上下文

**实现原理**
- relevant memories、skill delta、system reminders、task messages、file attachments

**代码支撑**
- [src/utils/attachments.ts](/Users/bobo/code/claude-code-source-code/src/utils/attachments.ts)

**实践含义**
- 模型每轮看到的都不是固定聊天历史，而是即时构造的工作面。

**代码理解支撑**
- attachments 会注入 memories、skill delta、task messages、system reminders，这证明 context 是逐轮拼出来的，不是原样聊天记录。

## 第 43 页：Permissions / Hooks / Classifier

**功能**
- 决定模型能否继续代表用户行动

**实现原理**
- allow / ask / deny、hook pre/post、classifier 决策链、auto mode

**代码支撑**
- [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)
- [src/utils/permissions/permissions.ts](/Users/bobo/code/claude-code-source-code/src/utils/permissions/permissions.ts)

**实践含义**
- 这是 Claude Code 真正的 autonomy boundary。

**代码理解支撑**
- permissions、hooks、classifier 都位于工具执行链中，说明约束点是在 runtime 主路径上，而不是外侧人工兜底。

## 第 44 页：Tasks / Subagents / Mailbox

**功能**
- 把异步执行体变成一等对象

**实现原理**
- task registry、local/remote agent、sidechain transcript、mailbox protocol

**代码支撑**
- [src/Task.ts](/Users/bobo/code/claude-code-source-code/src/Task.ts)
- [src/utils/task/framework.ts](/Users/bobo/code/claude-code-source-code/src/utils/task/framework.ts)
- [src/tools/AgentTool/runAgent.ts](/Users/bobo/code/claude-code-source-code/src/tools/AgentTool/runAgent.ts)

**实践含义**
- Claude Code 已经具备多执行体 runtime 的雏形。

**代码理解支撑**
- task registry、agent metadata、mailbox、sidechain transcript 同时存在，这已经是接近 actor model 的执行结构，而不是普通后台任务。

## 第 45 页：MCP / Plugins / Remote Capability

**功能**
- 把 Claude Code 扩展成能力枢纽

**实现原理**
- MCP client、plugin loader、remote session / remote agent

**代码支撑**
- [src/services/mcp/client.ts](/Users/bobo/code/claude-code-source-code/src/services/mcp/client.ts)
- [src/utils/plugins/pluginLoader.ts](/Users/bobo/code/claude-code-source-code/src/utils/plugins/pluginLoader.ts)

**实践含义**
- Claude Code 的能力上限来自协议与扩展面，不只来自模型。

**代码理解支撑**
- MCP client、plugin loader、remote capability 各有接入点，说明能力上限来自系统可接入什么，而不只是模型本体多强。

## 第 46 页：重要功能小结

**这一页要回答的问题**
- 为什么前面这些功能值得单独拆解。

**核心内容**
- 它们共同回答的是：
  - 怎么让系统继续工作
  - 怎么让模型能力受控
  - 怎么让成本和上下文可管理
  - 怎么让执行体和扩展体系成形

**希望听众带走什么**
- Claude Code 的核心不是一个点，而是一组互相支撑的 runtime 机制。

**代码理解支撑**
- 前面这些页分别落在 prompt、loop、pipeline、compact、recovery、task、extension，说明系统强项是控制链协同，不是单个亮点模块。

---

# 第六部分：理解边界与借鉴点（6 页）

## 第 47 页：如果要读这份代码，怎样建立理解顺序

**核心内容**
- 先读 `main.tsx`
- 再读 `QueryEngine.ts` / `query.ts`
- 再读 tool pipeline
- 再读 compact / recovery
- 最后读 control plane 和扩展系统

**代码支撑**
- [src/main.tsx](/Users/bobo/code/claude-code-source-code/src/main.tsx)
- [src/QueryEngine.ts](/Users/bobo/code/claude-code-source-code/src/QueryEngine.ts)
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)

**希望听众带走什么**
- 理解顺序决定理解质量，先抓主链，再看控制面和细节。

**代码理解支撑**
- 如果不先抓 `main.tsx`、`QueryEngine.ts`、`query.ts` 这条主链，后面的 compact、recovery、permissions 很容易被误读成局部补丁。

## 第 48 页：如果要修改这份代码，哪些链路必须先确认

**核心内容**
- 先判断改动落在哪一层
- 先确认状态载体
- 先确认 recovery / compact / cache 是否受影响

**代码支撑**
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)
- [src/utils/sessionStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/sessionStorage.ts)
- [src/services/compact/microCompact.ts](/Users/bobo/code/claude-code-source-code/src/services/compact/microCompact.ts)
- [src/utils/toolResultStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/toolResultStorage.ts)

**希望听众带走什么**
- 这种系统最怕改对表面、破坏底层不变量。

**代码理解支撑**
- compact、recovery、replacement、cache 逻辑高度耦合，说明很多表面修改都会影响底层续航语义。

## 第 49 页：从源码看，哪些设计最值得借鉴

**核心内容**
- turn loop 的恢复图思路
- transcript / recovery
- tool pipeline 的约束链
- content replacement / compact
- task runtime / mailbox

**代码支撑**
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)
- [src/utils/conversationRecovery.ts](/Users/bobo/code/claude-code-source-code/src/utils/conversationRecovery.ts)
- [src/services/tools/toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)
- [src/utils/toolResultStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/toolResultStorage.ts)
- [src/utils/task/framework.ts](/Users/bobo/code/claude-code-source-code/src/utils/task/framework.ts)

**希望听众带走什么**
- 真正值得借鉴的是不变量和控制链，不是目录结构。

**代码理解支撑**
- 值得借鉴的点横跨多个模块，说明本质是系统约束；而目录结构里已经混入大量历史演化和局部补偿。

## 第 50 页：从源码看，哪些地方体现了明显结构债

**核心内容**
- `query.ts` 的 God Loop 倾向
- `ToolUseContext` 过胖
- cache invariants 分散
- continuity surface 过多
- control plane owner 不够清晰

**代码支撑**
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)
- [src/Tool.ts](/Users/bobo/code/claude-code-source-code/src/Tool.ts)
- [src/utils/toolResultStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/toolResultStorage.ts)
- [src/utils/attachments.ts](/Users/bobo/code/claude-code-source-code/src/utils/attachments.ts)

**希望听众带走什么**
- 这份源码有很高的工程价值，但不适合被神化成“理想模板”。

**代码理解支撑**
- `query.ts` 的集中化、`ToolUseContext` 的膨胀、attachments 与 continuity 逻辑的扩张，都是成熟系统典型的结构债表现。

## 第 51 页：从代码演化角度看，更稳的方向是什么

**核心内容**
- 先建状态模型，再写实现
- 先把失败路径当一等对象
- 给主流程加 observability
- 不要只优化 happy path

**代码理解支撑**
- `query.ts` 已经事实性地表现出状态机形态，只是状态分散。
- recovery / compact / permissions / task lifecycle 都说明 failure path 是主路径的一部分。
- `queryProfiler.ts`、`promptCacheBreakDetection.ts`、`analyzeContext.ts` 说明 observability 不是附属品。

**代码支撑**
- [src/query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)
- [src/utils/queryProfiler.ts](/Users/bobo/code/claude-code-source-code/src/utils/queryProfiler.ts)
- [src/services/api/promptCacheBreakDetection.ts](/Users/bobo/code/claude-code-source-code/src/services/api/promptCacheBreakDetection.ts)
- [src/utils/analyzeContext.ts](/Users/bobo/code/claude-code-source-code/src/utils/analyzeContext.ts)

**希望听众带走什么**
- 更稳的方向，不是再加功能，而是把已经存在的隐式约束显式化。

## 第 52 页：总结页

**这一页要回答的问题**
- 整场分享最后应该留下什么结论。

**核心内容**
- Claude Code 不是聊天壳，而是 agent runtime。
- 它真正的强项是长期工作、恢复、压缩、能力治理和任务组织。
- 它真正值得学的是运行时不变量和控制链。
- 它的结构债也已经开始累积，因此更适合“借鉴原则”，不适合“照抄结构”。

**希望听众带走什么**
- 对负责人来说，Claude Code 的最大价值在于：它让我们看到了一套生产级 agent runtime 到底要补哪些账。

**代码理解支撑**
- 这个结论不是抽象印象，而是从整条证据链压出来的：宿主、loop、pipeline、recovery、compact、task、control plane 都在为“长期工作”买单。
