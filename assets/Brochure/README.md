# assets/Brochure/

โบรชัวร์ต้นฉบับของทั้ง 5 ซีรีส์ — **เอกสารอ้างอิงของตัวเลขทุกตัวใน `data/films.json`** (รูปถ่ายชุดเดียวกัน `scans\` อยู่ในคลัง `C:\Claude\top secret\Finnix\ไฟล์ต้นฉบับ\` แล้ว — v7.5)

| ไฟล์ | คืออะไร | ใครใช้ |
|---|---|---|
| `Finnix-Titanium.pdf` · `Finnix-Ceramic.pdf` · `Finnix-Crystalize.pdf` · `Finnix-Extra-clear.pdf` · `Finnix-Uvguard.pdf` | PDF ต้นฉบับ 17 หน้า 11 MB · สแกนภาพล้วน ไม่มี text layer | ไม่มีหน้าไหนลิงก์ถึง · **ห้ามลบโดยไม่ถาม** |
| `cover-SY · CM · CT · XT · SM .jpg` | ปกย่อ 880px | **หน้ารุ่น `/films/<id>.html` 5 หน้า** — แมป id ซีรีส์→ไฟล์อยู่ที่ `COVER` ใน `tools/build.py` (v9.1 เดิมแมปตามรหัส · CERAMIC PLUS ใช้รหัส CM ซ้ำ และยังไม่มีปก) |
| ต้นฉบับปก `CM.jpg` `CT.jpg` `CT.png` `SM.png` `XT.png` | สแกนปกความละเอียดสูง | **ย้ายไปคลังแล้ว (v7.5)** — `C:\Claude\top secret\Finnix\ไฟล์ต้นฉบับ\ต้นฉบับรูปบนเว็บ\Brochure\` |

**`CT.jpg` เป็นปกของ TITANIUM (รหัส `SY`) ไม่ใช่ CRYSTALIZE** — ชื่อไฟล์ไม่ตรงกับรหัสซีรีส์ จึงถูกย่อออกมาเป็น `cover-SY.jpg`
**เปิดดูรูปก่อนตั้งชื่อทุกครั้ง** ตั้งชื่อตามไฟล์ต้นทางเมื่อไหร่จะทับปก CRYSTALIZE ที่ใช้อยู่

ทุกค่าในโบรชัวร์ถอดลง `data/films.json` แล้ว — **อย่าเปิด PDF อ่านเพื่อหาสเปก** ให้ใช้ `films.json` กับ `docs/film-data.md`
