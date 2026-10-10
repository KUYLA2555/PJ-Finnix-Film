"""tools/format_css.py — จัดรูปแบบ CSS ที่ถูกบีบอัดเป็นบรรทัดเดียวให้อ่านได้ (หนึ่ง declaration ต่อบรรทัด)

ใช้:  python tools/format_css.py style.css journey.css           (เขียนทับ)
      python tools/format_css.py --check style.css               (ตรวจอย่างเดียว)

เปลี่ยนแค่ช่องว่างกับการขึ้นบรรทัดรอบ { } ; เท่านั้น — ก่อนเขียนจะเทียบกับต้นฉบับแบบตัดช่องว่างออก
ถ้าไม่ตรงกันแม้แต่ตัวเดียวจะไม่เขียนไฟล์ (กันการเปลี่ยนความหมายโดยไม่ตั้งใจ)
ไม่แตะเนื้อในวงเล็บ () กับสตริง เพราะ url(...;...) ของ Google Fonts มี ; อยู่ข้างใน
"""
import re, sys
from pathlib import Path

def tokens(css):
    """แยกเป็นชิ้น: '{' '}' ';' หรือข้อความ (comment / string / วงเล็บ อยู่ในข้อความก้อนเดียว)"""
    out, buf, i, depth = [], [], 0, 0
    while i < len(css):
        c = css[i]
        if css.startswith('/*', i):
            j = css.index('*/', i) + 2
            if buf and ''.join(buf).strip():
                out.append(''.join(buf)); buf = []
            out.append(css[i:j]); i = j; continue
        if c in '"\'':
            j = i + 1
            while css[j] != c:
                j += 2 if css[j] == '\\' else 1
            buf.append(css[i:j + 1]); i = j + 1; continue
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        if depth == 0 and c in '{};':
            out.append(''.join(buf)); buf = []; out.append(c)
        else:
            buf.append(c)
        i += 1
    if ''.join(buf).strip():
        out.append(''.join(buf))
    return out

def squash(s):
    return re.sub(r'\s+', ' ', s).strip()

def fmt(css):
    lines, level, decl = [], 0, ''
    pad = lambda: '  ' * level
    for t in tokens(css):
        if t.startswith('/*'):
            lines.append(pad() + t.strip()); continue
        if t == '{':
            sel = squash(decl); decl = ''
            # selector หลายตัว (a,b,c) ขึ้นบรรทัดละตัวถ้ายาว
            if len(sel) > 90 and not sel.startswith('@'):
                parts = [p.strip() for p in split_top(sel)]
                sel = (',\n' + pad()).join(parts)
            lines.append(pad() + sel + ' {'); level += 1
        elif t == ';':
            d = squash(decl); decl = ''
            if d:
                lines.append(pad() + d + ';')
        elif t == '}':
            d = squash(decl); decl = ''
            if d:
                lines.append(pad() + d + ';')
            level -= 1; lines.append(pad() + '}')
            if level == 0:
                lines.append('')
        else:
            decl += t
    if squash(decl):
        lines.append(squash(decl))
    return '\n'.join(lines).rstrip() + '\n'

def split_top(sel):
    """แยก selector ด้วย , ที่ไม่อยู่ในวงเล็บ เช่น :is(a,b) ต้องไม่ถูกแยก"""
    parts, buf, depth = [], '', 0
    for c in sel:
        depth += c == '('; depth -= c == ')'
        if c == ',' and depth == 0:
            parts.append(buf); buf = ''
        else:
            buf += c
    return parts + [buf]

def same(a, b):
    """เทียบแบบไม่สนช่องว่างรอบ { } ; , และ ; ตัวสุดท้ายก่อน } (ไม่มีผลต่อความหมาย)"""
    n = lambda s: re.sub(r';?\s*}', '}', re.sub(r'\s*([{};,])\s*', r'\1', squash(s)))
    return n(a) == n(b)

if __name__ == '__main__':
    check = '--check' in sys.argv
    files = [a for a in sys.argv[1:] if not a.startswith('--')]
    bad = 0
    for f in files:
        p = Path(f); src = p.read_text(encoding='utf-8'); out = fmt(src)
        ok = same(src, out)
        print(f'{f}: {len(src.splitlines())} → {len(out.splitlines())} บรรทัด · ความหมายเหมือนเดิม: {ok}')
        if not ok:
            bad += 1; continue
        if not check and out != src:
            p.write_text(out, encoding='utf-8', newline='\n')
    sys.exit(1 if bad else 0)
