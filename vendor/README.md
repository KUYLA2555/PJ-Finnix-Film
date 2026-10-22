# vendor/ — ไลบรารีภายนอกที่วางไว้ในเว็บเอง

CSP ของเว็บ (`HEAD_META` ใน `tools/build.py`) ให้โหลดสคริปต์ได้เฉพาะไฟล์ของเว็บเอง จึงต้องวางไฟล์ไว้ที่นี่แทนการลิงก์ CDN · **ห้ามแก้ไฟล์ในโฟลเดอร์นี้ด้วยมือ**

| ไฟล์ | คืออะไร |
|---|---|
| `model-viewer.min.js` | **`@google/model-viewer` 4.3.1** (npm · ไฟล์ `dist/model-viewer.min.js` รวม three.js r183 ไว้ในตัว · ES module 1.07 MB) · sha256 `283b0672384614b4847636c306fc93fe4b1fcadc76d668b4e47f0ca76bcf033b` · ใช้ที่หน้าแรกส่วน 04 (รถ 3D) — `app.js` ส่วนที่ 3 โหลดด้วย `import()` **เมื่อผู้ใช้กดปุ่มหมุนดูรถเท่านั้น** ไม่โหลดตอนเปิดหน้า (v9.5) |
| `LICENSE-model-viewer.txt` | สัญญาอนุญาต Apache-2.0 ของ model-viewer (ไฟล์ `LICENSE` จากแพ็กเกจเดียวกัน) — ต้องอยู่คู่กับไฟล์ข้างบนเสมอ |

**อัปเดตเวอร์ชัน**: `npm pack @google/model-viewer@<เวอร์ชัน>` ในโฟลเดอร์ชั่วคราว (ไม่ต้อง install) → แตกไฟล์ → คัดลอก `package/dist/model-viewer.min.js` กับ `package/LICENSE` มาทับ → แก้เวอร์ชันกับ sha256 ในตารางนี้ → ตรวจ `grep -c "eval(\|new Function" model-viewer.min.js` ต้องได้ 0 (CSP บล็อก) → เปิดหน้าแรกกดหมุนดูรถ

ไฟล์นี้มี URL ของตัวถอดรหัส Draco / KTX2 บน gstatic ซึ่งจะถูกเรียกเฉพาะเมื่อโมเดลถูกบีบอัดแบบนั้น — CSP บล็อกอยู่ **โมเดลที่ใช้ต้องเป็น GLB ธรรมดา ไม่บีบอัด Draco/KTX2**
