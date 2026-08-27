#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync-shared.py — ทำให้ "ของร่วม" ของทั้ง 7 หน้าตรงกันเสมอ โดยไม่ขัดข้อ 9

ปัญหาที่แก้
  ข้อ 9 ของบรีฟบังคับว่าหนึ่งหน้าต้องจบในไฟล์เดียว CSS/JS จึงแยกออกไปเป็นไฟล์ร่วมไม่ได้
  ผลคือของร่วม (tokens · nav · drawer · footer · noscript) ถูกคัดลอกไว้ 7 ชุด
  แก้ทีหนึ่งต้องแก้ 7 จุด และที่ผ่านมามันไถลออกจากกันเรื่อยๆ จนต้องไล่ตามแก้ทุกเวอร์ชัน

วิธีแก้
  เก็บฉบับจริงไว้ที่ tools/shared/<REGION>.txt ที่เดียว
  ในไฟล์หน้าเว็บคร่อมบริเวณนั้นด้วยเครื่องหมาย @shared / @end
  แล้วให้สคริปต์นี้คัดลอกฉบับจริงลงไปให้ครบทุกไฟล์

  **ไฟล์ที่ขึ้นเซิร์ฟเวอร์ยังเป็นไฟล์เดียวจบต่อหนึ่งหน้าเหมือนเดิมทุกประการ**
  ข้อ 9 กำหนดรูปแบบของผลลัพธ์ ไม่ได้ห้ามมีขั้นตอนประกอบ
  และถ้าลบเครื่องมือนี้ทิ้ง เว็บก็ยังทำงานได้เหมือนเดิม เพราะเนื้อหาอยู่ในไฟล์จริงอยู่แล้ว

วิธีใช้ (รันจาก root ของ repo)
  python tools/sync-shared.py            ตรวจอย่างเดียว ไม่แก้ไฟล์ — ต่างเมื่อไหร่ exit 1
  python tools/sync-shared.py --write    เขียนฉบับจริงลงทุกไฟล์
  python tools/sync-shared.py --pull index.html   ดึงเนื้อหาจากไฟล์นั้นขึ้นเป็นฉบับจริง

ลำดับการทำงานที่ตั้งใจ
  แก้ของร่วม -> แก้ที่ไฟล์ไหนก็ได้หนึ่งไฟล์ -> --pull ไฟล์นั้น -> --write -> ตรวจ
  หรือแก้ที่ tools/shared/ ตรงๆ แล้ว --write

หมายเหตุเรื่อง line ending
  ไฟล์หน้าเว็บใน working tree เป็น CRLF ส่วน tools/shared/ เก็บเป็น LF
  สคริปต์แปลงให้ตอนอ่าน/เขียน **ห้ามแปลงซ้ำสองรอบ** จะได้ CR CR LF แล้ว git
  จะมองไฟล์เป็น w/-text (ดูหัวข้อ line ending ใน CLAUDE.md)
