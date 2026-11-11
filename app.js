"use strict";
/* ==========================================================================
   app.js — JavaScript ของทั้งเว็บ (ไฟล์เดียว ใช้ทุกหน้า)

   ข้อมูลทั้งหมดมาจาก content.js ซึ่ง tools/build.py สร้างจาก data/*.json
   → ไฟล์นี้ไม่มีตัวเลขหรือข้อความสินค้าพิมพ์มือ จะแก้ข้อมูลให้แก้ที่ data/ แล้วรัน build

   แต่ละส่วนทำงานเฉพาะหน้าที่มี element ของมัน (เช็คด้วย if ($('#…')) ก่อนเสมอ)
   ลำดับ:
     1. reveal       — ค่อย ๆ แสดงบล็อก .reveal ตอนเลื่อนถึง (ทุกหน้า)
     2. เมนูมือถือ    — ปุ่ม ☰ (ทุกหน้า)
     3. หน้าแรก       — ปุ่มหยุดภาพเคลื่อนไหว (v8.9 หยุด/เล่นวิดีโอปกด้วย) · ตัวเลื่อนความเข้ม (v9.5 รถ 3D · v9.8 โหลด vendor/ เมื่อเลื่อนใกล้ถึง) · หน้าต่างรายละเอียด
     4. /films.html      — แนะนำซีรีส์ตาม ?need= + สลับความต้องการในหน้า · ปุ่มหยุดภาพ (v8.5 เลิกหน้าต่างรายละเอียด)
     5. ท้ายทุกหน้า       — หาร้าน + เพื่อนร่วมทาง: ค้นหาร้านบนแผนที่ (v8.8 โหลดเมื่อกดเปิด/ค้นหา · v10.0 ย้ายจากส่วนที่ 3 · เดิม /try.html)
     6. (ว่าง)           — เดิมเครื่องคำนวณราคา /films.html#price (ลบแล้ว v10.0)
     7. /dealers.html    — ค้นหาร้าน + ชิปจังหวัด + รายชื่อในกล่องเลื่อน + แผนที่ (โหลดเมื่อกดเปิด)
     8. ผลงาน           — /works.html กรองตามซีรีส์ · แสดงทีละ 12 (มือถือ 6 · v10.5) · หน้ารุ่น "รถที่ติด" ทีละแถว (v10.6) · ปุ่มเลื่อนภาพผลงาน (v10.4)
     9. ลูกเล่นตอนเลื่อนถึง — แผนภาพแสง (หน้าแรก) · v8.8 ขั้นตอนของ /experience.html ลบไปพร้อมหน้า
    10. (ว่าง)          — เดิม /faq.html (ลบแล้ว v8.4)
    11. หน้ารุ่น          — ปุ่มเลือกรหัส ↔ ตารางสเปก · กล่องคำนวณราคา (v8.2)
   ========================================================================== */

const data = window.FINNIX;            // ข้อมูลเว็บ (ซีรีส์ ราคา ร้าน)
const config = window.FINNIX_JOURNEY;  // ค่าตั้งของ journey (ภาพจำลอง การจับคู่ความต้องการ)
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const reduced = matchMedia("(prefers-reduced-motion: reduce)");
const seriesById = (id) => data.series.find((s) => s.id === id);
// v8.8 แผนที่ตอนยังไม่เลือกพื้นที่ = ภาพรวมประเทศไทย ไม่ปักจุด (เดิม q=FINNIX FILM Thailand ไปปักจุดหนึ่งในเชียงใหม่ที่ยังไม่รู้ว่าเป็นร้านใคร)
const THAILAND_MAP = "https://maps.google.com/maps?ll=13.2,101.0&z=5&output=embed";
// v8.6 เว็บอยู่ใต้ path ย่อยได้ (GitHub Pages) — ลิงก์ที่ JS สร้างห้ามขึ้นต้นด้วย / ให้ต่อจาก ROOT
// ROOT = ส่วนหน้า "app.js" ใน src ของสคริปต์นี้ ("" ที่หน้า root · "../" ที่หน้ารุ่น) — build.py ใส่ src แบบ relative ให้ทุกหน้า
const ROOT = ((document.currentScript && document.currentScript.getAttribute("src")) || "").replace(/app\.js(\?.*)?$/, "");


/* --------------------------------------------------------------------------
   1. reveal — อยู่บนสุดโดยตั้งใจ ถ้าโค้ดส่วนอื่น error เนื้อหาจะไม่ค้างที่ opacity:0
   -------------------------------------------------------------------------- */
if ("IntersectionObserver" in window && !reduced.matches) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("seen");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08 });

  $$(".reveal").forEach((el) => {
    el.classList.add("js-reveal");
    observer.observe(el);
  });
}


/* --------------------------------------------------------------------------
   2. เมนูมือถือ (≤1050px)
   -------------------------------------------------------------------------- */
if ($("#menu")) {
  const setMenu = (open) => {
    $("#menu").setAttribute("aria-expanded", String(open));
    $("#menu").setAttribute("aria-label", open ? "ปิดเมนู" : "เปิดเมนู");
    $("#nav").classList.toggle("open", open);
  };
  $("#menu").addEventListener("click", () => {
    setMenu($("#menu").getAttribute("aria-expanded") !== "true");
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") setMenu(false);
  });
  $$("#nav a").forEach((a) => a.addEventListener("click", () => setMenu(false)));
}


/* --------------------------------------------------------------------------
   3. หน้าแรก (ตามต้นแบบ FINNIX-Website)
      (ตัวเลื่อนเคยใช้ id ซ้ำกับ /try.html ซึ่งลบแล้วใน v8.1 — จึงเหลือที่หน้าแรกที่เดียว)
      ส่วน 06 หาร้าน + เพื่อนร่วมทาง ใช้ทุกหน้าแล้ว (v10.0) → ย้ายไปส่วนที่ 5
   -------------------------------------------------------------------------- */
