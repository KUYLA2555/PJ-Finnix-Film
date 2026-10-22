# FINNIX FILM — เว็บไซต์

เว็บไซต์ของ **บริษัท ฟินนิกซ์ ฟิล์ม จำกัด** (ฟิล์มกรองแสงรถยนต์) — static site ล้วน ไม่มี package manager
**v6.x (ตั้งแต่ 3 ต.ค. 2569)** โครงและดีไซน์ตามต้นแบบ `C:\Claude\FINNIX-Website` · เว็บฉบับเก่า (v5.7) เก็บไว้ที่ `C:\Claude\top secret\Finnix\`

**เว็บ:** https://kuyla2555.github.io/PJ-Finnix-Film/ (GitHub Pages · push เข้า `main` แล้วเว็บอัปเดตเองภายในราว 1 นาที)

> **ยังเป็นเว็บทดลอง** — ตัวเลขทุกตัวยังรอ `{{TEST_STANDARD}}` · ร้านตัวแทนกับรายการผลงานเป็นข้อมูลสมมติ · หลายช่องยังเป็นภาพชั่วคราว · ปิดการเก็บเข้า Google ไว้ (`noindex`)
> รายการที่ต้องปิดก่อนเปิดตัวจริงอยู่ท้าย `docs/CHANGELOG.md`

## เปิดดู

```powershell
python -m http.server 8000     # แล้วเปิด http://localhost:8000/
```

**เปิดผ่าน HTTP** — เปิดไฟล์ตรง ๆ ด้วย `file://` ไม่รองรับ · ลิงก์ทั้งเว็บเป็นแบบ relative (v8.6) จึงทำงานได้ทั้งที่ root ของโดเมนและใต้ path ย่อยอย่าง `/PJ-Finnix-Film/`

## โครงสร้าง

```
PJ_Finnix_Film/
├── index.html              หน้าแรก
├── films.html  about.html  dealers.html  works.html
│                           หน้าละไฟล์ ชื่อตามหน้า (v7.4) · films/<ซีรีส์>.html อีก 6 หน้าสร้างอัตโนมัติ
├── style.css  journey.css  สไตล์จากต้นแบบ
├── merge.css               คอมโพเนนต์ที่เพิ่มเอง
├── app.js                  JS ทั้งเว็บ
├── content.js              ข้อมูลที่ app.js ใช้ — สร้างอัตโนมัติ ห้ามแก้มือ
├── data/                   films.json · dealers.json · gallery.json — source of truth
├── tools/build.py          ตัวสร้าง content.js · หน้ารุ่น · header/footer
├── assets/                 รูปทั้งหมด (โลโก้ · ภาพ · ปกโบรชัวร์ · PDF) · video/ วิดีโอปกหน้าแรก (v8.9)
└── docs/                   HOW-TO-EDIT (คู่มือแก้ไข) · CHANGELOG · film-data
```

**แก้ตัวเลขหรือรายการ → แก้ `data/*.json` แล้วรัน `python tools/build.py`** ไม่ใช่แก้ที่ HTML ตรง ๆ
**วิธีแก้งานที่ทำบ่อย (เปลี่ยนเบอร์ · เพิ่มร้าน · เปลี่ยนภาพ · แก้เมนู) อยู่ที่ `docs/HOW-TO-EDIT.md`** · คู่มือเชิงเทคนิคอยู่ที่ `CLAUDE.md`
