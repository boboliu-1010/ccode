# Claude Code 源码深度解读：文档

这份文档面向正式分享和负责人阅读。目标不是做逐文件解释，而是先回答几个更有决策价值的问题：

1. Claude Code 从工程实现上到底是什么
2. 它为什么比常见 demo agent 更像生产级 runtime
3. 哪些机制真正支撑了“长期工作”
4. 这份源码最值得借鉴什么，又不该误读什么

相关提纲见：

- [10-Claude Code 源码深度解读-分享提纲.md](/Users/bobo/code/claude-code-source-code/docs/zh/10-Claude%20Code%20源码深度解读-分享提纲.md)

## 1. 先给结论：这份源码为什么值得看

Claude Code 值得研究，不是因为它“会调很多工具”，而是因为它已经为 agent runtime 里最难的几件事付过工程账：

- 长会话如何继续工作
- 工具结果过大时如何保持上下文稳定
- 中断后如何恢复到可继续运行状态
- 工具调用如何经过权限、钩子和分类器约束
- 多执行体如何有自己的生命周期、记录和消息协议

从这个角度看，这份代码不是一个聊天 CLI 的增强版，而是一个已经相当完整的 **terminal agent runtime（终端代理运行时）**。

对负责人来说，它的价值主要有三点：

- 它提供了一份少见的“生产级 agent runtime 样本”
- 它能帮助区分“功能多”和“系统真能长期工作”之间的差别
- 它既有值得借鉴的控制链，也有已经开始显现的结构债

## 2. Claude Code 到底是什么

如果只看使用体验，Claude Code 像一个“能改代码的命令行助手”。  
但从源码看，它更准确的定位是一个由多层组成的 runtime：

- **bootstrap / assembly（启动装配）**  
  [main.tsx](/Users/bobo/code/claude-code-source-code/src/main.tsx) 负责把 settings、auth、policy、plugins、skills、MCP、tools 装起来。
- **conversation host（会话宿主）**  
  [QueryEngine.ts](/Users/bobo/code/claude-code-source-code/src/QueryEngine.ts) 负责持有多轮消息、usage、file state、transcript 相关状态。
- **turn loop / runtime kernel（轮次循环 / 运行时内核）**  
  [query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts) 负责把一轮轮 `model -> tool -> model` 执行推进下去。
- **tool pipeline（工具执行流水线）**  
  [toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts) 负责 parse、validate、hooks、permissions、classifier、`tool.call()`、post-process。
- **control plane（控制面）**  
  包括 settings、auth、policy limits、managed settings、prompt stack。
- **task runtime（任务运行时）**  
  包括 task registry、subagents、mailbox、sidechain transcript。

这一层次划分很重要，因为它直接解释了为什么 Claude Code 不是“问一次模型、拿一个结果”的壳。

## 3. 总体架构：最关键的几层

### 3.1 `main.tsx`：系统装配入口

[main.tsx](/Users/bobo/code/claude-code-source-code/src/main.tsx) 处理的是运行前条件，而不是推理逻辑本身。它负责：

- 读取 settings / auth / policy
- 初始化 commands / tools
- 初始化 plugins / skills / MCP
- 配置权限模式、远程设置、遥测
- 进入 REPL 或 headless 模式

因此它更像启动器，而不是内核。

### 3.2 `QueryEngine.ts`：会话宿主

[QueryEngine.ts](/Users/bobo/code/claude-code-source-code/src/QueryEngine.ts) 的价值在于，它把“会话寿命”从单轮执行里单独抽出来。

关键代码片段：

```ts
export class QueryEngine {
  private mutableMessages: Message[]
  private totalUsage: NonNullableUsage
  private readFileState: FileStateCache
}
```

这说明它持有的不是一次回答，而是：

- 多轮消息视图
- 累计 usage
- 文件状态
- transcript 相关宿主状态

这也是为什么它更像 `conversation host（会话宿主）`。

### 3.3 `query.ts`：执行内核

[query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts) 是 Claude Code 的核心。它不是“发请求然后返回”，而是在维护一轮轮可继续的执行闭环。

关键代码片段：

```ts
type State = {
  messages: Message[]
  toolUseContext: ToolUseContext
  turnCount: number
  transition: Continue | undefined
}
```