// ปุ่มหยุด/เล่นภาพเคลื่อนไหว (เริ่มหยุดถ้าผู้ใช้ตั้งลดการเคลื่อนไหว)
if ($("#motion")) {
  const heroVideo = $("#hero-video");   // v8.9 วิดีโอปก — ปุ่มเดียวกันหยุด/เล่นวิดีโอ · ตั้งลดการเคลื่อนไหว = หยุดตั้งแต่เปิดหน้า
  const setPaused = (paused) => {
    document.body.classList.toggle("paused", paused);
    $("#motion").setAttribute("aria-pressed", String(paused));
    $("#motion").innerHTML = (paused ? "▶" : "Ⅱ") + " <span>" + (paused ? "เล่นภาพเคลื่อนไหว" : "หยุดภาพเคลื่อนไหว") + "</span>";
    if (heroVideo) {
      if (paused) heroVideo.pause();
      else heroVideo.play().catch(() => {});   // เบราว์เซอร์บางตัว (เช่นโหมดประหยัดแบต) ไม่ให้เล่นเอง — ค้างที่ภาพปก
    }
  };
  setPaused(reduced.matches);
  $("#motion").addEventListener("click", () => {
    setPaused($("#motion").getAttribute("aria-pressed") !== "true");
  });
}

// ตัวเลื่อนความเข้ม — ภาพจำลองเท่านั้น ไม่ใช่ค่า VLT · v9.5 ตัด Dark เหลือ Clear 40 60 80
//   ภาพเมือง (#tint-overlay ม่านเข้ม) หรือรถ 3D (.car3d — build.py เลือกให้ตามไฟล์ที่มี · ค่าอยู่ที่ CAR_3D)
//   รถ 3D: ระหว่างยังไม่โหลด สลับภาพนิ่ง car-<n>.jpg (มุมเดียวกัน) · v9.8 เลื่อนใกล้ถึงส่วนนี้แล้วโหลดไลบรารี vendor/ (~1 MB) กับโมเดลเอง
//   (ผู้สั่งงานสั่งเอาปุ่มออก ลากหมุนได้ทันที) · ปุ่มเหลือไว้ลองใหม่เมื่อโหลดพลาด และเมื่อเบราว์เซอร์เปิดโหมดประหยัดเน็ต (ให้กดเอง)
//   โหลดแล้วเปลี่ยนสีวัสดุกระจกของโมเดลแทน (ชื่อวัสดุมี glass/window · ไม่เจอ = วัสดุโปร่ง BLEND)
if ($("#tint-range")) {
  const LEVELS = ["Clear", "40", "60", "80"];
  const NAMES = ["ไม่ติดฟิล์ม", "ติดฟิล์มความเข้ม 40", "ติดฟิล์มความเข้ม 60", "ติดฟิล์มความเข้ม 80"];
  const SHADE = [0, 0.19, 0.34, 0.52];
  const FILM = [0.02, 0.03, 0.035];          // สีฟิล์มบนกระจก 3D (เกือบดำ) — ความทึบตาม data-glass
  const car = $(".car3d");
  const posters = car ? car.dataset.posters.split(" ") : [];
  const glassAlpha = car ? car.dataset.glass.split(" ").map(Number) : [];   // "none" → NaN = กระจกเดิมของโมเดล
  let viewer = null;
  let glass = [];                            // [{ material, original }]
  let current = 2;

  const paintGlass = () => {
    glass.forEach(({ material, original }) => {
      const alpha = glassAlpha[current];
      material.setAlphaMode("BLEND");
      material.pbrMetallicRoughness.setBaseColorFactor(Number.isNaN(alpha) ? original : [...FILM, alpha]);
    });
  };
  const setTint = (level) => {
    current = level;
    $("#tint-range").value = level;
    $("#tint-range").setAttribute("aria-valuetext", LEVELS[level]);
    $("#tint-output").textContent = LEVELS[level];
    if ($("#tint-overlay")) $("#tint-overlay").style.opacity = SHADE[level];
    if (car) {
      const poster = $(".car3d-poster");
      poster.src = ROOT + posters[level];
      poster.alt = "รถจำลอง" + NAMES[level];
      if (viewer) viewer.alt = car.dataset.alt + " · " + NAMES[level];
      paintGlass();
    }
    $$("[data-tint]").forEach((b) => {
      const active = Number(b.dataset.tint) === level;
      b.classList.toggle("active", active);
      b.setAttribute("aria-pressed", String(active));
    });
  };
  $("#tint-range").addEventListener("input", (e) => setTint(Number(e.target.value)));
  $$("[data-tint]").forEach((b) => b.addEventListener("click", () => setTint(Number(b.dataset.tint))));
  setTint(2);

  if (car) {
    const button = $(".car3d-load");         // ซ่อนอยู่ใน HTML — ไม่มี JS เห็นภาพนิ่งอย่างเดียว ไม่มีปุ่มค้าง
    const status = $(".car3d-status");
    let started = false;                     // viewer ได้ค่าหลัง import เสร็จ — กันเรียกซ้ำระหว่างนั้นด้วยตัวนี้
    const fail = () => {
      started = false;
      status.textContent = "โหลดรถ 3D ไม่ได้";
      button.lastChild.nodeValue = " ลองใหม่";
      button.hidden = false;
      if (viewer) viewer.remove();
      viewer = null;
      glass = [];
      car.classList.remove("is-3d");
    };
    const load = () => {
      if (started) return;                   // กำลังโหลดหรือโหลดแล้ว
      started = true;
      button.hidden = true;
      status.textContent = "กำลังโหลดรถ 3D…";
      import(new URL(ROOT + "vendor/model-viewer.min.js", document.baseURI).href).then(() => {
        viewer = document.createElement("model-viewer");
        viewer.setAttribute("src", ROOT + car.dataset.src);
        viewer.setAttribute("camera-orbit", car.dataset.orbit);
        viewer.setAttribute("camera-controls", "");
        viewer.setAttribute("disable-zoom", "");          // ล้อเมาส์ใช้เลื่อนหน้า ไม่ใช่ซูม
        viewer.setAttribute("touch-action", "pan-y");     // มือถือ: ลากแนวนอนหมุนรถ แนวตั้งเลื่อนหน้า
        viewer.setAttribute("interaction-prompt", "none");
        viewer.setAttribute("environment-image", "neutral");
        viewer.setAttribute("shadow-intensity", "1");
        viewer.setAttribute("loading", "eager");
        if (!reduced.matches) viewer.setAttribute("auto-rotate", "");   // หมุนช้า ๆ จนผู้ใช้ลากเอง
        viewer.alt = car.dataset.alt + " · " + NAMES[current];
        viewer.addEventListener("progress", (e) => {
          // ทีละ 10% (role=status อ่านออกเสียงทุกครั้งที่เปลี่ยน) · progress 100% ยิงหลัง load — อย่าทับข้อความ "ลากเพื่อหมุน"
          if (car.classList.contains("is-3d")) return;
          status.textContent = "กำลังโหลดรถ 3D… " + Math.floor(e.detail.totalProgress * 10) * 10 + "%";
        });
        viewer.addEventListener("load", () => {
          const materials = viewer.model.materials;
          let found = materials.filter((m) => /glass|window|windshield|glas/i.test(m.name));
          if (!found.length) found = materials.filter((m) => m.getAlphaMode() === "BLEND");
          glass = found.map((material) => ({ material, original: material.pbrMetallicRoughness.baseColorFactor.slice() }));
          paintGlass();
          car.classList.add("is-3d");
          status.textContent = "ลากเพื่อหมุนดูรถรอบคัน";
        });
        viewer.addEventListener("error", fail);
        $(".car3d-poster").after(viewer);   // ก่อนแถบปุ่มกับคำบรรยาย — สองอย่างนั้นจึงวาดทับรถ
      }).catch(fail);
    };
    button.addEventListener("click", load);
    if (navigator.connection && navigator.connection.saveData) {
      button.hidden = false;                 // โหมดประหยัดเน็ต — ~9.6 MB ให้ผู้ใช้เลือกเอง
    } else if ("IntersectionObserver" in window) {
      const near = new IntersectionObserver((entries) => {
        if (!entries.some((e) => e.isIntersecting)) return;
        near.disconnect();
        load();
      }, { rootMargin: "50% 0px" });         // เริ่มก่อนถึงราวครึ่งจอ — เลื่อนถึงแล้วมักโหลดเสร็จหรือใกล้เสร็จ
      near.observe(car);
    } else {
      load();
    }
  }
}

