/* สร้างโดย tools/build.py จาก data/*.json — ห้ามแก้ไฟล์นี้ตรง ๆ แก้ที่ data/ หรือ build.py แล้วรัน python tools/build.py */
window.FINNIX = {
 "carTypes": {
  "pickup2": "กระบะ 2 ประตู",
  "pickup4": "กระบะ 4 ประตู",
  "sedan": "รถเก๋ง",
  "suv": "รถ SUV",
  "mpv": "รถ MPV",
  "van": "รถตู้"
 },
 "series": [
  {
   "id": "titanium",
   "code": "SY",
   "name": "TITANIUM",
   "th": "ฟินนิกซ์ ไทเทเนี่ยม ฟิล์ม",
   "tag": "สุดยอดฟิล์มชั้นนำ เทคโนโลยีระดับโลก",
   "tech": "{{TECH_TITANIUM}}",
   "metalFree": null,
   "heat": "81–96%",
   "heatMax": 96,
   "vlt": "10–40%",
   "vltMax": 40,
   "uv": "99%",
   "variants": [
    {
     "code": "SY40",
     "darkness": null,
     "heat": 81,
     "vlt": 40
    },
    {
     "code": "SY20",
     "darkness": null,
     "heat": 89,
     "vlt": 20
    },
    {
     "code": "SY10",
     "darkness": null,
     "heat": 96,
     "vlt": 10
    }
   ],
   "price": {
    "pickup2": {
     "front": 10600,
     "full": 32000
    },
    "pickup4": {
     "front": 10600,
     "full": 33000
    },
    "sedan": {
     "front": 10600,
     "full": 33800
    },
    "suv": {
     "front": 10600,
     "full": 36000
    },
    "mpv": {
     "front": 10600,
     "full": 37800
    },
    "van": {
     "front": 12000,
     "full": 40600
    }
   },
   "logo": "assets/series/logo-titanium.png"
  },
  {
   "id": "ceramic",
   "code": "CM",
   "name": "CERAMIC",
   "th": "ฟินนิกซ์ เซรามิค ฟิล์ม",
   "tag": "ใส เคลียร์ ชัด",
   "tech": "เซรามิก ไม่มีชั้นโลหะ",
   "metalFree": true,
   "heat": "80–90%",
   "heatMax": 90,
   "vlt": "5–30%",
   "vltMax": 30,
   "uv": "99%",
   "variants": [
    {
     "code": "CM35",
     "darkness": 40,
     "heat": 80,
     "vlt": 30
    },
    {
     "code": "CM15",
     "darkness": 60,
     "heat": 90,
     "vlt": 15
    },
    {
     "code": "CM05",
     "darkness": 80,
     "heat": 90,
     "vlt": 5
    }
   ],
   "price": {
    "pickup2": {
     "front": 5600,
     "full": 10200
    },
    "pickup4": {
     "front": 5600,
     "full": 11000
    },
    "sedan": {
     "front": 5600,
     "full": 11800
    },
    "suv": {
     "front": 5600,
     "full": 13800
    },
    "mpv": {
     "front": 5600,
     "full": 15000
    },
    "van": {
     "front": 8000,
     "full": 17000
    }
   },
   "logo": "assets/series/logo-ceramic.png"
  },
  {
   "id": "ceramic-plus",
   "code": "CM",
   "name": "CERAMIC PLUS",
   "th": "ฟินนิกซ์ เซรามิค พลัส ฟิล์ม",
   "tag": null,
   "tech": "{{TECH_CERAMIC_PLUS}}",
   "metalFree": null,
   "heat": null,
   "heatMax": null,
   "vlt": null,
   "vltMax": null,
   "uv": null,
   "variants": [
    {
     "code": "CM35",
     "darkness": null,
     "heat": null,
     "vlt": null
    },
    {
     "code": "CM15",
     "darkness": null,
     "heat": null,
     "vlt": null
    },
    {
     "code": "CM05",
     "darkness": null,
     "heat": null,
     "vlt": null
    }
   ],
   "price": null,
   "logo": "assets/series/logo-ceramic-plus.png"
  },
  {
   "id": "crystalize",
   "code": "CT",
   "name": "CRYSTALIZE",
   "th": "ฟินนิกซ์ คริสตัลไลซ์ ฟิล์ม",
   "tag": "ฟิล์มกรองแสงใส แต่กันความร้อนได้สูง",
   "tech": "เคลือบโลหะหลายชั้น (sputtering)",
   "metalFree": false,
   "heat": "55–85%",
   "heatMax": 85,
   "vlt": "22–70%",
   "vltMax": 70,
   "uv": "99%",
   "variants": [
    {
     "code": "CT70",
     "darkness": null,
     "heat": 55,
     "vlt": 70
    },
    {
     "code": "CT40",
     "darkness": 40,
     "heat": 75,
     "vlt": 35
    },
    {
     "code": "CT20",
     "darkness": 60,
     "heat": 85,
     "vlt": 22
    }
   ],
   "price": null,
   "logo": "assets/series/logo-crystalize.png"
  },
  {
   "id": "extra-clear",
   "code": "XT",
   "name": "EXTRA CLEAR",
   "th": "ฟินนิกซ์ เอ็กซ์ตร้า เคลียร์",
   "tag": "ใส เคลียร์ ชัด",
   "tech": "เซรามิก ไม่มีชั้นโลหะ",
   "metalFree": true,
   "heat": "61–67%",
   "heatMax": 67,
   "vlt": "5–35%",
   "vltMax": 35,
   "uv": "100%",
   "variants": [
    {
     "code": "XT35",
     "darkness": 40,
     "heat": 61,
     "vlt": 35
    },
    {
     "code": "XT15",
     "darkness": 60,
     "heat": 63,
     "vlt": 15
    },
    {
     "code": "XT05",
     "darkness": 80,
     "heat": 67,
     "vlt": 5
    }
   ],
   "price": null,
   "logo": "assets/series/logo-extra-clear.png"
  },
  {
   "id": "uv-guard",
   "code": "SM",
   "name": "UV GUARD",
   "th": "ฟินนิกซ์ ยูวีการ์ด เซรามิค ฟิล์ม",
   "tag": "ใส เคลียร์ ชัด",
   "tech": "เซรามิก ไม่มีชั้นโลหะ",
   "metalFree": true,
   "heat": "52–63%",
   "heatMax": 63,
   "vlt": "5–40%",
   "vltMax": 40,
   "uv": "100%",
   "variants": [
    {
     "code": "SM35",
     "darkness": 40,
     "heat": 52,
     "vlt": 40
    },
    {
     "code": "SM15",
     "darkness": 60,
     "heat": 59,
     "vlt": 15
    },
    {
     "code": "SM05",
     "darkness": 80,
     "heat": 63,
     "vlt": 5
    }
   ],
   "price": {
    "pickup2": {
     "front": 4000,
     "full": 8600
    },
    "pickup4": {
     "front": 4000,
     "full": 9200
    },
    "sedan": {
     "front": 4000,
     "full": 9800
    },
    "suv": {
     "front": 4000,
     "full": 12000
    },
    "mpv": {
     "front": 4000,
     "full": 14000
    },
    "van": {
     "front": 5400,
     "full": 15800
    }
   },
   "logo": "assets/series/logo-uv-guard.png"
  }
 ],
 "dealers": [
  {
   "id": "fnx-bkk-001",
   "name": "ฟินนิกซ์ เซ็นเตอร์ ลาดพร้าว",
   "tier": "center",
   "address": "999/1 ถ.ลาดพร้าว แขวงจอมพล เขตจตุจักร กรุงเทพฯ 10900",
   "province": "กรุงเทพมหานคร",
   "phone": null,
   "lat": 13.8161,
   "lng": 100.5606,
   "hours": "จ-ส 09:00-18:00",
   "placeholder": true
  },
  {
   "id": "fnx-bkk-002",
   "name": "พระราม 2 ออโต้ฟิล์ม",
   "tier": "automotive",
   "address": "88 ถ.พระราม 2 แขวงแสมดำ เขตบางขุนเทียน กรุงเทพฯ 10150",
   "province": "กรุงเทพมหานคร",
   "phone": null,
   "lat": 13.6608,
   "lng": 100.4419,
   "hours": "ทุกวัน 09:00-19:00",
   "placeholder": true
  },
  {
   "id": "fnx-nbi-001",
   "name": "นนท์ฟิล์ม แคราย",
   "tier": "sub",
   "address": "55/7 ถ.ติวานนท์ ต.บางกระสอ อ.เมือง จ.นนทบุรี 11000",
   "province": "นนทบุรี",
   "phone": null,
   "lat": 13.8622,
   "lng": 100.5218,
   "hours": "จ-ส 08:30-18:00",
   "placeholder": true
  },
  {
   "id": "fnx-cnx-001",
   "name": "เชียงใหม่ คาร์ฟิล์ม",
   "tier": "center",
   "address": "285 ถ.มหิดล ต.ป่าแดด อ.เมือง จ.เชียงใหม่ 50100",
   "province": "เชียงใหม่",
   "phone": null,
   "lat": 18.7654,
   "lng": 98.9876,
   "hours": "จ-ส 09:00-18:00",
   "placeholder": true
  },
  {
   "id": "fnx-plk-001",
   "name": "พิษณุโลก ฟิล์มเฮาส์",
   "tier": "sub",
   "address": "12 ถ.มิตรภาพ ต.ในเมือง อ.เมือง จ.พิษณุโลก 65000",
   "province": "พิษณุโลก",
   "phone": null,
   "lat": 16.8211,
   "lng": 100.2659,
   "hours": "จ-ส 09:00-18:00",
   "placeholder": true
  },
  {
   "id": "fnx-kkn-001",
   "name": "ขอนแก่น พรีเมียมฟิล์ม",
   "tier": "automotive",
   "address": "171 ถ.มิตรภาพ ต.ในเมือง อ.เมือง จ.ขอนแก่น 40000",
   "province": "ขอนแก่น",
   "phone": null,
   "lat": 16.4322,
   "lng": 102.8236,
   "hours": "ทุกวัน 08:30-18:30",
   "placeholder": true
  },
  {
   "id": "fnx-cbi-001",
   "name": "ชลบุรี ออโต้ชิลด์",
   "tier": "automotive",
   "address": "39/4 ถ.สุขุมวิท ต.บ้านสวน อ.เมือง จ.ชลบุรี 20000",
   "province": "ชลบุรี",
   "phone": null,
   "lat": 13.3611,
   "lng": 100.9847,
   "hours": "จ-ส 09:00-18:00",
   "placeholder": true
  },
  {
   "id": "fnx-hkt-001",
   "name": "ภูเก็ต ซันบล็อกฟิล์ม",
   "tier": "sub",
   "address": "77 ถ.เทพกระษัตรี ต.รัษฎา อ.เมือง จ.ภูเก็ต 83000",
   "province": "ภูเก็ต",
   "phone": null,
   "lat": 7.8906,
   "lng": 98.3984,
   "hours": "จ-ส 09:00-18:00",
   "placeholder": true
  },
  {
   "id": "fnx-ska-001",
   "name": "หาดใหญ่ ฟิล์มโปร",
   "tier": "sub",
   "address": "246 ถ.กาญจนวนิช ต.หาดใหญ่ อ.หาดใหญ่ จ.สงขลา 90110",
   "province": "สงขลา",
   "phone": null,
   "lat": 7.0086,
   "lng": 100.4747,
   "hours": "จ-ส 09:00-18:00",
   "placeholder": true
  }
 ]
};
window.FINNIX_JOURNEY = {
 "heroFilm": "ceramic",
 "needToFilm": {
  "heat": "titanium",
  "clarity": "crystalize",
  "privacy": "ceramic",
  "balance": "uv-guard"
 },
 "needAlternatives": {
  "heat": [
   "ceramic",
   "crystalize"
  ],
  "clarity": [
   "titanium",
   "uv-guard"
  ],
  "privacy": [
   "extra-clear",
   "uv-guard"
  ],
  "balance": [
   "ceramic",
   "titanium"
  ]
 },
 "needMappingConfirmed": false,
 "needPhoto": {
  "heat": {
   "src": "assets/Page/1.jpg",
   "alt": "ครอบครัวนั่งในรถยามแดดเย็น คนขับใส่แว่นกันแดด ลูกหลับสบายอยู่เบาะหลัง",
   "x": "62%"
  },
  "clarity": {
   "src": "assets/Page/2.jpg",
   "alt": "มุมมองคนขับผ่านกระจกหน้ารถ เห็นถนนและตึกในเมืองชัดเจนตอนแดดเย็น",
   "x": "50%"
  },
  "privacy": {
   "src": "assets/Page/3.jpg",
   "alt": "กระจกข้างรถสีเข้มสะท้อนตึกยามเย็น เห็นผู้โดยสารด้านในเพียงรางๆ",
   "x": "68%"
  },
  "balance": {
   "src": "assets/Page/4.jpg",
   "alt": "รถ SUV สีดำจอดริมแม่น้ำเจ้าพระยา ฉากหลังวัดอรุณฯ ยามพระอาทิตย์ตก",
   "x": "70%"
  }
 }
};
