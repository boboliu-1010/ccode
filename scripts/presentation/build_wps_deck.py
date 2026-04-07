from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


TITLE_COLOR = RGBColor(11, 31, 68)
TEXT_COLOR = RGBColor(31, 41, 55)
MUTED_COLOR = RGBColor(71, 85, 105)
ACCENT = RGBColor(32, 82, 149)
BG = RGBColor(248, 250, 252)
LEAD_BG = RGBColor(16, 28, 63)
WHITE = RGBColor(255, 255, 255)
LINE = RGBColor(219, 228, 240)

FONT_SANS = "PingFang SC"
FONT_FALLBACK = "Avenir Next"


def set_run_font(run, size, color, bold=False):
    run.font.name = FONT_SANS
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


def set_text_frame_style(tf):
    tf.word_wrap = True
    tf.margin_left = Pt(6)
    tf.margin_right = Pt(6)
    tf.margin_top = Pt(4)
    tf.margin_bottom = Pt(4)


def add_bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_title(slide, text, lead=False):
    box = slide.shapes.add_textbox(Inches(0.65), Inches(0.45), Inches(11.6), Inches(0.85))
    tf = box.text_frame
    set_text_frame_style(tf)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = text
    set_run_font(r, 26 if not lead else 28, WHITE if lead else TITLE_COLOR, True)
    p.alignment = PP_ALIGN.LEFT
    if not lead:
        line = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(0.68), Inches(1.25), Inches(2.4), Inches(0.04)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = LINE
        line.line.fill.background()


def add_subtitle(slide, text, lead=False):
    box = slide.shapes.add_textbox(Inches(0.72), Inches(1.55), Inches(11.2), Inches(0.9))
    tf = box.text_frame
    set_text_frame_style(tf)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = text
    set_run_font(r, 16, WHITE if lead else MUTED_COLOR, False)


def add_bullets(slide, bullets, top=1.75, left=0.9, width=11.0, height=4.8, lead=False):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    set_text_frame_style(tf)
    tf.clear()
    first = True
    for item in bullets:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.level = 0
        p.bullet = True
        r = p.add_run()
        r.text = item
        set_run_font(r, 20 if not lead else 19, WHITE if lead else TEXT_COLOR)
        p.space_after = Pt(8)


def add_two_col_bullets(slide, left_title, left_items, right_title, right_items):
    for x, title, items in [
        (0.75, left_title, left_items),
        (6.45, right_title, right_items),
    ]:
        head = slide.shapes.add_textbox(Inches(x), Inches(1.7), Inches(4.9), Inches(0.45))
        tf = head.text_frame
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = title
        set_run_font(r, 17, ACCENT, True)
        add_bullets(slide, items, top=2.15, left=x, width=4.8, height=4.0)


def add_quote(slide, text):
    box = slide.shapes.add_textbox(Inches(0.95), Inches(5.6), Inches(10.8), Inches(0.9))
    tf = box.text_frame
    set_text_frame_style(tf)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = text
    set_run_font(r, 16, MUTED_COLOR, False)


def add_footer(slide, text):
    box = slide.shapes.add_textbox(Inches(10.5), Inches(6.85), Inches(2.2), Inches(0.3))
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    r = p.add_run()
    r.text = text
    set_run_font(r, 10, MUTED_COLOR)


def add_section_slide(prs, title, subtitle):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, LEAD_BG)
    add_title(slide, title, lead=True)
    add_subtitle(slide, subtitle, lead=True)
    return slide


