#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BambuPlot - Simplified Chinese localization generator
BambuPlot - 简体中文汉化生成器

Generates a Chinese-localized build of bambuplot-v1.1.0.html by injecting a
small i18n layer (translation dictionary + regex rules + DOM text scanner)
at the end of the app's IIFE.

通过在应用 IIFE 末尾注入一层轻量 i18n（翻译字典 + 正则规则 + DOM 文本扫描器），
生成 BambuPlot 的中文版。不修改任何业务逻辑。

Usage / 用法:
    python generate_zh.py
    python generate_zh.py --src bambuplot-v1.1.0.html --out bambuplot-v1.1.0-zh.html

Notes / 说明:
  * The source file's line endings (CRLF/LF) are preserved, so the generated
    file differs from the source only by the injected i18n layer.
    保留源文件的换行符，因此生成文件与源文件的差异仅为注入的 i18n 层。
  * G-code instructions (G0/G1/G28/M84 ...) are never modified. Only comment
    lines beginning with ';' - and the comment after a ';' separator on an
    instruction line - are translated.
    绝不修改 G 代码指令，仅翻译 ';' 开头的注释行与指令行分号后的注释。
  * Re-run after an upstream update to refresh the localized build.
    上游更新后重新运行本脚本即可刷新中文版。
"""
import argparse, io, os, re, json

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)

_argp = argparse.ArgumentParser(
    description="Generate the Simplified Chinese build of BambuPlot.")
_argp.add_argument("--src", default=os.path.join(_root, "bambuplot-v1.1.0.html"),
                   help="source single-file app (default: bambuplot-v1.1.0.html)")
_argp.add_argument("--out", default=os.path.join(_root, "bambuplot-v1.1.0-zh.html"),
                   help="output file (default: bambuplot-v1.1.0-zh.html)")
_args = _argp.parse_args()

SRC = _args.src
DST = _args.out

if not os.path.isfile(SRC):
    raise SystemExit("source not found: " + SRC)

# Read as bytes so the source file's line endings can be preserved exactly.
with open(SRC, "rb") as _f:
    _raw = _f.read()
_uses_crlf = b"\r\n" in _raw
html = _raw.decode("utf-8")
if _uses_crlf:
    html = html.replace("\r\n", "\n")

# ================================================================ 字典
ZH = {
    # ---- 页面标题 ----
    "BambuPlot — free pen plotter G-code for Bambu Lab":
        "BambuPlot — 拓竹免费笔式绘图仪 G 代码生成器",
    "free pen-plotter G-code generator": "免费笔式绘图仪 G 代码生成器",
    "Printer": "打印机",
    "Custom": "自定义",
    "✕ Clear all": "✕ 全部清除",

    # ---- 标签页 ----
    "Text": "文字",
    "Shapes": "形状",
    "Image": "图片",
    "3MF": "3MF",
    "Handwrite": "手写体",
    "Layers": "图层",
    "Pen": "画笔/设置",

    # ---- 需要整句匹配、且含易误伤子串的长句 ----
    "Convention: penPosition = nozzlePosition + toolOffset. Positive X = pen to the right of the nozzle, positive Y = pen toward the back — so a pen mounted 45 mm to the LEFT of the nozzle uses X = -45. The canvas always shows where the physical pen tip draws; the G-code moves the nozzle by (canvas point − toolOffset), so drawings are never visually shifted. The shaded bed strips show the area the pen tip cannot reach.":
        "约定：笔位置 = 喷嘴位置 + 工具偏移。X 为正 = 笔在喷嘴右侧，Y 为正 = 笔偏向后方——因此安装在喷嘴左侧 45 mm 的笔应设 X = -45。画布始终显示物理笔尖实际绘制的位置；G 代码让喷嘴移动（画布坐标 − 工具偏移），所以画面不会发生视觉偏移。热床上的阴影区域表示笔尖无法到达的位置。",
    # 以下是被 <b> 标签拆开后的独立文本片段
    "Convention:": "约定：",
    ". Positive X = pen to the right of the nozzle, positive Y = pen toward the back — so a pen mounted 45 mm to the LEFT of the nozzle uses X = -45. The canvas always shows where the physical pen tip draws; the G-code moves the nozzle by (canvas point − toolOffset), so drawings are never visually shifted. The shaded bed strips show the area the pen tip cannot reach.":
        "。X 为正 = 笔在喷嘴右侧，Y 为正 = 笔偏向后方——因此安装在喷嘴左侧 45 mm 的笔应设 X = -45。画布始终显示物理笔尖实际绘制的位置；G 代码让喷嘴移动（画布坐标 − 工具偏移），所以画面不会发生视觉偏移。热床上的阴影区域表示笔尖无法到达的位置。",
    "Positive X = pen to the right of the nozzle, positive Y = pen toward the back — so a pen mounted 45 mm to the LEFT of the nozzle uses X = -45. The canvas always shows where the physical pen tip draws; the G-code moves the nozzle by (canvas point − toolOffset), so drawings are never visually shifted. The shaded bed strips show the area the pen tip cannot reach.":
        "X 为正 = 笔在喷嘴右侧，Y 为正 = 笔偏向后方——因此安装在喷嘴左侧 45 mm 的笔应设 X = -45。画布始终显示物理笔尖实际绘制的位置；G 代码让喷嘴移动（画布坐标 − 工具偏移），所以画面不会发生视觉偏移。热床上的阴影区域表示笔尖无法到达的位置。",
    " s (G4 — time to clip on the pen)": " 秒（G4 — 用来夹上笔的时间）",
    "s (G4 — time to clip on the pen)": "秒（G4 — 用来夹上笔的时间）",
    "Positive X = pen to the right of the nozzle, positive Y = pen toward the back — so a pen mounted 45 mm to the LEFT of the nozzle uses X = -45. The canvas always shows where the physical pen tip draws; the G-code moves the nozzle by (canvas point − toolOffset), so drawings are never visually shifted. The shaded bed strips show the area the pen tip cannot reach.":
        "X 为正 = 笔在喷嘴右侧，Y 为正 = 笔偏向后方——因此安装在喷嘴左侧 45 mm 的笔应设 X = -45。画布始终显示物理笔尖实际绘制的位置；G 代码让喷嘴移动（画布坐标 − 工具偏移），所以画面不会发生视觉偏移。热床上的阴影区域表示笔尖无法到达的位置。",
    "penPosition = nozzlePosition + toolOffset": "笔位置 = 喷嘴位置 + 工具偏移",
    "Bambu printers don't accept raw G-code the way Marlin printers do. Most people use LAN/Developer Mode and Bambu Studio's G-code console to send commands directly, or paste short blocks into a calibration/custom G-code field. Procedures change over time and vary by firmware, so check Bambu Lab's wiki/forum for the current method on your printer. Always run a dry pass with the pen lifted first.":
        "拓竹打印机不像 Marlin 打印机那样直接接受原始 G 代码。大多数人使用 LAN/开发者模式和 Bambu Studio 的 G 代码控制台直接发送指令，或者把简短片段粘贴到校准/自定义 G 代码输入框。操作方法会随时间和固件版本变化，请查看 Bambu Lab 的 wiki/论坛了解你的机型的现行方法。务必先用抬笔状态空跑一遍。",
    "Bambu printers don't accept raw G-code the way Marlin printers do. Most people use": "拓竹打印机不像 Marlin 打印机那样直接接受原始 G 代码。大多数人使用",
    "and Bambu Studio's G-code console to send commands directly, or paste short blocks into a calibration/custom G-code field. Procedures change over time and vary by firmware, so check Bambu Lab's wiki/forum for the current method on your printer. Always run a dry pass with the pen lifted first.":
        "和 Bambu Studio 的 G 代码控制台直接发送指令，或者把简短片段粘贴到校准/自定义 G 代码输入框。操作方法会随时间和固件版本变化，请查看 Bambu Lab 的 wiki/论坛了解你的机型的现行方法。务必先用抬笔状态空跑一遍。",
    "LAN/Developer Mode": "LAN/开发者模式",

    # ---- label 内联片段（被 <input>/<b> 拆开的文本）----
    "↳ Dwell after homing —": "↳ 归位后等待 —",
    "Dwell after homing": "归位后等待",
    "Use G2/G3 arc moves (DO NOT USE THIS ON A BAMBULAB PRINTER": "使用 G2/G3 圆弧移动（不要在拓竹打印机上使用",
    "Use G2/G3 arc moves": "使用 G2/G3 圆弧移动",

    # ---- 文字面板 ----
    "Hello Bambu!": "你好 Bambu！",
    "Style": "样式",
    "Single-stroke (looks like writing)": "单笔划（像手写一样）",
    "My handwriting": "我的手写体",
    "Filled outline (any font)": "填充轮廓（任意字体）",
    "Letter spacing:": "字间距：",
    "Line spacing:": "行间距：",
    "Randomness:": "随机度：",
    "Font (13 plot-ready styles)": "字体（13 种适合绘图的样式）",
    "Bold": "粗体",
    "Italic": "斜体",
    "Line fill style": "线条填充方式",
    "Horizontal lines": "水平线",
    "Vertical lines": "垂直线",
    "Diagonal 45°": "45° 斜线",
    "Diagonal 135°": "135° 斜线",
    "Cross-hatch (denser ink)": "交叉排线（墨更浓）",
    "Cross-hatch": "交叉排线",
    "Line density:": "线条密度：",
    "Fill density:": "填充密度：",
    "Add text to bed": "添加文字到热床",
    "Pick a shape": "选择一个形状",
    "Filled (line-hatch)": "填充（排线）",
    "Add shape to bed": "添加形状到热床",
    "Freehand draw": "自由绘制",
    "✏️ Draw directly on bed": "✏️ 直接在热床上画",
    "✓ Drawing — sketch on the bed now": "✓ 绘制中 — 现在在热床上画",
    "SVG style": "SVG 样式",
    "Vector outlines (clean pen strokes)": "矢量轮廓（干净的笔画）",
    "Contour fill (concentric lines matching the shape)": "轮廓填充（贴合形状的同心线）",
    "Shaded (black fills + outline)": "明暗（黑色填充 + 轮廓）",
    "Shading spacing:": "排线间距：",
    "Threshold (darker = more ink):": "阈值（越暗墨越多）：",
    "Invert": "反相",
    "Convert & add to bed": "转换并添加到热床",
    "Output style": "输出样式",
    "Vector outline (clean single-stroke edges)": "矢量轮廓（干净的单笔边缘）",
    "Top-down silhouette (filled / hatch)": "俯视剪影（填充 / 排线）",
    "Fill angle": "填充角度",
    "Horizontal": "水平",
    "Vertical": "垂直",
    "Flip Y axis (match Bambu Studio top-down orientation)": "翻转 Y 轴（与 Bambu Studio 自上而下视角一致）",
    "Import to bed": "导入到热床",
    "Clear all": "全部清除",
    "Clear board": "清空热床",

    # ---- 画笔/设置 ----
    "Z draw (mm)": "落笔 Z (mm)",
    "Z lift (mm)": "抬笔 Z (mm)",
    "Draw feed (mm/min)": "绘图速度 (mm/min)",
    "Travel feed (mm/min)": "空驶速度 (mm/min)",
    "Z move feed (mm/min)": "Z 轴速度 (mm/min)",
    "Pen settle time after Z move (ms)": "Z 移动后笔稳定时间 (ms)",
    "Tool offset (pen tip vs nozzle)": "工具偏移（笔尖相对喷嘴）",
    "Tool offset X (mm)": "工具偏移 X (mm)",
    "Tool offset Y (mm)": "工具偏移 Y (mm)",
    "Home all axes (G28) at start": "开始时所有轴归位（G28）",
    "Disable motors (M84) at end": "结束时关闭电机（M84）",
    "Mirror X": "镜像 X",
    "Mirror Y": "镜像 Y",
    "My profile": "我的配置文件",
    "💾 Save profile + handwriting to file": "💾 保存配置 + 手写体到文件",
    "📂 Load profile + handwriting from file": "📂 从文件加载配置 + 手写体",

    # ---- 舞台 / G 代码面板 ----
    "G-code": "G 代码",
    "Preview": "预览",
    "Copy": "复制",
    "Download": "下载",
    "Step": "单步",
    "Speed": "速度",
    "▶ Play": "▶ 播放",
    "⏸ Pause": "⏸ 暂停",
    "Generate G-code": "生成 G 代码",
    "Undo stroke": "撤销这一笔",
    "Clear this version": "清除此版本",
    "Save & next letter": "保存并下一个字母",
    "Sketch": "草图",
    "Show/hide": "显示/隐藏",
    "Duplicate": "复制",
    "Delete": "删除",
    "Items": "项目",
    "Strokes": "笔画数",
    "Ink": "墨迹",
    "Lines:": "行数：",
    "Line": "直线",
    "Version": "版本",
    "Square": "正方形",
    "Circle": "圆形",
    "Triangle": "三角形",
    "Star": "星形",
    "Line ": "直线",
    "Text:": "文字：",
    "Handwriting:": "手写体：",
    "Shape:": "形状：",
    "SVG:": "SVG：",
    "3MF:": "3MF：",
    "Everything runs locally in your browser.": "所有内容都在你的浏览器本地运行。",

    # ---- 帮助文本（help-note）----
    "Built-in single-line plotter font — one continuous pen stroke per letter shape, just like real writing. Currently covers A–Z, 0–9 and basic punctuation (lowercase is auto-capitalised). Spacing is set in letter-sized units, so it stays proportional however big or small you scale the text on the bed.":
        "内置单线绘图字体——每个字母一笔连续画完，和真实手写一样。目前支持 A–Z、0–9 和常用标点（小写会自动转为大写）。间距以字母尺寸为单位，因此无论你在热床上把文字放大或缩小，比例都保持不变。",
    "No letters drawn yet.": "还没有绘制任何字母。",
    "✏️ Draw / edit my alphabet": "✏️ 绘制 / 编辑我的字母表",
    "Uses your own drawn letters wherever available (picking randomly between any versions you've drawn); anything you haven't drawn falls back to the built-in single-stroke font. Randomness nudges each letter up/down/sideways and varies where each line starts. Spacing is set in letter-sized units, so it stays proportional however big or small you scale the text.":
        "优先使用你自己绘制的字母（在已画的多个版本中随机挑选）；没画过的字母会回退到内置单笔字体。随机度会让每个字母上下左右轻微偏移，并改变每笔的起笔位置。间距以字母尺寸为单位，因此无论文字缩放多大都保持比例。",
    "Letters are rendered as fine engraving-style line fills, not single-stroke outlines — works with any font, but a closed loop like “O” will look like a filled ring rather than a hollow outline.":
        "字母会以细密的雕刻风格线条填充来绘制，而不是单笔轮廓——适用于任何字体，但像“O”这样的闭合笔画会呈现为实心圆环，而不是空心轮廓。",
    "Shapes are exact vector outlines — the cleanest, fastest thing to plot. Freehand mode lets you sketch a single continuous stroke right on the bed preview.":
        "形状是精确的矢量轮廓——最干净、最快的绘图内容。自由绘制模式让你直接在热床预览上画一笔连续的线条。",
    "Vector mode traces the actual shapes as single pen strokes — the cleanest result for logos and line art. Shaded mode draws one clean outline per shape and hatches only the black-filled areas. Filled mode hatches the shapes like a photo.":
        "矢量模式把实际形状描摹成一笔一笔的线条——标志和线稿的最干净效果。明暗模式为每个形状画一条干净轮廓，只对黑色填充区域排线。填充模式则像照片一样整体排线。",
    "Lower = denser/more filled shading; higher = lighter, more drawn-out strokes.":
        "数值越小排线越密、越实；越大越稀疏、线条越展开。",
    "Works best with high-contrast photos, logos or line drawings. Everything happens in your browser — nothing is uploaded anywhere.":
        "适合高对比度的照片、标志和线稿。所有处理都在你的浏览器中完成——不会上传到任何地方。",
    "Extracts the mesh geometry from the .3mf and renders a top-down view (the XY footprint — what the model looks like from above) as plottable pen paths. Works with any valid 3MF file. Everything runs locally in your browser, nothing is uploaded.":
        "从 .3mf 中提取网格几何，渲染俯视图（XY 投影——模型从上方看的样子）并转换为可绘制的笔路径。适用于任何有效的 3MF 文件。全部在浏览器本地运行，不会上传任何内容。",
    "Draw your own letters — tap a slot, sketch the character (lift and click again for a separate stroke, e.g. dotting an “i”), then save. Saved automatically in this browser.":
        "绘制你自己的字母——点击格子，勾勒字符（抬起后再点击可开始新的一笔，例如给“i”加点），然后保存。自动保存在此浏览器中。",
    "Draw up to 5 versions of this letter (tabs above) — BambuPlot picks a random one each time the letter appears, so repeats don't look identical.":
        "可以为这个字母绘制最多 5 个版本（上方标签页）——每次用到该字母时 BambuPlot 会随机挑一个，所以重复出现的字不会完全一样。",
    "Adds a brief pause (G4) right after every pen up/down move. Without it, some printer firmware starts the next sideways move before the pen has fully finished lifting or lowering, which can drag a faint stray line across the paper. If you still see stray marks, try raising this a bit (150–250ms); if moves feel sluggish, you can lower it.":
        "在每次抬笔/落笔后加入一个短暂停顿（G4）。如果没有它，某些打印机固件会在笔还没完全抬起或落下时就开始下一次横向移动，从而在纸上拖出一条淡淡的杂线。如果仍看到杂线，可以适当增大这个值（150–250ms）；如果觉得动作拖沓，可以减小。",
    "Convention: penPosition = nozzlePosition + toolOffset. Positive X = pen to the right of the nozzle, positive Y = pen toward the back — so a pen mounted 45 mm to the LEFT of the nozzle uses X = -45. The canvas always shows where the physical pen tip draws; the G-code moves the nozzle by (canvas point − toolOffset), so drawings are never visually shifted. The shaded bed strips show the area the pen tip cannot reach.":
        "约定：笔位置 = 喷嘴位置 + 工具偏移。X 为正 = 笔在喷嘴右侧，Y 为正 = 笔偏向后方——因此安装在喷嘴左侧 45 mm 的笔应设 X = -45。画布始终显示物理笔尖实际绘制的位置；G 代码让喷嘴移动（画布坐标 − 工具偏移），所以画面不会发生视觉偏移。热床上的阴影区域表示笔尖无法到达的位置。",
    "Replaces curved pen paths with true circular-arc moves (smaller, smoother G-code). Firmware support varies — Marlin and Klipper handle it well; Bambu does not!":
        "把曲线笔路径替换为真正的圆弧移动（G 代码更小更顺滑）。固件支持不一——Marlin 和 Klipper 支持良好；拓竹不支持！",
    "If your first dry-run plots mirrored or rotated, flip the matching axis above and regenerate — every printer's console reports coordinates slightly differently.":
        "如果第一次试运行发现图案镜像或旋转了，翻转上面对应的轴并重新生成——每台打印机的控制台坐标报告方式略有差异。",
    "How do I send this to a Bambu printer?": "如何把结果发送到拓竹打印机？",
    "Bambu printers don't accept raw G-code the way Marlin printers do. Most people use LAN/Developer Mode and Bambu Studio's G-code console to send commands directly, or paste short blocks into a calibration/custom G-code field. Procedures change over time and vary by firmware, so check Bambu Lab's wiki/forum for the current method on your printer. Always run a dry pass with the pen lifted first.":
        "拓竹打印机不像 Marlin 打印机那样直接接受原始 G 代码。大多数人使用 LAN/开发者模式和 Bambu Studio 的 G 代码控制台直接发送指令，或者把简短片段粘贴到校准/自定义 G 代码输入框。操作方法会随时间和固件版本变化，请查看 Bambu Lab 的 wiki/论坛了解你的机型的现行方法。务必先用抬笔状态空跑一遍。",
    "Saves your printer, Z/feed settings and your full drawn alphabet into one file you keep yourself — load it again any time (new device, new browser, etc.) to get everything back exactly as it was.":
        "把你的打印机、Z 轴/速度设置和整套手绘字母表保存到一个你自己保管的文件中——随时可以再次加载（换设备、换浏览器等），一切恢复原样。",
    "BambuPlot is a free, fan-made tool — not affiliated with Bambu Lab. Pen holder STLs aren't included; search Printables/MakerWorld for a mount for your model, or use Bambu's official Pen Module on A2L/H2 series printers.":
        "BambuPlot 是一个免费的爱好者作品，与 Bambu Lab 官方无关。不含笔夹 STL 文件；可以在 Printables/MakerWorld 搜索适合你机型的支架，或在 A2L/H2 系列打印机上使用官方画笔模组。",
    "drag to move · corner to resize · top handle to rotate · top edge = back (max Y)":
        "拖动移动 · 边角缩放 · 顶部手柄旋转 · 上边缘 = 后方（最大 Y）",
    "drag to move · corner to resize · top handle to rotate":
        "拖动移动 · 边角缩放 · 顶部手柄旋转",
    "click and drag on the bed to sketch a stroke": "在热床上点击并拖动即可画一笔",
    "Add something to the bed to generate G-code.": "往热床上添加内容以生成 G 代码。",
    "; your G-code will appear here": "; 生成的 G 代码会显示在这里",
    "Nothing on the bed yet.": "热床上还没有内容。",
    "Add text, a shape, or an image to get started": "添加文字、形状或图片即可开始",
    "NO REACHABLE AREA": "无可达区域",
    "tool offset too large for this bed": "工具偏移对此热床过大",
    "reachable": "可达",
    "shaded = unreachable by the pen": "阴影 = 笔尖无法到达",
    "Click or drop a photo / logo / SVG here": "点击或拖入照片 / 标志 / SVG",
    "Click or drop a Bambu Lab .3mf file here": "点击或拖入拓竹 .3mf 文件",
    "A – Z": "A – Z", "a – z": "a – z", "0 – 9": "0 – 9",

    # ---- 打印机备注 ----
    "Compact bed — great for small tags, keychains and stickers.": "热床较小——适合小标签、钥匙扣和贴纸。",
    "Open frame, easy to reach the toolhead to clip on a pen holder.": "开放框架，容易够到工具头来夹笔架。",
    "Open frame, easy toolhead access.": "开放框架，工具头容易接近。",
    "Enclosed — open the door/lid to mount the pen holder.": "封闭式——打开门/盖板才能安装笔架。",
    "Dual-nozzle X-series. Bed shown is the main-nozzle build area (256×256mm).": "双喷嘴 X 系列。显示的是主喷嘴的打印范围（256×256mm）。",
    "Bambu sells an official clip-on Pen Module for this printer — no DIY mount needed.": "拓竹为这款机型提供官方夹扣式画笔模组——无需自制支架。",
    "Official Pen Module available. Bed shown is the single-nozzle area (325×320mm).": "有官方画笔模组。显示的是单喷嘴区域（325×320mm）。",
    "Official Pen Module available.": "有官方画笔模组。",
    "Enter your own bed size on the right.": "在右侧输入你自己的热床尺寸。",

    # ---- 动态状态 / 提示 ----
    "Loading…": "加载中…",
    "Tracing…": "正在描摹…",
    "Processing…": "正在处理…",
    "Generating…": "正在生成…",
    "Plotting letters…": "正在绘制字母…",
    "Error — drop another file to try again": "出错——拖入其他文件重试",
    "Added to bed — drag to position it.": "已添加到热床——拖动来摆放位置。",
    "Sketch added.": "已添加草图。",
    "Type some text first.": "请先输入文字。",
    "No matching letters yet — draw some in the Handwrite tab first.": "还没有匹配的字母——请先在“手写体”标签页画一些。",
    "Nothing to plot — try different text or a lower threshold.": "没有可绘制内容——换个文字或降低阈值试试。",
    "No ink detected — try adjusting the threshold or invert.": "没有检测到墨迹——调整阈值或试试反相。",
    "Nothing to plot — the SVG looks empty. Try outline mode.": "没有可绘制内容——这个 SVG 似乎是空的。试试轮廓模式。",
    "No drawable vector paths in that SVG.": "这个 SVG 里没有可绘制的矢量路径。",
    "No silhouette edges found — try the filled mode instead.": "没有找到剪影边缘——试试填充模式。",
    "Could not chain outline — try the filled mode.": "无法串联轮廓——试试填充模式。",
    "Nothing to plot — try a lower density.": "没有可绘制内容——试试降低密度。",
    "Something went wrong building that text — try a shorter line or a different style.": "生成该文字时出错——试试更短的一行或换个样式。",
    "Something went wrong building that shape — try a lower fill density.": "生成该形状时出错——试试降低填充密度。",
    "Something went wrong tracing that — try a lower line density.": "描摹时出错——试试降低线条密度。",
    "Something went wrong — try the other output style, or a simpler model.": "处理出错——换个输出样式，或用更简单的模型。",
    "Something went wrong generating the G-code — try again, or simplify the design a bit.": "生成 G 代码时出错——请重试，或把设计简化一点。",
    "Could not read that SVG file.": "无法读取该 SVG 文件。",
    "Please choose an image or SVG file.": "请选择图片或 SVG 文件。",
    "Load a .3mf file first.": "请先加载 .3mf 文件。",
    "Add something to the bed first.": "请先往热床上添加内容。",
    "Drawing exceeds the drawable area — G-code not generated.": "图案超出可绘制区域——未生成 G 代码。",
    "G-code copied to clipboard.": "G 代码已复制到剪贴板。",
    "Copy failed — your browser may need a secure (HTTPS) connection.": "复制失败——浏览器可能需要安全（HTTPS）连接。",
    "Generate the G-code first.": "请先生成 G 代码。",
    "Download failed — try generating again.": "下载失败——请重新生成试试。",
    "Preview finished.": "预览结束。",
    "No moves found to preview.": "没有找到可预览的移动。",
    "Profile saved — keep that file somewhere safe.": "配置已保存——请把文件妥善保管。",
    "Could not read that file — is it a BambuPlot profile?": "无法读取该文件——它确实是 BambuPlot 配置文件吗？",
    "Invalid profile file.": "配置文件无效。",
    "Profile loaded.": "配置已加载。",
    "Nothing recognizable in that file.": "文件里没有可识别的内容。",
    "Clear everything from the bed and the generated G-code?": "确定要清除热床上的所有内容和已生成的 G 代码吗？",
    "Clear your entire handwriting set? This cannot be undone.": "确定要清除整套手写体吗？此操作无法撤销。",
    "Remove everything from the bed and the generated G-code": "清除热床上的所有内容和已生成的 G 代码",
    "Animate the toolpath on the bed": "在热床上动画演示刀具路径",
    "Copy G-code to clipboard": "复制 G 代码到剪贴板",
    "Download .gcode": "下载 .gcode 文件",
    "Advance one move": "前进一个移动",
    "Back to start": "回到开头",
    "Close preview": "关闭预览",
    "JSZip library not loaded — check your internet connection.": "JSZip 库未加载——请检查网络连接。",
    "Drawing exceeds the drawable area.": "图案超出可绘制区域。",
    "Nothing was generated. Move the item into the un-shaded area or reduce the tool offset, then try again.":
        "未生成任何内容。请把项目移动到非阴影区域，或减小工具偏移后重试。",
    "Tip: increase the line-density value (fewer, more spread-out lines) on your text/image/shapes for a lighter file.":
        "提示：把文字/图片/形状的线条密度调大（线更少、更稀疏）可以得到更轻量的文件。",
    "Generate anyway?": "仍要生成吗？",
    " triangles": " 个三角面",
    " — large model, processing may take a few seconds": " — 模型较大，处理可能需要几秒",
    "Strokes:": "笔画数：",
    "Ink path:": "墨迹路径：",
    "Est. draw time:": "预计绘制时间：",
    " broken points were skipped.": " 个损坏的点被跳过。",
    " more lines not shown here to keep the preview fast …": " 行未在此显示以保证预览流畅 …",
    "; The full file is included when you click download.": "; 点击下载时包含完整文件。",
    "This design has ": "当前设计有 ",
    " points, which may take a while and could feel like the page has frozen for a few seconds.": " 个点，可能需要一些时间，页面可能有几秒像卡住一样。",
    " point(s) would push the nozzle outside X0–": " 个点会使喷嘴超出 X0–",
    " — first seen in “": " — 首次出现在“",
    "; G-code not generated — fix the placement issue shown next to this panel, then generate again.":
        "; 未生成 G 代码——请先解决面板旁显示的位置问题，然后重新生成。",
    " width mm": " 宽度 mm", " depth mm": " 深度 mm",
    " mm": " mm", " px": " px", " done": " 已完成",
    " s (G4 — time to clip on the pen)": " 秒（G4 — 用来夹上笔的时间）",

    # ---- G 代码注释行（以 ; 开头，安全翻译）----
    "; Generated by BambuPlot — free pen-plotter G-code generator for Bambu Lab printers":
        "; 由 BambuPlot 生成 — 拓竹免费笔式绘图仪 G 代码生成器",
    "Printer:": "打印机：",
    "Bed:": "热床：",
    "; Coordinates assume the front-left corner of the bed is X0 Y0.":
        "; 坐标以热床左前角为 X0 Y0。",
    "; ALWAYS run a dry pass with the pen lifted first.":
        "; 务必先用抬笔状态空跑一遍。",
    "; absolute positioning": "; 绝对定位",
    "; millimeters": "; 毫米",
    "G90 ; absolute positioning": "G90 ; 绝对定位",
    "G21 ; millimeters": "G21 ; 毫米",
    "; home all axes": "; 所有轴归位",
    "G28 ; home all axes": "G28 ; 所有轴归位",
    "; G2/G3 arc moves enabled — requires firmware arc support":
        "; 已启用 G2/G3 圆弧移动 — 需要固件支持圆弧",
    "; Dwell":
        "; 停",
    "dwell — clip the pen holder on now, then the printer will continue automatically":
        "等待 — 现在夹上笔架，之后打印机会自动继续",
    "; Path coordinates below are NOZZLE positions (canvas pen path minus tool offset).":
        "; 下方路径坐标是喷嘴位置（画布笔路径减去工具偏移）。",
    "; Tool offset (penPosition = nozzlePosition + offset): X":
        "; 工具偏移（笔位置 = 喷嘴位置 + 偏移）：X",
    "; your G-code will appear here": "; 生成的 G 代码会显示在这里",
    " nozzle coordinate out of range: X": "喷嘴坐标超出范围：X",
    " (allowed X0-": "（允许 X0-",
}

# 属性级翻译（完整值匹配）
ZH_ATTR = {
    "title": {
        "Remove everything from the bed and the generated G-code": "清除热床上的所有内容和已生成的 G 代码",
        "Animate the toolpath on the bed": "在热床上动画演示刀具路径",
        "Copy G-code to clipboard": "复制 G 代码到剪贴板",
        "Download .gcode": "下载 .gcode 文件",
        "Advance one move": "前进一个移动",
        "Back to start": "回到开头",
        "Close preview": "关闭预览",
        "Show/hide": "显示/隐藏",
        "Duplicate": "复制",
        "Delete": "删除",
    },
    "placeholder": {
        "width mm": "宽度 mm",
        "depth mm": "深度 mm",
        "Hello Bambu!": "你好 Bambu！",
    },
}

# 正则规则（针对含数字的整句模板）
ZH_RE = [
    (re.compile(r"^(\d+) of (\d+) letters drawn\.$"), r"\1 / \2 个字母已绘制"),
    (re.compile(r"^No letters drawn yet\.$"), "还没有绘制任何字母。"),
    (re.compile(r"^(\d+) broken points were skipped\.$"), r"跳过了 \1 个损坏的点。"),
]

# ================================================================ JS 层
I18N = r"""
/* ===================== 中文汉化层 (BambuPlot i18n) ===================== */
var ZH = __ZH__;
var ZH_ATTR = __ZH_ATTR__;
var ZH_RE = __ZH_RE__;
var ZH_KEYS = Object.keys(ZH).sort(function(a,b){ return b.length-a.length; });
var ZH_RES = ZH_KEYS.map(function(k){
  var esc = k.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  // 词边界：两侧不允许紧邻 ASCII 字母/数字/下划线，
  // 但允许 - _ / . : ; , 空格 （ 等标点相邻，
  // 这样 "G-code" 不会被 "G" 误伤，而 "G 代码" 能正确替换。
  var re = new RegExp('(?<![A-Za-z0-9_])' + esc + '(?![A-Za-z0-9_])', 'g');
  return { re: re, to: ZH[k] };
});

