from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[2]
OUTLINE = ROOT / 'docs/zh/10-Claude Code 源码深度解读-分享提纲.md'
OUT = ROOT / 'docs/zh/10-Claude Code 源码调研.pptx'

FONT = 'Arial'
MONO = 'Courier New'

BG = RGBColor(4, 10, 24)
BG_2 = RGBColor(7, 16, 35)
PANEL = RGBColor(10, 22, 46)
PANEL_2 = RGBColor(14, 31, 63)
PANEL_3 = RGBColor(12, 26, 54)
CODE_BG = RGBColor(7, 15, 31)
TITLE = RGBColor(245, 248, 255)
TEXT = RGBColor(222, 230, 244)
MUTED = RGBColor(153, 171, 196)
ACCENT = RGBColor(72, 198, 255)
ACCENT_2 = RGBColor(156, 163, 255)
ACCENT_3 = RGBColor(61, 224, 199)
WARN = RGBColor(250, 204, 21)
LINE = RGBColor(38, 63, 110)
CODE_TEXT = RGBColor(190, 246, 255)

SLIDE_NOTES = {
    11: """补充说明：

- resume 时不是直接反序列化，而是先把历史修回 API 可继续状态。
- 所以 recovery 的目标不是“还原 UI”，而是“恢复一个还能继续跑的 runtime”。
- 这也是为什么 conversationRecovery.ts 会先过滤 unresolved tool use、orphaned thinking、whitespace-only assistant messages，再把消息恢复成可继续调用 API 的形态。

相关延伸材料：
- 06-走读附录：长会话与恢复机制.md
""",
    19: """补充说明：

4.2 tool result budget / content replacement 解决的是“冻结输出命运”。

关键文件：
- src/utils/toolResultStorage.ts
- src/services/compact/microCompact.ts

这一层解决的不是“截断输出”，而是：
- 大工具输出先落盘
- 上下文里只保留稳定 preview
- 某个 tool_use_id 一旦替换，后面始终使用同一 replacement string
- 恢复后还要重放同一 replacement，保护 prompt cache prefix

这层非常值钱，因为它说明 Claude Code 在认真维护长会话的稳定性，而不是简单把大文本塞进上下文。
""",
}


class SlideData:
    def __init__(self, num: int, title: str, fields: Dict[str, str]):
        self.num = num
        self.title = title
        self.fields = fields


def strip_links(text: str) -> str:
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text.replace('`', '').strip()


def parse_bullets(block: str) -> List[str]:
    items: List[str] = []
    for line in block.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith('- '):
            items.append(strip_links(s[2:]))
        elif re.match(r'^\d+\.\s+', s):
            items.append(strip_links(re.sub(r'^\d+\.\s+', '', s)))
    return items


def parse_code(block: str) -> str | None:
    m = re.search(r'```(?:\w+)?\n(.*?)```', block, re.S)
    if not m:
        return None
    return m.group(1).strip()


def parse_fields(block: str) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    current = None
    buf: List[str] = []
    for line in block.splitlines():
        m = re.match(r'^\*\*(.+?)\*\*$', line.strip())
        if m:
            if current is not None:
                fields[current] = '\n'.join(buf).strip()
            current = m.group(1)
            buf = []
        else:
            if current is not None:
                buf.append(line)
    if current is not None:
        fields[current] = '\n'.join(buf).strip()
    return fields


def parse_outline() -> List[SlideData]:
    text = OUTLINE.read_text()
    chunks = re.split(r'(?=^## 第 \d+ 页：)', text, flags=re.M)
    slides: List[SlideData] = []
    for chunk in chunks:
        if not chunk.startswith('## 第 '):
            continue
        lines = chunk.splitlines()
        m = re.match(r'^## 第 (\d+) 页：(.+)$', lines[0])
        if not m:
            continue
        num = int(m.group(1))
        title = m.group(2).strip()
        fields = parse_fields('\n'.join(lines[1:]))
        slides.append(SlideData(num, title, fields))
    return slides


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