// หน้าต่างรายละเอียด — การ์ดความต้องการ (data-guide) · รายชื่อซีรีส์มาจาก content.js
if ($("#detail")) {
  const dialog = $("#detail");
  let lastFocus;
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const filmLinks = () => '<div class="film-grid">' + data.series.map((s) =>
    `<a href="${ROOT}films/${esc(s.id)}.html"><strong>${esc(s.name)}</strong><small>${esc(s.th)}</small></a>`).join("") + "</div>";
  const openDetail = (markup) => {
    lastFocus = document.activeElement;
    $("#dialog-content").innerHTML = markup;
    if (!dialog.open) dialog.showModal();
    document.body.style.overflow = "hidden";
    dialog.querySelector(".dialog-close").focus();
  };
  dialog.addEventListener("close", () => {
    document.body.style.overflow = "";
    lastFocus?.focus();
  });
  $(".dialog-close").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (e) => {
    if (e.target !== dialog) return;
    const b = dialog.getBoundingClientRect();
    if (e.clientX < b.left || e.clientX > b.right || e.clientY < b.top || e.clientY > b.bottom) dialog.close();
  });
  $$("[data-need]").forEach((btn) => btn.addEventListener("click", () => openDetail(
    `<div class="dialog-eyebrow">YOUR LIFE / YOUR FINNIX</div><h2>${esc(btn.dataset.need)}</h2><p>${esc(btn.dataset.guide)}</p>` +
    '<h3>ซีรีส์ที่คุณสำรวจต่อได้</h3><p class="small">เลือกจากเฉดและสเปกจริงของแต่ละซีรีส์ เพื่อให้เหมาะกับคุณ</p>' + filmLinks())));
}

/* --------------------------------------------------------------------------
   4. /films.html — ?need=heat|clarity|privacy|balance → แนะนำซีรีส์ที่ตรง
      การจับคู่คำนวณใน build.py (needToFilm) — ยังเป็นร่าง รอบริษัทยืนยัน
      v8.0 ดีไซน์ตามไฟล์ต้นแบบ: การ์ดที่แนะนำ + ทางเลือกได้ขีดแดง (แทนกล่อง "ทางเลือกอื่น") ·
      v8.5 เลิกหน้าต่างรายละเอียด — การ์ด / ปุ่มบนภาพไปหน้ารุ่นตรง ๆ · ปุ่มหยุดภาพเคลื่อนไหว ·
      v9.9 ภาพใหญ่เปลี่ยนตามความต้องการ (config.needPhoto · ตำแหน่งภาพบนมือถือส่งผ่าน --photo-x ให้ merge.css)
   -------------------------------------------------------------------------- */
const NEED_NAMES = { heat: "กันร้อน", clarity: "มองชัด", privacy: "เป็นส่วนตัว", balance: "สมดุล" };

