from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


FONT = "Arial"
MONO = "Courier New"

TITLE = RGBColor(15, 23, 42)
TEXT = RGBColor(30, 41, 59)
MUTED = RGBColor(71, 85, 105)
ACCENT = RGBColor(37, 99, 235)
ACCENT_SOFT = RGBColor(219, 234, 254)
BG = RGBColor(248, 250, 252)
WHITE = RGBColor(255, 255, 255)
LEAD = RGBColor(16, 24, 40)
LINE = RGBColor(203, 213, 225)
CODE_BG = RGBColor(241, 245, 249)


def set_run_font(run, size, color, bold=False, font=FONT):
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


def style_tf(tf, top=4, bottom=4, left=8, right=8):
    tf.word_wrap = True
    tf.margin_top = Pt(top)
    tf.margin_bottom = Pt(bottom)
    tf.margin_left = Pt(left)
    tf.margin_right = Pt(right)
    tf.vertical_anchor = MSO_ANCHOR.TOP


def add_bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_title(slide, text, subtitle=None, lead=False):
    title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.38), Inches(12.1), Inches(0.7))
    tf = title_box.text_frame
    style_tf(tf, 2, 2, 2, 2)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = text
    set_run_font(r, 28 if lead else 24, WHITE if lead else TITLE, True)

    if subtitle:
        sub = slide.shapes.add_textbox(Inches(0.64), Inches(1.1), Inches(11.8), Inches(0.45))
        tf = sub.text_frame
        style_tf(tf, 2, 2, 2, 2)
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = subtitle
        set_run_font(r, 14, WHITE if lead else MUTED)

    if not lead:
        line = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(0.62), Inches(1.42), Inches(2.4), Inches(0.02)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = LINE
        line.line.fill.background()


def add_bullets(slide, bullets, x, y, w, h, size=18, color=TEXT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    style_tf(tf)
    tf.clear()
    for i, item in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.bullet = True
        p.level = 0
        p.space_after = Pt(8)
        r = p.add_run()
        r.text = item
        set_run_font(r, size, color)
    return box


def add_note(slide, text, x=0.72, y=6.68, w=11.9, h=0.35):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    style_tf(tf, 1, 1, 1, 1)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.add_run()
    r.text = text
    set_run_font(r, 11, MUTED)


def add_panel(slide, x, y, w, h, title, body_lines, title_fill=ACCENT_SOFT, line_color=ACCENT):
    shape = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = WHITE
    shape.line.color.rgb = line_color

    header = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(0.38)
    )
    header.fill.solid()
    header.fill.fore_color.rgb = title_fill
    header.line.color.rgb = title_fill
    tf = header.text_frame
    style_tf(tf, 2, 2, 6, 6)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = title
    set_run_font(r, 12, ACCENT, True)

    body = slide.shapes.add_textbox(Inches(x + 0.08), Inches(y + 0.44), Inches(w - 0.16), Inches(h - 0.5))
    tf = body.text_frame
    style_tf(tf)
    tf.clear()
    for i, item in enumerate(body_lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.bullet = False
        p.level = 0
        p.space_after = Pt(6)
        r = p.add_run()
        r.text = item
        set_run_font(r, 14, TEXT)
    return shape


def add_code_box(slide, x, y, w, h, code):
    shape = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = CODE_BG
    shape.line.color.rgb = LINE
    tf = shape.text_frame
    style_tf(tf, 6, 6, 8, 8)
    tf.clear()
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = code
    set_run_font(r, 13, TEXT, font=MONO)
    return shape


def add_chip(slide, x, y, w, h, text, fill=ACCENT_SOFT, color=ACCENT):
    shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = fill
    tf = shape.text_frame
    style_tf(tf, 1, 1, 4, 4)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = text
    set_run_font(r, 11, color, True)
    return shape


def connect(slide, x1, y1, x2, y2):
    line = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2)
    )
    line.line.color.rgb = ACCENT
    line.line.width = Pt(1.25)
    line.line.end_arrowhead = True
    return line


