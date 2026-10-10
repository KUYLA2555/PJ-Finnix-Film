"""tools/build.py — ตัวสร้างของเว็บ FINNIX FILM (v6.x)

รันจาก root ของโปรเจกต์:
    python tools/build.py           เขียนไฟล์
    python tools/build.py --check   ตรวจอย่างเดียว ไม่เขียน (ถ้ามีไฟล์ที่ยังไม่ตรง exit 1)

สคริปต์นี้ทำ 4 อย่าง:
  1. content.js              ← data/films.json + dealers.json (ข้อมูลที่ app.js ใช้ตอนรัน)
  2. films/<id>.html ×5       ← data/films.json (หน้ารุ่นสร้างทั้งไฟล์ — ห้ามแก้ HTML ของหน้ารุ่นตรง ๆ)
  3. บล็อกที่ใช้ซ้ำทุกหน้า    ← ใส่ระหว่างเครื่องหมายในหน้า HTML
        <!-- @assets -->  … <!-- @end assets -->    ลิงก์ CSS / JS ใน <head>
        <!-- @header -->  … <!-- @end header -->    แถบเมนูบน (ใส่ aria-current ให้เองตาม URL)
        <!-- @footer -->  … <!-- @end footer -->    footer + ปุ่มติดต่อลอย
  4. บล็อกที่สร้างจากข้อมูล   ← <!-- @gen:ชื่อ --> … <!-- @end gen:ชื่อ -->  (ดูรายชื่อที่ GEN ท้ายไฟล์)

ทุกอย่างระหว่างเครื่องหมายถูกเขียนทับทุกครั้งที่ build — แก้ที่ไฟล์นี้ ไม่ใช่ในหน้า
ไฟล์ผลลัพธ์เป็น static ล้วน ลบโฟลเดอร์ tools/ ทิ้งเว็บก็ยังทำงานเหมือนเดิม
"""
import html
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK = '--check' in sys.argv


# ============================================================================
#  ค่าที่แก้บ่อย — แก้ตรงนี้แล้วรัน python tools/build.py
#  ค่าที่ยังไม่มีให้ใส่ None — หน้าเว็บจะขึ้นเป็น {{ชื่อตัวแปร}} ให้เห็นว่ายังรอข้อมูล ห้ามเดา
# ============================================================================
SITE = {
    'company': 'บริษัท ฟินนิกซ์ ฟิล์ม จำกัด',
    'copyright_year': 2026,
    'hotline': '0635978497',              # ใช้ใน tel: (ตัวเลขล้วน)
    'hotline_display': '06-3597-8497',    # ใช้แสดงบนหน้า
    'line_url': None,                     # เช่น 'https://lin.ee/xxxx' — ใส่แล้วปุ่มลอยกลายเป็นปุ่ม LINE เอง
    'line_id': None,                      # {{LINE_OA_ID}}
    'facebook_url': None,                 # {{FACEBOOK_URL}}
    'instagram_url': None,                # {{INSTAGRAM_URL}}
    'address': None,                      # {{COMPANY_ADDRESS}}
    'email': None,                        # {{COMPANY_EMAIL}}
    'office_hours': None,                 # {{OFFICE_HOURS}}
    'reg_no': None,                       # {{COMPANY_REG_NO}}
}

# เมนูบน — (URL, ชื่อที่แสดง) · ปุ่ม "หาร้านใกล้คุณ" อยู่แยกทางขวาเสมอ
NAV = [
    ('/', 'หน้าแรก'),
    ('/films.html', 'ฟิล์ม'),           # ฟิล์มทุกซีรีส์ + ราคา (v8.0) · v8.3 เปลี่ยนชื่อเมนูจาก "ราคา"
    ('/works.html', 'ผลงาน'),           # v8.3 ย้ายมาแทนตำแหน่ง "เทคโนโลยี"
    ('/experience.html', 'ลองของจริง'),
    ('/about.html', 'เกี่ยวกับเรา'),     # v8.3 หน้าเทคโนโลยีเดิม เปลี่ยนเป็นหน้าเกี่ยวกับเรา
]

# ท้ายเว็บ (v7.1 · โครงตามรูปตัวอย่าง messageImage_1791443930138.jpg) — v8.1 ใช้แบบเดียวกันทุกหน้า (เดิมหน้าอื่นใช้ FOOT แถบลิงก์สีอ่อน)
# คอลัมน์ "บริการและการติดต่อ" กับไอคอน Facebook / LINE / โทร สร้างจาก SITE ใน home_footer_block()
HOME_FOOT = [
    ('รู้จัก FINNIX', [('/about.html', 'เกี่ยวกับเรา'), ('/works.html', 'ผลงานที่ติดตั้ง')]),   # v8.4 ลบ /faq.html
    ('ผลิตภัณฑ์', [('/films.html', 'ฟิล์มรถยนต์ทุกซีรีส์'), ('/films.html#price', 'ราคา'), ('/experience.html', 'ลองของจริง')]),
]
HOME_FOOT_LOGO = '/assets/logo-finnix-white.png'   # ครอบจาก LOGO FINNIX-01.png (ตัวอักษรขาว · นกและ FILM แดง) — ต้นฉบับอยู่ในคลัง top secret/Finnix/ไฟล์ต้นฉบับ/

# แถบ "ตอนต่อไป" ท้ายหน้าย่อย (v7.7 · <!-- @next -->) — หน้า → (ปลายทาง, ข้อความชวน) · 'series' = หน้ารุ่นทั้ง 5
# ปลายทางต้องมีชื่ออยู่ใน CHAPTERS (อังกฤษ, ไทย) — ตัวเดียวกับป้ายบนหัวของหน้านั้น
NEXT = {
    '/films.html': ('/experience.html', 'ลองสัมผัสของจริงก่อนตัดสินใจ'),   # v8.1 /try.html ลบแล้ว
    '/about.html': ('/experience.html', 'รู้จักฟิล์ม ผ่านการลองจริง'),   # v8.3 ข้อความจากไฟล์ต้นแบบ about
    '/experience.html': ('/dealers.html?experience=1', 'หาร้านที่มีจุดทดลองใกล้คุณ'),
    '/dealers.html': ('/works.html', 'ดูผลงานที่ติดตั้ง'),
    '/works.html': ('/dealers.html', 'หาร้านใกล้คุณ'),
    'series': ('/experience.html', 'ลองสัมผัสของจริงก่อนตัดสินใจ'),
}
CHAPTERS = {
    '/films.html': ('FIND YOUR FILM', 'ฟิล์มทุกซีรีส์'),
    '/about.html': ('ABOUT US', 'เกี่ยวกับเรา'),
    '/experience.html': ('TRY IT YOURSELF', 'ลองของจริง'),
    '/dealers.html': ('FIND FINNIX', 'หาร้านใกล้คุณ'),
    '/works.html': ('OUR WORK', 'ผลงานที่ติดตั้ง'),
}

