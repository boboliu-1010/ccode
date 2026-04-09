from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


FONT = "Arial"
MONO = "Courier New"

TITLE = RGBColor(244, 247, 255)
TEXT = RGBColor(221, 230, 244)
MUTED = RGBColor(137, 156, 190)
ACCENT = RGBColor(56, 189, 248)
ACCENT_2 = RGBColor(167, 139, 250)
ACCENT_SOFT = RGBColor(12, 22, 46)
BG = RGBColor(4, 10, 24)
WHITE = RGBColor(255, 255, 255)
LEAD = RGBColor(7, 12, 28)
LINE = RGBColor(25, 40, 72)
CODE_BG = RGBColor(6, 12, 28)
PANEL_BG = RGBColor(9, 18, 38)
PANEL_HDR = RGBColor(15, 31, 60)
CODE_HDR = RGBColor(15, 24, 48)
CODE_TEXT = RGBColor(197, 244, 255)
SCRIPT_DIR = Path(__file__).resolve().parent


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
        line.fill.fore_color.rgb = ACCENT
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
    shape.fill.fore_color.rgb = PANEL_BG
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


def add_plain_box(slide, x, y, w, h, body_lines, fill=WHITE, line_color=LINE, size=15):
    shape = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line_color
    tf = shape.text_frame
    style_tf(tf)
    tf.clear()
    for i, item in enumerate(body_lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.bullet = False
        p.level = 0
        p.space_after = Pt(6)
        r = p.add_run()
        r.text = item
        set_run_font(r, size, TEXT)
    return shape


def add_code_box(slide, x, y, w, h, code):
    return add_labeled_code_box(slide, x, y, w, h, "code", code)


def add_labeled_code_box(slide, x, y, w, h, label, code):
    shape = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = CODE_BG
    shape.line.color.rgb = ACCENT
    header = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(0.28)
    )
    header.fill.solid()
    header.fill.fore_color.rgb = CODE_HDR
    header.line.color.rgb = CODE_HDR
    tf = header.text_frame
    style_tf(tf, 1, 1, 6, 6)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = label
    set_run_font(r, 10, ACCENT, True, font=MONO)
    tf = shape.text_frame
    style_tf(tf, 16, 6, 10, 10)
    tf.clear()
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = code
    set_run_font(r, 12.5, CODE_TEXT, font=MONO)
    return shape


def add_image(slide, path, x, y, w, h):
    slide.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(w), height=Inches(h))


def add_chip(slide, x, y, w, h, text, fill=ACCENT_SOFT, color=ACCENT):
    shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = ACCENT
    tf = shape.text_frame
    style_tf(tf, 1, 1, 4, 4)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = text
    set_run_font(r, 11, color, True)
    return shape


def add_glow_bar(slide, x, y, w, h, color):
    shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
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
    add_glow_bar(slide, 0.0, 0.0, 13.333, 0.06, ACCENT)
    add_glow_bar(slide, 0.0, 7.44, 13.333, 0.06, ACCENT_2)
    add_title(
        slide,
        "Claude Code 使用技巧与注意事项",
        "从源码反推：怎样用得更稳、更准、更像专业工程协作",
        lead=True,
    )
    add_plain_box(
        slide,
        0.9,
        2.0,
        5.45,
        2.25,
        [
            "这份分享回答三个问题：",
            "1. Claude Code 从工程上到底是什么",
            "2. 为什么有些提示方式更稳定",
            "3. 用户应该怎样提需求、控边界、做验证",
        ],
        fill=RGBColor(10, 18, 36),
        line_color=ACCENT,
        size=17,
    )
    add_plain_box(
        slide,
        6.75,
        2.0,
        5.55,
        2.25,
        [
            "最终目标不是讲功能，而是形成一套可复用的使用方法：",
            "目标 + 范围 + 约束 + 验证",
            "先读代码，再做最小改动",
            "把源码里的默认工作方式转成用户提示词",
        ],
        fill=RGBColor(10, 18, 36),
        line_color=ACCENT_2,
        size=17,
    )
    add_chip(slide, 0.95, 4.65, 1.55, 0.38, "源码依据", fill=ACCENT_SOFT, color=ACCENT)
    add_chip(slide, 2.65, 4.65, 1.8, 0.38, "架构视角", fill=RGBColor(26, 19, 52), color=ACCENT_2)
    add_chip(slide, 4.6, 4.65, 1.75, 0.38, "使用方法", fill=ACCENT_SOFT, color=ACCENT)
    add_chip(slide, 6.55, 4.65, 1.95, 0.38, "提示词技巧", fill=RGBColor(26, 19, 52), color=ACCENT_2)
    add_chip(slide, 8.7, 4.65, 1.8, 0.38, "风险边界", fill=ACCENT_SOFT, color=ACCENT)
    add_plain_box(
        slide,
        0.95,
        5.35,
        11.35,
        0.78,
        [
            "核心判断：Claude Code 不是自由聊天助手，而是一个围绕 Prompt Stack、Turn Loop 和 Tool Pipeline 运行的 terminal agent runtime。"
        ],
        fill=RGBColor(8, 15, 33),
        line_color=ACCENT_2,
        size=15,
    )


