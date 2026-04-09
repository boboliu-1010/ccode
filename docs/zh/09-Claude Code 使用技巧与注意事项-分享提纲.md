# Claude Code 使用技巧与注意事项：分享提纲

这份提纲用于支撑后续 PPT。它不是完整正文，而是“每一页讲什么、素材是什么、源码依据在哪里”。

对应正文：
- [09-Claude Code 使用技巧与注意事项.md](/Users/bobo/code/claude-code-source-code/docs/zh/09-Claude%20Code%20使用技巧与注意事项.md)

## 术语对照

这组术语建议在 PPT 中统一按“英文术语（中文对照）”展示。

| 英文术语 | 中文对照 |
| --- | --- |
| `terminal agent runtime` | 终端代理运行时 |
| `prompt stack` | 提示词栈 |
| `conversation host` | 会话宿主 |
| `turn loop` | 轮次循环 |
| `runtime kernel` | 运行时内核 |
| `tool pipeline` | 工具执行流水线 |
| `control plane` | 控制面 |
| `Plan Mode workflow` | 规划模式工作流 |
| `dedicated tools` | 专用工具 |
| `parallel` | 并行 |
| `software engineering tasks` | 软件工程任务 |

## 0. 开场总结构图

用途：
- 这张图放在封面之后，用来先建立 Claude Code 的整体模型
- 它回答的问题不是“每个模块怎么实现”，而是“使用技巧为什么会受到这些架构层影响”

建议讲法：
- 最上层是用户输入
- 中间是 `prompt stack（提示词栈）`、`turn loop（轮次循环）`、`tool pipeline（工具执行流水线）`
- 下层是 tools / tasks / filesystem / shell
- 右侧是 settings / auth / policy 这些 `control plane（控制面）`
- 结论是：用户使用技巧之所以有效，是因为它们在影响这条主执行链和外围控制面

UML 总览图：

```mermaid
flowchart TD
    U["User Prompt<br/>用户输入"] --> PS["Prompt Stack<br/>提示词栈"]
    PS --> QE["QueryEngine<br/>Conversation Host / 会话宿主"]
    QE --> QL["query.ts<br/>Turn Loop / 轮次循环"]
    QL --> TP["Tool Pipeline<br/>工具执行流水线"]
    TP --> TOOLS["Tools / Bash / Read / Edit<br/>工具层"]
    TP --> TASKS["Tasks / Subagents / Mailbox<br/>任务与子代理"]
    TOOLS --> ENV["Filesystem / Shell / MCP<br/>执行环境"]
    TASKS --> ENV

    CP["Settings / Auth / Policy<br/>Control Plane / 控制面"] -.约束与裁决.-> PS
    CP -.约束与裁决.-> QE
    CP -.约束与裁决.-> QL
    CP -.约束与裁决.-> TP

    OBS["Telemetry / Profiling / Transcript<br/>可观测性与持久化"] -.记录与恢复.-> QE
    OBS -.记录与恢复.-> QL
    OBS -.记录与恢复.-> TP
```

这一页讲什么：
- Claude Code 不是自由聊天助手，而是一个 `terminal agent runtime（终端代理运行时）`
- 用户输入不会直接变成输出，而是经过 `prompt stack（提示词栈） -> turn loop（轮次循环） -> tool pipeline（工具执行流水线）`
- 使用技巧的作用，本质上是在影响这条链路的稳定性

架构支撑：
- `main.tsx` 负责整体 assembly
- `QueryEngine.ts` 负责 `conversation host（会话宿主）`
- `query.ts` 负责 `turn loop（轮次循环）`
- `toolExecution.ts` 负责 `tool pipeline（工具执行流水线）`
- settings / auth / policy 构成 `control plane（控制面）`