def add_bg(slide, color=BG):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_title(slide, title, subtitle=None):
    tb = slide.shapes.add_textbox(Inches(0.55), Inches(0.28), Inches(12.1), Inches(0.7))
    tf = tb.text_frame
    style_tf(tf, 0, 0, 0, 0)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = title
    set_run_font(r, 24, TITLE, True)
    if subtitle:
        sb = slide.shapes.add_textbox(Inches(0.58), Inches(0.92), Inches(12.0), Inches(0.38))
        tf = sb.text_frame
        style_tf(tf, 0, 0, 0, 0)
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = subtitle
        set_run_font(r, 11.5, MUTED)
    line = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(0.58), Inches(1.28), Inches(2.4), Inches(0.03))
    line.fill.solid()
    line.fill.fore_color.rgb = ACCENT
    line.line.fill.background()


def add_shape(slide, kind, x, y, w, h, fill=PANEL, line=LINE):
    shp = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.color.rgb = line
    return shp


def add_panel(slide, x, y, w, h, title, title_color=ACCENT, fill=PANEL):
    body = add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, x, y, w, h, fill=fill)
    hdr = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(0.32))
    hdr.fill.solid()
    hdr.fill.fore_color.rgb = PANEL_2
    hdr.line.fill.background()
    tf = hdr.text_frame
    style_tf(tf, 2, 2, 5, 5)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = title
    set_run_font(r, 11, title_color, True)
    return body


def add_text(slide, x, y, w, h, lines: List[str], size=16, color=TEXT, bullet=True):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    style_tf(tf)
    tf.clear()
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.bullet = bullet
        p.level = 0
        p.space_after = Pt(5)
        r = p.add_run()
        r.text = line
        set_run_font(r, size, color)
    return tb


def add_rich_lines(slide, x, y, w, h, sections: List[Tuple[str, List[str]]]):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    style_tf(tf)
    tf.clear()
    first = True
    for heading, items in sections:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(5)
        p.bullet = False
        r = p.add_run()
        r.text = heading
        set_run_font(r, 14.5, ACCENT_2, True)
        for item in items:
            pp = tf.add_paragraph()
            pp.bullet = True
            pp.space_after = Pt(4)
            rr = pp.add_run()
            rr.text = item
            set_run_font(rr, 13.4, TEXT)
    return tb


def add_code_box(slide, x, y, w, h, code, label='关键源码片段'):
    body = add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, x, y, w, h, fill=CODE_BG, line=ACCENT)
    hdr = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(0.28))
    hdr.fill.solid()
    hdr.fill.fore_color.rgb = PANEL_2
    hdr.line.fill.background()
    tf = hdr.text_frame
    style_tf(tf, 2, 2, 6, 6)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = label
    set_run_font(r, 10, ACCENT, True, MONO)
    tf = body.text_frame
    style_tf(tf, 14, 6, 10, 10)
    tf.clear()
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = code
    set_run_font(r, 10.5, CODE_TEXT, False, MONO)
    return body


def add_footer(slide, left, right=''):
    tb = slide.shapes.add_textbox(Inches(0.6), Inches(7.05), Inches(12.1), Inches(0.2))
    tf = tb.text_frame
    style_tf(tf, 0, 0, 0, 0)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = left
    set_run_font(r, 10, MUTED)
    if right:
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.RIGHT
        r2 = p2.add_run()
        r2.text = right
        set_run_font(r2, 9.5, MUTED)


def set_slide_notes(slide, text: str):
    notes_tf = slide.notes_slide.notes_text_frame
    notes_tf.clear()
    for i, line in enumerate(text.strip().splitlines()):
        p = notes_tf.paragraphs[0] if i == 0 else notes_tf.add_paragraph()
        p.text = line


def markdown_label_list(block: str) -> List[str]:
    items = parse_bullets(block)
    labels = []
    for item in items:
        labels.append(strip_links(item))
    return labels


def connect(slide, x1, y1, x2, y2, color=ACCENT):
    line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    line.line.color.rgb = color
    line.line.width = Pt(1.6)
    line.line.end_arrowhead = True
    return line


