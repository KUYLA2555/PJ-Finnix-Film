# FINNIX FILM — เว็บไซต์

เว็บไซต์ของ **บริษัท ฟินนิกซ์ ฟิล์ม จำกัด** (ฟิล์มกรองแสงรถยนต์) — static site ล้วน ไม่มี package manager
**v6.x (ตั้งแต่ 3 ต.ค. 2569)** โครงและดีไซน์ตามต้นแบบ `C:\Claude\FINNIX-Website` · เว็บฉบับเก่า (v5.7) เก็บไว้ที่ `C:\Claude\top secret\Finnix\`

> **repo ส่วนตัว ยังไม่พร้อมขึ้นเซิร์ฟเวอร์จริง** — ตัวเลขทุกตัวยังรอ `{{TEST_STANDARD}}` · ร้านตัวแทนกับรายการผลงานเป็นข้อมูลสมมติ · หลายช่องยังเป็นภาพชั่วคราว
> รายการที่ต้องปิดก่อนขึ้นจริงอยู่ท้าย `docs/CHANGELOG.md`

## เปิดดู

```powershell
python -m http.server 8000     # แล้วเปิด http://localhost:8000/
```

**ต้องเปิดผ่าน HTTP** — ลิงก์ทั้งหมดเป็น root-relative (`/films.html`) เปิดด้วย `file://` จะพัง

## โครงสร้าง

```
PJ_Finnix_Film/
├── index.html              หน้าแรก
├── films.html  about.html  experience.html  dealers.html  works.html
│                           หน้าละไฟล์ ชื่อตามหน้า (v7.4) · films/<ซีรีส์>.html อีก 5 หน้าสร้างอัตโนมัติ
├── style.css  journey.css  สไตล์จากต้นแบบ
├── merge.css               คอมโพเนนต์ที่เพิ่มเอง
├── app.js                  JS ทั้งเว็บ
├── content.js              ข้อมูลที่ app.js ใช้ — สร้างอัตโนมัติ ห้ามแก้มือ
├── data/                   films.json · dealers.json · gallery.json — source of truth
├── tools/build.py          ตัวสร้าง content.js · หน้ารุ่น · header/footer
├── assets/                 รูปทั้งหมด (โลโก้ · ภาพ · ปกโบรชัวร์ · PDF)
└── docs/                   HOW-TO-EDIT (คู่มือแก้ไข) · CHANGELOG · film-data
```

**แก้ตัวเลขหรือรายการ → แก้ `data/*.json` แล้วรัน `python tools/build.py`** ไม่ใช่แก้ที่ HTML ตรง ๆ
**วิธีแก้งานที่ทำบ่อย (เปลี่ยนเบอร์ · เพิ่มร้าน · เปลี่ยนภาพ · แก้เมนู) อยู่ที่ `docs/HOW-TO-EDIT.md`** · คู่มือเชิงเทคนิคอยู่ที่ `CLAUDE.md`
