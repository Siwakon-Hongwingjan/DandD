#!/usr/bin/env python3
"""สร้างหน้าเว็บ 4 หน้า (รัน: cd locations && python3 build.py)
- locations/สถานที่ทั้งหมด.html             จาก locations/NN-*.md  (ตารางกติกา)
- places/สถานที่และบทบรรยาย.html           จาก places/NN-*.md     (คำบรรยาย เหตุการณ์สุ่ม การ์ดกลุ่ม)
- character/แฟ้มตัวละคร.html               จาก character/NN-*.md  (แฟ้มละคน · ขึ้นต้นด้วย <!-- group: หมวด -->)
- dialog/เนื้อเรื่องหลัก.html               จาก dialog/NN-*.md     (เนื้อเรื่องหลัก)
โฟลเดอร์ที่ไม่ใช่ locations: 00-สารบัญ.md เป็นสารบัญหน้าแรก · ลิงก์ #id ที่ไม่อยู่ในหน้าตัวเอง ชี้ไปหน้าอื่นให้อัตโนมัติ"""
import re, html, glob, os
from urllib.parse import quote

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
esc = lambda t: html.escape(t, quote=False)

def inline(t):
    t = esc(t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?![\*\w])', r'<em>\1</em>', t)
    t = re.sub(r'\[([^\]]+)\]\((#[^)]+)\)', r'<a href="\2">\1</a>', t)
    return t

def slug(t, used):
    s = re.sub(r'[^\w฀-๿]+', '-', t).strip('-') or 'x'
    base, n = s, 2
    while s in used: s, n = f"{base}-{n}", n + 1
    used.add(s); return s

def heading(line, used):
    m = re.match(r'^(#{1,4})\s+(.*?)(?:\s*\{#([\w\-]+)\})?\s*$', line)
    lvl, text, hid = len(m.group(1)), m.group(2), m.group(3)
    if hid: used.add(hid)
    return lvl, text, hid or slug(text, used)

def render(md, used, toc, dlg=False, flat=False):
    # dlg: ย่อหน้าขึ้นบรรทัดใหม่ตามต้นฉบับ · flat: หัวข้อธรรมดา ไม่ห่อเป็นสถานที่/ไม่เข้าสารบัญข้าง
    out, lines, i = [], md.split("\n"), 0
    in_loc = False
    def close_loc():
        nonlocal in_loc
        if in_loc: out.append("</div></section>"); in_loc = False
    while i < len(lines):
        ln = lines[i]
        if not ln.strip(): i += 1; continue
        if ln.startswith("#"):
            lvl, text, hid = heading(ln, used)
            if flat:
                out.append(f'<h{lvl} id="{hid}">{inline(text)}</h{lvl}>')
            elif lvl == 1:
                close_loc(); toc.append((1, text, hid))
                out.append(f'<h1 class="cat" id="{hid}">{inline(text)}</h1>')
            elif lvl == 2:
                close_loc(); toc.append((2, text, hid)); in_loc = True
                out.append(f'<section class="loc" id="{hid}"><h2 onclick="this.parentNode.classList.toggle(\'closed\')">{inline(text)}<a class="up" href="#toc" onclick="event.stopPropagation()">↑ สารบัญ</a></h2><div class="body">')
            else:
                out.append(f'<h{lvl} id="{hid}">{inline(text)}</h{lvl}>')
            i += 1
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i]); i += 1
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            head, body = cells(rows[0]), [cells(r) for r in rows[2:]]
            t = "<div class='tw'><table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
            for r in body: t += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
            out.append(t + "</tbody></table></div>")
        elif re.match(r'^\s*[-*]\s+', ln) or re.match(r'^\s*\d+\.\s+', ln):
            items = []
            while i < len(lines) and (re.match(r'^\s*[-*]\s+', lines[i]) or re.match(r'^\s*\d+\.\s+', lines[i]) or (lines[i].startswith("  ") and lines[i].strip() and items)):
                items.append(lines[i]); i += 1
            def build(its):
                if all(x.lstrip().startswith(">") for x in its):  # คำพูดที่ย่อหน้าซ้อนใต้ข้อ
                    return "<blockquote>" + "<br>".join(inline(x.lstrip().lstrip("> ")) for x in its) + "</blockquote>"
                first = re.match(r'^\s*(\d+)\.\s', its[0])
                res, k = (f'<ol start="{first.group(1)}">' if first else "<ul>"), 0
                while k < len(its):
                    ind = len(its[k]) - len(its[k].lstrip())
                    txt = re.sub(r'^\s*([-*]|\d+\.)\s+', '', its[k])
                    sub = []
                    k += 1
                    while k < len(its) and (len(its[k]) - len(its[k].lstrip())) > ind:
                        sub.append(its[k]); k += 1
                    res += f"<li>{inline(txt)}" + (build(sub) if sub else "") + "</li>"
                return res + ("</ol>" if first else "</ul>")
            out.append(build(items))
        elif ln.startswith(">"):
            q = []
            while i < len(lines) and lines[i].startswith(">"):
                q.append(lines[i].lstrip("> ").rstrip()); i += 1
            out.append("<blockquote>" + "<br>".join(inline(x) for x in q) + "</blockquote>")
        elif ln.startswith("!["):  # รูปสถานที่: ![คำอธิบาย](picture:ชื่อไฟล์ในโฟลเดอร์ picture/)
            m = re.match(r'^!\[(.*?)\]\(picture:(.+)\)\s*$', ln)
            if m:
                src = "../picture/" + quote(m.group(2).strip())
                out.append(f'<figure class="pic"><img src="{src}" alt="{esc(m.group(1))}" loading="lazy"><figcaption>{esc(m.group(1))}</figcaption></figure>')
            else:
                out.append("<p>" + inline(ln) + "</p>")
            i += 1
        elif ln.strip() == "---":
            out.append("<hr>"); i += 1
        else:
            p = []
            while i < len(lines) and lines[i].strip() and not re.match(r'^(#|\||>|!\[|\s*[-*]\s|\s*\d+\.\s|---)', lines[i]):
                p.append(lines[i].strip()); i += 1
            out.append("<p>" + ("<br>" if dlg else " ").join(inline(x) for x in p) + "</p>")
    close_loc()
    return "\n".join(out)