function ZH_TR(s){
  if(typeof s!=='string' || !s) return s;
  var t = s.trim();
  if(!t) return s;
  if(Object.prototype.hasOwnProperty.call(ZH, t)) return ZH[t];
  for(var i=0;i<ZH_RE.length;i++){
    if(ZH_RE[i][0].test(t)) return t.replace(ZH_RE[i][0], ZH_RE[i][1]);
  }
  // 统一不可见空白后重试整句匹配（DOM 里 &nbsp; 是 \u00a0，字典里是普通空格）
  var norm = t.replace(/\u00a0/g, ' ');
  if(Object.prototype.hasOwnProperty.call(ZH, norm)) return ZH[norm];
  for(var m=0;m<ZH_RE.length;m++){
    if(ZH_RE[m][0].test(norm)) return norm.replace(ZH_RE[m][0], ZH_RE[m][1]);
  }
  // 子串替换（词边界保护），长键优先。
  // 注意：全局正则带 lastIndex 状态，必须先 reset 再 replace。
  var out = t, hit=false;
  for(var j=0;j<ZH_RES.length;j++){
    var re=ZH_RES[j].re;
    re.lastIndex=0;
    if(re.test(out)){
      re.lastIndex=0;
      out = out.replace(re, ZH_RES[j].to);
      hit=true;
    }
  }
  if(hit){
    // 精确还原原始前后空白：t 是 trim 后的，s 含原始空白，
    // 直接把 t 在 s 中的出现替换为 out，替换失败则退化为整体返回 out
    var idx = s.indexOf(t);
    if(idx>=0) return s.slice(0,idx) + out + s.slice(idx+t.length);
    return out;
  }
  return s;
}

