"""tools/work_photos.py — ภาพผลงานของ /works.html (v10.4)

ใช้:  python tools/work_photos.py                  ทำภาพทุกคันที่มี "source" ใน data/gallery.json
      python tools/work_photos.py <โฟลเดอร์คลัง>    ใช้คลังต้นฉบับที่อื่น (ไม่ใส่ = SOURCE_DIR ข้างล่าง)

แต่ละผลงานใน gallery.json ที่มี
  "source": ชื่อโฟลเดอร์ต้นฉบับในคลัง (ภาพเรียงตามเลขในชื่อไฟล์ เช่น Artboard 1.jpg … Artboard 7.jpg)
  "photo":  ชื่อไฟล์บนเว็บ (a-z 0-9 ขีด) → assets/works/<photo>-1.jpg … <photo>-<n>.jpg
  "blur":   (ไม่ใส่ก็ได้) กรอบเบลอป้ายทะเบียน {"เลขภาพ": [[x1, y1, x2, y2], …]} พิกัดของภาพต้นฉบับ
→ เบลอป้าย → ครอบเป็นจัตุรัส 800x800 → JPG (ffmpeg -q:v 5 · ลบ metadata/EXIF ทุกตัว รวมพิกัด GPS)
รันแล้วตามด้วย python tools/build.py — build ใส่ภาพลงการ์ดตามไฟล์ที่มีใน assets/works/

ต้นฉบับอยู่นอก repo (repo เป็น public · ต้นฉบับยังไม่เบลอป้าย) — อย่าวางต้นฉบับใน assets/
ไฟล์ใน assets/works/ ที่ไม่ตรงกับผลงานใน gallery.json แล้ว สคริปต์แค่แจ้ง ไม่ลบเอง
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = Path(r'C:\Claude\top secret\Finnix\ไฟล์ต้นฉบับ\ต้นฉบับรูปบนเว็บ\PIC_')
OUT = ROOT / 'assets' / 'works'
SIZE = 800
QUALITY = '5'          # ffmpeg -q:v (2 ชัดสุด · 31 แย่สุด) — 5 ที่ 800px ราว 70 KB ต่อภาพ ดูไม่ต่างจาก 3
IMAGE_EXT = {'.jpg', '.jpeg', '.png'}


def number(path):
    found = re.findall(r'\d+', path.stem)
    return int(found[-1]) if found else 0


def blur_filter(boxes):
    """[0:v] → เบลอทีละกรอบ → ครอบจัตุรัส → SIZE · คืน filter_complex"""
    steps, last = [], '0:v'
    if boxes:
        steps.append(f'[0:v]split={len(boxes) + 1}[base]' + ''.join(f'[c{i}]' for i in range(len(boxes))))
        last = 'base'
        for i, (x1, y1, x2, y2) in enumerate(boxes):
            w, h = x2 - x1, y2 - y1
            sigma = max(8, min(w, h) // 4)
            steps.append(f'[c{i}]crop={w}:{h}:{x1}:{y1},gblur=sigma={sigma}:steps=3[b{i}]')
            steps.append(f'[{last}][b{i}]overlay={x1}:{y1}[o{i}]')
            last = f'o{i}'
    steps.append(f'[{last}]scale={SIZE}:{SIZE}:force_original_aspect_ratio=increase:flags=lanczos,'
                 f'crop={SIZE}:{SIZE}[out]')
    return ';'.join(steps)


def main():
    if not shutil.which('ffmpeg'):
        sys.exit('ไม่พบ ffmpeg — ติดตั้งก่อน (ดู C:\\Claude\\CLAUDE.md)')
    source_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else SOURCE_DIR
    gallery = json.loads((ROOT / 'data' / 'gallery.json').read_text(encoding='utf-8'))
    OUT.mkdir(parents=True, exist_ok=True)
    expected, problems = set(), []
    for item in gallery['items']:
        if not item.get('source'):
            continue
        photo = item.get('photo', '')
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', photo):
            problems.append(f'{item["car"]}: "photo" ต้องเป็น a-z 0-9 ขีด (ได้ "{photo}")')
            continue
        folder = source_dir / item['source']
        images = sorted((p for p in folder.glob('*') if p.suffix.lower() in IMAGE_EXT), key=number)
        if not images:
            problems.append(f'{item["car"]}: ไม่พบภาพใน {folder}')
            continue
        blur = {int(k): v for k, v in item.get('blur', {}).items()}
        unknown = sorted(set(blur) - set(range(1, len(images) + 1)))
        if unknown:
            problems.append(f'{item["car"]}: "blur" อ้างภาพที่ {unknown} แต่โฟลเดอร์มี {len(images)} ภาพ')
        for n, src in enumerate(images, 1):
            out = OUT / f'{photo}-{n}.jpg'
            expected.add(out.name)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src),
                            '-filter_complex', blur_filter(blur.get(n, [])), '-map', '[out]',
                            '-map_metadata', '-1', '-q:v', QUALITY, str(out)], check=True)
        print(f'{photo}: {len(images)} ภาพ' + (f' · เบลอ {sum(len(v) for v in blur.values())} จุด' if blur else ''))
    stale = sorted(p.name for p in OUT.glob('*.jpg') if p.name not in expected)
    total = sum((OUT / name).stat().st_size for name in expected)
    print(f'รวม {len(expected)} ภาพ · {total / 1e6:.1f} MB → assets/works/')
    for name in stale:
        print('   ไม่มีผลงานใน gallery.json แล้ว (ลบเองถ้าไม่ใช้):', name)
    for p in problems:
        print('***', p)
    if problems:
        sys.exit(1)


if __name__ == '__main__':
    main()
