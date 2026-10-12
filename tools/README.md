# tools/ — เครื่องมือของโปรเจกต์ (v6.3)

| ไฟล์ | ทำอะไร |
|---|---|
| `build.py` | **ตัวสร้างของเว็บ** — `content.js` · หน้ารุ่น 5 หน้า · บล็อกร่วมทุกหน้า (`@assets` `@header` `@footer` `@next`) · บล็อกจากข้อมูล (`@gen:…`) · แปลงลิงก์ `href="/…"` `src="/…"` ทั้งหน้าเป็น relative (v8.6 · `relativize`) · อ่าน docstring หัวไฟล์ |
| `format_css.py` | จัดรูปแบบ CSS ที่ถูกบีบอัดเป็นบรรทัดเดียวให้อ่านได้ — เทียบความหมายกับต้นฉบับก่อนเขียนทุกครั้ง ไม่ตรงไม่เขียน (ใช้ครั้งแรกกับ `style.css` `journey.css` ใน v6.3) |

ไฟล์ที่ `build.py` สร้างเป็น static ล้วน ลบโฟลเดอร์นี้ทิ้งเว็บก็ยังทำงานเหมือนเดิม แค่แก้ข้อมูลต่อไม่สะดวก

```bash
export PYTHONIOENCODING=utf-8
python tools/build.py --check                  # ตรวจอย่างเดียว · ต้องได้ "ต่าง 0 ไฟล์"
python tools/format_css.py --check style.css   # ตรวจอย่างเดียว
```

`python tools/build.py` (ไม่มี `--check`) เขียนไฟล์ — **จงใจไม่ใส่ในบล็อกข้างบน** เพราะบล็อก ```bash มักถูกคัดลอกไปรันรวดเดียว

## แก้อะไร แล้วทำอะไร

| แก้อะไร | ที่ไหน |
|---|---|
| ตัวเลข · ราคา · ร้าน · ผลงาน | `data/films.json` · `dealers.json` · `gallery.json` แล้ว build |
| เบอร์โทร · LINE · ข้อมูลบริษัท | `SITE` บนสุดของ `build.py` |
| เมนูบน · ลิงก์ท้ายเว็บ | `NAV` · `HOME_FOOT` |
| ไฟล์ CSS / JS ที่ทุกหน้าโหลด | `ASSETS` |
| ภาพการ์ดซีรีส์ที่ `/films.html` | `SERIES_PHOTO` |
| ยืนยันการแนะนำซีรีส์ตามความต้องการ | `NEED_MAPPING_CONFIRMED` · ลำดับการแนะนำอยู่ที่ `need_rank` |
| หน้ารุ่น `films/<id>.html` | เทมเพลต `series_page()` — **ห้ามแก้ไฟล์ HTML ของหน้ารุ่นตรง ๆ** จะถูกเขียนทับ |
| header / footer | `header_block()` · `footer_block()` (= `home_footer_block()` ทุกหน้า) |
| บล็อก `@gen:ชื่อ` | ฟังก์ชัน `gen_ชื่อ()` — รายชื่อทั้งหมดอยู่ที่ `GEN` |
| เพิ่มหน้าใหม่ | คัดลอกหน้าที่มีอยู่ (มีเครื่องหมาย `@assets` `@header` `@footer` ครบ) แล้ว build |

คู่มือภาษาไทยแบบทีละขั้นสำหรับคนที่ไม่ใช่ dev อยู่ที่ `docs/HOW-TO-EDIT.md`

## ของเก่า

`sync-shared.py` + `shared/` ของเว็บเก่า (v3.3–v5.7) ย้ายไป `C:\Claude\top secret\Finnix\tools\` แล้ว (v6.2) พร้อม README ฉบับเดิมที่มีชุดสคริปต์ตรวจของเว็บเก่าทั้งหมด