这里最重要的不是 `messages`，而是它显式维护了：

- 当前执行状态
- 工具上下文
- turn 计数
- continuation / recovery 迁移

这说明它更接近 `state machine（状态机）` 或 `recovery graph（恢复图）`，而不是简单的 pipeline。

### 3.4 `toolExecution.ts`：工具调用不是直接执行

[toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts) 是理解 Claude Code “可控性”的关键。

工具调用真正经过的是：

- input parse
- validate / normalize
- pre hooks
- permissions / classifier
- `tool.call()`
- post hooks / result processing

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

这意味着模型不能直接碰系统，它只能提出动作请求，真正是否执行由 runtime 决定。

## 4. 主工作流程：一次请求如何流过 Claude Code

从工作流程看，Claude Code 的关键不是“回答问题”，而是把一次请求穿过多个层后仍然维持可继续状态。

简化后的主链路是：

1. 用户输入进入 CLI / REPL
2. `main.tsx` 完成 settings、auth、tools、policy 的装配
3. `QueryEngine.ts` 接管当前会话状态
4. `query.ts` 组装当前轮上下文
5. 模型返回 assistant 内容或 `tool_use`
6. `toolExecution.ts` 执行工具并生成 `tool_result`
7. `tool_result` 回灌到消息后继续下一轮
8. 必要时进入 compact、continuation、recovery

这里真正值得注意的是：Claude Code 的主流程从一开始就把失败、压缩、恢复和续写视为常规路径，而不是异常路径。

## 5. 为什么它比 demo agent 更像生产系统

这份源码最有价值的部分，是它已经认真处理了 production runtime 才会认真处理的问题。

### 5.1 Prompt Stack（提示词栈）不是文案，而是控制面

[systemPrompt.ts](/Users/bobo/code/claude-code-source-code/src/utils/systemPrompt.ts) 和 [prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts) 说明，Claude Code 的 system prompt 不是一段“帮助文案”，而是行为法则。

关键代码片段：

```ts
The user will primarily request you to perform software engineering tasks.
```

这段话的含义不是“偏好”，而是运行时默认世界观：

- 把请求当软件工程任务
- 偏好先读代码
- 偏好最小改动
- 偏好专用工具
- 要求如实汇报验证结果

这也是为什么很多用户技巧其实不是“prompt engineering 小技巧”，而是在配合系统默认行为。

### 5.2 Turn Loop（轮次循环）不是线性流水线，而是恢复图

很多 demo agent 的结构是：

- sample
- tool
- sample
- done

Claude Code 不是。它的 `turn loop` 中途还要处理：

- `prompt_too_long`
- `max_output_tokens`
- continuation
- stop hook
- reactive compact

因此这里真正被维护的是：

> 一条可继续、可恢复、可压缩的合法轨迹

这也是为什么 `query.ts` 值得被视为系统核心。

### 5.3 Transcript / Recovery（会话记录 / 恢复）是 durable state，不是聊天记录

[sessionStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/sessionStorage.ts) 和 [conversationRecovery.ts](/Users/bobo/code/claude-code-source-code/src/utils/conversationRecovery.ts) 说明，Claude Code 的 transcript 不是普通聊天日志。

它保存的是一条带 `parentUuid` 的消息链，而 recovery 的目标也不是“恢复 UI”，而是：

> 回到 API 还能继续运行的合法状态

关键代码片段：

```ts
const filteredToolUses = filterUnresolvedToolUses(migratedMessages)
const filteredThinking =
  filterOrphanedThinkingOnlyMessages(filteredToolUses)
```

这意味着恢复前要先修复坏掉的状态，而不是直接把历史喂回模型。

### 5.4 Compact（上下文压缩）不是摘要功能，而是工作面重建

[compact.ts](/Users/bobo/code/claude-code-source-code/src/services/compact/compact.ts) 和 [microCompact.ts](/Users/bobo/code/claude-code-source-code/src/services/compact/microCompact.ts) 说明，Claude Code 的 compact 不是简单“把历史总结一下”。

它更准确的作用是：

> 重建一个还能继续工作的最小 context

compact 的不同层次包括：