# v8.4 meta ความปลอดภัยทุกหน้า (ใส่ใน @assets ก่อน CSS/JS)
#   CSP — สคริปต์ได้เฉพาะไฟล์ของเว็บเอง (ไม่มี <script> inline) · ฟอนต์ Google Fonts · iframe แผนที่ Google เท่านั้น
#         style-src ต้องมี 'unsafe-inline' เพราะมี style="" ในหน้า (ตำแหน่งภาพ ฯลฯ) · เพิ่มบริการภายนอกใหม่ต้องเพิ่มที่นี่ ไม่งั้นถูกบล็อก
#   robots noindex — ไม่ให้ Google เก็บเข้าระบบค้นหา ระหว่างที่ร้าน/ผลงานยังเป็นข้อมูลสมมติ · **เอาออกตอนขึ้นเว็บจริง**
HEAD_META = [
    '<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; script-src \'self\'; style-src \'self\' \'unsafe-inline\' https://fonts.googleapis.com; font-src \'self\' https://fonts.gstatic.com; img-src \'self\' data:; frame-src https://maps.google.com https://www.google.com; connect-src \'self\'; object-src \'none\'; base-uri \'self\'; form-action \'self\'">',
    '<meta name="referrer" content="strict-origin-when-cross-origin">',
    '<meta name="robots" content="noindex, nofollow">',
]

# ไฟล์ CSS / JS ที่ทุกหน้าโหลด (ลำดับมีผล — style → journey → merge)
ASSETS = [
    '<link rel="stylesheet" href="/style.css">',
    '<link rel="stylesheet" href="/journey.css">',
    '<link rel="stylesheet" href="/merge.css">',
    '<script src="/content.js" defer></script>',
    '<script src="/app.js" defer></script>',
]

# ซีรีส์ที่โชว์ที่ /films.html เมื่อไม่ได้เลือกความต้องการ + การ์ดซีรีส์เด่นในส่วน 05 ของหน้าแรก (@gen:featured)
HERO_FILM = 'ceramic'

# /films.html การ์ดซีรีส์ (v8.0 ตามไฟล์ต้นแบบ C:/Claude/films.html) — ภาพประกอบบรรยากาศ ไม่ใช่สีฟิล์มจริง · (ภาพ, object-position)
# sedan.jpg มาจากไฟล์ต้นแบบนั้น (ผู้สั่งงานอนุมัติ 10 ต.ค. 2569) · ได้ภาพจริงรายซีรีส์เมื่อไรเปลี่ยนที่นี่ที่เดียว
SERIES_PHOTO = {
    'titanium': ('/assets/sedan.jpg', '72% center'),
    'ceramic': ('/assets/car.jpg', '80% center'),
    'crystalize': ('/assets/sedan.jpg', '100% center'),
    'extra-clear': ('/assets/glass.jpg', '70% center'),
    'uv-guard': ('/assets/hero.jpg', '30% center'),     # ต้นแบบใช้ glass.png ซ้ำกับใบ 04 — เปลี่ยนให้ 5 ใบไม่ซ้ำกัน
}

# ความต้องการ → ซีรีส์ ยังเป็นร่างที่คำนวณจากตัวเลข (ดู need_rank ข้างล่าง)
# บริษัทยืนยันแล้วเปลี่ยนเป็น True — ข้อความ "ยังรอบริษัทยืนยัน" บนหน้าเว็บจะหายไป
NEED_MAPPING_CONFIRMED = False
NEEDS = [('heat', 'กันร้อน'), ('clarity', 'มองชัด'), ('privacy', 'เป็นส่วนตัว'), ('balance', 'สมดุล')]

# โลโก้ — logo-finnix-web.png คือโลโก้บริษัท (817x96 พื้นใส) · โลโก้ซีรีส์ครอบจาก finnix-*.png (ต้นฉบับอยู่ในคลัง) ให้ชิดตัวอักษร
LOGO_SERIES = '/assets/series/logo-{id}.png'
COVER = {'SY': 'cover-SY.jpg', 'CM': 'cover-CM.jpg', 'CT': 'cover-CT.jpg', 'XT': 'cover-XT.jpg', 'SM': 'cover-SM.jpg'}
TECH_TH = {'ceramic': 'เซรามิก ไม่มีชั้นโลหะ', 'metalize-sputtering': 'เคลือบโลหะหลายชั้น (sputtering)'}
SPEC_FIELDS = [
    ('heatReject', 'ลดความร้อนจากแสงแดด<span class="nb">โดยรวม</span>'),
    ('vlt', 'แสงส่องผ่าน'),
    ('darkness', 'ความเข้ม'),
    ('reflect', 'สะท้อนแสง'),
    ('uv', 'ป้องกันรังสี UV'),
    ('ir', 'ป้องกันรังสี IR'),
]


# ============================================================================
#  ตัวช่วย
# ============================================================================
e = html.escape
changed = []


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def write(path, text):
    """เขียนเฉพาะไฟล์ที่เนื้อหาเปลี่ยน · โหมด --check แค่จดว่าไฟล์ไหนจะเปลี่ยน"""
    full = ROOT / path
    old = full.read_text(encoding='utf-8') if full.exists() else None
    if old == text:
        return
    changed.append(path)
    if not CHECK:
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(text, encoding='utf-8', newline='\n')


def var(text):
    """ห่อ {{VAR}} ด้วย <span class="var"> ให้เห็นชัดบนหน้าว่ายังรอข้อมูล"""
    return re.sub(r'(\{\{[A-Z_0-9]+\}\})', r'<span class="var">\1</span>', text)


def value_or_var(value, var_name):
    return e(value) if value else f'<span class="var">{{{{{var_name}}}}}</span>'


def rng(values, unit='%'):
    """ช่วงค่า เช่น 81–96% (ข้ามค่า None)"""
    values = [v for v in values if v is not None]
    lo, hi = min(values), max(values)
    return f'{lo:g}{unit}' if lo == hi else f'{lo:g}–{hi:g}{unit}'


def png_size(url):
    data = (ROOT / url.lstrip('/')).read_bytes()[16:24]
    return struct.unpack('>II', data)


def series_logo(series_id, name, lazy=True):
    """<img> โลโก้ซีรีส์ พร้อม width/height จริง (กัน layout กระโดดตอนโหลด)"""
    url = LOGO_SERIES.format(id=series_id)
    w, h = png_size(url)
    lazy_attr = ' loading="lazy"' if lazy else ''
    return f'<img src="{url}" alt="{e(name)}" width="{w}" height="{h}"{lazy_attr}>'


def company_logo(alt='FINNIX FILM หน้าแรก'):
    return f'<img src="/assets/logo-finnix-web.png" alt="{alt}" width="817" height="96">'


def indent(block, prefix):
    return '\n'.join(prefix + line if line else line for line in block.split('\n'))


# ============================================================================
#  ข้อมูล
# ============================================================================
films = load('data/films.json')
dealers = load('data/dealers.json')
gallery = load('data/gallery.json')
meta = films['meta']
SERIES = films['series']


def tech_label(s):
    return TECH_TH.get(s['tech'], s['tech'])