/* --- 原生对话框 --- */
(function(){
  var _a=window.alert, _c=window.confirm;
  window.alert=function(m){ return _a.call(window, ZH_TR(m)); };
  window.confirm=function(m){ return _c.call(window, ZH_TR(m)); };
})();

/* --- 静态属性 --- */
function ZH_ATTRS(root){
  var els = root.querySelectorAll('*');
  for(var i=0;i<els.length;i++){
    var el=els[i];
    for(var attr in ZH_ATTR){
      if(!ZH_ATTR.hasOwnProperty(attr)) continue;
      var v=el.getAttribute && el.getAttribute(attr);
      if(v && Object.prototype.hasOwnProperty.call(ZH_ATTR[attr], v)) el.setAttribute(attr, ZH_ATTR[attr][v]);
    }
  }
}

/* --- DOM 文本扫描（覆盖 innerHTML/textContent 动态插入）---
   注意：只翻译“注释/说明性”文本，绝不碰真实 G 指令。
   判定：若文本块以 ';' 开头或整块就是一条已知的提示文案才翻译；
   以 G/M/F/S/T/N 等指令字母开头的行一律原样保留。 --- */
var ZH_SKIP = {};
var ZH_INSTR_RE = /^\s*[GMTFSHNOPQRXYZIJKLBE]\s*[\d.]/i;
function ZH_TR_ATTR_EL(el){ return false; }
function ZH_IS_INSTRUCTIONS(s){
  var t = s.trim();
  if(!t) return false;
  var lines = t.split('\n');
  // 只有“注释 + 指令”混合、且指令行本身不含已知可译中文/英文提示片段时，
  // 才整体跳过。纯注释块（每行都以 ; 开头）允许逐行译。
  var hasInstr = false;
  for(var i=0;i<lines.length;i++){
    var lt = lines[i].trim();
    if(!lt) continue;
    // 形如 "G90 ; absolute positioning" 的带注释指令行 → 指令行
    if(ZH_INSTR_RE.test(lt)) hasInstr = true;
  }
  return hasInstr;
}
function ZH_SCAN(){
  var w=document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
    acceptNode: function(n){
      var p=n.parentElement;
      if(!p) return NodeFilter.FILTER_REJECT;
      var tag=p.tagName;
      if(tag==='SCRIPT'||tag==='STYLE'||tag==='NOSCRIPT'||tag==='TEXTAREA'||tag==='TITLE') return NodeFilter.FILTER_REJECT;
      if(ZH_TR_ATTR_EL(p)) return NodeFilter.FILTER_REJECT;
      if(!n.nodeValue || !n.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_ACCEPT;
    }
  });
  var n, list=[];
  while((n=w.nextNode())) list.push(n);
  for(var i=0;i<list.length;i++){
    var nd=list[i], raw=nd.nodeValue;
    // G 代码块（含指令行）→ 只逐行翻译注释行，绝不碰指令。
    // 注意：var 是函数作用域，下列变量每轮必须显式重置，
    // 否则上一轮遗留的值会被下一轮误用（曾导致品牌名被覆盖）。
    var translated = undefined;
    if(ZH_IS_INSTRUCTIONS(raw)){
      var lines=raw.split('\n'), changed=false;
      for(var L=0;L<lines.length;L++){
        var lt=lines[L].trim();
        var t=undefined, t2=undefined, cmd=undefined, cmt=undefined, semi=-1;
        if(lt.charAt(0)===';'){
          t=ZH_TR(lt);
          if(t!==lt){ lines[L]=lines[L].replace(lt, t); changed=true; }
        } else if(ZH_INSTR_RE.test(lt)){
          // 形如 "G90 ; absolute positioning" —— 只译分号后的注释部分
          semi=lt.indexOf(';');
          if(semi>=0){
            cmd=lt.slice(0,semi).trim();
            cmt=lt.slice(semi+1).trim();
            t2=ZH_TR(cmt);
            if(t2!==cmt){ lines[L]=lines[L].replace(lt, cmd+' ; '+t2); changed=true; }
          }
        }
      }
      if(changed) translated=lines.join('\n');
    }
    if(translated===undefined) translated=ZH_TR(raw);
    if(translated!==raw) nd.nodeValue=translated;
  }
}
function ZH_BOOT(){
  ZH_ATTRS(document.body);
  ZH_SCAN();
  document.title = ZH_TR(document.title);
  document.documentElement.setAttribute('lang','zh-CN');
}
if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', ZH_BOOT);
else ZH_BOOT();
setInterval(ZH_SCAN, 350);
/* ===================== 中文汉化层 END ===================== */
"""

def js_str(s):
    return json.dumps(s, ensure_ascii=False)

zh_js = "{\n" + ",\n".join("  %s: %s" % (js_str(k), js_str(v)) for k, v in ZH.items()) + "\n}"
attr_js = json.dumps(ZH_ATTR, ensure_ascii=False, indent=2)
re_js = "[\n" + ",\n".join("  [/%s/, %s]" % (p.pattern.replace("/", "\\/"), js_str(r)) for p, r in ZH_RE) + "\n]"

i18n = (I18N.replace("__ZH__", zh_js)
            .replace("__ZH_ATTR__", attr_js)
            .replace("__ZH_RE__", re_js))

# 1) toast 函数：进入时就翻译
html = html.replace("function toast(msg){\n", "function toast(msg){ msg=ZH_TR(msg);\n", 1)
assert "function toast(msg){ msg=ZH_TR(msg);" in html, "toast patch failed"

# 2) 注入 i18n 层（IIFE 内部，函数声明提升，toast 可引用）
marker = "})();\n</script>"
assert marker in html, "inject marker not found"
html = html.replace(marker, "})();\n" + i18n + "\n</script>", 1)

# Restore the source file's original line endings before writing.
_out = html.replace("\n", "\r\n") if _uses_crlf else html
with open(DST, "wb") as f:
    f.write(_out.encode("utf-8"))

print("OK -> " + DST)
print("source bytes: %d   output bytes: %d" % (len(_raw), len(_out.encode("utf-8"))))