def add_architecture_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG)
    add_title(slide, "从源码看：Claude Code 是什么", "一个 terminal agent runtime（终端代理运行时）的最小架构图")

    add_panel(slide, 0.85, 1.85, 2.2, 1.0, "入口层", ["main.tsx", "bootstrap / assembly"], title_fill=PANEL_HDR)
    add_panel(slide, 3.45, 1.85, 2.4, 1.0, "会话层", ["QueryEngine.ts", "conversation host"], title_fill=PANEL_HDR)
    add_panel(slide, 6.25, 1.85, 2.4, 1.0, "执行层", ["query.ts", "turn loop / runtime kernel"], title_fill=PANEL_HDR)
    add_panel(slide, 9.05, 1.85, 3.1, 1.0, "工具执行层", ["toolExecution.ts", "tool pipeline"], title_fill=PANEL_HDR)

    add_panel(slide, 1.7, 3.65, 3.2, 1.15, "能力面", ["Tools / Bash / Read / Edit", "Tasks / Subagents / Mailbox"], title_fill=PANEL_HDR)
    add_panel(slide, 5.35, 3.65, 2.45, 1.15, "执行环境", ["Filesystem / Shell", "MCP"], title_fill=PANEL_HDR)
    add_panel(slide, 8.15, 3.65, 3.2, 1.15, "控制面", ["Settings / Auth / Policy", "Prompt / Permissions"], title_fill=PANEL_HDR)

    connect(slide, 3.05, 2.35, 3.45, 2.35)
    connect(slide, 5.85, 2.35, 6.25, 2.35)
    connect(slide, 8.65, 2.35, 9.05, 2.35)
    connect(slide, 10.6, 2.85, 9.75, 3.65)
    connect(slide, 7.8, 4.22, 8.15, 4.22)
    connect(slide, 4.9, 4.22, 5.35, 4.22)

    add_plain_box(
        slide,
        1.35,
        5.35,
        10.65,
        0.75,
        ["一句话：Claude Code 不是“模型 API + 终端壳”，而是由会话层、轮次循环、工具执行层和控制面组成的本地代理运行时。"],
        fill=ACCENT_SOFT,
        line_color=ACCENT,
        size=15,
    )
    add_note(slide, "关键文件：main.tsx / QueryEngine.ts / query.ts / toolExecution.ts")


def add_stage_box(slide, x, y, w, h, title, body):
    shape = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = PANEL_BG
    shape.line.color.rgb = ACCENT
    shape.line.width = Pt(1.8)
    tf = shape.text_frame
    style_tf(tf, 8, 8, 12, 12)
    tf.clear()
    p1 = tf.paragraphs[0]
    p1.alignment = PP_ALIGN.CENTER
    r1 = p1.add_run()
    r1.text = title
    set_run_font(r1, 20, ACCENT, True)
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(6)
    r2 = p2.add_run()
    r2.text = body
    set_run_font(r2, 14, TEXT)
    return shape


def add_overview(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG)
    add_title(slide, "结构图：Claude Code 的主执行链", "用最少的层说明系统是怎么跑起来的")

    add_stage_box(slide, 0.55, 2.15, 2.0, 1.45, "User Prompt", "用户输入\n目标 / 范围 / 约束")
    add_stage_box(slide, 2.95, 2.15, 2.15, 1.45, "Prompt Stack", "提示词栈\n默认行为约束")
    add_stage_box(slide, 5.5, 2.15, 2.15, 1.45, "QueryEngine", "会话宿主\nConversation Host")
    add_stage_box(slide, 8.05, 2.15, 2.15, 1.45, "query.ts", "轮次循环\nTurn Loop")
    add_stage_box(slide, 10.6, 2.15, 2.15, 1.45, "Tool Pipeline", "工具执行流水线")

    connect(slide, 2.55, 2.88, 2.95, 2.88)
    connect(slide, 5.1, 2.88, 5.5, 2.88)
    connect(slide, 7.65, 2.88, 8.05, 2.88)
    connect(slide, 10.2, 2.88, 10.6, 2.88)

    add_stage_box(slide, 2.35, 4.55, 3.2, 1.4, "Tools / Tasks", "Bash / Read / Edit\nSubagents / Mailbox")
    add_stage_box(slide, 6.0, 4.55, 2.4, 1.4, "Environment", "Filesystem / Shell\nMCP")
    add_stage_box(slide, 8.85, 4.55, 3.0, 1.4, "Control Plane", "Settings / Auth / Policy")

    connect(slide, 11.65, 3.6, 10.15, 4.55)
    connect(slide, 5.55, 5.25, 6.0, 5.25)
    connect(slide, 8.4, 5.25, 8.85, 5.25)

    add_plain_box(
        slide,
        0.75,
        6.35,
        12.0,
        0.42,
        ["重点：用户技巧之所以有效，是因为它们会直接影响 Prompt Stack、Turn Loop 和 Tool Pipeline 这条主链。"],
        fill=ACCENT_SOFT,
        line_color=ACCENT,
        size=13,
    )


