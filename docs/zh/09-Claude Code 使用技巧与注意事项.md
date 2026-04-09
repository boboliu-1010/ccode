# Claude Code 使用技巧与注意事项

这份文档从使用者视角总结 Claude Code 的实用技巧。目标不是讲架构，而是回答两个问题：

1. 平时怎样提需求，Claude Code 更容易表现稳定
2. 这些技巧为什么成立，源码里有什么依据

相关源码主要来自：

- [src/constants/prompts.ts](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts)
- [src/utils/messages.ts](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts)
- [src/tools/BashTool/prompt.ts](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts)

## 1. 任务要写成“目标 + 范围 + 约束 + 验证”

推荐写法：

```text
目标：修复/实现……
范围：只改 …… 相关代码
约束：不要做无关重构；不要新增不必要文件
验证：运行 …… 测试，并说明结果
```

为什么有效：

- Claude Code 的默认任务模型是“软件工程任务”，不是自由聊天。
- 明确范围和验证能减少它在“分析 / 实现 / 顺手优化”之间摇摆。

源码支撑：

- [prompts.ts#L221](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L221)
- [prompts.ts#L230](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L230)
- [prompts.ts#L240](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L240)

## 2. 明确要求“先读代码，再改代码”

推荐写法：

```text
先看 src/foo.ts 和 src/bar.ts，再决定改法。
```

为什么有效：

- 系统提示明确偏好“先理解现有实现，再修改”。
- 直接点名关键文件，能减少无关探索和上下文噪音。

源码支撑：

- [prompts.ts#L230](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L230)
- [messages.ts#L3344](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3344)

## 3. 明确强调“最小改动”和“优先复用”

推荐写法：

```text
做最小必要改动；优先复用现有函数、工具和模式；不要新造一层抽象。
```

为什么有效：

- Claude Code 明确反对 one-time helpers（一锤子 helper）和 premature abstraction（过早抽象）。
- 这会让它更愿意顺着现有结构修，而不是顺手重构出一套新设计。

源码支撑：

- [prompts.ts#L200](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L200)
- [prompts.ts#L203](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L203)
- [messages.ts#L3344](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3344)

## 4. 能不新建文件，就不要新建文件

推荐写法：

```text
除非绝对必要，不要新建文件，优先修改现有文件。
```

为什么有效：

- 系统提示明确把“避免 file bloat（文件膨胀）”设成默认偏好。
- 这对小改动特别有效，能减少它通过额外 helper / doc / temp file 绕开现有结构。

源码支撑：

- [prompts.ts#L231](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L231)

## 5. 优先让它用 dedicated tools（专用工具），不要滥用 Bash

推荐写法：

```text
优先直接读写文件，不要用 Bash 做本可由专用工具完成的事情。
```

为什么有效：

- 在源码里，Bash 被设定为 fallback tool（兜底工具），不是首选。
- 专用工具更容易被审查、被解释，也更容易受权限系统约束。

源码支撑：

- [prompts.ts#L301](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L301)
- [prompts.ts#L305](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L305)
- [BashTool prompt#L297](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts#L297)

## 6. 验证要求要写清楚，而且要它如实汇报

推荐写法：

```text
改完后跑相关测试；如果没跑，请明确说明没有跑，不要默认当作成功。
```

为什么有效：

- 源码里对“未验证却宣称完成”是强约束。
- 这能减少“看起来完成了，但其实没验证”的常见风险。

源码支撑：

- [prompts.ts#L211](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L211)
- [prompts.ts#L240](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L240)

## 7. 独立查询要显式允许 parallel（并行）

推荐写法：

```text
如果这些查询彼此独立，可以并行完成；不要重复做相同搜索。
```

为什么有效：

- Claude Code 的系统提示明确鼓励 independent tool calls（独立工具调用）并行化。
- Bash prompt 和 Plan Mode 相关提示里也都强调能并行就并行。

源码支撑：

- [prompts.ts#L310](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L310)
- [prompts.ts#L319](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L319)
- [messages.ts#L3344](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3344)
- [BashTool prompt#L298](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts#L298)

## 8. 高风险动作要显式要求“先确认”

推荐写法：

```text
涉及 push、删除、覆盖、外部发送、破坏性 git 操作时，先告诉我并确认。
```

为什么有效：

- 系统提示对 reversibility（可逆性）和 blast radius（影响范围）非常敏感。
- 只要动作难以回滚，默认就是应该确认。

源码支撑：

- [prompts.ts#L258](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L258)
- [BashTool prompt#L304](/Users/bobo/code/claude-code-source-code/src/tools/BashTool/prompt.ts#L304)

## 9. 做方案时，先走 Plan Mode 风格

推荐写法：

```text
先不要实现。先快速读关键文件，给我一个可执行计划；只问代码里无法确定的问题。
```

为什么有效：

- 源码里的 Plan Mode 明确规定：先 Explore（探索），再 Update plan（更新计划），最后再问用户代码里解决不了的问题。
- 用这种方式提需求，最接近系统原生的计划工作流。

源码支撑：

- [messages.ts#L3336](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3336)
- [messages.ts#L3350](/Users/bobo/code/claude-code-source-code/src/utils/messages.ts#L3350)

## 10. 一句最通用的增强指令

推荐写法：

```text
先读相关代码再改；优先复用现有实现；做最小必要改动；验证后如实汇报。
```

为什么有效：

- 这句话几乎把源码里最稳定的行为约束压成了一句。
- 不会过度限制模型，但能显著减少“改太多、想太多、报太满”这几类常见偏差。

源码支撑：

- [prompts.ts#L203](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L203)
- [prompts.ts#L230](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L230)
- [prompts.ts#L240](/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L240)

## 11. 最后压成一个用户清单

如果只保留用户最该记住的 6 条：

1. 用“目标 + 范围 + 约束 + 验证”提任务
2. 明确要求先读代码
3. 明确要求最小改动、优先复用
4. 优先 dedicated tools，不要默认走 Bash
5. 验证结果要如实汇报
6. 高风险动作先确认