源码依据：
- [main.tsx](/Users/bobo/code/claude-code-source-code/src/main.tsx)
- [QueryEngine.ts](/Users/bobo/code/claude-code-source-code/src/QueryEngine.ts)
- [query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)
- [toolExecution.ts](/Users/bobo/code/claude-code-source-code/src/services/tools/toolExecution.ts)

## 1. 封面

标题：
- `Claude Code 使用技巧与注意事项`

副标题：
- `从源码反推的用户侧最佳实践`

讲述目标：
- 这不是功能介绍，而是使用方法论
- 所有建议都来自源码，不是个人经验

## 2. 先给结论：Claude Code 不是什么

核心信息：
- 不是自由聊天助手
- 不是“随便说一句就稳定帮你把工程活干好”
- 更像软件工程代理
- 输入越工程化，表现通常越稳定

架构支撑：
- `prompt stack（提示词栈）` 把 Claude Code 的默认角色定义成软件工程代理，而不是自由聊天助手

源码依据：
- [prompts.ts#L221](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L221)

关键代码片段：

```ts
The user will primarily request you to perform software engineering tasks.
```

## 3. 从源码看：Claude Code 是什么

核心信息：
- `main.tsx`：`bootstrap / assembly（启动 / 装配）`
- `QueryEngine.ts`：`conversation host（会话宿主）`
- `query.ts`：`turn loop / runtime kernel（轮次循环 / 运行时内核）`
- `toolExecution.ts`：`tool pipeline（工具执行流水线）`
- settings / auth / prompt / policy：`control plane（控制面）`

讲述重点：
- 先建立“`terminal agent runtime（终端代理运行时）`”这个模型
- 说明它默认按软件工程任务运行

架构支撑：
- `main.tsx` 负责 assembly
- `QueryEngine.ts` 负责 `conversation host（会话宿主）`
- `query.ts` 负责 `turn loop（轮次循环）`
- `toolExecution.ts` 负责 `tool pipeline（工具执行流水线）`

源码依据：
- [main.tsx](/Users/bobo/code/claude-code-source-code/src/main.tsx)
- [QueryEngine.ts](/Users/bobo/code/claude-code-source-code/src/QueryEngine.ts)
- [query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)

关键代码点：
- `main.tsx` 负责 settings / auth / tools / plugins / MCP 的 assembly
- `QueryEngine.ts` 持有 messages、usage、file state、transcript
- `query.ts` 负责 `model -> tool -> model` 的 turn loop

关键代码片段：

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

## 4. 从源码反推：默认偏好的工作方式

核心信息：
- 先读代码
- 最小改动
- 优先复用
- 优先 `dedicated tools（专用工具）`
- 验证后如实汇报
- 高风险动作先确认

讲述重点：
- 后面所有技巧都从这些偏好推导出来

架构支撑：
- 这些偏好主要落在 `prompt stack（提示词栈）`
- 执行层再由 `tool pipeline（工具执行流水线）` 和权限系统兜底

源码依据：
- [prompts.ts#L230](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L230)
- [prompts.ts#L203](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L203)
- [prompts.ts#L305](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L305)
- [prompts.ts#L240](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L240)
- [prompts.ts#L258](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L258)

关键代码点：
- `do not propose changes to code you haven't read`
- `Don't create helpers ... for one-time operations`
- `Do NOT use the Bash tool ... when a relevant dedicated tool is provided`
- `Report outcomes faithfully`
- `ask for confirmation before proceeding`

关键代码片段：

```ts
In general, do not propose changes to code you haven't read.
```

```ts
Do NOT use the Bash tool to run commands when a relevant dedicated tool is provided.
```

```ts
Report outcomes faithfully: if tests fail, say so ...
```

```ts
ask for confirmation before proceeding
```

## 5. 技巧 1：任务写成“目标 + 范围 + 约束 + 验证”

推荐写法：

```text
目标：修复/实现……
范围：只改 …… 相关代码
约束：不要做无关重构；不要新增不必要文件
验证：运行 …… 测试，并说明结果
```

为什么有效：
- 能减少分析 / 实现 / 顺手优化之间的歧义

架构支撑：
- `prompt stack（提示词栈）` 默认把请求理解成软件工程任务
- `turn loop（轮次循环）` 会围绕用户给出的目标、范围和验证要求持续推进

源码依据：
- [prompts.ts#L221](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L221)
- [prompts.ts#L230](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L230)
- [prompts.ts#L240](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L240)

关键代码点：
- `software engineering tasks`
- `do not propose changes to code you haven't read`
- `Report outcomes faithfully`

关键代码片段：

```ts
The user will primarily request you to perform software engineering tasks.
```

```ts
In general, do not propose changes to code you haven't read.
```

```ts
Report outcomes faithfully: if tests fail, say so ...
```

## 6. 技巧 2：明确要求先读代码，再改代码

推荐写法：

```text
先看 src/foo.ts 和 src/bar.ts，再决定改法。
```

为什么有效：
- 符合系统默认工作顺序
- 能减少无关探索

架构支撑：
- `prompt stack（提示词栈）` 明确要求先读代码
- `Plan Mode workflow（规划模式工作流）` 也要求先 explore，再规划或实现

源码依据：
- [prompts.ts#L230](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L230)
- [messages.ts#L3344](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3344)

关键代码点：
- `read it first`
- `Explore — Use ... to read code`
- `Look for existing functions, utilities, and patterns to reuse`

关键代码片段：

```ts
In general, do not propose changes to code you haven't read.
If a user asks about or wants you to modify a file, read it first.
```

```md
1. **Explore** — Use ${getReadOnlyToolNames()} to read code.
Look for existing functions, utilities, and patterns to reuse.
```

## 7. 技巧 3：强调最小改动、优先复用

推荐写法：

```text
做最小必要改动；优先复用现有函数、工具和模式；不要新造一层抽象。
```

为什么有效：
- 能压住顺手重构和过早抽象

架构支撑：
- `prompt stack（提示词栈）` 本身就在抑制范围漂移和不必要抽象
- `tool pipeline（工具执行流水线）` 更适合执行局部、清晰、可验证的改动

源码依据：
- [prompts.ts#L200](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L200)
- [prompts.ts#L203](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L203)

关键代码点：
- `Don't add features, refactor code, or make "improvements" beyond what was asked`
- `Don't create helpers, utilities, or abstractions for one-time operations`

关键代码片段：

```ts
Don't add features, refactor code, or make "improvements" beyond what was asked.
```

```ts
Don't create helpers, utilities, or abstractions for one-time operations.
```

## 8. 技巧 4：优先 dedicated tools（专用工具），不要默认 Bash

推荐写法：

```text
优先直接读写文件，不要用 Bash 做本可由专用工具完成的事情。
```

为什么有效：
- Bash 是 fallback，不是首选
- 专用工具更容易被解释和审查

架构支撑：
- `tool pipeline（工具执行流水线）` 里 `dedicated tools（专用工具）` 是一等能力面
- Bash 是更自由也更高风险的 fallback surface

源码依据：
- [prompts.ts#L301](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L301)
- [prompts.ts#L305](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L305)
- [BashTool prompt#L297](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts#L297)

关键代码点：
- `default to using the dedicated tool`
- `Do NOT use the Bash tool ...`
- `If the commands are independent and can run in parallel`

关键代码片段：

```ts
default to using the dedicated tool and only fallback on using the Bash tool ...
```

```ts
Do NOT use the Bash tool to run commands when a relevant dedicated tool is provided.
```

```ts
If the commands are independent and can run in parallel, make multiple Bash tool calls in a single message.
```

## 9. 技巧 5：验证要求要写清楚，而且要如实汇报

推荐写法：

```text
改完后跑相关测试；如果没跑，请明确说明没有跑。
```

为什么有效：
- 可以减少“看似完成、其实没验证”的风险

架构支撑：
- `prompt stack（提示词栈）` 明确要求 verify 和 faithful reporting
- `turn loop（轮次循环）` 默认不会替用户假设“验证已经完成”

源码依据：
- [prompts.ts#L211](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L211)
- [prompts.ts#L240](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L240)

关键代码点：
- `verify it actually works`
- `Never claim "all tests pass" when output shows failures`

关键代码片段：

```ts
Before reporting a task complete, verify it actually works.
```

```ts
Never claim "all tests pass" when output shows failures.
```

## 10. 技巧 6：高风险动作要显式要求先确认

推荐写法：

```text
涉及 push、删除、覆盖、外部发送、破坏性 git 操作时，先告诉我并确认。
```

为什么有效：
- 这是系统默认的保守策略

架构支撑：
- `prompt stack（提示词栈）` 先定义高风险动作的确认边界
- `tool pipeline（工具执行流水线）` 和 Bash 约束负责在执行面进一步收紧

源码依据：
- [prompts.ts#L258](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L258)
- [BashTool prompt#L304](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts#L304)

关键代码点：
- `reversibility and blast radius`
- `ask for confirmation before proceeding`
- `Only use destructive operations when they are truly the best approach`

关键代码片段：

```ts
Carefully consider the reversibility and blast radius of actions.
```

```ts
ask for confirmation before proceeding
```

```ts
Only use destructive operations when they are truly the best approach.
```

## 11. 技巧 7：独立查询可以显式允许 parallel（并行）

推荐写法：

```text
如果这些查询彼此独立，可以并行完成；不要重复做相同搜索。
```

为什么有效：
- 系统原生鼓励独立工具调用并行化

架构支撑：
- `tool pipeline（工具执行流水线）` 原生支持 independent tool calls 并行
- `Plan Mode workflow（规划模式工作流）` 也鼓励先并行探索，再收敛实现

源码依据：
- [prompts.ts#L310](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L310)
- [messages.ts#L3344](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3344)
- [BashTool prompt#L298](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts#L298)

关键代码点：
- `make all independent tool calls in parallel`
- `parallelize complex searches`
- `If the commands are independent and can run in parallel`

关键代码片段：

```ts
make all independent tool calls in parallel
```

```md
1. **Explore** — Use ${getReadOnlyToolNames()} to read code.
Look for existing functions, utilities, and patterns to reuse.
```

```ts
If the commands are independent and can run in parallel, make multiple Bash tool calls ...
```

## 12. 常见误区与注意事项

核心信息：
- 不要把 Claude Code 当自由聊天助手
- 不要一上来让它大改一遍
- 不要默认它已经验证过
- 不要把高风险授权写得太模糊

架构支撑：
- 这些误区本质上都在对抗 `prompt stack（提示词栈）` 的默认约束
- 一旦输入方式偏离默认工作流，`turn loop（轮次循环）` 的稳定性就更容易下降

源码依据：
- [prompts.ts#L221](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L221)
- [prompts.ts#L200](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L200)
- [prompts.ts#L240](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L240)
- [prompts.ts#L258](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L258)

关键代码点：
- `software engineering tasks`
- `Don't add features ... beyond what was asked`
- `Report outcomes faithfully`
- `ask for confirmation before proceeding`

关键代码片段：

```ts
The user will primarily request you to perform software engineering tasks.
```

```ts
Don't add features, refactor code, or make "improvements" beyond what was asked.
```

```ts
Report outcomes faithfully ...
```

```ts
ask for confirmation before proceeding
```

## 13. 最小使用清单

最终压成 6 条：

1. 任务写成“目标 + 范围 + 约束 + 验证”
2. 明确要求先读代码
3. 明确要求最小改动、优先复用
4. 优先 dedicated tools（专用工具），不要默认 Bash
5. 验证结果要如实汇报
6. 高风险动作先确认