if ($("#need-message")) {
  const needOf = (a) => new URL(a.href).searchParams.get("need");
  // v9.9 ภาพใหญ่เปลี่ยนตามความต้องการ (NEED_PHOTO ใน build.py) · ไม่ได้เลือก = ภาพที่เขียนไว้ใน HTML
  const photo = $(".films-feature-photo");
  const basePhoto = { src: photo.getAttribute("src"), alt: photo.alt };

  const applyNeed = (rawNeed) => {
    const need = NEED_NAMES[rawNeed] ? rawNeed : null;
    const chosen = seriesById((need && config.needToFilm[need]) || config.heroFilm);

    const shot = need && (config.needPhoto || {})[need];
    const src = shot ? ROOT + shot.src : basePhoto.src;
    if (photo.getAttribute("src") !== src) photo.src = src;  // ภาพเดิมค้างไว้จนภาพใหม่โหลดเสร็จ (เบราว์เซอร์ทำเอง)
    photo.alt = shot ? shot.alt : basePhoto.alt;
    if (shot) photo.style.setProperty("--photo-x", shot.x);
    else photo.style.removeProperty("--photo-x");

    $("#film-eyebrow").textContent = (need ? "RECOMMENDED · " : "FEATURED · ") + chosen.code + " SERIES";
    $("#film-name").textContent = chosen.name;
    $("#film-th").textContent = chosen.th;
    $("#film-tag").textContent = `${chosen.tag} · ลดความร้อน ${chosen.heat} · แสงส่องผ่าน ${chosen.vlt}`;
    $("#hero-film-link").href = `${ROOT}films/${chosen.id}.html`;

    // ล้างผลของความต้องการก่อนหน้า (v7.7 สลับในหน้าได้หลายครั้ง)
    $$(".series-card.highlight").forEach((c) => c.classList.remove("highlight"));
    $("#need-message").textContent = "";
    $$(".need-switch a").forEach((a) => {
      if (needOf(a) === need) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    });
    if (!need) return;

    const alternatives = (config.needAlternatives[need] || []).map(seriesById).filter(Boolean);
    [chosen, ...alternatives].forEach((s) => $(`.series-card[data-id="${s.id}"]`)?.classList.add("highlight"));
    const also = alternatives.length ? ` (รองลงมา ${alternatives.map((s) => s.name).join(" · ")})` : "";
    const note = config.needMappingConfirmed ? "" : " — เป็นคำแนะนำจากตัวเลขในโบรชัวร์ ยังรอบริษัทยืนยัน";
    $("#need-message").textContent = `ถ้าอยากได้${NEED_NAMES[need]} ลองเริ่มที่ ${chosen.name}${also}${note}`;
  };

  // v7.7 ปุ่มความต้องการบนหน้านี้ — สลับในหน้าโดยไม่โหลดใหม่ (ไม่มี JS = ลิงก์ ?need= ธรรมดา)
  $$(".need-switch a").forEach((a) => a.addEventListener("click", (e) => {
    e.preventDefault();
    const need = needOf(a) === new URLSearchParams(location.search).get("need") ? null : needOf(a);  // กดซ้ำ = ยกเลิก
    history.replaceState(null, "", need ? "?need=" + need : location.pathname);
    applyNeed(need);
    const copy = $(".films-feature-copy");
    copy.classList.remove("swap");
    void copy.offsetWidth;  // เริ่มแอนิเมชันใหม่ทุกครั้งที่กด
    copy.classList.add("swap");
  }));

  applyNeed(new URLSearchParams(location.search).get("need"));
}

// ภาพบนสุดเลื่อนช้า ๆ (CSS) — ปุ่มหยุด/เล่น · เริ่มหยุดถ้าผู้ใช้ตั้งลดการเคลื่อนไหว · ไม่มี JS ปุ่มซ่อนอยู่ (hidden)
if ($("#film-motion")) {
  const button = $("#film-motion");
  const setPaused = (paused) => {
    $("#film-hero").classList.toggle("paused", paused);
    button.setAttribute("aria-pressed", String(paused));
    button.firstElementChild.textContent = paused ? "▶" : "Ⅱ";
    button.querySelector(".films-motion-label").textContent = paused ? "เล่นภาพ" : "หยุดภาพ";
  };
  button.hidden = reduced.matches;  // ตั้งลดการเคลื่อนไหว = ภาพไม่ขยับอยู่แล้ว ไม่ต้องมีปุ่ม
  setPaused(reduced.matches);
  button.addEventListener("click", () => setPaused(button.getAttribute("aria-pressed") !== "true"));
}


/* --------------------------------------------------------------------------
   5. ท้ายทุกหน้า — หาร้าน + เพื่อนร่วมทาง (v10.0 · เดิมหน้าแรกส่วน 06 ในส่วนที่ 3 · ส่วนที่ 5 เดิมคือ /try.html ลบแล้ว v8.1)
      markup จาก find_family_block() ใน build.py · id ขึ้นต้น ff- ไม่ชนกับฟอร์มของ /dealers.html (ส่วนที่ 7)
      ค้นหาร้านบน Google Maps (รายชื่อร้านเต็มอยู่ที่ /dealers.html)
      v8.8 แผนที่ไม่โหลดจนกว่าจะกด "เปิดแผนที่" หรือค้นหา (ไม่ส่ง IP ผู้เข้าชมให้ Google ตั้งแต่เปิดหน้า) · เปิดเปล่า = ภาพรวมประเทศไทย ไม่ปักจุดใด
   -------------------------------------------------------------------------- */