- microcompact
- snip
- autocompact
- reactive compact

compact 后保留的也不只是 summary，还包括 boundary、tail messages、attachments、skills、plan mode 信息等。

### 5.5 Content Replacement（内容替换）是在维护前缀稳定性

[toolResultStorage.ts](/Users/bobo/code/claude-code-source-code/src/utils/toolResultStorage.ts) 是整份代码里很值钱的一层。

关键代码片段：

```ts
export type ContentReplacementState = {
  seenIds: Set<string>
  replacements: Map<string, string>
}
```

这一层处理的是：

- 工具输出太大时先落盘
- 上下文里只放稳定 preview
- 一旦某个 tool result 被替换，其命运就被冻结
- 恢复时还要重放同一 replacement

它的真正作用不是“省 token”，而是维护 prompt cache prefix 的稳定性。

### 5.6 Task Runtime（任务运行时）说明它已经进入多执行体阶段

[Task.ts](/Users/bobo/code/claude-code-source-code/src/Task.ts)、[framework.ts](/Users/bobo/code/claude-code-source-code/src/utils/task/framework.ts) 和 [runAgent.ts](/Users/bobo/code/claude-code-source-code/src/tools/AgentTool/runAgent.ts) 说明，Claude Code 已经不只是单轮对话。

它已经有：

- task identity
- task lifecycle
- local / remote agent
- sidechain transcript
- mailbox protocol

这更接近 `actor model（参与者模型）`，而不是“顺手开个后台线程”。

## 6. 功能面：不要平铺看功能，要按系统职责看

如果从产品功能看，Claude Code 功能很多；但从系统职责看，更适合按下面几类理解。

### 6.1 交互层

- CLI / REPL
- commands
- headless / SDK
- plan mode
- structured output

### 6.2 执行层

- Read / Write / Edit / Grep / Glob
- BashTool
- Agent / Task / REPL
- file state / edit safety

### 6.3 扩展层

- MCP
- plugins
- skills
- remote session / remote agent

### 6.4 治理层

- auth
- policy limits
- managed settings
- permission rules
- hooks / classifier

### 6.5 续航层

- transcript
- recovery
- compact
- content replacement
- session memory

### 6.6 可观测性

- query profiler
- prompt cache break detection
- analyzeContext
- telemetry / metadata

从管理视角看，功能多本身不重要；重要的是这些功能已经能围绕一条主执行链形成体系。

## 7. 哪些理解最值得带走

如果要把整份源码压成几条判断，我会保留下面这些。

### 7.1 最值得借鉴的是“不变量”，不是文件结构

Claude Code 最值得学的不是它今天的目录长相，而是它已经显式维护了这些 runtime 约束：

- `tool_use -> tool_result` 必须闭合
- transcript 必须可恢复
- 大输出不能让上下文失控
- context 不能无限膨胀
- 能力面不能无边界暴露
- 异步执行体必须有生命周期和消息协议

### 7.2 真正拉开层次的是长期工作能力

这份代码和 demo agent 的差别，主要不在“功能覆盖”，而在：

- 会话会不会长时间跑下去
- 中断后能不能恢复
- 成本会不会失控
- 权限边界能不能落地
- 失败路径是不是系统级对象

### 7.3 这份代码也已经有明显结构债

它不是模板，问题也很清楚：

- `query.ts` 已经接近 God Loop
- `ToolUseContext` 过胖
- cache invariants 分散
- continuity surface 过多
- control plane owner 不够清晰

因此，这份源码更适合被看成：

- 一份成熟 runtime 的约束样本
- 一份生产补丁和结构债并存的演化记录

而不是一份可以直接照抄的架构蓝图。

## 8. 对 Marcus 这样的负责人，最值得带走的三点

如果这份材料要发给负责人，我认为最值得带走的不是细节，而是下面三点：

1. Claude Code 的价值不在“能调很多工具”，而在它已经解决了长期工作所需的关键 runtime 问题。
2. 这份源码最值得借鉴的是控制链和不变量，而不是目录结构和补丁实现。
3. 真正的生产级 agent runtime，不是“模型够强”就行，而是外层必须持续维护状态、压缩、恢复、权限、任务和可观测性。

这也是这份源码最稀缺的地方。