def make(src, dlg):
    used, toc, chunks, tocbody, group = set(), [], [], "", None
    for f in sorted(glob.glob(os.path.join(src, "[0-9][0-9]-*.md"))):
        md = open(f, encoding="utf-8").read()
        g = re.match(r'<!--\s*group:\s*(.*?)\s*-->\s*', md)  # แฟ้มตัวละคร: หมวดเปลี่ยน -> แทรก h1 หมวด
        if g:
            md = md[g.end():]
            if g.group(1) != group:
                group = g.group(1); gid = slug(group, used); toc.append((1, group, gid))
                chunks.append(f'<h1 class="cat" id="{gid}">{inline(group)}</h1>')
        if dlg and os.path.basename(f).startswith("00-"):
            tocbody = render(md, used, toc, dlg, flat=True)  # 00-สารบัญ.md = สารบัญเขียนมือ (มีบรรยากาศ/รายชื่อคน)
        else:
            chunks.append(render(md, used, toc, dlg))
    side, grid, cat_open = [], [], False
    for lvl, text, hid in toc:
        if lvl == 1:
            if cat_open: grid.append("</div>")
            side.append(f'<div class="sc">{inline(text)}</div>')
            grid.append(f'<h3>{inline(text)}</h3><div class="cards">'); cat_open = True
        else:
            side.append(f'<a class="sl" href="#{hid}">{inline(text)}</a>')
            grid.append(f'<a class="card" href="#{hid}">{inline(text)}</a>')
    if cat_open: grid.append("</div>")
    return dict(used=used, side=side, grid=grid, tocbody=tocbody, chunks=chunks, n=sum(1 for t in toc if t[0] == 2))