def add_content_slide(prs, title, bullets, subtitle=None, quote=None, footer=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG)
    add_title(slide, title)
    if subtitle:
        add_subtitle(slide, subtitle)
        top = 2.15
    else:
        top = 1.7
    add_bullets(slide, bullets, top=top)
    if quote:
        add_quote(slide, quote)
    if footer:
        add_footer(slide, footer)
    return slide


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, LEAD_BG)
    add_title(slide, "Claude Code Source 代码走读", lead=True)
    add_subtitle(slide, "基于源码的 runtime 架构、主调用链与关键设计", lead=True)
    add_bullets(
        slide,
        [
            "重点：turn loop、compact、tool execution、task runtime",
            "目标：先建立整体模型，再进入关键代码",
        ],
        top=2.45,
        left=0.85,
        width=11.3,
        height=2.0,
        lead=True,
    )

    add_content_slide(
        prs,
        "分享目录",
        [
            "这份仓库本质上是什么",
            "架构总览与主执行链路",
            "turn loop 与 conversation host",
            "recovery、compact 与 context 装配",
            "tool execution、task runtime 与 mailbox",
            "认证、策略、扩展系统与可观测性",
            "最后总结与阅读建议",
        ],
    )

    add_section_slide(prs, "一、先建立整体模型", "先回答：这份仓库到底是什么，以及应该先从哪几层开始读。")

    add_content_slide(
        prs,
        "这份仓库本质上是什么",
        [
            "不是简单聊天 CLI，也不是薄薄的 SDK demo",
            "更接近一个完整的本地 agent runtime",
            "核心包括：CLI/TUI、会话状态、turn loop、认证/API、策略控制、扩展系统",
            "阅读时不要只把它理解成“调用模型 API 的壳”",
        ],
    )

    add_content_slide(
        prs,
        "最值得先记住的入口文件",
        [
            "main.tsx：总入口与总装配",
            "query.ts：turn loop runtime kernel",
            "QueryEngine.ts：conversation host",
            "Tool.ts：工具协议与 ToolUseContext",
            "tools.ts：工具注册中心",
        ],
    )

    add_section_slide(prs, "二、先看主链路", "从启动到一次完整 turn，先把系统怎么跑起来看清。")

    add_content_slide(
        prs,
        "架构总览",
        [
            "main.tsx 把系统装起来",
            "query.ts 让系统跑起来",
            "API 层负责模型适配",
            "tools / MCP / plugins / skills 提供能力面",
            "settings / auth / policy 决定约束边界",
        ],
        quote="一句话：main.tsx 负责装配，query.ts 负责推进，其余模块提供能力、状态和约束。",
    )

    add_content_slide(
        prs,
        "主执行链路",
        [
            "用户输入进入 main.tsx",
            "构造 commands / tools / app state / QueryEngine",
            "query.ts 发起模型请求",
            "若出现 tool_use，进入 tool orchestration",
            "tool_result 回灌后继续下一轮",
        ],
        quote="这是一个“模型调用”和“工具调用”反复往返的闭环。",
    )

    add_content_slide(
        prs,
        "启动阶段：先把 runtime surface 装好",
        [
            "参数解析与认证预热",
            "settings 合并、GrowthBook / telemetry 初始化",
            "remote managed settings 与 policy limits 初始化",
            "commands / tools / MCP / skills 注册",
            "重点不是“启动聊天”，而是把整套运行时表面装配完成",
        ],
    )

    add_section_slide(prs, "三、为什么 query.ts 是核心", "真正把 Claude Code 变成 agent runtime 的，是 turn loop。")

    add_content_slide(
        prs,
        "为什么 query.ts 是核心",
        [
            "它不是一次 API 调用的包装层，而是 runtime kernel",
            "负责准备 messages、context 治理、模型请求、streaming 输出",
            "负责处理 tool_use / tool_result",
            "负责决定 continue / retry / compact / stop",
        ],
    )

    add_content_slide(
        prs,
        "turn loop 的结构",
        [
            "先做 context 治理：tool result budget、snip、microcompact、collapse、autocompact",
            "再构造 API 请求并接收 streaming 输出",
            "若出现 tool_use，进入工具执行器",
            "tool_result 回写 messages 后，决定是否继续下一轮",
            "因此它更像带 recovery 分支的 state machine，而不是线性 pipeline",
        ],
    )

    add_content_slide(
        prs,
        "QueryEngine.ts：conversation host",
        [
            "不是内核本身，而是会话宿主",
            "负责保持多轮消息历史、聚合 usage、维护 permission denial",
            "持有 readFileState、预落盘 transcript、做 SDK/headless 输出投影",
            "可以简单记成：query.ts 负责一轮怎么跑，QueryEngine.ts 负责一段会话怎么活",
        ],
    )

    add_section_slide(prs, "四、长会话为什么还能稳定工作", "关键不是“回答更聪明”，而是 runtime 如何保住连续性。")

    add_content_slide(
        prs,
        "为什么会话可以恢复",
        [
            "Claude Code 维护的是可恢复消息链，不只是聊天记录",
            "sessionStorage.ts 负责 durable transcript",
            "conversationRecovery.ts 会过滤坏消息并补 continuation",
            "恢复目标不是忠实回放磁盘内容，而是把系统修回 API 可继续状态",
        ],
    )

    add_content_slide(
        prs,
        "为什么大 tool result 不会拖垮上下文",
        [
            "关键机制是 tool result budget / content replacement",
            "解决的不是“截断输出”，而是“冻结输出命运”",
            "某个 tool_use_id 一旦决定替换，后面必须稳定复用相同 replacement",
            "价值是保护 prompt cache prefix，降低 long-running session 漂移",
        ],
    )

    add_content_slide(
        prs,
        "compact：分层整理，而不是一刀切摘要",
        [
            "运行时至少有 microcompact、snip、context collapse、autocompact、reactive compact、/compact、session memory compact",
            "要按两条轴来理解：主动整理 vs 被动恢复；轻量缩减 vs full compact",
            "full compact 的目标也不是简单摘要，而是重建可继续工作的最小 context",
        ],
    )

    add_content_slide(
        prs,
        "compact 后到底保留什么",
        [
            "compact boundary",
            "summary",
            "messagesToKeep",
            "文件恢复 attachment",
            "plan_mode、invoked_skills、deferred tools / MCP delta、hook results",
        ],
        quote="结论：compact 后不是只剩一段摘要，而是尽量保住当前工作面。",
    )

    add_content_slide(
        prs,
        "Skills 与 attachments 怎么进上下文",
        [
            "Skills 不是普通文档，而是结构化能力单元",
            "skill 被扫描到只是 capability 可见，真正调用时才把正文展开进 context",
            "attachments.ts 更像 context router，会按 turn 注入 memories、skills、plan_mode、mailbox、delta 等工作面信息",
            "不是所有关键上下文都常驻在 messages 中",
        ],
    )

    add_section_slide(prs, "五、执行能力并不只来自模型", "Claude Code 的执行力来自 tool pipeline 和 async runtime。")

    add_content_slide(
        prs,
        "tool call 不是直接执行",
        [
            "真实路径不是 findToolByName -> tool.call 这么短",
            "前面还有 schema 校验、validateInput、speculative classifier、pre-tool hooks、permission 决策",
            "后面还有 result block 处理、content replacement、post-tool hooks、attachment/contextModifier",
            "autonomy boundary 在 tool pipeline，而不是 UI 表面",
        ],
    )

    add_content_slide(
        prs,
        "task / subagent / mailbox 是异步执行底座",
        [
            "Task.ts 定义统一 task 类型与生命周期",
            "task/framework.ts 负责注册、轮询、GC、notification",
            "runAgent.ts 负责 subagent、sidechain transcript、metadata",
            "teammateMailbox.ts 提供显式 mailbox 协议",
            "agent / teammate 已经是有 identity、有 transcript、有恢复路径的执行体",
        ],
    )

    add_content_slide(
        prs,
        "为什么消息不是“即时打断式”到达",
        [
            "mailbox 与 pendingMessages 的投递发生在 turn 边界",
            "task-notification 也会在下一轮作为结构化事件进入主会话",
            "这牺牲了一点即时性，但换来了 turn 内状态一致性",
            "因此多 agent 协作更像 actor mailbox，而不是共享同一个 transcript",
        ],
    )

    add_content_slide(
        prs,
        "关键状态载体",
        [
            "messages：turn-local 工作面",
            "transcript / sidechain：durable history",
            "ToolUseContext：工具执行总线",
            "AppState：宿主共享状态",
            "attachments / sidecar artifacts：按需重注入的工作面",
        ],
        quote="不要把系统简化成“只有消息数组”。",
    )

    add_section_slide(prs, "六、为什么它更像产品化 runtime", "最后再看控制面、扩展面和可观测性。")

    add_content_slide(
        prs,
        "认证、策略和服务端控制",
        [
            "服务端负责裁决，客户端负责执行",
            "控制面包括 OAuth / API key、policy_limits、remote managed settings、forceLoginOrgUUID",
            "更准确地说，不是“客户端封用户”，而是“服务端决定，客户端落实”",
        ],
    )

    add_content_slide(
        prs,
        "API、Prompt 与扩展系统",
        [
            "client.ts / claude.ts 不是薄封装，而是多 provider 统一适配层",
            "prompt stack 在这里是一层 control plane",
            "MCP / plugins / commands / skills 都是一级扩展面",
            "这也是为什么它更像完整 runtime，而不是单点功能工具",
        ],
    )

    add_content_slide(
        prs,
        "可观测性为什么重要",
        [
            "queryProfiler.ts：慢在哪个阶段",
            "analyzeContext.ts：上下文是谁吃掉的",
            "promptCacheBreakDetection.ts：cache 为什么断了",
            "没有可观测性，就很难持续优化 harness",
        ],
    )

    add_section_slide(prs, "七、给读者的落点", "最后只保留最应该带走的结论。")

    add_two_col_bullets(
        prs.slides.add_slide(prs.slide_layouts[6]),
        "从源码提炼的使用建议",
        [
            "高质量任务描述最好包含：目标、范围、约束、验证",
            "先读相关代码再改",
            "优先复用现有实现",
            "做最小必要改动",
            "验证后如实汇报",
        ],
        "最值得先抓住的三条线",
        [
            "main.tsx -> query.ts -> tools",
            "settings -> auth -> api client",
            "policy / managed settings -> 本地执行",
            "先抓主链路，再看扩展面",
        ],
    )
    last = prs.slides[-1]
    add_bg(last, BG)
    add_title(last, "最后总结")

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, LEAD_BG)
    add_title(slide, "谢谢", lead=True)
    add_subtitle(slide, "这份源码最值得看的，不只是功能，而是它已经为长时间工作的 runtime 付过哪些工程账。", lead=True)

    out = "docs/zh/00-代码总览与运行时走读-WPS兼容版.pptx"
    prs.save(out)
    print(out)


if __name__ == "__main__":
    build()