def add_lead(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, LEAD)
    add_title(
        slide,
        "Claude Code 使用技巧与注意事项",
        "从源码反推的用户侧最佳实践",
        lead=True,
    )
    add_bullets(
        slide,
        [
            "先说明 Claude Code 从工程上是什么，再解释怎样用会更稳",
            "每条技巧都附架构支撑、源码依据和关键代码片段",
        ],
        0.9,
        2.05,
        11.4,
        1.8,
        size=18,
        color=WHITE,
    )
    add_chip(slide, 0.95, 4.2, 1.55, 0.38, "源码支撑")
    add_chip(slide, 2.65, 4.2, 1.8, 0.38, "双语术语")
    add_chip(slide, 4.6, 4.2, 1.75, 0.38, "WPS 兼容")
    add_note(slide, "建议节奏：先建立整体模型，再解释默认偏好，最后落到用户技巧。", 0.88, 6.8, 11.8, 0.3)


def add_overview(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG)
    add_title(slide, "总结构图：Claude Code 的主执行链", "terminal agent runtime（终端代理运行时）视角")

    add_panel(slide, 0.7, 1.8, 2.0, 0.95, "输入", ["User Prompt", "用户输入"])
    add_panel(slide, 2.95, 1.8, 2.05, 0.95, "约束层", ["Prompt Stack", "提示词栈"])
    add_panel(slide, 5.25, 1.8, 2.2, 0.95, "会话层", ["QueryEngine", "Conversation Host"])
    add_panel(slide, 7.75, 1.8, 2.2, 0.95, "执行层", ["query.ts", "Turn Loop"])
    add_panel(slide, 10.2, 1.8, 2.15, 0.95, "工具层", ["Tool Pipeline", "工具执行流水线"])

    add_panel(slide, 2.1, 3.45, 3.0, 1.15, "能力面", ["Tools / Bash / Read / Edit", "Tasks / Subagents / Mailbox"])
    add_panel(slide, 5.35, 3.45, 2.7, 1.15, "执行环境", ["Filesystem / Shell / MCP"])
    add_panel(slide, 8.3, 3.45, 3.25, 1.15, "外围控制面", ["Settings / Auth / Policy", "Control Plane / 控制面"])
    add_panel(slide, 3.15, 5.0, 5.5, 0.95, "可观测性与恢复", ["Telemetry / Profiling / Transcript", "可观测性、持久化、恢复"])

    connect(slide, 2.7, 2.28, 2.95, 2.28)
    connect(slide, 5.0, 2.28, 5.25, 2.28)
    connect(slide, 7.45, 2.28, 7.75, 2.28)
    connect(slide, 9.95, 2.28, 10.2, 2.28)
    connect(slide, 8.85, 2.75, 8.85, 3.42)
    connect(slide, 6.7, 4.58, 6.0, 4.58)
    connect(slide, 6.7, 4.58, 6.7, 5.0)

    add_note(
        slide,
        "一句话：用户技巧之所以有效，是因为它们在影响 prompt stack（提示词栈）→ turn loop（轮次循环）→ tool pipeline（工具执行流水线）这条主链。",
    )


def add_content(prs, title, one_liner, bullets, code=None, note=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG)
    add_title(slide, title)
    add_panel(slide, 0.72, 1.68, 12.0, 0.78, "本页一句话", [one_liner])
    add_bullets(slide, bullets, 0.82, 2.72, 6.1, 3.2, size=17)
    if code:
        add_panel(slide, 7.15, 2.72, 5.25, 0.6, "关键代码片段", [])
        add_code_box(slide, 7.15, 3.05, 5.25, 2.3, code)
    if note:
        add_note(slide, note)
    return slide