def series_summary(s):
    v = s['variants']
    return {
        'id': s['id'],
        'code': s['codePrefix'],
        'name': s['name']['en'],
        'th': s['name']['th'],
        'tag': s['tagline'],
        'tech': tech_label(s),
        'metalFree': s['metalFree'],
        'heat': rng([x['heatReject'] for x in v]),
        'heatMin': min(x['heatReject'] for x in v),
        'heatMax': max(x['heatReject'] for x in v),
        'vlt': rng([x['vlt'] for x in v]),
        'vltMax': max(x['vlt'] for x in v),
        'uv': rng([x['uv'] for x in v]),
        'variants': [{'code': x['code'], 'darkness': x['darkness'], 'heat': x['heatReject'], 'vlt': x['vlt']} for x in v],
        'price': s.get('price'),
        'logo': LOGO_SERIES.format(id=s['id']),
    }


summary = [series_summary(s) for s in SERIES]
by_id = {s['id']: s for s in summary}


# ความต้องการ → ซีรีส์ (ร่าง · คำนวณจากตัวเลขใน films.json · รอ {{NEED_TO_FILM_MAPPING}})
#   heat    = ซีรีส์ที่ลดความร้อนสูงสุด
#   clarity = ซีรีส์ที่แสงส่องผ่านสูงสุด
#   privacy = ซีรีส์ที่รหัสเข้มสุด (VLT ต่ำสุด) ยังลดความร้อนได้มากที่สุด
#   balance = ซีรีส์เซรามิกไม่มีโลหะที่ราคาเริ่มต้นต่ำสุด
def ranked(key):
    return [s['id'] for s in sorted(summary, key=key, reverse=True)]


def privacy_key(s):
    darkest = min(s['variants'], key=lambda x: x['vlt'])
    return (-darkest['vlt'], darkest['heat'])


priced_ceramic = [s for s in summary if s['price'] and s['metalFree']]
need_rank = {
    'heat': ranked(lambda s: s['heatMax']),
    'clarity': ranked(lambda s: s['vltMax']),
    'privacy': ranked(privacy_key),
    'balance': [s['id'] for s in sorted(priced_ceramic, key=lambda s: s['price']['sedan']['full'])]
               + [s['id'] for s in summary if s not in priced_ceramic],
}
need_to_film = {need: ids[0] for need, ids in need_rank.items()}
need_alternatives = {need: ids[1:3] for need, ids in need_rank.items()}


# ============================================================================
#  1. content.js
# ============================================================================
content = {
    'carTypes': meta['carTypes'],
    'series': summary,
    'dealers': [
        # v8.4 ร้านสมมติ (placeholder) ไม่ส่งเบอร์ออกไป — เบอร์ 081000000x ใน dealers.json กดโทรได้จริง จะโทรไปหาคนอื่น
        {k: (None if k == 'phone' and d.get('placeholder') else d.get(k))
         for k in ('id', 'name', 'tier', 'address', 'province', 'phone', 'lat', 'lng', 'hours', 'placeholder')}
        for d in dealers['dealers']
    ],
}
journey = {
    'heroFilm': HERO_FILM,
    'needToFilm': need_to_film,
    'needAlternatives': need_alternatives,
    'needMappingConfirmed': NEED_MAPPING_CONFIRMED,
}
write('content.js',
      '/* สร้างโดย tools/build.py จาก data/*.json — ห้ามแก้ไฟล์นี้ตรง ๆ แก้ที่ data/ หรือ build.py แล้วรัน python tools/build.py */\n'
      'window.FINNIX = ' + json.dumps(content, ensure_ascii=False, indent=1) + ';\n'
      'window.FINNIX_JOURNEY = ' + json.dumps(journey, ensure_ascii=False, indent=1) + ';\n')


# ============================================================================
#  2. หน้ารุ่น films/<id>.html — สร้างทั้งไฟล์
# ============================================================================
def spec_table(variants):
    """ตารางสเปก — ปุ่มเลือกรหัสไฮไลต์คอลัมน์ได้ (app.js ส่วนที่ 11) · แถวลดความร้อนตัวใหญ่ (v8.2 ตามต้นแบบ ceramic.html)"""
    head = ''.join(f'<th scope="col">{e(v["code"])}</th>' for v in variants)
    rows = []
    for key, label in SPEC_FIELDS:
        values = [v[key] for v in variants]
        if all(x is None for x in values):
            continue
        cls = ' class="heat"' if key == 'heatReject' else ''
        cells = ''.join(f'<td>{"—" if x is None else f"{x:g}%"}</td>' for x in values)
        rows.append(f'      <tr{cls}><th scope="row">{label}</th>{cells}</tr>')
    return ('<div class="table-wrap" tabindex="0" role="region" aria-label="ตารางสเปก — เลื่อนแนวนอนได้บนมือถือ">\n'
            '  <table class="spec-table sp-table" id="spec-table">\n'
            f'    <thead><tr><th scope="col">ค่า</th>{head}</tr></thead>\n'
            '    <tbody>\n' + '\n'.join(rows) + '\n    </tbody>\n'
            '  </table>\n'
            '</div>')


def shade_opacity(vlt):
    """ความทึบของชั้นสีเข้มบนภาพจำลอง — ช่วงเดียวกับไฟล์ต้นแบบ ceramic.html (แสงผ่าน 5% ≈ .82 · 15% ≈ .63 · 30% ≈ .35)"""
    return min(.9, max(.05, .91 - .019 * vlt))


def shade_picker(variants):
    """ปุ่มเลือกรหัส (v8.2 แทนบันไดความเข้ม v7.8) — ภาพเดียวกัน + ชั้นสีเข้มตามค่าแสงส่องผ่าน · กดแล้วไฮไลต์คอลัมน์ในตาราง
    ภาพจำลองความทึบ ไม่ใช่สีจริงของฟิล์ม (ป้ายบอกอยู่ใต้ปุ่ม)"""
    if any(v['vlt'] is None for v in variants):
        return '<!-- ปุ่มเลือกรหัส: บางรหัสไม่มีค่าแสงส่องผ่าน จึงไม่แสดง -->'
    buttons = '\n'.join(
        f'  <button type="button" class="sp-shade" data-col="{i}" aria-pressed="false" aria-label="เลือกรหัส {e(v["code"])} แสงผ่าน {v["vlt"]:g}%">'
        f'<span class="sp-shade-scene" style="--shade:{shade_opacity(v["vlt"]):.2f}"><img src="/assets/glass.jpg" alt="" loading="lazy">'
        f'<span class="sp-shade-mark" aria-hidden="true">✓</span></span>'
        f'<b>{e(v["code"])}</b><small>แสงผ่าน {v["vlt"]:g}%</small></button>'
        for i, v in enumerate(variants, 1))
    return f'<div class="sp-shades" role="group" aria-label="เลือกรหัสเพื่อไฮไลต์ในตาราง">\n{buttons}\n</div>'