def add_cover_slide(prs: Presentation, sd: SlideData):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG_2)
    add_title(slide, 'Claude Code 源码调研', '总体架构、工作流程、功能设计、产出形态与开发流程建议')
    hero = add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, 0.62, 1.72, 12.0, 0.88, fill=RGBColor(8, 24, 52), line=ACCENT)
    tf = hero.text_frame
    style_tf(tf, 6, 6, 12, 12)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = '通过足够的源码理解，帮助用户和团队更好地使用 Claude Code。'
    set_run_font(r, 19, TITLE, True)
    add_panel(slide, 0.72, 2.95, 5.72, 2.5, '调研目标', title_color=ACCENT)
    add_text(slide, 0.95, 3.32, 5.22, 2.0, [
        '为什么同样是 Claude Code，有的人越用越顺，有的人越用越乱。',
        '为什么它更适合工程任务，而不是自由聊天式请求。',
        '怎样组织任务、边界和验证，才能让它稳定地产出结果。',
    ], size=16.5)
    add_panel(slide, 6.74, 2.95, 5.86, 2.5, '调研范围', title_color=ACCENT_2)
    add_text(slide, 6.97, 3.32, 5.34, 2.0, [
        '先用源码建立最小必要架构模型。',
        '再讲工作流程、功能和典型产出。',
        '最后把结论落到开发流程建议与代码走读入口。',
    ], size=16.5)
    add_panel(slide, 0.72, 5.82, 11.88, 0.9, '调研结论', title_color=WARN, fill=PANEL_3)
    add_text(slide, 0.93, 6.17, 11.45, 0.35, ['Claude Code 不是自由聊天助手，而是一套围绕工程任务构建的 terminal agent runtime（终端代理运行时）。'], size=17, bullet=False)
    add_footer(slide, 'Claude Code 源码调研', '封面')


def add_overview_diagram(prs: Presentation, sd: SlideData):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide)
    add_title(slide, sd.title, '从用户输入到主执行链，再到控制面和续航能力。')
    q = parse_bullets(sd.fields.get('这一页要回答的问题', ''))
    if q:
        add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, 0.62, 1.55, 12.02, 0.58, fill=PANEL_3, line=ACCENT)
        add_text(slide, 0.84, 1.72, 11.55, 0.22, q, size=14.5, bullet=False)
    boxes = [
        ('用户输入', 0.78, 2.55, 1.55, 0.7, ACCENT),
        ('Prompt Stack\n提示词栈', 2.6, 2.48, 1.95, 0.84, ACCENT),
        ('QueryEngine\n会话宿主', 4.95, 2.48, 1.95, 0.84, ACCENT_2),
        ('query.ts\nTurn Loop', 7.28, 2.48, 1.95, 0.84, ACCENT_2),
        ('Tool Pipeline\n工具执行链', 9.62, 2.44, 2.35, 0.92, ACCENT_3),
    ]
    for txt, x, y, w, h, color in boxes:
        shp = add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, x, y, w, h, fill=PANEL, line=color)
        tf = shp.text_frame
        style_tf(tf, 8, 8, 8, 8)
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        for idx, line in enumerate(txt.split('\n')):
            r = p.add_run()
            r.text = ('' if idx == 0 else '\n') + line
            set_run_font(r, 15 if idx == 0 else 12.5, TITLE if idx == 0 else color, idx == 0)
    connect(slide, 2.33, 2.9, 2.6, 2.9)
    connect(slide, 4.55, 2.9, 4.95, 2.9)
    connect(slide, 6.9, 2.9, 7.28, 2.9)
    connect(slide, 9.24, 2.9, 9.62, 2.9)
    cp = add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, 0.92, 4.38, 4.2, 1.0, fill=PANEL, line=WARN)
    tf = cp.text_frame
    style_tf(tf, 6, 6, 10, 10)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = 'Settings / Auth / Policy / Prompt\n控制面'
    set_run_font(r, 16, TITLE, True)
    obs = add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, 5.42, 4.38, 3.28, 1.0, fill=PANEL, line=ACCENT_2)
    tf = obs.text_frame
    style_tf(tf, 6, 6, 10, 10)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = 'Transcript / Recovery\nCompact / Observability'
    set_run_font(r, 15.5, TITLE, True)
    env = add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, 9.02, 4.38, 3.22, 1.0, fill=PANEL, line=ACCENT_3)
    tf = env.text_frame
    style_tf(tf, 6, 6, 10, 10)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = 'Tools / Tasks / MCP\n执行环境与扩展能力'
    set_run_font(r, 15.5, TITLE, True)
    connect(slide, 5.95, 3.32, 5.95, 4.38, WARN)
    connect(slide, 8.25, 3.32, 7.1, 4.38, ACCENT_2)
    connect(slide, 10.82, 3.36, 10.82, 4.38, ACCENT_3)
    takeaway = parse_bullets(sd.fields.get('希望听众带走什么', ''))
    if takeaway:
        add_panel(slide, 0.82, 6.08, 11.85, 0.72, '调研结论', title_color=ACCENT)
        add_text(slide, 1.04, 6.38, 11.35, 0.2, takeaway, size=14.5, bullet=False)
    add_footer(slide, 'Claude Code 源码调研', '总体架构')