def add_tip(prs, title, one_liner, tip, why, architecture, code, source_note):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG)
    add_title(slide, title)
    add_panel(slide, 0.72, 1.62, 12.0, 0.75, "本页一句话", [one_liner])
    add_panel(slide, 0.72, 2.58, 3.55, 1.58, "推荐写法", tip)
    add_panel(slide, 4.52, 2.58, 3.8, 1.58, "为什么有效", why)
    add_panel(slide, 8.57, 2.58, 4.15, 1.58, "架构支撑", architecture)
    add_panel(slide, 0.72, 4.45, 12.0, 0.56, "关键代码片段", [])
    add_code_box(slide, 0.72, 4.82, 12.0, 1.2, code)
    add_note(slide, source_note)
    return slide


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    add_lead(prs)
    add_overview(prs)

    add_content(
        prs,
        "Claude Code 不是什么",
        "Claude Code 不是自由聊天助手，而是默认按 software engineering tasks（软件工程任务）来理解用户请求。",
        [
            "不是“随便说一句就稳定帮你把工程活干好”的黑盒",
            "更像 software engineering agent（软件工程代理）",
            "所以输入越工程化，它通常越稳定",
        ],
        "The user will primarily request you to perform software engineering tasks.",
        "源码依据：/Users/bobo/code/claude-code-source-code/src/constants/prompts.ts#L221",
    )

    add_content(
        prs,
        "从源码看：Claude Code 是什么",
        "Claude Code 是 terminal agent runtime（终端代理运行时），不是只包了一层模型 API 的 CLI。",
        [
            "main.tsx：bootstrap / assembly（启动 / 装配）",
            "QueryEngine.ts：conversation host（会话宿主）",
            "query.ts：turn loop / runtime kernel（轮次循环 / 运行时内核）",
            "toolExecution.ts：tool pipeline（工具执行流水线）",
            "settings / auth / policy：control plane（控制面）",
        ],
        "export class QueryEngine {\n  private mutableMessages: Message[]\n  private totalUsage: NonNullableUsage\n  private readFileState: FileStateCache\n}\n\ntype State = {\n  messages: Message[]\n  toolUseContext: ToolUseContext\n  turnCount: number\n  transition: Continue | undefined\n}",
        "源码依据：QueryEngine.ts、query.ts、toolExecution.ts",
    )

    add_content(
        prs,
        "默认偏好的工作方式",
        "后面的所有使用技巧，都是把源码里的默认偏好显式写进用户提示里。",
        [
            "先读代码，再改代码",
            "最小必要改动，优先复用",
            "优先 dedicated tools（专用工具）",
            "验证后如实汇报",
            "高风险动作先确认",
        ],
        "In general, do not propose changes to code you haven't read.\nDo NOT use the Bash tool to run commands when a relevant dedicated tool is provided.\nReport outcomes faithfully: if tests fail, say so ...",
        "源码依据：prompts.ts#L230 / #L203 / #L305 / #L240 / #L258",
    )

    add_tip(
        prs,
        "技巧 1：目标 + 范围 + 约束 + 验证",
        "最稳定的输入方式，是把任务写成“目标 + 范围 + 约束 + 验证”。",
        [
            "目标：修复/实现……",
            "范围：只改……相关代码",
            "约束：不要做无关重构",
            "验证：跑测试并说明结果",
        ],
        [
            "减少分析 / 实现 / 顺手优化之间的歧义",
            "让 turn loop（轮次循环）围绕明确目标推进",
        ],
        [
            "prompt stack（提示词栈）默认把请求理解成软件工程任务",
            "turn loop（轮次循环）会围绕目标、范围和验证持续推进",
        ],
        "The user will primarily request you to perform software engineering tasks.\nIn general, do not propose changes to code you haven't read.\nReport outcomes faithfully: if tests fail, say so ...",
        "源码依据：prompts.ts#L221 / #L230 / #L240",
    )

    add_tip(
        prs,
        "技巧 2：先读代码，再改代码",
        "“先读代码，再改代码”不是建议项，而是源码里的默认工作顺序。",
        [
            "先看 src/foo.ts 和 src/bar.ts",
            "再决定改法",
        ],
        [
            "减少无关探索和上下文噪音",
            "更容易沿用现有实现",
        ],
        [
            "prompt stack（提示词栈）明确要求先读代码",
            "Plan Mode workflow（规划模式工作流）先 Explore 再规划",
        ],
        "In general, do not propose changes to code you haven't read.\nIf a user asks about or wants you to modify a file, read it first.\n\n1. Explore — Use read-only tools to read code.\nLook for existing functions, utilities, and patterns to reuse.",
        "源码依据：prompts.ts#L230，messages.ts#L3344",
    )

    add_tip(
        prs,
        "技巧 3：最小改动、优先复用",
        "把“最小改动、优先复用”写出来，能明显降低顺手重构和过早抽象。",
        [
            "做最小必要改动",
            "优先复用现有函数、工具和模式",
            "不要新造一层抽象",
        ],
        [
            "抑制范围漂移",
            "避免 one-time helper 和过早抽象",
        ],
        [
            "prompt stack（提示词栈）本身就在压制不必要改动",
            "tool pipeline（工具执行流水线）更适合局部、清晰、可验证的改动",
        ],
        "Don't add features, refactor code, or make \"improvements\" beyond what was asked.\nDon't create helpers, utilities, or abstractions for one-time operations.",
        "源码依据：prompts.ts#L200 / #L203",
    )

    add_tip(
        prs,
        "技巧 4：优先 dedicated tools（专用工具）",
        "Claude Code 更偏好 dedicated tools（专用工具），Bash 在源码里是 fallback，不是首选。",
        [
            "优先直接读写文件",
            "不要用 Bash 做本可由专用工具完成的事情",
        ],
        [
            "专用工具更容易被解释和审查",
            "也更容易受权限和执行链约束",
        ],
        [
            "tool pipeline（工具执行流水线）里，dedicated tools 是一等能力面",
            "Bash 是更自由也更高风险的 fallback",
        ],
        "default to using the dedicated tool and only fallback on using the Bash tool ...\nDo NOT use the Bash tool to run commands when a relevant dedicated tool is provided.",
        "源码依据：prompts.ts#L301 / #L305，BashTool prompt#L297",
    )

    add_tip(
        prs,
        "技巧 5：验证要求要写清楚",
        "不要默认 Claude Code 已经验证过，验证要求必须显式写出来。",
        [
            "改完后跑相关测试",
            "如果没跑，请明确说明没有跑",
        ],
        [
            "减少“看似完成、其实没验证”的风险",
            "避免把未验证结果包装成完成状态",
        ],
        [
            "prompt stack（提示词栈）明确要求 verify 和 faithful reporting",
            "turn loop（轮次循环）不会替用户假设“验证已经完成”",
        ],
        "Before reporting a task complete, verify it actually works.\nNever claim \"all tests pass\" when output shows failures.",
        "源码依据：prompts.ts#L211 / #L240",
    )

    add_tip(
        prs,
        "技巧 6：高风险动作先确认",
        "高风险动作先确认，不是额外保守，而是 Claude Code 的默认安全边界。",
        [
            "涉及 push、删除、覆盖、外部发送、破坏性 git 操作时",
            "先告诉我并确认",
        ],
        [
            "难以回滚的动作需要更强边界",
            "能减少误执行带来的 blast radius",
        ],
        [
            "prompt stack（提示词栈）先定义确认边界",
            "tool pipeline（工具执行流水线）和 Bash 约束负责执行面收紧",
        ],
        "Carefully consider the reversibility and blast radius of actions.\nask for confirmation before proceeding\nOnly use destructive operations when they are truly the best approach.",
        "源码依据：prompts.ts#L258，BashTool prompt#L304",
    )

    add_content(
        prs,
        "两个进阶技巧：parallel 与 Plan Mode",
        "对彼此独立的查询，显式允许 parallel（并行），更贴近 Claude Code 的原生工作方式。",
        [
            "独立查询可以显式允许 parallel（并行）",
            "做方案时，先走 Plan Mode workflow（规划模式工作流）",
            "也就是：先 Explore，再规划，再实现",
        ],
        "make all independent tool calls in parallel\n\n1. Explore — Use read-only tools to read code.\n2. Update the plan file.\n3. Ask the user only what code cannot answer.",
        "源码依据：prompts.ts#L310，messages.ts#L3336 / #L3344，BashTool prompt#L298",
    )

    add_content(
        prs,
        "常见误区与注意事项",
        "大多数误用，本质上都在对抗 Claude Code 源码里的默认工作流。",
        [
            "不要把 Claude Code 当自由聊天助手来用",
            "不要一上来就让它“大改一遍”",
            "不要默认它已经验证过",
            "不要把高风险授权写得太模糊",
        ],
        "The user will primarily request you to perform software engineering tasks.\nDon't add features, refactor code, or make \"improvements\" beyond what was asked.\nReport outcomes faithfully ...",
        "源码依据：prompts.ts#L221 / #L200 / #L240 / #L258",
    )

    add_content(
        prs,
        "最小使用清单",
        "这 6 条就是可以直接拍照带走的 Claude Code 最小使用清单。",
        [
            "任务写成：目标 + 范围 + 约束 + 验证",
            "明确要求先读代码",
            "明确要求最小改动、优先复用",
            "优先 dedicated tools（专用工具），不要默认 Bash",
            "验证结果要如实汇报",
            "高风险动作先确认",
        ],
        None,
        "建议展示方式：这页只保留动词和结论，不再放源码，作为最后的拍照页。",
    )

    out = Path("/Users/bobo/code/claude-code-source-code/docs/zh/09-Claude Code 使用技巧与注意事项-WPS兼容版.pptx")
    prs.save(out)
    print(out)


if __name__ == "__main__":
    build()