def price_section(s):
    """หน้ารุ่น — ราคา (v8.2 ตามต้นแบบ ceramic.html): กล่องคำนวณพื้นมืดซ้าย + ตารางราคาเต็มขวา
    กล่องคำนวณต้องใช้ JS → ใส่ hidden แล้ว app.js ส่วนที่ 11 เปิด (ไม่มี JS เห็นแค่ตาราง)"""
    year = meta['priceYear']
    if not s.get('price'):
        return ('<section class="sp-price" id="price">\n'
                '  <div class="sp-inner">\n'
                '    <div class="eyebrow"><span></span> PRICE</div>\n'
                '    <h2>ราคา</h2>\n'
                '    <p class="note">โบรชัวร์ของซีรีส์นี้ไม่มีตารางราคา สอบถามได้ที่ร้านติดตั้ง</p>\n'
                '    <a class="pill" href="/dealers.html">หาร้านใกล้คุณ</a>\n'
                '  </div>\n'
                '</section>')
    name = e(s['name']['en'])
    rows = '\n'.join(
        f'          <tr data-car="{k}"><th scope="row">{e(meta["carTypes"][k])}</th><td>{p["front"]:,}</td><td>{p["full"]:,}</td></tr>'
        for k, p in s['price'].items())
    default_car = 'sedan' if 'sedan' in s['price'] else next(iter(s['price']))
    options = ''.join(
        f'<option value="{k}"{" selected" if k == default_car else ""}>{e(meta["carTypes"][k])}</option>' for k in s['price'])
    amount = f'{s["price"][default_car]["full"]:,}'
    return (f'<section class="sp-price" id="price">\n'
            f'  <div class="sp-inner">\n'
            f'    <div class="sp-price-head">\n'
            f'      <div>\n'
            f'        <div class="eyebrow"><span></span> PRICE {year}</div>\n'
            f'        <h2>ราคาตามเอกสารผลิตภัณฑ์</h2>\n'
            f'      </div>\n'
            f'      <p>ราคาจากโบรชัวร์ปี {year} · ราคาจริงยืนยันที่ร้าน</p>\n'
            f'    </div>\n'
            f'    <div class="sp-price-layout">\n'
            f'      <div class="sp-estimate" data-name="{name}" hidden>\n'
            f'        <div class="eyebrow">{name} · ราคาตามเอกสารปี {year}</div>\n'
            f'        <label for="sp-car">ประเภทรถ</label>\n'
            f'        <select id="sp-car">{options}</select>\n'
            f'        <fieldset>\n'
            f'          <legend>ตำแหน่งกระจก</legend>\n'
            f'          <div class="sp-positions">'
            f'<label><input type="radio" name="sp-position" value="front">บานหน้า</label>'
            f'<label><input type="radio" name="sp-position" value="full" checked>รอบคัน</label></div>\n'
            f'        </fieldset>\n'
            f'        <div class="sp-result" aria-live="polite">\n'
            f'          <small>ราคาตามเอกสารปี {year}</small>\n'
            f'          <p class="sp-amount"><strong id="sp-amount">{amount}</strong> <span>บาท</span></p>\n'
            f'          <p class="sp-caption" id="sp-caption">{e(meta["carTypes"][default_car])} · รอบคัน · {name}</p>\n'
            f'          <a class="pill" href="/dealers.html">หาร้านใกล้คุณ</a>\n'
            f'        </div>\n'
            f'      </div>\n'
            f'      <div class="table-wrap" tabindex="0" role="region" aria-label="ตารางราคา — เลื่อนแนวนอนได้บนมือถือ">\n'
            f'        <table class="spec-table sp-price-table" id="sp-price-table">\n'
            f'          <thead><tr><th scope="col">ประเภทรถ</th><th scope="col">บานหน้า (บาท)</th><th scope="col">รอบคัน (บาท)</th></tr></thead>\n'
            f'          <tbody>\n{rows}\n          </tbody>\n'
            f'        </table>\n'
            f'      </div>\n'
            f'    </div>\n'
            f'  </div>\n'
            f'</section>')