def add_workflow_diagram(prs: Presentation, sd: SlideData):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide)
    add_title(slide, sd.title, '一次请求如何被推进、约束、回灌、压缩和恢复。')
    q = parse_bullets(sd.fields.get('这一页要回答的问题', ''))
    if q:
        add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, 0.62, 1.55, 12.02, 0.58, fill=PANEL_3, line=ACCENT)
        add_text(slide, 0.84, 1.72, 11.55, 0.22, q, size=14.5, bullet=False)
    steps = [
        ('用户输入', 0.82, 2.55, 1.45),
        ('装配环境', 2.45, 2.55, 1.5),
        ('会话宿主', 4.18, 2.55, 1.5),
        ('turn loop', 5.92, 2.55, 1.5),
        ('tool pipeline', 7.65, 2.55, 1.8),
        ('结果回灌', 9.7, 2.55, 1.5),
        ('继续 / compact / recovery', 4.8, 4.45, 3.4),
    ]
    colors = [ACCENT, ACCENT, ACCENT_2, ACCENT_2, ACCENT_3, ACCENT_3, WARN]
    for (txt, x, y, w), color in zip(steps, colors):
        shp = add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, x, y, w, 0.78, fill=PANEL, line=color)
        tf = shp.text_frame
        style_tf(tf, 8, 8, 8, 8)
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = txt
        set_run_font(r, 15, TITLE, True)
    connect(slide, 2.27, 2.94, 2.45, 2.94)
    connect(slide, 3.95, 2.94, 4.18, 2.94)
    connect(slide, 5.68, 2.94, 5.92, 2.94)
    connect(slide, 7.42, 2.94, 7.65, 2.94)
    connect(slide, 9.45, 2.94, 9.7, 2.94)
    connect(slide, 10.45, 3.33, 8.15, 4.45, WARN)
    connect(slide, 6.5, 4.45, 6.5, 3.33, WARN)
    core = parse_bullets(sd.fields.get('核心内容', ''))
    add_panel(slide, 0.86, 5.62, 11.8, 1.05, '流程要点', title_color=ACCENT_2)
    add_text(slide, 1.06, 5.98, 11.35, 0.55, core[:4], size=13.8)
    add_footer(slide, 'Claude Code 源码调研', '工作流程')