"""
import io, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED = os.path.join(ROOT, 'tools', 'shared')
PAGES = ['about.html', 'centers.html', 'contact.html', 'faq.html', 'gallery.html', 'index.html',
         'technology.html']

# ชื่อบริเวณ -> (เป็น CSS หรือ HTML, คำอธิบายสั้นๆ)
# CSS ใช้เครื่องหมาย /* */ ส่วน HTML/JS ใช้ <!-- -->
REGIONS = [
    ('TOKENS',      'css',  ':root tokens — สี ระยะ ฟอนต์ easing'),
    ('NAV_CSS',     'css',  'แถบ nav ลอย'),
    ('DRAWER_CSS',  'css',  'เมนูมือถือ'),
    ('FOOTER_CSS',  'css',  'footer'),
    ('NOSCRIPT',    'html', 'บล็อกสำรองเมื่อ JS ไม่ทำงาน'),
    ('NAV_HTML',    'html', 'markup ของ nav'),
    ('DRAWER_HTML', 'html', 'markup ของเมนูมือถือ'),
    ('FOOTER_HTML', 'html', 'markup ของ footer'),
    ('JS_NAV',      'js',   'JS ของ nav กับ drawer'),
]
KIND = {n: k for n, k, _ in REGIONS}


def marks(name):
    """คู่เครื่องหมายเปิด-ปิดของบริเวณนั้น"""
    if KIND[name] == 'css':
        return '/* @shared:%s */' % name, '/* @end:%s */' % name
    return '<!-- @shared:%s -->' % name, '<!-- @end:%s -->' % name


def read(path):
    return io.open(path, encoding='utf-8', newline='').read()


def write(path, text):
    io.open(path, 'w', encoding='utf-8', newline='').write(text)


def nl_of(text):
    return '\r\n' if '\r\n' in text else '\n'


def canon(name, page, nl):
    """ฉบับจริงของบริเวณนั้น ปรับ line ending และใส่ aria-current ให้ตรงหน้า"""
    raw = read(os.path.join(SHARED, name + '.txt')).replace('\r\n', '\n').rstrip('\n')
    key = page[:-5]                                   # about.html -> about
    raw = raw.replace('@CUR:%s@' % key, ' aria-current="page"')
    raw = re.sub(r'@CUR:[a-z]+@', '', raw)            # หน้าอื่นไม่ต้องมี
    return raw.replace('\n', nl)


def extract(text, name):
    """เนื้อหาระหว่างเครื่องหมาย — คืน None ถ้าไฟล์นั้นยังไม่ได้คร่อมไว้"""
    a, b = marks(name)
    if a not in text or b not in text:
        return None
    i = text.index(a) + len(a)
    j = text.index(b, i)
    return text[i:j].strip('\r\n')


def replace(text, name, body, nl):
    a, b = marks(name)
    i = text.index(a) + len(a)
    j = text.index(b, i)
    return text[:i] + nl + body + nl + text[j:]


def cmd_check():
    bad = 0
    missing = 0
    for page in PAGES:
        s = read(os.path.join(ROOT, page))
        nl = nl_of(s)
        for name, _, _ in REGIONS:
            got = extract(s, name)
            if got is None:
                print('  %-16s %-12s ยังไม่ได้คร่อมเครื่องหมาย' % (page, name))
                missing += 1
                continue
            want = canon(name, page, nl)
            if got.replace('\r\n', '\n') != want.replace('\r\n', '\n'):
                print('  %-16s %-12s *** ไม่ตรงกับฉบับจริง' % (page, name))
                bad += 1
    total = len(PAGES) * len(REGIONS)
    print('ตรวจ %d บริเวณ (%d ไฟล์ x %d บริเวณ) | ไม่ตรง %d | ยังไม่คร่อม %d'
          % (total, len(PAGES), len(REGIONS), bad, missing))
    return 1 if (bad or missing) else 0


def cmd_write():
    changed = 0
    for page in PAGES:
        p = os.path.join(ROOT, page)
        s = read(p)
        nl = nl_of(s)
        before = s
        for name, _, _ in REGIONS:
            if extract(s, name) is None:
                print('  ข้าม %s / %s (ยังไม่ได้คร่อมเครื่องหมาย)' % (page, name))
                continue
            s = replace(s, name, canon(name, page, nl), nl)
        if s != before:
            write(p, s)
            changed += 1
            print('  เขียน %s' % page)
    print('เขียนไป %d ไฟล์' % changed)
    # กัน CR CR LF ที่เคยเกิดใน v3.2
    for page in PAGES:
        b = open(os.path.join(ROOT, page), 'rb').read()
        lone = sum(1 for i, c in enumerate(b) if c == 13 and b[i + 1:i + 2] != b'\n')
        if lone:
            print('  *** %s มี CR เดี่ยว %d จุด' % (page, lone))
            return 1
    return 0


def cmd_pull(src):
    """ดึงเนื้อหาในไฟล์ที่ระบุขึ้นเป็นฉบับจริง (ใส่ @CUR@ กลับให้อัตโนมัติ)"""
    s = read(os.path.join(ROOT, src))
    key = src[:-5]
    for name, _, _ in REGIONS:
        got = extract(s, name)
        if got is None:
            print('  ข้าม %s (ไม่มีในไฟล์นี้)' % name)
            continue
        body = got.replace('\r\n', '\n')
        if name in ('NAV_HTML', 'DRAWER_HTML') and '@CUR' not in body:
            # ใส่ token กลับให้ลิงก์ที่ชี้ไปหน้าอื่นทุกอัน รวมปุ่ม CTA ที่ชี้ centers.html
            # เว้นเฉพาะลิงก์โลโก้ (class="brand") ซึ่งชี้ index.html แต่ไม่ใช่ลิงก์เมนู
            body = body.replace(' aria-current="page"', '')

            def tok(m):
                head, page = m.group(0), m.group(1)
                if 'class="brand"' in head:
                    return head
                return head + '@CUR:%s@' % page

            body = re.sub(r'<a href="([a-z]+)\.html"(?:\s+class="[^"]*")?', tok, body)
        write(os.path.join(SHARED, name + '.txt'), body + '\n')
        print('  ดึง %-12s จาก %s (%d ตัวอักษร)' % (name, src, len(body)))
    return 0


def main():
    os.chdir(ROOT)
    args = sys.argv[1:]
    if not args:
        sys.exit(cmd_check())
    if args[0] == '--write':
        sys.exit(cmd_write())
    if args[0] == '--pull' and len(args) > 1:
        sys.exit(cmd_pull(args[1]))
    print(__doc__)
    sys.exit(2)


if __name__ == '__main__':
    main()