def series_page(s, number):
    """หน้ารุ่น (v8.2 ดีไซน์ตามไฟล์ต้นแบบ C:/Claude/ceramic.html · เนื้อหาเดิมทั้งหมดจาก films.json)
    ภาพใหญ่พื้นมืด → แถบลิงก์ในหน้า → ภาพรวม (โลโก้ ปกโบรชัวร์ ค่าหลัก 6 ช่อง) → ความเข้มและสเปก → ราคา → ทางเลือกอื่น"""
    sm = by_id[s['id']]
    variants = sorted(s['variants'], key=lambda x: x['vlt'])
    metal_head, metal_note = {
        True: ('ไม่มีชั้นโลหะ', 'ไม่รบกวนสัญญาณ 5G · GPS · บัตรทางด่วน'),
        False: ('มีชั้นโลหะ', 'แจ้งช่างก่อนถ้าเรื่องสัญญาณสำคัญกับคุณ'),
        None: ('ยังไม่ระบุ', 'เอกสารยังไม่ระบุว่ามีชั้นโลหะหรือไม่'),
    }[s['metalFree']]
    claim = f'\n      <p class="sp-hero-claim">{e(s["claim"])}</p>' if s.get('claim') else ''
    others = sorted((x for x in summary if x['id'] != s['id']), key=lambda x: abs(x['heatMax'] - sm['heatMax']))[:2]
    # ภาพการ์ดทางเลือก — ใช้ SERIES_PHOTO ของซีรีส์นั้น แต่ถ้าซ้ำกับภาพที่ใช้ในหน้านี้แล้ว (ภาพใหญ่ / การ์ดก่อนหน้า) เลือกภาพอื่นแทน
    used = {SERIES_PHOTO[s['id']][0]}
    alt_photos = []
    for a in others:
        photo_src, photo_pos = SERIES_PHOTO[a['id']]
        if photo_src in used:
            photo_src = next(p for p in ('/assets/glass.jpg', '/assets/hero.jpg', '/assets/car.jpg', '/assets/sedan.jpg') if p not in used)
            photo_pos = 'center'
        used.add(photo_src)
        alt_photos.append((photo_src, photo_pos))
    alternatives = '\n'.join(
        f'      <a class="sp-alt" href="/films/{a["id"]}.html">\n'
        f'        <span class="sp-alt-photo"><img src="{src}" style="object-position:{pos}" alt="" loading="lazy"><span>ภาพประกอบบรรยากาศ</span></span>\n'
        f'        <span class="sp-alt-copy"><span><strong>{e(a["name"])}</strong><small>ลดความร้อน {a["heat"]} · แสงส่องผ่าน {a["vlt"]}</small></span><i aria-hidden="true">↗</i></span>\n'
        f'      </a>' for a, (src, pos) in zip(others, alt_photos))
    name_en, name_th = s['name']['en'], s['name']['th']
    codes = ' · '.join(e(v['code']) for v in variants)
    photo, pos = SERIES_PHOTO[s['id']]

    return f'''<!-- JOB: CONSIDER | USER FEELS: รุ่นนี้เหมาะกับเราไหม | NEXT: /experience.html
     สร้างโดย tools/build.py จาก data/films.json — ห้ามแก้ไฟล์นี้ตรง ๆ แก้ที่ series_page() ใน build.py
     v8.2 ดีไซน์ตามไฟล์ต้นแบบ C:/Claude/ceramic.html (เนื้อหาเดิม) · CSS หมวด 7 ของ merge.css · JS ส่วนที่ 11 ของ app.js -->
<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{e(name_en)} | FINNIX FILM</title>
  <meta name="description" content="{e(name_th)} — {e(s["tagline"])}">
  <!-- @assets --><!-- @end assets -->
</head>
<body class="inner-page series-page">
<a class="skip" href="#main">ข้ามไปเนื้อหา</a>
<!-- @header --><!-- @end header -->

<main id="main">

  <nav class="sp-crumb" aria-label="เส้นทางหน้าเว็บ"><a href="/">หน้าแรก</a><span aria-hidden="true">/</span><a href="/films.html">ฟิล์มทุกซีรีส์</a><span aria-hidden="true">/</span><span aria-current="page">{e(name_en)}</span></nav>

  <!-- ภาพใหญ่พื้นมืด — ภาพประกอบจาก SERIES_PHOTO ใน build.py (ไม่ใช่ผลงานติดตั้งจริง) -->
  <section class="sp-hero" id="film-hero">
    <img class="sp-hero-photo" src="{photo}" style="object-position:{pos}" alt="" fetchpriority="high">
    <div class="sp-hero-copy">
      <div class="eyebrow">{number:02d} <span></span> {e(s["codePrefix"])} SERIES · FINNIX FILM</div>
      <h1>{e(name_en)}</h1>
      <p class="sp-hero-th">{e(name_th)}</p>
      <span class="red-line" aria-hidden="true"></span>
      <h2>{e(s["tagline"])}</h2>{claim}
      <div class="sp-hero-actions">
        <a class="pill sp-white" href="#price">ดูราคา</a>
        <a class="pill light" href="#spec">ดูค่าสเปก</a>
      </div>
    </div>
    <span class="sp-hero-note">ภาพประกอบบรรยากาศ</span>
  </section>

  <nav class="sp-nav" aria-label="เนื้อหาในหน้านี้">
    <span class="sp-nav-title">{e(name_en)}</span>
    <span class="sp-nav-links"><a href="#overview">รู้จักซีรีส์</a><a href="#spec">ความเข้มและสเปก</a><a href="#price">ราคา</a><a href="/experience.html">ลองของจริง</a></span>
  </nav>

  <!-- ภาพรวม — โลโก้ + ปกโบรชัวร์ซ้าย · ค่าหลัก 6 ช่องขวา (ช่วงค่าจาก films.json) -->
  <section class="sp-overview" id="overview">
    <div class="sp-overview-brand">
      <div class="eyebrow"><span></span> {e(s["codePrefix"])} SERIES · {len(variants)} รหัสความเข้ม</div>
      <p class="sp-logo">{series_logo(s["id"], name_en)}</p>
      <p class="sp-codes">{codes}</p>
      <figure class="cover">
        <img src="/assets/Brochure/{COVER[s["codePrefix"]]}" alt="ปกโบรชัวร์ {e(name_th)}" loading="lazy" width="880" height="1245">
        <figcaption>ปกโบรชัวร์ต้นฉบับของบริษัท</figcaption>
      </figure>
    </div>
    <dl class="sp-facts">
      <div><dt>เทคโนโลยี</dt><dd>{var(e(tech_label(s)))}</dd></div>
      <div><dt>ชั้นโลหะ</dt><dd>{metal_head}<small>{metal_note}</small></dd></div>
      <div><dt>ลดความร้อน</dt><dd class="num">{sm["heat"]}</dd></div>
      <div><dt>แสงส่องผ่าน</dt><dd class="num">{sm["vlt"]}</dd></div>
      <div><dt>กัน UV</dt><dd class="num">{sm["uv"]}</dd></div>
      <div><dt>รับประกัน</dt><dd class="num">{meta["warrantyYears"]} <small>ปี</small></dd></div>
    </dl>
  </section>

  <!-- ความเข้มและสเปก — ปุ่มเลือกรหัสไฮไลต์คอลัมน์ในตาราง (app.js ส่วนที่ 11) -->
  <section class="sp-spec" id="spec">
    <div class="sp-spec-intro">
      <div class="eyebrow"><span></span> SPEC · {len(variants)} รหัสความเข้ม</div>
      <h2>ค่าสเปกทั้ง {len(variants)} รหัส</h2>
      <p class="note">ภาพจำลองความทึบจากค่าแสงส่องผ่าน ไม่ใช่สีจริงของฟิล์ม · กดรหัสเพื่อดูในตาราง</p>
      <p class="sp-selection" id="sp-selection" aria-live="polite" hidden><strong id="sp-selected-code"></strong><span id="sp-selected-light"></span></p>
    </div>
{indent(shade_picker(variants), "    ")}
    <div class="sp-spec-table">
{indent(spec_table(variants), "      ")}
      <p class="sp-source">ถอดจากโบรชัวร์ของบริษัทปี {meta["dataYear"]} · ทุกค่าต้องอ่านคู่กับมาตรฐานที่ใช้วัด ซึ่งยังรอ <span class="var">{{{{TEST_STANDARD}}}}</span></p>
    </div>
  </section>

{indent(price_section(s), "  ")}

  <section class="sp-alts">
    <div class="sp-alts-head">
      <h2>ทางเลือกอื่นที่อยาก<span class="nb">ให้ลอง</span></h2>
      <a class="sp-text-link" href="/films.html">ดูฟิล์มทุกซีรีส์</a>
    </div>
    <div class="sp-alt-grid">
{alternatives}
    </div>
  </section>

  <!-- @next --><!-- @end next -->

</main>

<!-- @footer --><!-- @end footer -->
</body>
</html>
'''


# ============================================================================
#  3. บล็อกที่ใช้ซ้ำทุกหน้า
# ============================================================================
def assets_block(url):
    return '\n'.join(HEAD_META + ASSETS)


def header_block(url):
    def current(href):
        here = url == href.split('#')[0]   # v8.0 /films.html#price ไฮไลต์ที่ /films.html
        return ' aria-current="page"' if here else ''
    links = '\n'.join(f'    <a href="{href}"{current(href)}>{label}</a>' for href, label in NAV)
    # ปุ่ม "หาร้านใกล้คุณ" ทางขวาถูกซ่อนบนมือถือ → ใส่ซ้ำในเมนูพับ (.nav-extra โชว์เฉพาะ ≤1050)
    links += f'\n    <a class="nav-extra" href="/dealers.html"{current("/dealers.html")}>หาร้านใกล้คุณ</a>'
    return (f'<header>\n'
            f'  <a href="/" class="logo">{company_logo()}</a>\n'
            f'  <nav id="nav" aria-label="เมนูหลัก">\n{links}\n  </nav>\n'
            f'  <a class="pill nav-dealer" href="/dealers.html"{current("/dealers.html")}>หาร้านใกล้คุณ</a>\n'
            f'  <button id="menu" aria-label="เปิดเมนู" aria-controls="nav" aria-expanded="false"><span></span><span></span></button>\n'
            f'</header>')


ICONS = {
    'facebook': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.5 21v-7.5H16l.4-3h-2.9V8.6c0-.9.3-1.5 1.5-1.5h1.5V4.4c-.3 0-1.2-.1-2.2-.1-2.2 0-3.7 1.3-3.7 3.8v2.4H8.1v3h2.5V21z"/></svg>',
    'line': ('<svg class="ico-line" viewBox="0 0 24 24" aria-hidden="true">'
             '<path d="M12 2.5C6.2 2.5 1.5 6.3 1.5 11c0 4.2 3.7 7.7 8.8 8.4.3.1.8.2.9.6.1.3.1.8 0 1.1l-.1.9c0 .3-.2 1 .9.6 1.1-.5 6.1-3.6 8.3-6.2 1.5-1.7 2.3-3.4 2.3-5.4 0-4.7-4.7-8.5-10.5-8.5z"/>'
             '<text x="12" y="13.3" text-anchor="middle">LINE</text></svg>'),
    'phone': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15 15 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1z"/></svg>',
}