def add_capability_slide(prs: Presentation, sd: SlideData):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide)
    add_title(slide, sd.title, '先从用户感知的能力面理解，再进入主要功能。')
    thesis = parse_bullets(sd.fields.get('这一页要回答的问题', ''))
    code = parse_code(sd.fields.get('关键代码片段', ''))
    if thesis:
        add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, 0.62, 1.55, 12.02, 0.58, fill=PANEL_3, line=ACCENT)
        add_text(slide, 0.82, 1.72, 11.6, 0.22, thesis, size=14.5, bullet=False)
    cards = [
        ('交互', ['REPL', 'commands', 'structured output'], 0.82, 2.5, ACCENT),
        ('执行', ['Read / Edit / Bash', 'tool pipeline', 'task runtime'], 3.05, 2.5, ACCENT_2),
        ('扩展', ['skills', 'MCP', 'plugins', 'remote capability'], 5.28, 2.5, ACCENT_3),
        ('控制', ['prompt stack', 'settings', 'policy', 'permissions'], 7.51, 2.5, WARN),
        ('续航', ['transcript', 'recovery', 'compact', 'replacement'], 9.74, 2.5, ACCENT),
        ('可观测性', ['profiler', 'cache break', 'context analysis'], 3.95, 4.75, ACCENT_2),
    ]
    for title, items, x, y, color in cards:
        add_panel(slide, x, y, 2.05, 1.6, title, title_color=color)
        add_text(slide, x+0.08, y+0.37, 1.9, 1.1, items, size=12.6)
    if code:
        add_code_box(slide, 6.35, 4.74, 6.25, 1.38, code, '关键源码片段')
    else:
        add_panel(slide, 6.35, 4.74, 6.25, 1.38, '功能面判断依据', title_color=ACCENT_2)
        add_text(slide, 6.55, 5.12, 5.85, 0.78, [
            'commands、tools、MCP、policy、recovery、profiling 虽然分散在不同模块里，',
            '但它们共同服务的是一条主执行链，因此功能面比目录结构更适合作为用户理解入口。'
        ], size=12.2, bullet=False)
    takeaway = parse_bullets(sd.fields.get('希望听众带走什么', ''))
    add_panel(slide, 0.86, 6.22, 11.8, 0.58, '调研结论', title_color=ACCENT_3)
    add_text(slide, 1.06, 6.44, 11.35, 0.18, takeaway or ['功能多本身不重要，关键是这些能力能围绕主执行链协同。'], size=14.2, bullet=False)
    add_footer(slide, 'Claude Code 源码调研', '功能介绍')


def add_codewalk_architecture_slide(prs: Presentation, sd: SlideData):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide)
    add_title(slide, sd.title, '按主执行链和控制链理解代码结构，而不是按目录平铺。')
    core = parse_bullets(sd.fields.get('核心内容', ''))
    code = parse_code(sd.fields.get('关键代码片段', ''))
    takeaway = parse_bullets(sd.fields.get('希望听众带走什么', ''))

    # Diagram area
    nodes = [
        ('main.tsx', 0.75, 1.9, 1.7, 0.7, ACCENT),
        ('QueryEngine.ts', 2.8, 1.9, 2.0, 0.7, ACCENT_2),
        ('query.ts', 5.25, 1.9, 1.7, 0.7, ACCENT_2),
        ('toolExecution.ts', 7.3, 1.9, 2.2, 0.7, ACCENT_3),
        ('compact / recovery', 9.95, 1.9, 2.35, 0.7, WARN),
    ]
    for txt, x, y, w, h, color in nodes:
        shp = add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, x, y, w, h, fill=PANEL, line=color)
        tf = shp.text_frame
        style_tf(tf, 6, 6, 8, 8)
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = txt
        set_run_font(r, 14.2, TITLE, True)
    connect(slide, 2.45, 2.25, 2.8, 2.25)
    connect(slide, 4.8, 2.25, 5.25, 2.25)
    connect(slide, 6.95, 2.25, 7.3, 2.25)
    connect(slide, 9.5, 2.25, 9.95, 2.25)

    control = add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, 1.25, 3.1, 3.4, 0.78, fill=PANEL, line=ACCENT)
    tf = control.text_frame
    style_tf(tf, 6, 6, 8, 8)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = 'settings / auth / policy / prompt'
    set_run_font(r, 13.8, TITLE, True)

    ext = add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, 5.2, 3.1, 3.1, 0.78, fill=PANEL, line=ACCENT_2)
    tf = ext.text_frame
    style_tf(tf, 6, 6, 8, 8)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = 'tasks / MCP / plugins / skills'
    set_run_font(r, 13.2, TITLE, True)

    msgs = add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, 8.75, 3.1, 2.55, 0.78, fill=PANEL, line=ACCENT_3)
    tf = msgs.text_frame
    style_tf(tf, 6, 6, 8, 8)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = 'messages / transcript'
    set_run_font(r, 13.4, TITLE, True)

    connect(slide, 3.0, 3.1, 3.75, 2.6, ACCENT)
    connect(slide, 6.75, 3.1, 6.2, 2.6, ACCENT_2)
    connect(slide, 10.0, 3.1, 10.6, 2.6, ACCENT_3)

    add_panel(slide, 0.75, 4.15, 5.35, 2.0, '代码结构拆法', title_color=ACCENT_2)
    add_text(slide, 0.95, 4.52, 4.95, 1.48, core[:7], size=13.2)
    if code:
        add_code_box(slide, 6.35, 4.15, 6.0, 2.0, code, '关键源码片段')
    if takeaway:
        add_panel(slide, 0.75, 6.45, 11.62, 0.58, '调研结论', title_color=WARN, fill=PANEL_3)
        add_text(slide, 0.95, 6.67, 11.2, 0.18, takeaway, size=14.0, bullet=False)
    add_footer(slide, 'Claude Code 源码调研', '代码走读概略')