if ($("#ff-form")) {
  const panel = $("#ff-map");
  const locate = $("#ff-locate");
  const status = $("#ff-status");
  const openMap = (src) => {
    let frame = panel.querySelector("iframe");
    if (!frame) {
      frame = document.createElement("iframe");
      frame.title = "แผนที่ Google ค้นหาร้าน FINNIX";
      frame.referrerPolicy = "strict-origin-when-cross-origin";   // v9.9 ส่งแค่โดเมน ไม่ส่ง URL หน้าเต็มให้ Google (ตรงกับ meta referrer ของเว็บ)
      panel.prepend(frame);
      panel.classList.add("is-live");
    }
    frame.src = src;
  };
  const updateMap = (query, latLng) => {
    openMap("https://maps.google.com/maps?q=" + encodeURIComponent(query) +
      (latLng ? "&ll=" + encodeURIComponent(latLng) + "&z=12" : "") + "&output=embed");
    $("#ff-map-link").href = latLng
      ? "https://www.google.com/maps/search/FINNIX+FILM/@" + latLng + ",12z"
      : "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(query);
  };
  $("#ff-load-map").hidden = false;
  $("#ff-load-map").addEventListener("click", () => openMap(THAILAND_MAP));
  $("#ff-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const q = $("#ff-query").value.trim();
    if (!q) return;
    updateMap("FINNIX FILM " + q);
    status.textContent = "แสดงผลการค้นหาบน Google Maps สำหรับ " + q;
  });
  locate.addEventListener("click", () => {
    if (!navigator.geolocation) {
      status.textContent = "อุปกรณ์นี้ไม่รองรับตำแหน่ง กรุณาพิมพ์พื้นที่ที่ต้องการ";
      return;
    }
    status.textContent = "กำลังขอตำแหน่งจากอุปกรณ์…";
    locate.disabled = true;
    navigator.geolocation.getCurrentPosition((pos) => {
      updateMap("FINNIX FILM", pos.coords.latitude + "," + pos.coords.longitude);
      status.textContent = "ตั้งแผนที่ใกล้ตำแหน่งของคุณแล้ว";
      locate.disabled = false;
    }, () => {
      status.textContent = "ไม่สามารถใช้ตำแหน่งได้ กรุณาพิมพ์จังหวัดหรือเขตแทน";
      locate.disabled = false;
    }, { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 });
  });
}


/* --------------------------------------------------------------------------
   6. (ว่าง) — เดิมเครื่องคำนวณราคา /films.html#price (v8.0 · เดิมหน้า /price.html) ผู้สั่งงานสั่งเอาออกใน v10.0
      ราคาอยู่ที่หน้ารุ่น (ส่วนที่ 11) · คงเลขส่วนไว้ให้เลขที่อ้างในเอกสารยังตรง
   -------------------------------------------------------------------------- */


/* --------------------------------------------------------------------------
   7. /dealers.html — ค้นหาร้าน (ชื่อ จังหวัด ที่อยู่) + ใช้ตำแหน่งปัจจุบัน + แผนที่ Google (v8.3 ตามไฟล์ต้นแบบ dealers.html)
      v8.4 แสดงทุกร้านในกล่องเลื่อนขึ้นลง (เลิกปุ่ม "แสดงเพิ่ม" ตามคำสั่ง) · ร้านสมมติไม่มีเบอร์ (build.py ไม่ส่ง) → ขึ้น "เบอร์โทร · รอข้อมูล" (data-var="DEALER_PHONE" · v8.8)
      แผนที่เป็นภาพประกอบก่อน — โหลด Google Maps (iframe) เมื่อกด "เปิดแผนที่" / "ดูบนแผนที่" เท่านั้น
      ไม่มี JS = ไม่มีปุ่มเปิดแผนที่ (hidden) ใช้ลิงก์ "เปิด Google Maps" ใต้แผนที่แทน
   -------------------------------------------------------------------------- */
