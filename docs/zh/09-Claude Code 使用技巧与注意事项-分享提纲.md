# Claude Code 使用技巧与注意事项：分享提纲

这份提纲用于支撑后续 PPT。它不是完整正文，而是“每一页讲什么、素材是什么、源码依据在哪里”。

对应正文：
- [09-Claude Code 使用技巧与注意事项.md](/Users/bobo/code/claude-code-source-code/docs/zh/09-Claude%20Code%20使用技巧与注意事项.md)

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

源码依据：
- [prompts.ts#L221](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L221)

## 3. 从源码看：Claude Code 是什么

核心信息：
- `main.tsx`：bootstrap / assembly
- `QueryEngine.ts`：conversation host
- `query.ts`：turn loop / runtime kernel
- `toolExecution.ts`：tool pipeline
- settings / auth / prompt / policy：control plane

讲述重点：
- 先建立“terminal agent runtime”这个模型
- 说明它默认按软件工程任务运行

源码依据：
- [main.tsx](/Users/bobo/code/claude-code-source-code/src/main.tsx)
- [QueryEngine.ts](/Users/bobo/code/claude-code-source-code/src/QueryEngine.ts)
- [query.ts](/Users/bobo/code/claude-code-source-code/src/query.ts)

关键代码点：
- `main.tsx` 负责 settings / auth / tools / plugins / MCP 的 assembly
- `QueryEngine.ts` 持有 messages、usage、file state、transcript
- `query.ts` 负责 `model -> tool -> model` 的 turn loop

## 4. 从源码反推：默认偏好的工作方式

核心信息：
- 先读代码
- 最小改动
- 优先复用
- 优先 dedicated tools
- 验证后如实汇报
- 高风险动作先确认

讲述重点：
- 后面所有技巧都从这些偏好推导出来

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

源码依据：
- [prompts.ts#L221](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L221)
- [prompts.ts#L230](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L230)
- [prompts.ts#L240](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L240)

关键代码点：
- `software engineering tasks`
- `do not propose changes to code you haven't read`
- `Report outcomes faithfully`

## 6. 技巧 2：明确要求先读代码，再改代码

推荐写法：

```text
先看 src/foo.ts 和 src/bar.ts，再决定改法。
```

为什么有效：
- 符合系统默认工作顺序
- 能减少无关探索

源码依据：
- [prompts.ts#L230](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L230)
- [messages.ts#L3344](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3344)

关键代码点：
- `read it first`
- `Explore — Use ... to read code`
- `Look for existing functions, utilities, and patterns to reuse`

## 7. 技巧 3：强调最小改动、优先复用

推荐写法：

```text
做最小必要改动；优先复用现有函数、工具和模式；不要新造一层抽象。
```

为什么有效：
- 能压住顺手重构和过早抽象

源码依据：
- [prompts.ts#L200](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L200)
- [prompts.ts#L203](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L203)

关键代码点：
- `Don't add features, refactor code, or make "improvements" beyond what was asked`
- `Don't create helpers, utilities, or abstractions for one-time operations`

## 8. 技巧 4：优先 dedicated tools，不要默认 Bash

推荐写法：

```text
优先直接读写文件，不要用 Bash 做本可由专用工具完成的事情。
```

为什么有效：
- Bash 是 fallback，不是首选
- 专用工具更容易被解释和审查

源码依据：
- [prompts.ts#L301](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L301)
- [prompts.ts#L305](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L305)
- [BashTool prompt#L297](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts#L297)

关键代码点：
- `default to using the dedicated tool`
- `Do NOT use the Bash tool ...`
- `If the commands are independent and can run in parallel`

## 9. 技巧 5：验证要求要写清楚，而且要如实汇报

推荐写法：

```text
改完后跑相关测试；如果没跑，请明确说明没有跑。
```

为什么有效：
- 可以减少“看似完成、其实没验证”的风险

源码依据：
- [prompts.ts#L211](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L211)
- [prompts.ts#L240](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L240)

关键代码点：
- `verify it actually works`
- `Never claim "all tests pass" when output shows failures`

## 10. 技巧 6：高风险动作要显式要求先确认

推荐写法：

```text
涉及 push、删除、覆盖、外部发送、破坏性 git 操作时，先告诉我并确认。
```

为什么有效：
- 这是系统默认的保守策略

源码依据：
- [prompts.ts#L258](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L258)
- [BashTool prompt#L304](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts#L304)

关键代码点：
- `reversibility and blast radius`
- `ask for confirmation before proceeding`
- `Only use destructive operations when they are truly the best approach`

## 11. 技巧 7：独立查询可以显式允许 parallel

推荐写法：

```text
如果这些查询彼此独立，可以并行完成；不要重复做相同搜索。
```

为什么有效：
- 系统原生鼓励独立工具调用并行化

源码依据：
- [prompts.ts#L310](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L310)
- [messages.ts#L3344](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3344)
- [BashTool prompt#L298](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts#L298)

关键代码点：
- `make all independent tool calls in parallel`
- `parallelize complex searches`
- `If the commands are independent and can run in parallel`

## 12. 常见误区与注意事项

核心信息：
- 不要把 Claude Code 当自由聊天助手
- 不要一上来让它大改一遍
- 不要默认它已经验证过
- 不要把高风险授权写得太模糊

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

## 13. 最小使用清单

最终压成 6 条：

1. 任务写成“目标 + 范围 + 约束 + 验证”
2. 明确要求先读代码
3. 明确要求最小改动、优先复用
4. 优先 dedicated tools，不要默认 Bash
5. 验证结果要如实汇报
6. 高风险动作先确认