def add_codewalk_order_slide(prs: Presentation, sd: SlideData):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide)
    add_title(slide, sd.title, '先抓主执行链，再补续航、扩展和控制。')
    core = parse_bullets(sd.fields.get('核心内容', ''))
    code = parse_code(sd.fields.get('关键代码片段', ''))
    takeaway = parse_bullets(sd.fields.get('希望听众带走什么', ''))

    first = ['main.tsx', 'QueryEngine.ts', 'query.ts', 'toolExecution.ts']
    second = ['compact / recovery', 'tasks / MCP / skills']

    add_panel(slide, 0.75, 1.72, 5.75, 1.45, '第一遍：主执行链', title_color=ACCENT)
    x = 0.98
    for idx, label in enumerate(first):
        shp = add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, x, 2.18, 1.15 if idx != 1 else 1.45, 0.55, fill=PANEL, line=ACCENT)
        tf = shp.text_frame
        style_tf(tf, 5, 5, 6, 6)
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = label
        set_run_font(r, 11.6, TITLE, True)
        if idx < len(first) - 1:
            nx = x + (1.15 if idx != 1 else 1.45) + 0.18
            connect(slide, x + (1.15 if idx != 1 else 1.45), 2.45, nx, 2.45)
            x = nx

    add_panel(slide, 6.8, 1.72, 5.55, 1.45, '第二遍：续航与扩展', title_color=ACCENT_2)
    for i, label in enumerate(second):
        xx = 7.15 + i * 2.5
        shp = add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, xx, 2.18, 1.95, 0.55, fill=PANEL, line=ACCENT_2)
        tf = shp.text_frame
        style_tf(tf, 5, 5, 6, 6)
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = label
        set_run_font(r, 11.4, TITLE, True)
        if i == 0:
            connect(slide, xx + 1.95, 2.45, xx + 2.3, 2.45, ACCENT_2)

    add_panel(slide, 0.75, 3.55, 5.75, 2.2, '阅读顺序的原因', title_color=ACCENT_3)
    add_text(slide, 0.95, 3.92, 5.35, 1.7, core[:8], size=13.1)
    if code:
        add_code_box(slide, 6.8, 3.55, 5.55, 2.2, code, '关键源码片段')
    if takeaway:
        add_panel(slide, 0.75, 6.05, 11.6, 0.62, '调研结论', title_color=WARN, fill=PANEL_3)
        add_text(slide, 0.95, 6.3, 11.2, 0.18, takeaway, size=14.0, bullet=False)
    add_footer(slide, 'Claude Code 源码调研', '代码走读概略')


def add_keyfiles_slide(prs: Presentation, sd: SlideData):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide)
    add_title(slide, sd.title, '围绕五个高价值入口文件建立整体模型。')
    core = parse_bullets(sd.fields.get('核心内容', ''))
    takeaway = parse_bullets(sd.fields.get('希望听众带走什么', ''))

    center = add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, 5.45, 2.2, 2.4, 0.78, fill=PANEL, line=ACCENT)
    tf = center.text_frame
    style_tf(tf, 6, 6, 8, 8)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = '五个入口文件'
    set_run_font(r, 16, TITLE, True)

    related = [
        ('main.tsx', 1.0, 1.55, ACCENT),
        ('QueryEngine.ts', 8.9, 1.55, ACCENT_2),
        ('query.ts', 1.15, 3.25, ACCENT_2),
        ('toolExecution.ts', 8.55, 3.25, ACCENT_3),
        ('sessionStorage.ts', 4.75, 4.2, WARN),
    ]
    for txt, x, y, color in related:
        shp = add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, x, y, 2.0, 0.64, fill=PANEL, line=color)
        tf = shp.text_frame
        style_tf(tf, 5, 5, 8, 8)
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = txt
        set_run_font(r, 12.6, TITLE, True)
        connect(slide, x + 1.0, y + 0.64, 6.65, 2.98, color)

    add_panel(slide, 0.75, 5.15, 11.6, 1.25, '为什么优先看这五个文件', title_color=ACCENT_2)
    add_text(slide, 0.95, 5.52, 11.2, 0.78, core[:8], size=13.2)
    if takeaway:
        add_panel(slide, 0.75, 6.56, 11.6, 0.58, '调研结论', title_color=WARN, fill=PANEL_3)
        add_text(slide, 0.95, 6.79, 11.2, 0.18, takeaway, size=14.0, bullet=False)
    add_footer(slide, 'Claude Code 源码调研', '代码走读概略')