if ($("#dealer-count")) {
  const telHref = (phone) => "tel:" + String(phone).replace(/[^+0-9]/g, "");
  let matches = [];
  let mapQuery = null;   // v8.8 null = ภาพรวมประเทศไทย (THAILAND_MAP) ไม่ปักจุด
  let mapLatLng = null;

  const mapSrc = () => !mapQuery ? THAILAND_MAP : "https://maps.google.com/maps?q=" + encodeURIComponent(mapQuery) +
    (mapLatLng ? "&ll=" + encodeURIComponent(mapLatLng) + "&z=13" : "") + "&output=embed";

  const closeMap = () => {
    $("#map-live").replaceChildren();
    $("#map-live").hidden = true;
  };
  const openMap = () => {
    const frame = document.createElement("iframe");
    frame.title = "แผนที่ " + $("#map-title").textContent;
    frame.referrerPolicy = "strict-origin-when-cross-origin";   // v9.9 ส่งแค่โดเมน ไม่ส่ง URL หน้าเต็มให้ Google (ตรงกับ meta referrer ของเว็บ)
    frame.src = mapSrc();
    const close = document.createElement("button");
    close.type = "button";
    close.className = "dl-map-close";
    close.textContent = "ปิดแผนที่ ×";
    close.addEventListener("click", () => {
      closeMap();
      $("#load-map").focus();
    });
    $("#map-live").replaceChildren(frame, close);
    $("#map-live").hidden = false;
  };

  // ตั้งพื้นที่ของแผนที่ — ถ้าเปิดแผนที่อยู่แล้วก็โหลดพื้นที่ใหม่เลย · ยังไม่เปิดก็แค่เปลี่ยนป้ายกับลิงก์ Google Maps
  const updateMap = (query, latLng, label) => {
    mapQuery = query;
    mapLatLng = latLng || null;
    $("#map-title").textContent = label || query;
    $("#map-heading").textContent = label || query;
    $("#map-link").href = "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(latLng || query || "Thailand");
    const frame = $("#map-live iframe");
    if (frame) frame.src = mapSrc();
  };

  const action = (text, href) => {
    const a = document.createElement("a");
    a.textContent = text;
    a.href = href;
    return a;
  };

  const dealerCard = (d) => {
    const card = document.createElement("article");
    card.className = "dealer-card";
    const province = document.createElement("span");
    province.className = "dealer-province";
    province.textContent = d.province;
    const title = document.createElement("h3");
    title.textContent = d.name;
    const address = document.createElement("p");
    address.textContent = d.address + (d.hours ? " · " + d.hours : "");
    const actions = document.createElement("div");
    actions.className = "dealer-actions";
    if (d.phone) actions.append(action("โทรหาร้าน", telHref(d.phone)));
    else if (d.placeholder) {
      const pending = document.createElement("span");
      pending.className = "var";
      pending.textContent = "เบอร์โทร · รอข้อมูล";   // v8.8 เดิมขึ้น {{DEALER_PHONE}}
      pending.dataset.var = "DEALER_PHONE";
      pending.title = "ร้านตัวอย่าง — ยังไม่มีเบอร์จริง";
      actions.append(pending);
    }
    if (d.lat && d.lng) {
      const onMap = action("ดูบนแผนที่ ↗", "#map");
      onMap.addEventListener("click", (e) => {
        e.preventDefault();
        updateMap(d.name, `${d.lat},${d.lng}`, d.name);
        openMap();
        $("#map").scrollIntoView({ behavior: reduced.matches ? "auto" : "smooth", block: "nearest" });
      });
      const route = action("เส้นทาง", `https://www.google.com/maps/dir/?api=1&destination=${d.lat},${d.lng}`);
      route.target = "_blank";
      route.rel = "noopener noreferrer";
      actions.append(onMap, route);
    }
    card.append(province, title, address, actions);
    return card;
  };

  const renderDealers = (query) => {
    const q = query.toLowerCase();
    matches = data.dealers.filter((d) => `${d.name} ${d.province} ${d.address}`.toLowerCase().includes(q));
    $("#dealer-results").replaceChildren();
    $("#dealer-results").scrollTop = 0;
    $("#dealer-count").textContent = query
      ? `พบ ${matches.length} ร้าน สำหรับ "${query}"`
      : `ร้านทั้งหมด ${matches.length} แห่ง`;
    if (!matches.length) {
      // การ์ดว่าง (ตามต้นแบบ) — ชวนโทรสำนักงานใหญ่ให้ช่วยหาร้าน
      const empty = document.createElement("div");
      empty.className = "dl-empty";
      const p = document.createElement("p");
      p.textContent = "ยังไม่พบร้านในพื้นที่นี้ ลองจังหวัดใกล้เคียง หรือโทร Hotline ให้ช่วยแนะนำ";
      const tel = $(".dl-hotline a");
      if (tel) {
        const call = action(`โทร ${tel.firstChild.textContent.trim()}`, tel.getAttribute("href"));
        call.className = "pill filled";
        empty.append(p, call);
      } else {
        empty.append(p);
      }
      $("#dealer-results").append(empty);
      return;
    }
    $("#dealer-results").append(...matches.map(dealerCard));
  };

  $("#load-map").hidden = false;
  $("#load-map").addEventListener("click", openMap);

  // v7.7 ชิปจังหวัด — สร้างจากจังหวัดที่มีร้านจริงใน dealers.json พร้อมจำนวนร้าน
  const setChip = (province) => $$("#dealer-chips button").forEach((b) =>
    b.setAttribute("aria-pressed", String(b.dataset.province === province)));
  const provinces = [...new Set(data.dealers.map((d) => d.province).filter(Boolean))];
  $("#dealer-chips").append(...["", ...provinces].map((province) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "pill";
    b.dataset.province = province;
    const n = province ? data.dealers.filter((d) => d.province === province).length : data.dealers.length;
    const small = document.createElement("small");
    small.textContent = n;
    b.append((province || "ทั้งหมด") + " ", small);
    b.addEventListener("click", () => {
      setChip(province);
      $("#dealer-query").value = province;
      updateMap(province ? "FINNIX FILM " + province : null, null, province || "พื้นที่ที่คุณสะดวก");
      renderDealers(province);
    });
    return b;
  }));
  $("#dealer-chips").hidden = false;
  setChip("");

  $("#dealer-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const q = $("#dealer-query").value.trim();
    if (!q) return;
    setChip(provinces.includes(q) ? q : null);
    updateMap("FINNIX FILM " + q, null, q);
    renderDealers(q);
  });

  $("#locate").addEventListener("click", () => {
    const status = $("#location-status");
    if (!navigator.geolocation) {
      status.textContent = "อุปกรณ์นี้ไม่รองรับตำแหน่ง กรุณาพิมพ์พื้นที่ที่ต้องการ";
      return;
    }
    status.textContent = "กำลังขอตำแหน่งจากอุปกรณ์…";
    $("#locate").disabled = true;
    navigator.geolocation.getCurrentPosition((pos) => {
      const { latitude, longitude } = pos.coords;
      updateMap("FINNIX FILM", `${latitude},${longitude}`, "บริเวณตำแหน่งของคุณ");
      // เรียงร้านจากใกล้ไปไกล แล้วแสดงร้านในจังหวัดที่ใกล้ที่สุด
      const nearest = data.dealers
        .filter((d) => d.lat && d.lng)
        .sort((a, b) => Math.hypot(a.lat - latitude, a.lng - longitude) - Math.hypot(b.lat - latitude, b.lng - longitude))[0];
      if (nearest) {
        setChip(nearest.province);
        renderDealers(nearest.province);
      }
      status.textContent = "ตั้งแผนที่ใกล้ตำแหน่งของคุณแล้ว กด \"เปิดแผนที่\" เพื่อดู";
      $("#locate").disabled = false;
    }, () => {
      status.textContent = "ไม่สามารถใช้ตำแหน่งได้ กรุณาพิมพ์จังหวัดหรือเขตแทน";
      $("#locate").disabled = false;
    }, { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 });
  });

  // v8.8 ข้อความ ?experience=1 ("หาร้านที่มีจุดทดลอง") ลบไปพร้อมหน้า /experience.html
  renderDealers("");
}