def foot_icon(name, label, href, var_name=None):
    """ไอคอนช่องทางติดต่อ — มีลิงก์เป็น <a> · ยังไม่มีเป็น <span> จาง ๆ กดไม่ได้ (ไม่ใช่ปุ่มที่กดแล้วไม่ทำอะไร)"""
    if href:
        external = ' target="_blank" rel="noopener noreferrer"' if href.startswith('http') else ''
        return f'<a class="foot-icon" href="{e(href)}" aria-label="{label}"{external}>{ICONS[name]}</a>'
    return f'<span class="foot-icon is-pending" role="img" aria-label="{label} — ยังไม่มีลิงก์" title="{label} · รอ {{{{{var_name}}}}}">{ICONS[name]}</span>'


def home_footer_block():
    """ท้ายเว็บ — 4 คอลัมน์ + แถวล่าง (v7.1 หน้าแรก · v8.1 ทุกหน้า) · ไม่มีปุ่มโทรลอย · พื้นดำมาจาก .home-footer ใน merge.css"""
    tel = f'tel:{SITE["hotline"]}'
    icons = ''.join([
        foot_icon('facebook', 'Facebook', SITE['facebook_url'], 'FACEBOOK_URL'),
        foot_icon('line', 'LINE', SITE['line_url'], 'LINE_OA_ID'),
        foot_icon('phone', f'โทร {SITE["hotline_display"]}', tel),
    ])
    cols = ''.join(
        f'  <nav aria-label="{title}">\n    <h2>{title}</h2>\n'
        + ''.join(f'    <a href="{href}">{label}</a>\n' for href, label in links)
        + '  </nav>\n'
        for title, links in HOME_FOOT)
    # LINE ในคอลัมน์ติดต่อ (v7.2 แทนที่ Hotline) — มีลิงก์เป็น <a> · ยังไม่มีเป็น <span> จาง กดไม่ได้
    if SITE['line_url']:
        line_link = (f'<a class="foot-line" href="{e(SITE["line_url"])}" target="_blank" rel="noopener noreferrer">'
                     f'{ICONS["line"]}LINE FINNIX</a>')
    else:
        line_link = (f'<span class="foot-line is-pending" title="LINE · รอ {{{{LINE_OA_ID}}}}">'
                     f'{ICONS["line"]}LINE FINNIX <small>(เร็ว ๆ นี้)</small></span>')
    w, h = png_size(HOME_FOOT_LOGO)
    return (f'<footer class="home-footer">\n'
            f'<div class="home-footer-grid">\n'
            f'  <div class="home-footer-brand">\n'
            f'    <a class="home-footer-logo" href="/"><img src="{HOME_FOOT_LOGO}" alt="FINNIX FILM หน้าแรก" width="{w}" height="{h}" loading="lazy"></a>\n'
            f'    <p>ฟิล์มกรองแสงสำหรับรถยนต์<br>ความสบายที่อยู่กับคุณในทุกการเดินทาง</p>\n'
            f'    <p class="home-footer-company">{SITE["company"]}</p>\n'
            f'    <div class="home-footer-social">{icons}</div>\n'
            f'  </div>\n'
            f'{cols}'
            f'  <div class="home-footer-contact">\n'
            f'    <h2>บริการและการติดต่อ</h2>\n'
            f'    <a href="/dealers.html">ค้นหาร้าน FINNIX</a>\n'
            f'    <a href="/dealers.html#contact">ติดต่อสำนักงานใหญ่</a>\n'
            f'    {line_link}\n'
            f'    <p>ให้ร้านช่วยแนะนำรุ่นและเฉด<br>ที่เหมาะกับรถของคุณ</p>\n'
            f'  </div>\n'
            f'</div>\n'
            f'<div class="home-footer-bottom">\n'
            f'  <span>© {SITE["copyright_year"]} {SITE["company"]}</span>\n'
            f'  <span>BEAUTIFULLY REAL.</span>\n'
            f'  <span>CLEARER PEOPLE. BRIGHTER TOMORROW.</span>\n'
            f'</div>\n'
            f'</footer>')


def footer_block(url):
    """v8.1 ทุกหน้าใช้ท้ายเว็บแบบหน้าแรก (4 คอลัมน์ พื้นดำ) · ไม่มีปุ่มลอยโทร Hotline แล้ว (ผู้สั่งงานสั่งเอาออกทุกหน้า)
    เบอร์โทร / LINE / Facebook กดได้จากไอคอนในท้ายเว็บ"""
    return home_footer_block()


def next_block(url):
    """แถบ "ตอนต่อไป" ท้ายหน้าย่อย (v7.7) — ค่าอยู่ที่ NEXT / CHAPTERS"""
    href, text = NEXT['series' if url.startswith('/films/') else url]
    en, th = CHAPTERS[href.split('?')[0].split('#')[0]]
    return (f'<nav class="next-chapter dark" aria-label="ตอนต่อไป">\n'
            f'  <a href="{href}">\n'
            f'    <span class="eyebrow">NEXT <span></span> {e(en)} <em class="eyebrow-th">{th}</em></span>\n'
            f'    <strong><span>{e(text)}</span></strong>\n'
            f'    <i aria-hidden="true">→</i>\n'
            f'  </a>\n'
            f'</nav>')


# ============================================================================
#  4. บล็อกที่สร้างจากข้อมูล — ใส่ <!-- @gen:ชื่อ --><!-- @end gen:ชื่อ --> ในหน้าไหนก็ได้
# ============================================================================
# gen_facts / gen_needs — v6.4 ถอดออกจากหน้าแรกแล้ว (ต้นแบบไม่มี) · ยังไม่มีหน้าที่ใช้ เก็บไว้ย้ายไปใส่หน้าอื่น
def gen_facts():
    """ตัวเลขเด่น 4 ช่อง (เดิมอยู่หน้าแรก)"""
    top = max(summary, key=lambda x: x['heatMax'])
    uv_min = min(v['uv'] for s in SERIES for v in s['variants'])
    metal_free = [x for x in summary if x['metalFree'] is True]
    facts = [
        (f'{meta["warrantyYears"]}<small>ปี</small>', 'รับประกันทุกซีรีส์', 'ระยะเท่ากันทุกรุ่น ไม่ลดหลั่นตามราคา'),
        (f'{top["heatMax"]}<small>%</small>', 'ลดความร้อนสูงสุด', f'รหัสเข้มสุดของ {e(top["name"])}'),
        (f'{uv_min}<small>%</small>', 'กันยูวีอย่างต่ำ', 'ทุกรหัสในทุกซีรีส์ ไม่มีข้อยกเว้น'),
        (f'{len(metal_free)}<small>ซีรีส์</small>', 'ไม่มีชั้นโลหะ', ' · '.join(e(x['name']) for x in metal_free)),
    ]
    items = '\n'.join(f'  <div class="fact"><b>{num}</b><h3>{title}</h3><p>{text}</p></div>' for num, title, text in facts)
    return f'<div class="facts-grid">\n{items}\n</div>'