CSS = """
:root{--bg:#faf8f4;--fg:#22201d;--mut:#6b655c;--card:#fff;--line:#e2dccf;--acc:#9a5b13;--acc2:#f3e7d3;--side:#f1ece2}
@media(prefers-color-scheme:dark){:root{--bg:#171512;--fg:#ece6da;--mut:#a39a8a;--card:#211e19;--line:#38332b;--acc:#e0a45c;--acc2:#2f2718;--side:#1d1a15}}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:12px}
body{margin:0;font:16px/1.65 "Sarabun","Noto Sans Thai","Tahoma",system-ui,sans-serif;background:var(--bg);color:var(--fg)}
aside{position:fixed;top:0;bottom:0;left:0;width:300px;background:var(--side);border-right:1px solid var(--line);overflow-y:auto;padding:12px}
main{margin-left:300px;padding:20px 28px 80px;max-width:1100px}
.sc{margin:14px 0 4px;font-weight:700;color:var(--acc);font-size:.9rem}
.sl{display:block;padding:3px 8px;border-radius:6px;color:var(--fg);text-decoration:none;font-size:.9rem}.sl:hover{background:var(--acc2)}
#q{width:100%;padding:9px 11px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg);font:inherit}
#cnt{color:var(--mut);font-size:.8rem;margin:4px 2px}
h1.cat{margin:38px 0 8px;padding-bottom:6px;border-bottom:2px solid var(--acc);color:var(--acc);font-size:1.6rem}
.loc{background:var(--card);border:1px solid var(--line);border-radius:12px;margin:14px 0;overflow:hidden}
.loc>h2{margin:0;padding:12px 16px;font-size:1.25rem;cursor:pointer;background:var(--acc2);display:flex;justify-content:space-between;gap:10px;align-items:center}
.loc>h2::before{content:"▾";margin-right:8px;color:var(--acc)}.loc.closed>h2::before{content:"▸"}
.up{font-size:.75rem;font-weight:400;color:var(--mut);text-decoration:none;margin-left:auto}
.body{padding:4px 18px 14px}.loc.closed .body{display:none}
h3{margin:20px 0 6px;font-size:1.05rem;color:var(--acc)}
.tw{overflow-x:auto;margin:8px 0}table{border-collapse:collapse;width:100%;font-size:.93rem}
th,td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}th{background:var(--acc2)}
blockquote{margin:10px 0;padding:8px 14px;border-left:4px solid var(--acc);background:var(--acc2);border-radius:0 8px 8px 0;font-style:italic}
code{background:var(--acc2);padding:1px 5px;border-radius:4px;font-size:.9em}
.pic{margin:10px 0}.pic img{display:block;width:100%;max-height:360px;object-fit:cover;border-radius:10px;border:1px solid var(--line)}.pic figcaption{color:var(--mut);font-size:.8rem;text-align:center;margin-top:4px}
ul,ol{margin:6px 0;padding-left:22px}li{margin:2px 0}
main a{color:var(--acc)}
.cards{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px}.card{padding:7px 12px;border:1px solid var(--line);border-radius:999px;background:var(--card);color:var(--fg);text-decoration:none;font-size:.9rem}.card:hover{background:var(--acc2);border-color:var(--acc)}
#toc h3{margin:14px 0 6px}#top{position:fixed;right:16px;bottom:16px;background:var(--acc);color:#fff;border-radius:999px;padding:8px 14px;text-decoration:none;font-size:.85rem;box-shadow:0 2px 8px #0004}
details{margin:6px 0}summary{cursor:pointer;padding:3px 8px}
.hide{display:none!important}
@media(max-width:860px){aside{position:static;width:auto;max-height:220px}main{margin-left:0;padding:14px}}
@media print{aside,#top,#q{display:none}main{margin:0;max-width:none}.loc.closed .body{display:block}.loc{break-inside:auto}}
"""
# บทพูด: คำพูดในกล่องไม่เอียง (ให้ท่าทาง *(…)* เป็นตัวเอียงสีจางแทน)
CSS_DLG = "blockquote{font-style:normal}em{color:var(--mut)}blockquote em{font-style:italic}"
JS = """
const q=document.getElementById('q'),cnt=document.getElementById('cnt');
q.addEventListener('input',()=>{const k=q.value.trim().toLowerCase();let n=0;
document.querySelectorAll('.loc').forEach(s=>{const hit=!k||s.textContent.toLowerCase().includes(k);s.classList.toggle('hide',!hit);
const a=document.querySelector('.sl[href="#'+s.id+'"]');if(a)a.classList.toggle('hide',!hit);if(hit&&k){s.classList.remove('closed');n++}});
cnt.textContent=k?('พบ '+n+' สถานที่'):''});
"""