/* --------------------------------------------------------------------------
   8. ผลงาน — /works.html กรองตามซีรีส์ · แสดงทีละ 12 คัน (v8.2 ตามไฟล์ต้นแบบ works.html · v8.5 เลิกหน้าต่างรายละเอียด)
      + หน้ารุ่น "รถที่ติด <ซีรีส์>" (v10.6 · #sp-work-grid · แสดงทีละแถว)
      v10.5 การ์ดเล็กลง (ผู้สั่งงานสั่ง): 4 คอลัมน์ · ≤1250 3 · ≤760 1 → ทีละ 12 = เต็มแถวพอดีทั้ง 4 และ 3 คอลัมน์ (มือถือ 1 คอลัมน์ทีละ 6 · เดิมทีละ 6 ทุกจอ)
      ไม่มี JS = เห็นครบทุกคัน ปุ่ม "ดูผลงานเพิ่มเติม" ซ่อนอยู่ (hidden) — ไม่มีปุ่มที่กดแล้วไม่ทำอะไร
      v10.4 ภาพจริงทั้งชุดต่อคัน: CSS เลื่อนแนวนอนด้วย scroll-snap (ปัดนิ้วได้แม้ไม่มี JS) · JS เปิดปุ่ม ‹ › + ตัวนับ "1 / 7"
      ปุ่มวนรอบ (ภาพสุดท้าย → ภาพแรก) ไม่ปิดปุ่มที่ปลาย — ปุ่มที่ถูก disabled ตอนโฟกัสอยู่ทำโฟกัสหลุด
   -------------------------------------------------------------------------- */
// 8ก ปุ่มเลื่อนภาพ — ทุกการ์ดผลงานในหน้า
$$(".work-slides").forEach((track) => {
  const nav = track.parentElement.querySelector(".work-nav");
  if (!nav) return;   // คันที่มีภาพเดียวไม่มีปุ่ม
  const total = track.children.length;
  const counter = nav.querySelector(".work-counter");
  let current = -1;
  const show = (index) => {
    if (index === current) return;
    current = index;
    counter.textContent = `${index + 1} / ${total}`;
  };
  const sync = () => {   // อ่านจากตำแหน่งเลื่อนจริง (ปัดนิ้ว · ลากแทร็กแพด · ปุ่มลูกศรคีย์บอร์ด)
    const width = track.clientWidth;
    if (width) show(Math.min(total - 1, Math.max(0, Math.round(track.scrollLeft / width))));   // width 0 = การ์ดถูกซ่อนอยู่
  };
  const go = (step) => {
    sync();
    const target = (Math.max(current, 0) + step + total) % total;
    track.scrollTo({ left: target * track.clientWidth, behavior: reduced.matches ? "auto" : "smooth" });
    show(target);   // ตัวนับเปลี่ยนทันทีที่กด ไม่รอ scroll event
  };
  nav.querySelector(".work-prev").addEventListener("click", () => go(-1));
  nav.querySelector(".work-next").addEventListener("click", () => go(1));
  track.addEventListener("scroll", sync, { passive: true });
  track.addEventListener("work:sync", sync);
  nav.hidden = false;
});

// 8ข กริดการ์ด — แสดงทีละชุด + ห้ามเหลือใบเดียวในแถวสุดท้าย · ใช้ทั้ง /works.html และหน้ารุ่น
// จำนวนคอลัมน์ตามเบรกพอยต์ของ merge.css หมวด 12/15 (4 · ≤1250 → 3 · ≤760 → 1)
const workColumns = () => (matchMedia("(max-width: 760px)").matches ? 1 : matchMedia("(max-width: 1250px)").matches ? 3 : 4);

// unit — หน่วยใน "แสดง X จาก N …" (หน้ารุ่นนับเป็นคัน ให้ตรงกับหัวส่วน "15 คัน" · v10.7)
// v10.7 เลิกตัวนับ "ทั้งหมด · 30 ผลงาน" เหนือตัวกรอง — ชิปบอกจำนวนอยู่แล้ว
function workGrid({ grid, more, status, unit = "ผลงาน", filters = [], first, step }) {
  const cards = [...grid.querySelectorAll(".work-card")];
  let filter = "all";
  let limit = first();
  const matching = () => cards.filter((c) => filter === "all" || c.dataset.series === filter);

  const update = () => {
    const matched = matching();
    const shown = matched.slice(0, limit);
    cards.forEach((c) => { c.hidden = !shown.includes(c); });
    filters.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.filter === filter)));
    // 3 คอลัมน์มี 4 ใบ → 2+2 (.is-pairs) · ยังเหลือใบเดียว (1 ใบ · 5 · 7 · 9 …) → ใบสุดท้ายเต็มแถว (.is-wide)
    const cols = workColumns();
    const pairs = cols === 3 && shown.length === 4;
    const perRow = pairs ? 2 : cols;
    const wide = perRow > 1 && shown.length % perRow === 1 ? shown[shown.length - 1] : null;
    grid.classList.toggle("is-pairs", pairs);
    cards.forEach((c) => c.classList.toggle("is-wide", c === wide));
    more.hidden = matched.length <= limit;
    status.textContent = `แสดง ${shown.length} จาก ${matched.length} ${unit}`;
    // การ์ดที่เพิ่งกลับมาแสดง/เปลี่ยนขนาด — ตำแหน่งเลื่อนอาจถูกรีเซ็ต ให้ตัวนับอ่านใหม่
    grid.querySelectorAll(".work-slides").forEach((t) => t.dispatchEvent(new Event("work:sync")));
  };

  let resizeTimer;
  addEventListener("resize", () => {   // หมุนจอ/ย่อหน้าต่างข้ามเบรกพอยต์ → คิด .is-pairs / .is-wide ใหม่
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(update, 150);
  });
  filters.forEach((b) => b.addEventListener("click", () => {
    filter = b.dataset.filter;
    limit = first();
    update();
  }));
  more.addEventListener("click", () => {
    const firstNew = matching()[limit];
    limit += step();
    update();
    firstNew?.querySelector(".work-film-link, .work-slides")?.focus({ preventScroll: true });
  });
  update();
}