def add_sequence_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG)
    add_title(slide, "时序图：一次请求如何流过 Claude Code", "用一条 request → tool → result 链解释用户提示词为什么有效")
    lanes = [
        ("User", 1.0),
        ("Prompt Stack", 3.35),
        ("QueryEngine", 5.7),
        ("query.ts", 8.05),
        ("Tool Pipeline", 10.35),
    ]

    for name, x in lanes:
        add_stage_box(slide, x, 1.72, 1.65, 0.82, name, "")
        line = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT, Inches(x + 0.825), Inches(2.54), Inches(x + 0.825), Inches(6.0)
        )
        line.line.color.rgb = LINE
        line.line.width = Pt(1.2)

    def seq_msg(x1, x2, y, text):
        connect(slide, x1, y, x2, y)
        add_plain_box(
            slide,
            min(x1, x2) + 0.12,
            y - 0.14,
            max(1.0, abs(x2 - x1) - 0.24),
            0.3,
            [text],
            fill=PANEL_HDR,
            line_color=ACCENT,
            size=11.5,
        )

    seq_msg(1.82, 4.17, 2.95, "任务输入 / 约束")
    seq_msg(4.17, 6.52, 3.45, "组装 prompt 与 context")
    seq_msg(6.52, 8.87, 3.95, "启动 turn loop")
    seq_msg(8.87, 11.17, 4.45, "决定是否调用工具")
    seq_msg(11.17, 8.87, 4.95, "tool result 回灌")
    seq_msg(8.87, 6.52, 5.45, "继续 / 收敛")

    add_plain_box(
        slide,
        0.75,
        6.35,
        12.0,
        0.42,
        ["结论：目标、范围、约束、验证写得越清楚，越能稳定影响 prompt stack、turn loop 和 tool pipeline 的每一步。"],
        fill=ACCENT_SOFT,
        line_color=ACCENT,
        size=13,
    )


def add_content(prs, title, one_liner, bullets, code=None, note=None, snippet_label="源码代码"):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG)
    add_title(slide, title)
    add_plain_box(slide, 0.72, 1.68, 12.0, 0.72, [one_liner], fill=ACCENT_SOFT, line_color=ACCENT, size=16)
    add_bullets(slide, bullets, 0.82, 2.68, 6.1, 3.35, size=17)
    if code:
        add_labeled_code_box(slide, 7.15, 2.7, 5.25, 2.7, snippet_label, code)
    if note:
        add_note(slide, note)
    return slide


def add_tip(prs, title, one_liner, tip, why, architecture, code, source_note, snippet_label="源码提示词"):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG)
    add_title(slide, title)
    add_plain_box(slide, 0.72, 1.62, 12.0, 0.72, [one_liner], fill=ACCENT_SOFT, line_color=ACCENT, size=16)
    add_panel(slide, 0.72, 2.55, 3.55, 1.7, "示例提示词", tip)
    add_panel(slide, 4.52, 2.55, 3.8, 1.7, "源码解释", why)
    add_panel(slide, 8.57, 2.55, 4.15, 1.7, "证据链", architecture)
    add_labeled_code_box(slide, 0.72, 4.55, 12.0, 1.35, snippet_label, code)
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
        "源码依据：src/constants/prompts.ts#L221",
        snippet_label="源码提示词",
    )

    add_architecture_slide(prs)
    add_sequence_slide(prs)

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
        snippet_label="源码提示词",
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
        snippet_label="源码提示词",
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
        snippet_label="源码提示词",
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
        snippet_label="源码提示词",
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
        snippet_label="源码提示词",
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
        snippet_label="源码提示词",
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
        snippet_label="源码提示词",
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
        snippet_label="源码提示词",
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
        snippet_label="源码提示词",
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
        None,
    )

    out = Path(__file__).resolve().parents[2] / "docs/zh/09-Claude Code 使用技巧与注意事项.pptx"
    prs.save(out)
    print(out)


if __name__ == "__main__":
    build()
