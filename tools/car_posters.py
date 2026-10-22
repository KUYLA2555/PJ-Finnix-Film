"""tools/car_posters.py — ภาพนิ่งรถ 3D ของหน้าแรกส่วน 04 (v9.5)

รันจาก root ของโปรเจกต์ (ต้องมี Chrome หรือ Edge):
    python tools/car_posters.py     อ่าน CAR_3D ใน build.py → เรนเดอร์ assets/3d/car.glb ทุกระดับความเข้ม → assets/3d/car-<n>.jpg
แล้วรัน python tools/build.py — ภาพนิ่งครบเมื่อไร หน้าแรกเปลี่ยนจากภาพเมืองเป็นรถ 3D เอง

ภาพนิ่ง = มุมกล้อง CAR_3D['orbit'] เดียวกับตอนเปิด 3D · ความทึบกระจกตาม CAR_3D['glass'] · พื้น #111517 (สีของ .dark)
เปลี่ยนโมเดล มุมกล้อง หรือความทึบกระจก ต้องรันใหม่ · วิธีหาวัสดุกระจกกับสีฟิล์ม (FILM) ต้องตรงกับ app.js ส่วนที่ 3
ใช้ Chrome headless + SwiftShader (เรนเดอร์ WebGL ด้วย CPU) — ไม่ต้องมีการ์ดจอ
"""
import ast
import base64
import functools
import http.server
import re
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 720

# ค่าตั้งจาก build.py โดยไม่รัน build (CAR_3D เป็นค่าคงที่ล้วน)
tree = ast.parse((ROOT / 'tools' / 'build.py').read_text(encoding='utf-8'))
CAR = next(ast.literal_eval(n.value) for n in tree.body
           if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'CAR_3D')
model = ROOT / CAR['src'].lstrip('/')
if not model.exists():
    raise SystemExit(f'ไม่มีไฟล์โมเดล {model}')

PAGE = '''<!doctype html><meta charset="utf-8">
<style>body{margin:0;background:#111517}model-viewer{position:fixed;top:0;left:0;width:%(w)dpx;height:%(h)dpx}#out{display:none}</style>
<pre id="out"></pre>
<model-viewer id="mv" src="%(src)s" camera-orbit="%(orbit)s" environment-image="neutral" shadow-intensity="1" interaction-prompt="none"></model-viewer>
<script type="module">
  const out = document.getElementById("out");
  const GLASS = %(glass)s, FILM = [0.02, 0.03, 0.035];
  // รอด้วย setTimeout ไม่ใช่ requestAnimationFrame — rAF แทบไม่เดินใน headless (ดู skill browser-verify) แต่เวลาเสมือนเดิน
  const frame = () => new Promise((r) => setTimeout(r, 400));
  await import("/vendor/model-viewer.min.js");
  const mv = document.getElementById("mv");
  mv.addEventListener("error", (e) => { out.textContent += "ERROR " + JSON.stringify(e.detail) + "\\n"; });
  mv.addEventListener("load", async () => {
    const mats = mv.model.materials;
    let glass = mats.filter((m) => /glass|window|windshield|glas/i.test(m.name));
    if (!glass.length) glass = mats.filter((m) => m.getAlphaMode() === "BLEND");
    const original = glass.map((m) => m.pbrMetallicRoughness.baseColorFactor.slice());
    out.textContent += "GLASS " + glass.map((m) => m.name).join("|") + "\\n";
    for (let n = 0; n < GLASS.length; n++) {
      glass.forEach((m, i) => {
        m.setAlphaMode("BLEND");
        m.pbrMetallicRoughness.setBaseColorFactor(GLASS[n] === null ? original[i] : [...FILM, GLASS[n]]);
      });
      await frame(); await frame();
      const img = new Image();
      await new Promise((r) => { img.onload = r; img.src = mv.toDataURL("image/png"); });
      const c = document.createElement("canvas");
      c.width = %(w)d; c.height = %(h)d;
      const g = c.getContext("2d");
      g.fillStyle = "#111517"; g.fillRect(0, 0, c.width, c.height);
      g.drawImage(img, 0, 0, c.width, c.height);
      out.textContent += "IMG" + n + " " + c.toDataURL("image/jpeg", 0.86) + "\\n";
    }
    out.textContent += "ALL-RENDERED\\n";
  });
</script>'''


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/__render.html'):
            body = (PAGE % {'w': W, 'h': H, 'src': CAR['src'], 'orbit': CAR['orbit'],
                            'glass': str(CAR['glass']).replace('None', 'null')}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def log_message(self, *args):
        pass


server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
chrome = next((p for p in (r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                           r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                           shutil.which('chrome'), shutil.which('google-chrome')) if p and Path(p).exists()), None)
if not chrome:
    raise SystemExit('ไม่เจอ Chrome หรือ Edge')
with tempfile.TemporaryDirectory() as profile:
    dom = subprocess.run([chrome, '--headless=new', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
                          f'--user-data-dir={profile}', f'--window-size={W + 40},{H + 200}', '--virtual-time-budget=60000',
                          '--dump-dom', f'http://127.0.0.1:{server.server_address[1]}/__render.html'],
                         capture_output=True, text=True, encoding='utf-8', timeout=300).stdout
server.shutdown()

images = re.findall(r'IMG(\d+) data:image/jpeg;base64,([A-Za-z0-9+/=]+)', dom)
if '\nALL-RENDERED' not in dom or len(images) != len(CAR['glass']):   # มีขึ้นบรรทัดใหม่นำหน้า = ผลจริง ไม่ใช่ข้อความในสคริปต์
    log = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
    raise SystemExit('เรนเดอร์ไม่สำเร็จ:\n' + '\n'.join(line[:120] for line in (log.group(1) if log else dom[:2000]).splitlines()))
print(re.search(r'GLASS (.*)', dom).group(1).strip() or '(ไม่เจอวัสดุกระจก — ภาพนิ่งทุกระดับจะเหมือนกัน)', '← วัสดุกระจก')
for n, data in images:
    path = ROOT / CAR['poster'].format(n=n).lstrip('/')
    path.write_bytes(base64.b64decode(data))
    print(f'{path.relative_to(ROOT).as_posix()}  {path.stat().st_size // 1024} KB')