if ($("#work-grid")) {   // /works.html — ทีละ 12 (มือถือ 6) + ปุ่มกรองซีรีส์
  const page = () => (workColumns() === 1 ? 6 : 12);
  workGrid({ grid: $("#work-grid"), more: $("#work-more"), status: $("#work-shown"),
    filters: $$("[data-filter]"), first: page, step: page });
}
if ($("#sp-work-grid")) {   // หน้ารุ่น (v10.6) — แถวแรกแถวเดียว (มือถือ 2 คัน) แล้วเปิดเพิ่มทีละแถว (มือถือทีละ 4)
  workGrid({ grid: $("#sp-work-grid"), more: $("#sp-work-more"), status: $("#sp-work-shown"), unit: "คัน",
    first: () => (workColumns() === 1 ? 2 : workColumns()), step: () => (workColumns() === 1 ? 4 : workColumns()) });
}


/* --------------------------------------------------------------------------
   9. ลูกเล่นตอนเลื่อนถึง (v7.7) — ค่าเริ่มต้นใน CSS คือสภาพสุดท้ายเสมอ
      JS ใส่ .js-play ก่อน (ซ่อน/ย่อ) แล้วใส่ .playing เมื่อเลื่อนถึง · ไม่มี JS หรือตั้งลดการเคลื่อนไหว = เห็นครบทันที
      .light-diagram (หน้าแรก)
   -------------------------------------------------------------------------- */
if ("IntersectionObserver" in window && !reduced.matches) {
  const players = $$(".light-diagram");   // v8.4 เหลือแผนภาพแสงหน้าแรก (heat-meter · layers ไม่มีหน้าที่ใช้แล้ว)
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("playing");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.35 });
  players.forEach((el) => {
    el.classList.add("js-play");
    [...el.children].forEach((child, i) => child.style.setProperty("--i", i));  // ลำดับหน่วงเวลาของลูก
    observer.observe(el);
  });
  // v8.8 ขั้นตอนที่ /experience.html (ขั้นกลางจอสว่างขึ้น) ลบไปพร้อมหน้า
}


/* --------------------------------------------------------------------------
   10. (ว่าง) — เดิม /faq.html ช่องค้นหาคำถาม ลบไปพร้อมหน้าใน v8.4 · คงเลขส่วนไว้
   -------------------------------------------------------------------------- */


/* --------------------------------------------------------------------------
   11. หน้ารุ่น /films/<id>.html (v8.2 ตามไฟล์ต้นแบบ ceramic.html)
       ปุ่มเลือกรหัส → ไฮไลต์คอลัมน์ในตารางสเปก + บอกรหัสที่เลือก · กล่องคำนวณราคา → ไฮไลต์แถวในตารางราคา
       ไม่มี JS = ตารางครบ · กล่องคำนวณซ่อนอยู่ (hidden)
   -------------------------------------------------------------------------- */
if ($("#spec-table")) {
  const table = $("#spec-table");
  const shades = $$(".sp-shade");
  const vltRow = [...table.tBodies[0].rows].find((r) => r.cells[0].textContent.startsWith("แสงส่องผ่าน"));
  const choose = (col) => {
    shades.forEach((b) => b.setAttribute("aria-pressed", String(Number(b.dataset.col) === col)));
    // ช่องที่กินหลายคอลัมน์ (CERAMIC PLUS ยังไม่มีค่า — "รอข้อมูล" ช่องเดียวทั้งแถว) ไม่ไฮไลต์ ไม่งั้นติดสีเฉพาะตอนเลือกรหัสแรก
    [...table.rows].forEach((row) => [...row.cells].forEach((cell, i) => cell.classList.toggle("col-on", i === col && cell.colSpan === 1)));
    $("#sp-selected-code").textContent = table.tHead.rows[0].cells[col].textContent;
    $("#sp-selected-light").textContent = vltRow ? `แสงส่องผ่าน ${vltRow.cells[col].textContent}` : "";
    $("#sp-selection").hidden = false;
  };
  if (shades.length) {
    shades.forEach((b) => b.addEventListener("click", () => choose(Number(b.dataset.col))));
    choose(Math.ceil(shades.length / 2));  // เริ่มที่รหัสกลางแบบต้นแบบ
  }
}

if ($(".sp-estimate")) {
  const box = $(".sp-estimate");
  const rows = $$("#sp-price-table tbody tr");
  const update = () => {
    const car = $("#sp-car").value;
    const col = $('[name="sp-position"]:checked').value === "front" ? 1 : 2;
    const row = rows.find((r) => r.dataset.car === car);
    rows.forEach((r) => {
      r.classList.toggle("row-on", r === row);
      [...r.cells].forEach((c, i) => c.classList.toggle("cell-on", r === row && i === col));
    });
    $("#sp-amount").textContent = row.cells[col].textContent;
    $("#sp-caption").textContent = `${row.cells[0].textContent} · ${col === 1 ? "บานหน้า" : "รอบคัน"} · ${box.dataset.name}`;
  };
  box.hidden = false;
  $("#sp-car").addEventListener("change", update);
  $$('[name="sp-position"]').forEach((r) => r.addEventListener("change", update));
  update();
}