# หน้าทั้ง 4: (คีย์, โฟลเดอร์, dlg?, ไฟล์ผลลัพธ์, ชื่อหน้า, ช่องค้นหา, css เสริม)
PAGES = [
    ("loc", BASE, False, "สถานที่ทั้งหมด.html", "ตารางกติกาสถานที่", "ค้นหา เช่น ดาบ, ราคา, ขโมย, ช่างตีเหล็ก", ""),
    ("places", os.path.join(ROOT, "places"), True, "สถานที่และบทบรรยาย.html", "สถานที่และบทบรรยาย", "ค้นหา เช่น ตลาด, ชา, ตะเกียง, เหตุการณ์สุ่ม", CSS_DLG),
    ("char", os.path.join(ROOT, "character"), True, "แฟ้มตัวละคร.html", "แฟ้มตัวละคร", "ค้นหา เช่น ราชา, ลับ, ตะเกียง, ป้าโมนา", CSS_DLG),
    ("dlg", os.path.join(ROOT, "dialog"), True, "เนื้อเรื่องหลัก.html", "เนื้อเรื่องหลัก", "ค้นหา เช่น ราชา, มาเรน, พิธี, ประตู", CSS_DLG),
]
OUT = {k: os.path.join(d, fn) for k, d, _, fn, *_ in PAGES}

def href(frm, to):  # ลิงก์สัมพัทธ์จากไฟล์ frm ไป to (percent-encode ไทย)
    return quote(os.path.relpath(OUT[to], os.path.dirname(OUT[frm])).replace(os.sep, "/"), safe="/.")

def page(key, title, head, toc_html, m, ph, css=""):
    menu = "".join(f'<a class="sl" href="{href(key, k)}">{n}</a>' for k, _, _, _, n, *_ in PAGES if k != key)
    return f"""<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — ม่านเวทีของจอมมาร</title><style>{CSS}{css}</style></head><body>
<aside><input id="q" type="search" placeholder="{ph}"><div id="cnt"></div><details><summary><strong>↔ สลับหน้า</strong></summary>{menu}</details>{''.join(m['side'])}</aside>
<main>{head}<div id="toc">{toc_html}</div>
{''.join(m['chunks'])}</main><a id="top" href="#toc">↑ สารบัญ</a><script>{JS}</script></body></html>"""

def relink(text, own, others):
    # #id ที่ไม่อยู่ในหน้านี้ -> ชี้ไปหน้าอื่นที่มี id นั้น (ตามลำดับ) · ไม่พบเลย -> เก็บไว้รายงาน
    miss = set()
    def r(m):
        i = m.group(1)
        if i in own or i == "toc": return m.group(0)
        for used, path in others:
            if i in used: return f'href="{path}#{i}"'
        miss.add(i); return m.group(0)
    return re.sub(r'href="#([^"\']+)"', r, text), miss

M = {k: make(d, dlg) for k, d, dlg, *_ in PAGES}
loc_head = ('<h1 style="margin-top:0">สารบัญสถานที่ — ม่านเวทีของจอมมาร</h1>'
            '<p style="color:var(--mut)">คู่มือ DM: ใครอยู่ที่ไหน ทำอะไรได้ ของและราคา บริการ ค่าความยาก และข้อมูลที่รู้ได้ '
            'กดชื่อสถานที่เพื่อข้ามไป · กดหัวข้อเพื่อพับ/กาง · ช่องค้นหาซ้ายมือกรองทุกสถานที่ · ลิงก์ 📖 พาไปคำบรรยายของสถานที่นั้น</p>')
allmiss = set()
for key, _, _, fn, name, ph, css in PAGES:
    m = M[key]
    if key == "loc": head, tocb = loc_head, '<h2 style="margin:8px 0">สารบัญ</h2>' + "".join(m['grid'])
    else: head, tocb = "", m['tocbody']
    txt = page(key, name, head, tocb, m, ph, css)
    txt, miss = relink(txt, m['used'], [(M[k]['used'], href(key, k)) for k in M if k != key])
    allmiss |= miss
    if "@@HEAD" in txt: print(f"⚠️ {name}: ยังมีหัวแฟ้มที่ยังไม่เติม (@@HEAD)")
    open(OUT[key], "w", encoding="utf-8").write(txt)
    print(f"สร้างแล้ว: {OUT[key]} | {name}: {m['n']} ส่วน | {len(txt) // 1024} KB")
if allmiss: print("⚠️ ลิงก์ที่ไม่พบปลายทางทุกหน้า:", sorted(allmiss))
