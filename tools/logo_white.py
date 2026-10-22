"""tools/logo_white.py — โลโก้ซีรีส์ฉบับพื้นมืด (v9.4) สำหรับกระจกดำที่เลื่อนขึ้นบนการ์ด /films.html

รันจาก root ของโปรเจกต์ (ต้องมี ffmpeg):
    python tools/logo_white.py      อ่าน assets/series/logo-<id>.png ทุกไฟล์ → เขียน logo-<id>-white.png ข้างกัน

เปลี่ยนไฟล์โลโก้ซีรีส์เมื่อไร ให้รันสคริปต์นี้ก่อน แล้วค่อยรัน build.py
วิธี: พิกเซลสีกลาง (ดำ/เทา) พับความสว่าง c → max(c, 255-c) — ดำกลายเป็นขาว · เทาอ่อน/สีเงินคงเดิม
      น้ำหนักลดตามความอิ่มสี (อิ่มสี 0 = เต็ม · ≥60 = ไม่แตะ) → แดง ทอง ฟ้า เหลืองของแบรนด์คงเดิม
      × ความทึบ (alpha ≤64 = ไม่แตะ · ≥192 = เต็ม) → เงาเข้มจาง ๆ คงเข้ม กลืนกับกระจกดำ ไม่กลายเป็นแสงขาวฟุ้ง
      (แสงขาวรอบตัวอักษร TITANIUM มีอยู่ในไฟล์ต้นฉบับเอง ไม่ได้เกิดจากสคริปต์นี้)
"""
import subprocess
from pathlib import Path

SERIES = Path(__file__).resolve().parent.parent / 'assets' / 'series'

SAT = '(max(max(r(X,Y),g(X,Y)),b(X,Y))-min(min(r(X,Y),g(X,Y)),b(X,Y)))'
WEIGHT = f'clip(1-{SAT}/60,0,1)*clip((alpha(X,Y)-64)/128,0,1)'


def channel(c):
    v = f'{c}(X,Y)'
    return f"'{v}+{WEIGHT}*(max({v},255-{v})-{v})'"


VF = f"format=rgba,geq=r={channel('r')}:g={channel('g')}:b={channel('b')}:a='alpha(X,Y)'"

for src in sorted(SERIES.glob('logo-*.png')):
    if src.stem.endswith('-white'):
        continue
    dst = src.with_name(f'{src.stem}-white.png')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-vf', VF, '-frames:v', '1', str(dst)], check=True)
    print(f'{src.name} → {dst.name}')