def generic_slide(prs: Presentation, sd: SlideData):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide)
    subtitle = ''
    if 1 <= sd.num <= 6:
        subtitle = '总体架构'
    elif 7 <= sd.num <= 12:
        subtitle = '工作流程'
    elif 13 <= sd.num <= 23:
        subtitle = '功能介绍'
    elif 24 <= sd.num <= 27:
        subtitle = '产出'
    elif 28 <= sd.num <= 37:
        subtitle = '开发流程建议'
    else:
        subtitle = '代码走读概略'
    add_title(slide, sd.title, subtitle)
    question = parse_bullets(sd.fields.get('这一页要回答的问题', ''))
    core = parse_bullets(sd.fields.get('核心内容', ''))
    sources = markdown_label_list(sd.fields.get('代码支撑', ''))
    insight = parse_bullets(sd.fields.get('代码理解支撑', ''))
    takeaway = parse_bullets(sd.fields.get('希望听众带走什么', ''))
    code = parse_code(sd.fields.get('关键代码片段', ''))

    if question:
        add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, 0.62, 1.5, 12.02, 0.68, fill=PANEL_3, line=ACCENT)
        add_text(slide, 0.84, 1.77, 11.55, 0.2, question, size=14.5, bullet=False)
        top_y = 2.38
    else:
        top_y = 1.55

    add_panel(slide, 0.62, top_y, 7.0, 3.95, '核心内容', title_color=ACCENT_2)
    if core:
        add_text(slide, 0.82, top_y+0.38, 6.65, 3.48, core[:9], size=15.2)
    else:
        sections = []
        for key in ('功能', '实现原理', '使用技巧'):
            if key in sd.fields:
                sections.append((key, parse_bullets(sd.fields.get(key, '')) or [strip_links(sd.fields.get(key, ''))]))
        add_rich_lines(slide, 0.8, top_y+0.38, 6.68, 3.42, sections)

    if code:
        add_code_box(slide, 7.82, top_y, 4.8, 1.95, code, '关键源码片段')
        add_panel(slide, 7.82, top_y+2.12, 4.8, 1.83, '这段代码说明什么', title_color=ACCENT_3)
        add_text(slide, 8.02, top_y+2.48, 4.4, 1.38, insight[:4] or ['这段代码支撑了当前页的判断。'], size=13.2)
    else:
        add_panel(slide, 7.82, top_y, 4.8, 2.22, '实现含义', title_color=ACCENT_3)
        add_text(slide, 8.02, top_y+0.38, 4.4, 1.72, insight[:5] or ['本页重点在于建立整体理解，而不是展开单段代码。'], size=13.2)
        add_panel(slide, 7.82, top_y+2.42, 4.8, 1.53, '相关代码', title_color=ACCENT)
        add_text(slide, 8.02, top_y+2.78, 4.35, 1.08, sources[:4] or ['本页无单独源码列表'], size=11.6)

    add_panel(slide, 0.62, 6.55, 12.02, 0.68, '调研结论', title_color=WARN, fill=PANEL_3)
    add_text(slide, 0.84, 6.83, 11.58, 0.18, takeaway or ['本页的重点是建立正确心智模型。'], size=14.2, bullet=False)
    footer_right = ' / '.join(sources[:4])
    add_footer(slide, 'Claude Code 源码调研', footer_right)