def gen_needs():
    """กล่องเลือกตามความต้องการ 4 กล่อง พร้อมซีรีส์ที่แนะนำ (เดิมอยู่หน้าแรก)"""
    tiles = []
    for key, label in NEEDS:
        s = by_id[need_to_film[key]]
        tiles.append(f'  <a class="need quiz-choice" href="/films.html?need={key}">\n'
                     f'    <span class="need-copy"><strong>{label}</strong><small>แนะนำ<br><span class="nb">{e(s["name"])} →</span></small></span>\n'
                     f'  </a>')
    return '<div class="need-track">\n' + '\n'.join(tiles) + '\n</div>'


def gen_need_links():
    """/films.html — ปุ่มความต้องการ 4 ปุ่ม เข้าระบบแนะนำ ?need= (v7.6 · ชื่อจาก NEEDS · v7.9 ถอดจากหน้าแรก · v8.0 ลูกศรแยก span ชิดขวา)"""
    return ('<div class="need-links-row">\n'
            + '\n'.join(f'  <a class="pill" href="/films.html?need={key}">{label} <span aria-hidden="true">→</span></a>' for key, label in NEEDS)
            + '\n</div>')


def gen_featured():
    """หน้าแรก ส่วน 05 — ซีรีส์เด่น (HERO_FILM) ในการ์ดภาพรถ · v7.9 แทน "CERAMIC PLUS" ของต้นแบบ ซึ่งไม่มีในโบรชัวร์"""
    s = by_id[HERO_FILM]
    return (f'<p class="product-name">FINNIX<br><strong>{e(s["name"])}</strong></p>\n'
            f'<p>{e(s["th"])} · {e(s["tag"])}</p>\n'
            f'<a class="pill filled" href="/films/{s["id"]}.html">สำรวจ {e(s["name"])}</a>\n'
            f'<a class="text-button" href="/films.html">ดูฟิล์มทุกรุ่น</a>')


def gen_series_cards():
    """/films.html — การ์ดซีรีส์ 5 ใบ (v8.0 ตามไฟล์ต้นแบบ) · ภาพ + เลข + ชื่อ · แถวบน 3 ใบ แถวล่าง 2 ใบ
    v8.5 ไม่มีหน้าต่างคั่นแล้ว — กดภาพ/ชื่อไปหน้ารุ่นทันที · ค่าหลักขึ้นบนการ์ด · ปุ่ม "ดูสเปก" / "ดูราคา" ไปส่วนนั้นของหน้ารุ่นตรง ๆ"""
    cards = []
    for i, x in enumerate(summary, 1):
        src, pos = SERIES_PHOTO[x['id']]
        if x['price']:
            price = f'บานหน้าเริ่มต้น <b>{min(p["front"] for p in x["price"].values()):,}</b> บาท'
        else:
            price = 'ยังไม่มีราคาในเอกสาร'
        cards.append(
            f'  <article class="series-card" data-id="{x["id"]}">\n'
            f'    <a class="card-button" href="/films/{x["id"]}.html">\n'
            f'      <span class="card-photo"><img src="{src}" style="object-position:{pos}" alt="" loading="lazy"><span class="card-number">{i:02d}</span></span>\n'
            f'      <span class="card-line"><span><strong>{e(x["name"])}</strong><small>{e(x["th"])}</small></span></span>\n'
            f'    </a>\n'
            f'    <p class="card-facts"><span class="nb">ลดความร้อน <b>{x["heat"]}</b></span> · <span class="nb">แสงส่องผ่าน <b>{x["vlt"]}</b></span><br>{price}</p>\n'
            f'    <p class="card-links"><a class="pill" href="/films/{x["id"]}.html#spec">ดูสเปก <span aria-hidden="true">→</span></a>'
            f'<a class="pill" href="/films/{x["id"]}.html#price">ดูราคา <span aria-hidden="true">→</span></a></p>\n'
            f'  </article>')
    return '<div class="series-grid">\n' + '\n'.join(cards) + '\n</div>'


def gen_hq():
    """/dealers.html — ข้อมูลสำนักงานใหญ่ (ค่ามาจาก SITE ด้านบน) · v8.3 Hotline ตัวใหญ่ตามต้นแบบ dealers.html แล้วตามด้วยรายการเดิม"""
    rows = [
        ('ที่อยู่', value_or_var(SITE['address'], 'COMPANY_ADDRESS')),
        ('อีเมล', value_or_var(SITE['email'], 'COMPANY_EMAIL')),
        ('เวลาทำการ', value_or_var(SITE['office_hours'], 'OFFICE_HOURS')),
        ('LINE', value_or_var(SITE['line_id'], 'LINE_OA_ID')),
        ('Facebook', value_or_var(SITE['facebook_url'], 'FACEBOOK_URL')),
        ('Instagram', value_or_var(SITE['instagram_url'], 'INSTAGRAM_URL')),
        ('เลขทะเบียนนิติบุคคล', value_or_var(SITE['reg_no'], 'COMPANY_REG_NO')),
    ]
    items = '\n'.join(f'  <dt>{k}</dt><dd>{v}</dd>' for k, v in rows)
    return (f'<div class="dl-hotline">\n'
            f'  <small>HEAD OFFICE / HOTLINE</small>\n'
            f'  <a href="tel:{SITE["hotline"]}">{SITE["hotline_display"]} <span aria-hidden="true">↗</span></a>\n'
            f'</div>\n'
            f'<dl>\n{items}\n</dl>')


def gen_company():
    """/about.html — ข้อมูลบริษัท 3 แถว (v8.3 ตามต้นแบบ about) · ชื่อบริษัทกับเบอร์มาจาก SITE"""
    return ('<dl class="ab-details">\n'
            f'  <div><dt>บริษัท</dt><dd>{SITE["company"]}</dd></div>\n'
            '  <div><dt>ผลิตภัณฑ์</dt><dd>ฟิล์มกรองแสงและฟิล์มใสกันรอยรถยนต์</dd></div>\n'
            f'  <div><dt>สำนักงานใหญ่</dt><dd><a class="ab-phone" href="tel:{SITE["hotline"]}">{SITE["hotline_display"]}</a></dd></div>\n'
            '</dl>')


ID_BY_NAME = {x['name']: x['id'] for x in summary}   # v8.5 การ์ดผลงานลิงก์ไปหน้ารุ่นของฟิล์มที่ใช้
WORK_COUNT = {x['name']: sum(1 for item in gallery['items'] if item['series'] == x['name']) for x in summary}
WORK_PHOTO_ICON = ('<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="3" y="5" width="26" height="22" rx="2"/>'
                   '<circle cx="11" cy="12" r="2.5"/><path d="m4 23 7-6 5 4 5-8 8 10"/></svg>')


def gen_works_meta():
    """/works.html — ตัวเลขใต้หัวหน้า (v8.2 ตามต้นแบบ works.html) · นับจาก gallery.json"""
    series = sum(1 for n in WORK_COUNT.values() if n)
    return (f'<p class="works-meta"><span><b>{len(gallery["items"])}</b> รายการตัวอย่าง</span>'
            f'<span><b>{series:02d}</b> ซีรีส์ฟิล์ม</span></p>')