def function_slide(prs: Presentation, sd: SlideData):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide)
    add_title(slide, sd.title, '功能 / 实现原理 / 使用技巧 / 代码理解')
    question = parse_bullets(sd.fields.get('这一页要回答的问题', ''))
    if question:
        add_shape(slide, MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, 0.62, 1.5, 12.02, 0.68, fill=PANEL_3, line=ACCENT)
        add_text(slide, 0.84, 1.77, 11.55, 0.2, question, size=14.5, bullet=False)
        top_y = 2.38
    else:
        top_y = 1.55
    add_panel(slide, 0.62, top_y, 3.92, 1.35, '功能', title_color=ACCENT)
    add_text(slide, 0.82, top_y+0.37, 3.5, 0.88, parse_bullets(sd.fields.get('功能', '')) or [strip_links(sd.fields.get('功能', ''))], size=13.6)
    add_panel(slide, 0.62, top_y+1.52, 3.92, 2.18, '实现原理', title_color=ACCENT_2)
    add_text(slide, 0.82, top_y+1.89, 3.5, 1.7, parse_bullets(sd.fields.get('实现原理', '')) or [strip_links(sd.fields.get('实现原理', ''))], size=13.0)
    add_panel(slide, 4.72, top_y, 3.1, 3.7, '使用技巧', title_color=ACCENT_3)
    add_text(slide, 4.92, top_y+0.37, 2.7, 3.18, parse_bullets(sd.fields.get('使用技巧', '')) or [strip_links(sd.fields.get('使用技巧', ''))], size=12.8)
    code = parse_code(sd.fields.get('关键代码片段', ''))
    insight = parse_bullets(sd.fields.get('代码理解支撑', ''))
    sources = markdown_label_list(sd.fields.get('代码支撑', ''))
    if code:
        add_code_box(slide, 8.02, top_y, 4.62, 2.1, code, '关键源码片段')
        add_panel(slide, 8.02, top_y+2.28, 4.62, 1.42, '这段代码说明什么', title_color=WARN)
        add_text(slide, 8.2, top_y+2.62, 4.22, 0.94, insight[:4], size=12.8)
    else:
        add_panel(slide, 8.02, top_y, 4.62, 2.0, '实现含义', title_color=WARN)
        add_text(slide, 8.2, top_y+0.38, 4.22, 1.46, insight[:5], size=12.8)
        add_panel(slide, 8.02, top_y+2.18, 4.62, 1.52, '相关代码', title_color=ACCENT)
        add_text(slide, 8.2, top_y+2.54, 4.22, 1.0, sources[:4] or ['本页无单独源码列表'], size=11.4)
    takeaway = parse_bullets(sd.fields.get('希望听众带走什么', ''))
    add_panel(slide, 0.62, 6.55, 12.02, 0.68, '调研结论', title_color=WARN, fill=PANEL_3)
    add_text(slide, 0.84, 6.83, 11.58, 0.18, takeaway or ['理解机制之后，才能推出更稳定的使用方式。'], size=14.0, bullet=False)
    add_footer(slide, 'Claude Code 源码调研', ' / '.join(sources[:4]))


def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    slides = parse_outline()
    for sd in slides:
        if sd.num == 1:
            add_cover_slide(prs, sd)
        elif sd.num == 4:
            add_overview_diagram(prs, sd)
        elif sd.num == 10:
            add_workflow_diagram(prs, sd)
        elif sd.num == 13:
            add_capability_slide(prs, sd)
        elif sd.num == 38:
            add_codewalk_architecture_slide(prs, sd)
        elif sd.num == 39:
            add_codewalk_order_slide(prs, sd)
        elif sd.num == 40:
            add_keyfiles_slide(prs, sd)
        elif '功能' in sd.fields:
            function_slide(prs, sd)
        else:
            generic_slide(prs, sd)

        slide = prs.slides[-1]
        notes = SLIDE_NOTES.get(sd.num)
        if notes:
            set_slide_notes(slide, notes)

    prs.save(OUT)
    print(f'Wrote {OUT}')


if __name__ == '__main__':
    build_deck()