def gen_gallery():
    """/works.html — ปุ่มกรอง + การ์ดผลงาน (data/gallery.json) · v8.2 ดีไซน์ตามไฟล์ต้นแบบ C:/Claude/works.html
    ช่องภาพเป็นกรอบ "รอภาพผลงานจริง" (หน้านี้ห้ามใช้ภาพ AI) · ปุ่มแสดงเพิ่มใช้ JS → hidden แล้ว app.js ส่วนที่ 8 เปิด
    v8.5 ปุ่ม "ดูรายละเอียด" (หน้าต่างที่ข้อมูลซ้ำกับการ์ด) → ลิงก์ "ดูฟิล์ม <ซีรีส์> →" ไปหน้ารุ่นตรง ๆ"""
    total = len(gallery['items'])
    # v7.7 จำนวนคันต่อซีรีส์บนปุ่ม (ซีรีส์ที่ยังไม่มีผลงานไม่ขึ้นปุ่ม — กดแล้วจะว่างเปล่า)
    chips = [f'  <button class="work-filter" data-filter="all" aria-pressed="true">ทั้งหมด <small>{total}</small></button>']
    chips += [f'  <button class="work-filter" data-filter="{e(x["name"])}" aria-pressed="false">{e(x["name"])} <small>{WORK_COUNT[x["name"]]}</small></button>'
              for x in summary if WORK_COUNT[x['name']]]
    # เรียงสลับซีรีส์ (รอบละคันต่อซีรีส์ ตามต้นแบบ) — แสดงทีละ 6 คันจะได้เห็นหลายซีรีส์ตั้งแต่แรก · ข้อมูลใน gallery.json ไม่เปลี่ยน
    queues = [[item for item in gallery['items'] if item['series'] == x['name']] for x in summary]
    ordered = [q[r] for r in range(max(map(len, queues))) for q in queues if r < len(q)]
    ordered += [item for item in gallery['items'] if item not in ordered]   # ซีรีส์สะกดไม่ตรง films.json ก็ยังขึ้น
    cards = []
    for i, item in enumerate(ordered, 1):
        roof = ' class="roof"'
        specs = ''.join(
            f'<div{roof if f["position"] == "หลังคาแก้ว" else ""}><dt>{e(f["position"])}</dt><dd>{e(f["code"])}</dd></div>'
            for f in item['fit'])
        cards.append(f'  <article class="work-card" data-series="{e(item["series"])}">\n'
                     f'    <div class="work-photo"><div class="work-placeholder">{WORK_PHOTO_ICON}<p>รอภาพผลงานจริง</p><small>FINNIX FILM</small></div>'
                     f'<span class="work-index">{i:02d}</span><span class="work-photo-label">ภาพผลงานกำลังอัปเดต</span></div>\n'
                     f'    <div class="work-content">\n'
                     f'      <p class="work-series">{e(item["series"])}</p>\n'
                     f'      <h3>{e(item["car"])}</h3>\n'
                     f'      <dl class="work-spec">{specs}</dl>\n'
                     f'      <div class="work-bottom"><small>รายการตัวอย่าง</small>'
                     f'<a class="work-film-link" href="/films/{ID_BY_NAME.get(item["series"], "")}.html">ดูฟิล์ม {e(item["series"])} <span aria-hidden="true">→</span></a></div>\n'
                     f'    </div>\n'
                     f'  </article>')
    return ('<div class="works-toolbar">\n'
            '  <h2>เลือกดูตามซีรีส์</h2>\n'
            f'  <p class="works-count" id="work-count" role="status">{total} รายการตัวอย่าง</p>\n'
            '</div>\n'
            '<div class="works-filters" role="group" aria-label="กรองผลงานตามซีรีส์">\n' + '\n'.join(chips) + '\n</div>\n'
            '<div class="work-grid" id="work-grid">\n' + '\n'.join(cards) + '\n</div>\n'
            '<div class="works-more">\n'
            '  <button type="button" class="pill" id="work-more" hidden>ดูตัวอย่างเพิ่มเติม <span aria-hidden="true">+</span></button>\n'
            '  <p id="work-shown" aria-live="polite"></p>\n'
            '</div>')


GEN = {
    'facts': gen_facts,
    'needs': gen_needs,
    'need-links': gen_need_links,
    'featured': gen_featured,
    'series-cards': gen_series_cards,
    'hq': gen_hq,
    'gallery': gen_gallery,
    'works-meta': gen_works_meta,
    'company': gen_company,
}
SHARED = {'assets': assets_block, 'header': header_block, 'footer': footer_block}


def fill(src, name, block):
    """แทนเนื้อหาระหว่าง <!-- @name --> กับ <!-- @end name --> โดยย่อหน้าตามบรรทัดของเครื่องหมายเปิด"""
    pattern = re.compile(rf'^([ \t]*)<!-- @{re.escape(name)} -->.*?<!-- @end {re.escape(name)} -->', re.S | re.M)

    def replace(m):
        pad = m.group(1)
        return f'{pad}<!-- @{name} -->\n{indent(block, pad)}\n{pad}<!-- @end {name} -->'
    return pattern.subn(replace, src)


# ============================================================================
#  เขียนทุกหน้า
# ============================================================================
# v7.4 หน้าละไฟล์ชื่อตามหน้า: index.html (หน้าแรก) · <หน้า>.html ที่ root · films/<id>.html (หน้ารุ่น สร้างทั้งไฟล์)
pages = set(ROOT.glob('*.html')) | set((ROOT / 'films').glob('*.html'))
pages |= {ROOT / 'films' / f'{s["id"]}.html' for s in SERIES}
problems = []
for page in sorted(pages):
    rel = page.relative_to(ROOT).as_posix()
    url = '/' if rel == 'index.html' else '/' + rel
    if rel.startswith('films/'):
        series_id = rel[len('films/'):-len('.html')]
        number = [s['id'] for s in SERIES].index(series_id) + 1
        src = series_page(next(s for s in SERIES if s['id'] == series_id), number)
    else:
        src = page.read_text(encoding='utf-8')
    for name, make in SHARED.items():
        src, count = fill(src, name, make(url))
        if count != 1:
            problems.append(f'{rel}: เครื่องหมาย @{name} มี {count} คู่ (ต้องมี 1)')
    if url in NEXT or url.startswith('/films/'):
        src, count = fill(src, 'next', next_block(url))
        if count != 1:
            problems.append(f'{rel}: เครื่องหมาย @next มี {count} คู่ (ต้องมี 1)')
    elif '<!-- @next -->' in src:
        problems.append(f'{rel}: มีเครื่องหมาย @next แต่ไม่มีหน้านี้ใน NEXT ของ build.py')
    for name, make in GEN.items():
        src, _ = fill(src, f'gen:{name}', make())
    write(rel, src)

print(f'หน้า {len(pages)} · ซีรีส์ {len(SERIES)} · ร้าน {len(dealers["dealers"])} · ผลงาน {len(gallery["items"])} · '
      f'need→film {need_to_film} | {"ต่าง" if CHECK else "เขียน"} {len(changed)} ไฟล์')
for path in changed:
    print('  ', path)
for p in problems:
    print('***', p)
if problems or (CHECK and changed):
    sys.exit(1)
