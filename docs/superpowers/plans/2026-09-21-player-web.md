# เว็บผู้เล่นและ DM (Firebase) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** เว็บที่ผู้เล่น 6 คนเลือกชื่อแล้วดูชีท เลือกอาวุธ ดูสกิลทรี ซื้อของ และ DM ดูชีททุกคน กดปลดท่า แก้เงินและของ

**Architecture:** เว็บสถิต (HTML + ES modules ไม่มีขั้น build) โฮสต์บน Firebase Hosting อ่านเขียน Firestore แบบเรียลไทม์ ผู้เล่นเข้าด้วย Auth แบบ anonymous แล้วเลือกชื่อ ส่วน DM ล็อกอินอีเมล+รหัสผ่าน กฎ Firestore กันผู้เล่นแก้สถานะ ปลดท่า และจองอาวุธซ้ำ ข้อมูลกติกา (ต้นสกิล ของในร้าน) เป็นไฟล์ JSON แปลงจากไฟล์ `.md` ด้วยสคริปต์

**Tech Stack:** Firebase (Hosting, Firestore, Auth) SDK 10.12.2 ผ่าน CDN · Node ≥ 20 (`node:test` ไม่ใช้เฟรมเวิร์กทดสอบ) · `@firebase/rules-unit-testing` + Firebase Emulator (ต้องมี Java) · `firebase-admin` สำหรับสคริปต์ seed

**Spec:** `docs/superpowers/specs/2026-09-21-player-web-design.md` (อ่านคู่กับแผนนี้)

## Global Constraints

- **ไม่มี PIN:** ผู้เล่น anonymous auth + เลือกชื่อเก็บใน `localStorage` (คีย์ `stage.playerId`) · DM คืออีเมล `dm@stage.local` เท่านั้น (ค่าคงที่ตายตัวทั้งในกฎและใน `firebase.js`)
- ผู้เล่น 6 คน id/ชื่อ: `gun`=กัน · `anvas`=อันวาส · `pongpaeng`=ป๋องแป๋ง · `hong`=หง · `dream`=ดรีม · `phet`=เพชร
- เงินเก็บเป็นจำนวนเต็มทองแดง: 1 ทอง = 10 เงิน = 100 ทองแดง (ทอง=100 ทองแดง, เงิน=10 ทองแดง)
- อาวุธ 6 ชนิดห้ามซ้ำ (`weapons/{id}.claimedBy`) เลือกแล้วล็อก DM รีเซ็ตได้ · ทางเลือก "ไม่ผูกอาวุธ" ใช้ `path: "unbound"`
- **DM เท่านั้นที่ปลดท่า** และเท่านั้นที่แก้สถานะ (level hp maxHp ac abilities notes unlocked unboundCenter) ผู้เล่นแก้ได้แค่ `copper` (ลดลงเท่านั้น และตอนร้านเปิด) `inventory` และ `path`/`weaponId` ครั้งแรก
- ข้อมูลที่ส่งไปเบราว์เซอร์ผู้เล่นต้องไม่มีคำว่า **ผนึก / ตื่นพลัง / กลับบ้าน** (ตัวแปลงต้องล้มถ้าเจอ) · วงที่ 2-3 ของต้นสกิลไม่ใส่
- ไม่มีขั้น build · ไม่ใช้เฟรมเวิร์ก UI · ไม่ทำ: ทอยลูกเต๋า แชต ระบบต่อสู้ น้ำหนักของ รูปโปรไฟล์ ปุ่ม "ขอปลดท่า" การตรวจราคาฝั่งเซิร์ฟเวอร์ ราคาผู้กล้า +20%
- โปรเจกต์ไม่ใช่ git repo: ทุก Task จบที่ขั้น "รันตรวจ" ไม่มีขั้น commit · ทุกคำสั่ง `npm`/`node` รันในโฟลเดอร์ `web/`
- ส่วนที่ผมเสนอเพิ่มจากสเปก (ให้ตรวจ): ท่ากลางของ "ไม่ผูกอาวุธ" ให้ **DM เป็นคนเลือกให้** (`unboundCenter`) · ท่าลับที่ DM ปลดแล้วขึ้นข้อความ "✨ ท่าลับปลดแล้ว — DM จะแจ้งรายละเอียด" เพราะ JSON ไม่เก็บรายละเอียดท่าลับ · ของในกระเป๋าเก็บ `{itemId, name, qty}` (ชื่อคัดลอกมาตอนเพิ่ม) จึงเพิ่มของที่ไม่มีในร้านได้

---

## File Structure

```
web/
  package.json               scripts + devDependencies
  firebase.json              hosting + firestore rules + emulator port
  firestore.rules            กฎความปลอดภัย
  public/
    index.html               เปลือกหน้าเดียว
    css/style.css            ธีมหน้าต่างเกม
    data/{weapons,unbound,items}.json   สร้างโดย tools/convert.mjs (items เขียนมือ)
    js/
      money.js               แปลง/แสดงเงิน (ฟังก์ชันล้วน)
      players.js             รายชื่อผู้เล่น 6 คน (ใช้ทั้งเว็บและ seed)
      firebase-config.js     ค่า config จาก Firebase Console (ผู้ใช้กรอก)
      firebase.js            init + auth + re-export ฟังก์ชัน Firestore
      ui.js                  h() สร้าง DOM, mount()
      data.js                loadData()
      app.js                 router (#/ #/me #/dm #/dm/<id>)
      player.js              หน้าผู้เล่น: สถานะ · อาวุธและสกิล · ร้านค้า
      dm.js                  หน้า DM: ภาพรวม · รายละเอียดผู้เล่น
  tools/
    convert.mjs              .md -> JSON + ตรวจคำต้องห้าม
    overrides.json           แก้ข้อความที่มีคำต้องห้าม (เริ่มเป็น {})
    seed.mjs                 สร้างเอกสารเริ่มต้น + บัญชี DM
  test/
    money.test.mjs · convert.test.mjs · rules.test.mjs
```

---

### Task 1: โครงโปรเจกต์และโมดูลเงิน

**Files:**
- Create: `web/package.json`, `web/public/js/money.js`, `web/public/js/players.js`
- Test: `web/test/money.test.mjs`

**Interfaces:**
- Produces: `money.js` → `toCopper({gold?,silver?,copper?}): number` · `format(total: number): string` (โยน `RangeError` ถ้าไม่ใช่จำนวนเต็ม ≥ 0) · `players.js` → `PLAYERS: {id:string,name:string}[]`

- [ ] **Step 1: สร้าง `web/package.json` แล้วติดตั้ง**

```json
{
  "name": "stage-web",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "node --test test/money.test.mjs test/convert.test.mjs",
    "test:rules": "firebase emulators:exec --project stage-test --only firestore \"node --test test/rules.test.mjs\"",
    "convert": "node tools/convert.mjs",
    "seed": "node tools/seed.mjs",
    "serve": "firebase emulators:start --only hosting,firestore"
  },
  "devDependencies": {
    "@firebase/rules-unit-testing": "^3.0.4",
    "firebase": "^10.12.2",
    "firebase-admin": "^12.1.0",
    "firebase-tools": "^13.9.0"
  }
}
```

Run: `cd web && npm install` · Expected: ติดตั้งเสร็จไม่มี error (ต้องมี Node ≥ 20 · ถ้า `node -v` ต่ำกว่านี้ ให้อัปเดตก่อน)

- [ ] **Step 2: เขียนเทสต์ที่ล้ม `web/test/money.test.mjs`**

```js
import test from "node:test";
import assert from "node:assert/strict";
import { toCopper, format } from "../public/js/money.js";

test("toCopper: 1 ทอง = 100, 1 เงิน = 10", () => {
  assert.equal(toCopper({ gold: 2, silver: 3, copper: 5 }), 235);
  assert.equal(toCopper({ silver: 1 }), 10);
  assert.equal(toCopper({}), 0);
});

test("format: ไม่แสดงหน่วยที่เป็นศูนย์", () => {
  assert.equal(format(235), "2 ทอง 3 เงิน 5 ทองแดง");
  assert.equal(format(100), "1 ทอง");
  assert.equal(format(10), "1 เงิน");
  assert.equal(format(0), "0 ทองแดง");
});

test("format: ค่าติดลบหรือทศนิยมโยน RangeError", () => {
  assert.throws(() => format(-1), RangeError);
  assert.throws(() => format(1.5), RangeError);
});
```

- [ ] **Step 3: รันให้เห็นว่าล้ม**

Run: `npm test -- test/money.test.mjs` (หรือ `node --test test/money.test.mjs`) · Expected: FAIL (`Cannot find module .../money.js`)

- [ ] **Step 4: เขียน `web/public/js/money.js` และ `web/public/js/players.js`**

```js
// money.js — เงินเก็บเป็นทองแดงจำนวนเต็ม: 1 ทอง = 10 เงิน = 100 ทองแดง
export const toCopper = ({ gold = 0, silver = 0, copper = 0 }) => gold * 100 + silver * 10 + copper;

export function format(total) {
  if (!Number.isInteger(total) || total < 0) throw new RangeError("copper must be a non-negative integer");
  const g = Math.floor(total / 100), s = Math.floor((total % 100) / 10), c = total % 10;
  const parts = [[g, "ทอง"], [s, "เงิน"], [c, "ทองแดง"]].filter(([n]) => n > 0).map(([n, u]) => `${n} ${u}`);
  return parts.length ? parts.join(" ") : "0 ทองแดง";
}
```

```js
// players.js — ใช้ทั้งเว็บและ tools/seed.mjs
export const PLAYERS = [
  { id: "gun", name: "กัน" },
  { id: "anvas", name: "อันวาส" },
  { id: "pongpaeng", name: "ป๋องแป๋ง" },
  { id: "hong", name: "หง" },
  { id: "dream", name: "ดรีม" },
  { id: "phet", name: "เพชร" },
];
```

- [ ] **Step 5: รันตรวจ**

Run: `node --test test/money.test.mjs` · Expected: PASS ทั้ง 3 เทสต์

---

### Task 2: ตัวแปลงข้อมูลกติกาเป็น JSON

**Files:**
- Create: `web/tools/convert.mjs`, `web/tools/overrides.json` (เริ่มเป็น `{}`), `web/public/data/items.json`
- Generate: `web/public/data/weapons.json`, `web/public/data/unbound.json`
- Test: `web/test/convert.test.mjs`

**Interfaces:**
- Produces (`convert.mjs` export): `convertWeapons(md: string)`, `convertUnbound(md: string)`, `assertSafe(obj)` (โยน `Error` ถ้าเจอคำต้องห้าม), `build(read?)` → `{ weapons, unbound }` (ใช้ overrides แล้ว `assertSafe`)
- Produces (รูปแบบ JSON): `weapons.json` = `[{id:"sword",name:"ดาบ",fullName,role,hitDie,center:{name,effect},moves:[{id:"sword-1",slot:1,name,effect,unlock,tier,secret:false} | {id:"sword-6",slot:6,tier,secret:true}]}]` · `unbound.json` = `{center:[{id:"u-c1",name,who,effect,stat}], ring1:[{id:"u-1",slot,name,effect,unlock,tier}]}` · `items.json` = `[{id,name,price(ทองแดง),desc,category}]`
- id ของอาวุธ: `sword` `shield` `bow` `codex` `guitar` `staff` (ดาบ โล่ ธนู คัมภีร์ กีต้าร์ คฑา ตามลำดับหัวข้อ 3-8 ของ `weapon-trees.md`)

- [ ] **Step 1: เขียนเทสต์ที่ล้ม `web/test/convert.test.mjs`**

```js
import test from "node:test";
import assert from "node:assert/strict";
import { build, assertSafe } from "../tools/convert.mjs";

test("weapons: 6 อาวุธ ท่ากลาง 1 วงที่ 1 ครบ 10 ท่า ท่าลับ 1 ท่า", () => {
  const { weapons } = build();
  assert.deepEqual(weapons.map((w) => w.id), ["sword", "shield", "bow", "codex", "guitar", "staff"]);
  for (const w of weapons) {
    assert.ok(w.center.name && w.center.effect, `${w.id} center`);
    assert.deepEqual(w.moves.map((m) => m.slot), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], w.id);
    assert.equal(w.moves.filter((m) => m.secret).length, 1, `${w.id} secret`);
    for (const m of w.moves.filter((x) => x.secret)) assert.equal(m.name, undefined);
  }
  assert.equal(weapons[0].moves[0].name, "ดาบสวนกลับ");
  assert.equal(weapons[0].center.name, "ดาบแห่งรุ่งแสง");
});

test("unbound: ท่ากลาง 12 และวิชาวงที่ 1 ครบ 10", () => {
  const { unbound } = build();
  assert.equal(unbound.center.length, 12);
  assert.equal(unbound.ring1.length, 10);
  assert.equal(unbound.center[0].name, "ปฐมพยาบาลแห่งโลกเดิม");
  assert.equal(unbound.ring1[0].name, "วิชาดาบสามัญ");
});

test("ข้อมูลที่จะส่งให้ผู้เล่นไม่มีคำต้องห้าม", () => {
  const out = JSON.stringify(build());
  for (const w of ["ผนึก", "ตื่นพลัง", "กลับบ้าน"]) assert.ok(!out.includes(w), w);
});

test("assertSafe โยน Error เมื่อเจอคำต้องห้ามและบอก id", () => {
  assert.throws(() => assertSafe({ moves: [{ id: "x-1", effect: "ถูกผนึก" }] }), /x-1/);
});
```

- [ ] **Step 2: รันให้เห็นว่าล้ม**

Run: `node --test test/convert.test.mjs` · Expected: FAIL (`Cannot find module .../convert.mjs`)

- [ ] **Step 3: เขียน `web/tools/convert.mjs`**

```js
// แปลง weapon-trees.md / unbound-path.md เป็น JSON ที่ส่งให้ผู้เล่นได้ (ไม่มีวงที่ 2-3 ไม่มีคำต้องห้าม)
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..");
const OVERRIDES = path.join(HERE, "overrides.json");
const BANNED = ["ผนึก", "ตื่นพลัง", "กลับบ้าน"];

// ลำดับตามหัวข้อ 3-8 ของ weapon-trees.md · role/hitDie จาก weapons.md หัวข้อ 2
const WEAPONS = [
  { id: "sword", key: "ดาบ", role: "นักดวลโจมตีจุดเดียว", hitDie: "d10" },
  { id: "shield", key: "โล่", role: "ผู้ปกป้องทีม", hitDie: "d10" },
  { id: "bow", key: "ธนู", role: "ระยะไกล + สอดแนม", hitDie: "d8" },
  { id: "codex", key: "คัมภีร์", role: "เวทโจมตี + ความรู้", hitDie: "d6" },
  { id: "guitar", key: "กีต้าร์", role: "เสริม/ลดพลังด้วยดนตรี", hitDie: "d8" },
  { id: "staff", key: "คฑา", role: "ผู้รักษา + ผู้ปกป้อง", hitDie: "d8" },
];

const clean = (s) => s.replace(/\*\*|\*/g, "").trim();
const cells = (line) => line.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
const isRow = (l) => /^\|\s*\d+\s*\|/.test(l);

// บรรทัดใต้หัวข้อระดับ `level` ที่ test ผ่าน จนถึงหัวข้อระดับเดียวกันหรือสูงกว่าถัดไป
function section(lines, test, level) {
  const start = lines.findIndex((l) => l.startsWith("#".repeat(level) + " ") && test(l));
  if (start < 0) throw new Error("ไม่พบหัวข้อ");
  let end = lines.length;
  for (let i = start + 1; i < lines.length; i++) {
    const m = lines[i].match(/^(#+) /);
    if (m && m[1].length <= level) { end = i; break; }
  }
  return lines.slice(start + 1, end);
}

export function convertWeapons(md) {
  const lines = md.split("\n");
  return WEAPONS.map((w) => {
    const at = (l) => l.includes(` ${w.key} — `);
    const sec = section(lines, at, 2);
    const title = lines.find((l) => l.startsWith("## ") && at(l));
    const ci = sec.findIndex((l) => l.startsWith("### ● กลาง"));
    const center = {
      name: clean(sec[ci].replace(/^### ● กลาง:\s*/, "").replace(/\*\([^)]*\)\*/, "")),
      effect: clean(sec.slice(ci + 1).find((l) => l.trim())),
    };
    const ri = sec.findIndex((l) => l.startsWith("### วงที่ 1"));
    const rows = [];
    for (let i = ri + 1; i < sec.length && !sec[i].startsWith("#"); i++) if (isRow(sec[i])) rows.push(cells(sec[i]));
    const moves = rows.map(([slot, name, effect, unlock, tier]) => {
      const id = `${w.id}-${slot}`;
      if (name.includes("ลับ")) return { id, slot: +slot, tier, secret: true }; // ท่าลับ: ไม่ส่งชื่อ/ผล/เงื่อนไข
      return { id, slot: +slot, name: clean(name), effect: clean(effect), unlock: clean(unlock), tier, secret: false };
    });
    return { id: w.id, name: w.key, fullName: clean(title.split(" — ")[1]), role: w.role, hitDie: w.hitDie, center, moves };
  });
}

export function convertUnbound(md) {
  const lines = md.split("\n");
  const center = section(lines, (l) => l.includes("ท่ากลาง"), 2).filter(isRow).map(cells)
    .map(([n, name, who, effect, stat]) => ({ id: `u-c${n}`, name: clean(name), who, effect: clean(effect), stat }));
  const ring1 = section(lines, (l) => l.startsWith("### ตารางวิชา"), 3).filter(isRow).map(cells)
    .map(([slot, name, effect, learn, quest, tier]) => ({
      id: `u-${slot}`, slot: +slot, name: clean(name), effect: clean(effect),
      unlock: `${clean(learn)} · ภารกิจฝึก: ${clean(quest)}`, tier,
    }));
  return { center, ring1 };
}

export function assertSafe(obj) {
  const hits = [];
  (function walk(v, p) {
    if (typeof v === "string") { for (const b of BANNED) if (v.includes(b)) hits.push(`${p}: "${b}"`); }
    else if (v && typeof v === "object") {
      const here = v.id ? `${p}<${v.id}>` : p;
      for (const [k, x] of Object.entries(v)) walk(x, `${here}.${k}`);
    }
  })(obj, "$");
  if (hits.length) throw new Error("คำต้องห้ามหลุดเข้าข้อมูลผู้เล่น (แก้ใน tools/overrides.json ด้วย id ของท่า):\n" + hits.join("\n"));
}

export function build(read = (f) => readFileSync(path.join(ROOT, f), "utf8")) {
  const weapons = convertWeapons(read("weapon-trees.md"));
  const unbound = convertUnbound(read("unbound-path.md"));
  const ov = existsSync(OVERRIDES) ? JSON.parse(readFileSync(OVERRIDES, "utf8")) : {};
  for (const m of [...weapons.flatMap((w) => w.moves), ...unbound.ring1]) Object.assign(m, ov[m.id] ?? {});
  assertSafe({ weapons, unbound });
  return { weapons, unbound };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const { weapons, unbound } = build();
  const dir = path.join(ROOT, "web", "public", "data");
  mkdirSync(dir, { recursive: true });
  const out = (f, d) => writeFileSync(path.join(dir, f), JSON.stringify(d, null, 1) + "\n");
  out("weapons.json", weapons);
  out("unbound.json", unbound);
  console.log(`weapons ${weapons.length} · unbound center ${unbound.center.length} ring1 ${unbound.ring1.length}`);
}
```

และสร้าง `web/tools/overrides.json` เป็น `{}`

- [ ] **Step 4: รันเทสต์ และแก้ข้อความที่มีคำต้องห้าม (ถ้ามี)**

Run: `node --test test/convert.test.mjs`
Expected: ผ่านทั้งหมด **หรือ** ล้มที่ "คำต้องห้ามหลุดเข้าข้อมูลผู้เล่น" พร้อมรายการ เช่น `$<...>: "ผนึก"` ถ้าล้ม ให้เพิ่มใน `tools/overrides.json` โดยใช้ id ของท่าในรายการนั้น เขียนข้อความใหม่ที่ **คงเงื่อนไขไว้แต่ตัดคำต้องห้ามออก** เช่น

```json
{
  "sword-1": { "unlock": "ภารกิจล่าสไลม์ 10 ตัว + ภารกิจเฉพาะตัวของดาบ: ทำให้แม่ทัพมารยอมจำนนด้วยการโจมตีของตัวเอง" }
}
```

รันซ้ำจนผ่าน (ท่าลับไม่มีข้อความจึงไม่ต้อง override)

- [ ] **Step 5: สร้างไฟล์ข้อมูลและ `items.json`**

Run: `node tools/convert.mjs` · Expected: พิมพ์ `weapons 6 · unbound center 12 ring1 10` และมี `public/data/weapons.json`, `unbound.json`

สร้าง `web/public/data/items.json` (ราคาเป็นทองแดง จากตารางร้านใน `locations/`; DM เพิ่มของนอกร้านผ่านหน้า DM ได้เสมอ ส่วนการเพิ่มสินค้าในร้านคือแก้ไฟล์นี้):

```json
[
  { "id": "book-sword", "name": "ตำราท่าดาบพื้นฐานฉบับชาวบ้าน", "price": 500, "desc": "ตำรา 5 เหรียญทอง", "category": "ตำรา" },
  { "id": "book-defend", "name": "ตำราป้องกันตัว", "price": 500, "desc": "ตำรา 5 เหรียญทอง", "category": "ตำรา" },
  { "id": "book-archery", "name": "ตำรายิงธนูมือใหม่", "price": 200, "desc": "ตำรา 2 เหรียญทอง", "category": "ตำรา" },
  { "id": "book-monster", "name": "คู่มือมอนสเตอร์ (ย่อ)", "price": 100, "desc": "อ่านแล้วตอบคำถามทดสอบได้", "category": "ตำรา" },
  { "id": "herb", "name": "สมุนไพร (ต่อชนิด)", "price": 10, "desc": "1 เหรียญเงินต่อชนิด", "category": "วัตถุดิบ" },
  { "id": "feather", "name": "ขนนก (ต่อเส้น)", "price": 10, "desc": "1 เหรียญเงินต่อเส้น", "category": "วัตถุดิบ" },
  { "id": "ration", "name": "เสบียงติดตัว (ต่อวัน)", "price": 50, "desc": "5 เหรียญเงินต่อวัน", "category": "เสบียง" }
]
```

- [ ] **Step 6: รันตรวจรอบสุดท้าย**

Run: `node --test test/money.test.mjs test/convert.test.mjs` · Expected: PASS ทั้งหมด และ `grep -c "ผนึก" public/data/*.json` ต้องได้ 0 ทุกไฟล์

---

### Task 3: กฎความปลอดภัย Firestore และสคริปต์ seed

**Files:**
- Create: `web/firebase.json`, `web/firestore.rules`, `web/tools/seed.mjs`
- Test: `web/test/rules.test.mjs`

**Interfaces:**
- Produces (โครงเอกสารที่ Task 4-6 ใช้): `players/{id}` = `{name, level, hp, maxHp, ac, abilities:{str,dex,con,int,wis,cha}, notes, copper, inventory:[{itemId|null,name,qty}], path: null|"weapon"|"unbound", weaponId: null|string, unboundCenter: null|string, unlocked: string[]}` · `weapons/{id}` = `{claimedBy: null|string}` · `config/game` = `{shopOpen: boolean}` · `log/{auto}` = `{playerId, type, detail, ts}`
- DM ในกฎ = `request.auth.token.get('email','') == 'dm@stage.local'`

- [ ] **Step 1: เขียน `web/firebase.json`**

```json
{
  "hosting": { "public": "public", "ignore": ["firebase.json", "**/.*", "**/node_modules/**"] },
  "firestore": { "rules": "firestore.rules" },
  "emulators": { "firestore": { "port": 8080 }, "hosting": { "port": 5000 }, "ui": { "enabled": false } }
}
```

- [ ] **Step 2: เขียนเทสต์กฎที่ล้ม `web/test/rules.test.mjs`**

```js
import test, { before, after, beforeEach } from "node:test";
import { readFileSync } from "node:fs";
import { initializeTestEnvironment, assertSucceeds, assertFails } from "@firebase/rules-unit-testing";

let env;
before(async () => {
  env = await initializeTestEnvironment({
    projectId: "stage-test",
    firestore: { rules: readFileSync(new URL("../firestore.rules", import.meta.url), "utf8") },
  });
});
after(() => env.cleanup());
beforeEach(async () => {
  await env.clearFirestore();
  await env.withSecurityRulesDisabled(async (ctx) => {
    const db = ctx.firestore();
    await db.doc("config/game").set({ shopOpen: true });
    await db.doc("players/gun").set({ name: "กัน", level: 1, copper: 500, inventory: [], path: null, weaponId: null, unboundCenter: null, unlocked: [] });
    await db.doc("weapons/sword").set({ claimedBy: null });
    await db.doc("weapons/bow").set({ claimedBy: null });
  });
});
const player = () => env.authenticatedContext("anon-1").firestore();
const dm = () => env.authenticatedContext("dm-1", { email: "dm@stage.local" }).firestore();
const asAdmin = (fn) => env.withSecurityRulesDisabled((ctx) => fn(ctx.firestore()));

test("ผู้เล่นแก้สถานะและปลดท่าเองไม่ได้", async () => {
  await assertFails(player().doc("players/gun").update({ level: 9 }));
  await assertFails(player().doc("players/gun").update({ unlocked: ["sword-1"] }));
});

test("DM แก้สถานะและปลดท่าได้", async () => {
  await assertSucceeds(dm().doc("players/gun").update({ level: 2, unlocked: ["sword-1"] }));
});

test("ผู้เล่นซื้อของได้เมื่อร้านเปิด (เงินลด ของเพิ่ม)", async () => {
  await assertSucceeds(player().doc("players/gun").update({ copper: 400, inventory: [{ itemId: "herb", name: "สมุนไพร", qty: 1 }] }));
});

test("ผู้เล่นเพิ่มเงินให้ตัวเองไม่ได้", async () => {
  await assertFails(player().doc("players/gun").update({ copper: 900 }));
});

test("ร้านปิดอยู่ ผู้เล่นซื้อไม่ได้", async () => {
  await asAdmin((db) => db.doc("config/game").set({ shopOpen: false }));
  await assertFails(player().doc("players/gun").update({ copper: 400, inventory: [] }));
});

test("จองอาวุธ: batch จองอาวุธ + ตั้ง path ผ่านได้", async () => {
  const db = player();
  const b = db.batch();
  b.update(db.doc("weapons/sword"), { claimedBy: "gun" });
  b.update(db.doc("players/gun"), { path: "weapon", weaponId: "sword" });
  await assertSucceeds(b.commit());
});

test("จองอาวุธที่มีคนจองแล้วไม่ได้", async () => {
  await asAdmin((db) => db.doc("weapons/sword").set({ claimedBy: "dream" }));
  const db = player();
  const b = db.batch();
  b.update(db.doc("weapons/sword"), { claimedBy: "gun" });
  b.update(db.doc("players/gun"), { path: "weapon", weaponId: "sword" });
  await assertFails(b.commit());
});

test("ตั้ง weaponId โดยไม่จองอาวุธจริงไม่ได้", async () => {
  await assertFails(player().doc("players/gun").update({ path: "weapon", weaponId: "bow" }));
});

test("เลือกไม่ผูกอาวุธได้ครั้งแรก แต่เปลี่ยนภายหลังไม่ได้", async () => {
  await assertSucceeds(player().doc("players/gun").update({ path: "unbound" }));
  await assertFails(player().doc("players/gun").update({ path: "weapon", weaponId: "bow" }));
});

test("DM รีเซ็ตอาวุธได้", async () => {
  await asAdmin(async (db) => {
    await db.doc("weapons/sword").set({ claimedBy: "gun" });
    await db.doc("players/gun").update({ path: "weapon", weaponId: "sword" });
  });
  const db = dm();
  const b = db.batch();
  b.update(db.doc("weapons/sword"), { claimedBy: null });
  b.update(db.doc("players/gun"), { path: null, weaponId: null, unlocked: [] });
  await assertSucceeds(b.commit());
});

test("ผู้เล่นแก้ config/game ไม่ได้ และอ่าน log ไม่ได้ แต่เขียน log ได้", async () => {
  await assertFails(player().doc("config/game").update({ shopOpen: false }));
  await assertSucceeds(player().collection("log").add({ playerId: "gun", type: "buy", detail: "x", ts: new Date() }));
  await assertFails(player().collection("log").get());
  await assertSucceeds(dm().collection("log").get());
});
```

- [ ] **Step 3: รันให้เห็นว่าล้ม**

Run: `npm run test:rules` · Expected: FAIL (ยังไม่มี `firestore.rules` → error `ENOENT`) · (ต้องมี Java: `java -version`)

- [ ] **Step 4: เขียน `web/firestore.rules`**

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    function signedIn() { return request.auth != null; }
    function isDM() { return signedIn() && request.auth.token.get('email', '') == 'dm@stage.local'; }
    function changed() { return request.resource.data.diff(resource.data).affectedKeys(); }
    function shopOpen() { return get(/databases/$(database)/documents/config/game).data.shopOpen == true; }

    match /players/{id} {
      allow read: if signedIn();
      allow create, delete: if isDM();
      allow update: if isDM()
        // ซื้อของ: เงินลดเท่านั้น และต้องร้านเปิด
        || (signedIn() && shopOpen() && changed().hasOnly(['copper', 'inventory'])
            && request.resource.data.copper >= 0 && request.resource.data.copper <= resource.data.copper)
        // เลือกเส้นทางครั้งแรกครั้งเดียว
        || (signedIn() && resource.data.path == null && changed().hasOnly(['path', 'weaponId'])
            && ((request.resource.data.path == 'unbound' && request.resource.data.weaponId == null)
                || (request.resource.data.path == 'weapon'
                    && getAfter(/databases/$(database)/documents/weapons/$(request.resource.data.weaponId)).data.claimedBy == id)));
    }

    match /weapons/{w} {
      allow read: if signedIn();
      allow create, delete: if isDM();
      allow update: if isDM()
        || (signedIn() && resource.data.claimedBy == null && changed().hasOnly(['claimedBy'])
            && request.resource.data.claimedBy is string);
    }

    match /config/{doc} {
      allow read: if signedIn();
      allow write: if isDM();
    }

    match /log/{entry} {
      allow read, delete: if isDM();
      allow create: if signedIn() && request.resource.data.keys().hasOnly(['playerId', 'type', 'detail', 'ts']);
    }
  }
}
```

- [ ] **Step 5: รันตรวจ**

Run: `npm run test:rules` · Expected: PASS ทั้ง 11 เทสต์ (ถ้ามีเทสต์ล้ม ให้แก้กฎ ไม่ใช่แก้เทสต์)

- [ ] **Step 6: เขียน `web/tools/seed.mjs`** (รันครั้งเดียวตอน deploy ใน Task 7)

```js
// ใช้: node tools/seed.mjs <serviceAccount.json> <รหัสผ่าน DM>
// ใช้ batch.create: ถ้าเคย seed แล้วจะล้มโดยไม่ทับข้อมูลเดิม
import { readFileSync } from "node:fs";
import { initializeApp, cert } from "firebase-admin/app";
import { getAuth } from "firebase-admin/auth";
import { getFirestore } from "firebase-admin/firestore";
import { PLAYERS } from "../public/js/players.js";

const [keyPath, dmPassword] = process.argv.slice(2);
if (!keyPath || !dmPassword) { console.error("usage: node tools/seed.mjs <serviceAccount.json> <dm-password>"); process.exit(1); }
initializeApp({ credential: cert(JSON.parse(readFileSync(keyPath, "utf8"))) });
const db = getFirestore();
const weapons = JSON.parse(readFileSync(new URL("../public/data/weapons.json", import.meta.url), "utf8"));

const b = db.batch();
for (const p of PLAYERS) {
  b.create(db.doc(`players/${p.id}`), {
    name: p.name, level: 1, hp: 10, maxHp: 10, ac: 10,
    abilities: { str: 10, dex: 10, con: 10, int: 10, wis: 10, cha: 10 },
    notes: "", copper: 0, inventory: [], path: null, weaponId: null, unboundCenter: null, unlocked: [],
  });
}
for (const w of weapons) b.create(db.doc(`weapons/${w.id}`), { claimedBy: null });
b.create(db.doc("config/game"), { shopOpen: false });
await b.commit();

try { await getAuth().createUser({ email: "dm@stage.local", password: dmPassword }); }
catch (e) { if (e.code !== "auth/email-already-exists") throw e; }
console.log(`seed แล้ว: ${PLAYERS.length} ผู้เล่น · ${weapons.length} อาวุธ · บัญชี DM dm@stage.local`);
```

- [ ] **Step 7: รันตรวจ syntax**

Run: `node --check tools/seed.mjs` · Expected: ไม่มี output (ผ่าน) · ตัวจริงรันใน Task 7

---

### Task 4: เปลือกเว็บ ล็อกอิน และตัวสลับหน้า

**Files:**
- Create: `web/public/index.html`, `web/public/css/style.css`, `web/public/js/firebase-config.js`, `web/public/js/firebase.js`, `web/public/js/ui.js`, `web/public/js/data.js`, `web/public/js/app.js`

**Interfaces:**
- Consumes: `PLAYERS` (Task 1) · ไฟล์ `data/*.json` (Task 2) · โครงเอกสารและกฎ (Task 3)
- Produces: `firebase.js` → `db`, `auth`, `DM_EMAIL`, `isDM(): boolean`, `signInPlayer(): Promise<User>`, `signInDM(password): Promise<UserCredential>`, และ re-export จาก Firestore: `doc, collection, onSnapshot, updateDoc, addDoc, writeBatch, runTransaction, arrayUnion, arrayRemove, serverTimestamp, query, orderBy, limit` · `ui.js` → `h(tag, attrs, ...kids): HTMLElement` (attr ที่ขึ้นต้น `on` = event listener, `class` = className), `mount(root, ...kids)` · `data.js` → `loadData(): Promise<{weapons,unbound,items}>` · Task 5 ต้อง export `renderPlayer(root, data, id): () => void` (ฟังก์ชันยกเลิก listener) และ Task 6 ต้อง export `renderDM(root, data, id): () => void`

- [ ] **Step 1: เขียน `web/public/index.html`**

```html
<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>ม่านเวทีของจอมมาร — สถานะผู้กล้า</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <main id="app">กำลังโหลด…</main>
  <script type="module" src="js/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: กรอก `web/public/js/firebase-config.js`**

สร้างโปรเจกต์ใน Firebase Console (Task 7 ขั้น 1) แล้วคัดลอกค่าจาก Project settings → Your apps → Web app → Config มาใส่ (ค่าพวกนี้ไม่ใช่ความลับ ความปลอดภัยอยู่ที่ `firestore.rules`):

```js
export const firebaseConfig = {
  apiKey: "…",
  authDomain: "…firebaseapp.com",
  projectId: "…",
  appId: "…",
};
```

- [ ] **Step 3: เขียน `web/public/js/firebase.js`**

```js
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getAuth, signInAnonymously, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import {
  getFirestore, doc, collection, onSnapshot, updateDoc, addDoc, writeBatch, runTransaction,
  arrayUnion, arrayRemove, serverTimestamp, query, orderBy, limit,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";
import { firebaseConfig } from "./firebase-config.js";

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
export const DM_EMAIL = "dm@stage.local";

export const isDM = () => auth.currentUser?.email === DM_EMAIL;
export async function signInPlayer() {
  await auth.authStateReady();
  return auth.currentUser ?? (await signInAnonymously(auth)).user;
}
export const signInDM = (password) => signInWithEmailAndPassword(auth, DM_EMAIL, password);

export { doc, collection, onSnapshot, updateDoc, addDoc, writeBatch, runTransaction, arrayUnion, arrayRemove, serverTimestamp, query, orderBy, limit };
```

- [ ] **Step 4: เขียน `web/public/js/ui.js` และ `web/public/js/data.js`**

```js
// ui.js
export function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (k === "class") el.className = v;
    else if (v !== false && v != null) el.setAttribute(k, v === true ? "" : v);
  }
  for (const kid of kids.flat()) if (kid != null && kid !== false) el.append(kid.nodeType ? kid : String(kid));
  return el;
}
export const mount = (root, ...kids) => root.replaceChildren(...kids.flat().filter(Boolean));
```

```js
// data.js
const get = (f) => fetch(`data/${f}.json`).then((r) => { if (!r.ok) throw new Error(`โหลด ${f} ไม่ได้`); return r.json(); });
export const loadData = async () => {
  const [weapons, unbound, items] = await Promise.all([get("weapons"), get("unbound"), get("items")]);
  return { weapons, unbound, items };
};
```

- [ ] **Step 5: เขียน `web/public/js/app.js`** (ตัวสลับหน้า: `#/` เลือกชื่อ · `#/me` หน้าผู้เล่น · `#/dm` และ `#/dm/<id>` หน้า DM)

```js
import { PLAYERS } from "./players.js";
import { h, mount } from "./ui.js";
import { loadData } from "./data.js";
import { signInPlayer } from "./firebase.js";
import { renderPlayer } from "./player.js";
import { renderDM } from "./dm.js";

const root = document.getElementById("app");
const KEY = "stage.playerId";
let data;
let stop = () => {};

async function route() {
  stop(); stop = () => {};
  const [, page, arg] = location.hash.split("/");
  if (page === "dm") { stop = renderDM(root, data, arg); return; }
  const id = localStorage.getItem(KEY);
  if (page === "me" && id) { await signInPlayer(); stop = renderPlayer(root, data, id); return; }
  renderPicker();
}

function renderPicker() {
  mount(root,
    h("h1", {}, "เลือกตัวละครของคุณ"),
    h("div", { class: "picker" }, PLAYERS.map((p) =>
      h("button", { class: "card", onclick: () => { localStorage.setItem(KEY, p.id); location.hash = "#/me"; } }, p.name))),
    h("a", { href: "#/dm", class: "muted dmlink" }, "สำหรับ DM"));
}

window.addEventListener("hashchange", route);
data = await loadData();
route();
```

- [ ] **Step 6: เขียน `web/public/css/style.css`** (ธีมหน้าต่างเกม สีน้ำเงินเข้ม รองรับมือถือ)

```css
:root { --bg:#070b18; --line:#3a5fb0; --acc:#5cc8ff; --gold:#f5c96a; --mut:#8a94b8; --fg:#e8f0ff; --ok:#6ee7a0; --hp:#ff5c7a; }
* { box-sizing: border-box; }
body { margin: 0; color: var(--fg); font: 16px/1.6 "Sarabun","Noto Sans Thai",system-ui,sans-serif;
  background: radial-gradient(1200px 600px at 50% -10%, #14276a 0%, var(--bg) 62%) fixed; }
main { max-width: 760px; margin: 0 auto; padding: 16px; }
h1, h2, h3 { margin: 12px 0 6px; letter-spacing: .02em; } h1 { color: var(--acc); text-shadow: 0 0 12px #5cc8ff66; } h3 { color: var(--gold); }
.muted { color: var(--mut); } a { color: var(--acc); }
button { background: linear-gradient(180deg, #1c2f6b, #101c45); color: var(--fg); border: 1px solid var(--line); border-radius: 4px; padding: 8px 14px; font: inherit; cursor: pointer; }
button:hover:not(:disabled) { border-color: var(--acc); box-shadow: 0 0 10px #5cc8ff66; } button:disabled { opacity: .4; cursor: not-allowed; }
input, select, textarea { background: #050914; color: var(--fg); border: 1px solid var(--line); border-radius: 4px; padding: 6px 8px; font: inherit; max-width: 100%; }
.picker { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; }
.card { padding: 22px 8px; font-size: 1.15rem; }
/* หน้าต่างสถานะ: กรอบเรืองฟ้า มุมตัด เส้นแสงด้านบน */
.window { position: relative; margin: 10px 0; padding: 14px 16px; border: 1px solid var(--line);
  background: linear-gradient(180deg, rgba(26,44,98,.86), rgba(10,18,44,.88));
  box-shadow: 0 0 20px #2a5bd744, inset 0 0 0 1px #ffffff10;
  clip-path: polygon(0 0, calc(100% - 14px) 0, 100% 14px, 100% 100%, 14px 100%, 0 calc(100% - 14px)); }
.window::before { content: ""; position: absolute; left: 0; top: 0; right: 0; height: 2px; background: linear-gradient(90deg, var(--acc), transparent 70%); }
.lv { color: var(--gold); border: 1px solid var(--gold); padding: 0 10px; border-radius: 2px; font-weight: 700; }
.tabs { display: flex; gap: 6px; margin: 10px 0; flex-wrap: wrap; } .tabs button.on { border-color: var(--acc); color: var(--acc); box-shadow: 0 0 10px #5cc8ff55; }
.row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin: 6px 0; }
.stat { background: #050914cc; border: 1px solid var(--line); border-radius: 3px; padding: 6px 12px; min-width: 88px; text-align: center; }
.stat small { display: block; color: var(--mut); letter-spacing: .08em; } .stat b { font-size: 1.15rem; }
.abil { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin: 8px 0; }
.bar { height: 10px; margin: 4px 0 10px; background: #050914; border: 1px solid var(--line); } .bar i { display: block; height: 100%; background: linear-gradient(90deg, var(--hp), #ff9a5c); }
.wgrid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 10px; }
.wcard { text-align: left; } .wcard.taken { opacity: .45; }
.node { position: relative; margin: 6px 0; padding: 8px 12px 8px 14px; border: 1px solid var(--line); border-left: 4px solid var(--line); background: #050914aa; }
.node.off { opacity: .55; } .node.on { border-color: var(--ok); border-left-color: var(--ok); box-shadow: 0 0 12px #6ee7a044; }
.node .tier { position: absolute; right: 10px; top: 8px; } .node p { margin: 2px 0; } .node small { color: var(--mut); }
.item { justify-content: space-between; } .dmlink { display: inline-block; margin-top: 20px; }
table { width: 100%; border-collapse: collapse; } td, th { border-bottom: 1px solid var(--line); padding: 6px; text-align: left; }
```

- [ ] **Step 7: รันตรวจ (ยังไม่มี player.js/dm.js จึงตรวจแค่ syntax)**

Run: `for f in public/js/*.js; do node --check "$f" || echo "FAIL $f"; done` · Expected: ไม่มี `FAIL` (ไฟล์ที่ import URL จาก CDN แค่ผ่าน syntax เท่านั้น) · ตรวจการทำงานจริงหลัง Task 5-6

---

### Task 5: หน้าผู้เล่น (สถานะ · อาวุธและสกิล · ร้านค้า)

**Files:**
- Create: `web/public/js/player.js`

**Interfaces:**
- Consumes: `firebase.js` (Task 4), `ui.js`, `money.js` (`format`), `PLAYERS`, `data` = `{weapons, unbound, items}`
- Produces: `renderPlayer(root: HTMLElement, data, id: string): () => void`

- [ ] **Step 1: เขียน `web/public/js/player.js`**

```js
import { db, doc, collection, onSnapshot, updateDoc, addDoc, writeBatch, runTransaction, serverTimestamp } from "./firebase.js";
import { h, mount } from "./ui.js";
import { format } from "./money.js";
import { PLAYERS } from "./players.js";

const ABIL = [["str", "STR"], ["dex", "DEX"], ["con", "CON"], ["int", "INT"], ["wis", "WIS"], ["cha", "CHA"]];
const mod = (n) => Math.floor((n - 10) / 2);
const sign = (n) => (n >= 0 ? `+${n}` : `${n}`);
const nameOf = (id) => PLAYERS.find((p) => p.id === id)?.name ?? id;
const stat = (label, value) => h("div", { class: "stat" }, h("small", {}, label), h("b", {}, value));
const log = (playerId, type, detail) => addDoc(collection(db, "log"), { playerId, type, detail, ts: serverTimestamp() });

export function renderPlayer(root, data, id) {
  const st = { me: undefined, weapons: {}, game: { shopOpen: false }, tab: "sheet" };
  const draw = () => {
    if (st.me === undefined) return;
    if (st.me === null) return mount(root, h("p", {}, "ยังไม่มีข้อมูลตัวละครนี้ (ให้ DM รัน seed ก่อน)"), back());
    mount(root, header(st), tabs(st, draw), body(st, data, id));
  };
  const offs = [
    onSnapshot(doc(db, "players", id), (s) => { st.me = s.exists() ? s.data() : null; draw(); }),
    onSnapshot(collection(db, "weapons"), (s) => { st.weapons = Object.fromEntries(s.docs.map((d) => [d.id, d.data()])); draw(); }),
    onSnapshot(doc(db, "config", "game"), (s) => { st.game = s.data() ?? st.game; draw(); }),
  ];
  return () => offs.forEach((off) => off());
}

const back = () => h("a", { href: "#/", class: "muted", onclick: () => localStorage.removeItem("stage.playerId") }, "เปลี่ยนตัวละคร");

function header(st) {
  return h("div", { class: "row" }, h("h1", {}, st.me.name), h("span", { class: "lv" }, `Lv.${st.me.level}`), back());
}

function tabs(st, draw) {
  const t = (key, label) => h("button", { class: st.tab === key ? "on" : "", onclick: () => { st.tab = key; draw(); } }, label);
  return h("div", { class: "tabs" }, t("sheet", "สถานะ"), t("skill", "อาวุธและสกิล"), t("shop", "ร้านค้า"));
}

function body(st, data, id) {
  if (st.tab === "skill") return skillTab(st, data, id);
  if (st.tab === "shop") return shopTab(st, data, id);
  return sheetTab(st.me);
}

function sheetTab(me) {
  return h("section", { class: "window" },
    h("div", { class: "row" }, stat("HP", `${me.hp}/${me.maxHp}`), stat("AC", me.ac), stat("เงิน", format(me.copper))),
    h("div", { class: "bar" }, h("i", { style: `width:${me.maxHp > 0 ? Math.max(0, Math.min(100, (me.hp / me.maxHp) * 100)) : 0}%` })),
    h("div", { class: "abil" }, ABIL.map(([k, label]) => stat(label, `${me.abilities[k]} (${sign(mod(me.abilities[k]))})`))),
    me.notes ? h("p", { class: "muted" }, me.notes) : null,
    h("h3", {}, "กระเป๋า"),
    me.inventory.length ? h("ul", {}, me.inventory.map((i) => h("li", {}, `${i.name} × ${i.qty}`))) : h("p", { class: "muted" }, "ว่างเปล่า"));
}

// ---------- อาวุธและสกิล ----------
function skillTab(st, data, id) {
  const me = st.me;
  if (!me.path) return chooser(st, data, id);
  if (me.path === "unbound") {
    const center = data.unbound.center.find((c) => c.id === me.unboundCenter);
    return h("section", { class: "window" },
      h("h2", {}, "ผู้ไม่ผูกอาวุธ"),
      h("h3", {}, "ท่ากลาง (ความรู้จากโลกเดิม)"),
      center ? node({ ...center, unlock: "", tier: "" }, true) : h("p", { class: "muted" }, "รอ DM เลือกให้"),
      h("h3", {}, "วิชา (วงที่ 1)"),
      data.unbound.ring1.map((m) => node(m, me.unlocked.includes(m.id))));
  }
  const w = data.weapons.find((x) => x.id === me.weaponId);
  return h("section", { class: "window" },
    h("h2", {}, `${w.name} — ${w.fullName}`),
    h("p", { class: "muted" }, `${w.role} · ลูกเต๋าพลังชีวิต ${w.hitDie}`),
    h("h3", {}, "ท่ากลาง (ฟรี)"),
    node({ name: w.center.name, effect: w.center.effect, unlock: "", tier: "" }, true),
    h("h3", {}, "วงที่ 1"),
    w.moves.map((m) => node(m, me.unlocked.includes(m.id))));
}

function node(m, on) {
  const hidden = m.secret;
  const title = hidden ? (on ? "✨ ท่าลับปลดแล้ว — DM จะแจ้งรายละเอียด" : "❓ ท่าลับ") : m.name;
  return h("div", { class: `node ${on ? "on" : "off"}` },
    h("b", {}, title),
    hidden ? null : h("p", {}, m.effect),
    hidden || !m.unlock ? null : h("small", {}, `ปลดโดย: ${m.unlock}`),
    h("span", { class: "tier" }, m.tier ?? ""));
}

function chooser(st, data, id) {
  return h("section", { class: "window" },
    h("h2", {}, "เลือกอาวุธโบราณ"),
    h("p", { class: "muted" }, "เลือกแล้วเปลี่ยนไม่ได้ และแต่ละอาวุธมีได้คนเดียว"),
    h("div", { class: "wgrid" }, data.weapons.map((w) => {
      const owner = st.weapons[w.id]?.claimedBy;
      return h("button", { class: `wcard ${owner ? "taken" : ""}`, disabled: !!owner, onclick: () => claim(id, w) },
        h("b", {}, `${w.name} — ${w.fullName}`), h("br"), h("small", {}, w.role), owner ? h("div", {}, `มีเจ้าของ: ${nameOf(owner)}`) : null);
    })),
    h("h3", {}, "หรือ"),
    h("button", { onclick: () => goUnbound(id) }, "ไม่ผูกอาวุธ (เส้นทางผู้ไม่ผูกอาวุธ)"));
}

async function claim(id, w) {
  if (!confirm(`เลือก ${w.name} ใช่ไหม? เลือกแล้วเปลี่ยนไม่ได้`)) return;
  try {
    const b = writeBatch(db);
    b.update(doc(db, "weapons", w.id), { claimedBy: id });
    b.update(doc(db, "players", id), { path: "weapon", weaponId: w.id });
    await b.commit();
    await log(id, "claim", w.id);
  } catch { alert("เลือกไม่ได้ อาจมีคนเลือกไปแล้ว ลองใหม่"); }
}

async function goUnbound(id) {
  if (!confirm("เลือกไม่ผูกอาวุธใช่ไหม? เลือกแล้วเปลี่ยนไม่ได้")) return;
  try { await updateDoc(doc(db, "players", id), { path: "unbound" }); await log(id, "claim", "unbound"); }
  catch { alert("เลือกไม่ได้ ลองใหม่"); }
}

// ---------- ร้านค้า ----------
function shopTab(st, data, id) {
  if (!st.game.shopOpen) return h("p", { class: "window muted" }, "ร้านปิดอยู่ (DM ยังไม่เปิดร้าน)");
  return h("section", { class: "window" },
    h("div", { class: "row" }, stat("เงินของคุณ", format(st.me.copper))),
    data.items.map((it) => h("div", { class: "row item" },
      h("span", {}, `${it.name} — ${format(it.price)}`), h("small", { class: "muted" }, it.desc),
      h("button", { disabled: st.me.copper < it.price, onclick: () => buy(id, it) }, "ซื้อ"))));
}

async function buy(id, it) {
  try {
    await runTransaction(db, async (tx) => {
      const ref = doc(db, "players", id);
      const me = (await tx.get(ref)).data();
      if (me.copper < it.price) throw new Error("เงินไม่พอ");
      const inv = me.inventory.map((x) => ({ ...x }));
      const row = inv.find((x) => x.itemId === it.id);
      if (row) row.qty += 1; else inv.push({ itemId: it.id, name: it.name, qty: 1 });
      tx.update(ref, { copper: me.copper - it.price, inventory: inv });
    });
    await log(id, "buy", it.name);
  } catch (e) { alert(e.message || "ซื้อไม่ได้ (ร้านอาจปิดแล้ว)"); }
}
```

- [ ] **Step 2: รันตรวจ syntax**

Run: `node --check public/js/player.js` · Expected: ไม่มี output · ตรวจการทำงานจริงใน Task 7

---

### Task 6: หน้า DM (ภาพรวม · รายละเอียดผู้เล่น)

**Files:**
- Create: `web/public/js/dm.js`

**Interfaces:**
- Consumes: `firebase.js` (`isDM`, `signInDM`, Firestore functions), `ui.js`, `money.js` (`format`), `data`
- Produces: `renderDM(root, data, id?: string): () => void`

- [ ] **Step 1: เขียน `web/public/js/dm.js`**

```js
import {
  db, doc, collection, onSnapshot, updateDoc, addDoc, writeBatch, arrayUnion, arrayRemove,
  serverTimestamp, query, orderBy, limit, isDM, signInDM,
} from "./firebase.js";
import { h, mount } from "./ui.js";
import { format } from "./money.js";

const ABIL = [["str", "STR"], ["dex", "DEX"], ["con", "CON"], ["int", "INT"], ["wis", "WIS"], ["cha", "CHA"]];
const log = (playerId, type, detail) => addDoc(collection(db, "log"), { playerId, type, detail, ts: serverTimestamp() });
const editing = (root) => root.contains(document.activeElement) && document.activeElement.matches("input,textarea,select");

export function renderDM(root, data, id) {
  if (!isDM()) { loginForm(root); return () => {}; }
  const st = { players: {}, game: { shopOpen: false }, log: [] };
  const draw = () => {
    if (editing(root)) return; // ไม่ล้างช่องที่ DM กำลังพิมพ์ (ponytail: อัปเดตสดข้ามไปตอนพิมพ์ ค่าจะรีเฟรชเมื่อกดบันทึกหรือย้ายโฟกัส)
    mount(root, id ? detail(st, data, id, draw) : overview(st));
  };
  const offs = [
    onSnapshot(collection(db, "players"), (s) => { st.players = Object.fromEntries(s.docs.map((d) => [d.id, d.data()])); draw(); }),
    onSnapshot(doc(db, "config", "game"), (s) => { st.game = s.data() ?? st.game; draw(); }),
    onSnapshot(query(collection(db, "log"), orderBy("ts", "desc"), limit(30)), (s) => { st.log = s.docs.map((d) => d.data()); draw(); }),
  ];
  return () => offs.forEach((off) => off());
}

function loginForm(root) {
  const pw = h("input", { type: "password", placeholder: "รหัสผ่าน DM" });
  const go = async () => {
    try { await signInDM(pw.value); window.dispatchEvent(new HashChangeEvent("hashchange")); }
    catch { alert("รหัสผ่านไม่ถูกต้อง"); }
  };
  mount(root, h("h1", {}, "DM"), h("div", { class: "row" }, pw, h("button", { onclick: go }, "เข้าสู่ระบบ")), h("a", { href: "#/", class: "muted" }, "กลับ"));
}

function overview(st) {
  const rows = Object.entries(st.players).map(([id, p]) => h("tr", {},
    h("td", {}, h("a", { href: `#/dm/${id}` }, p.name)),
    h("td", {}, `Lv.${p.level}`),
    h("td", {}, p.path === "weapon" ? p.weaponId : p.path === "unbound" ? "ไม่ผูกอาวุธ" : "ยังไม่เลือก"),
    h("td", {}, `${p.unlocked.length} ท่า`),
    h("td", {}, format(p.copper))));
  return [
    h("h1", {}, "DM"),
    h("div", { class: "row" },
      h("button", { onclick: () => updateDoc(doc(db, "config", "game"), { shopOpen: !st.game.shopOpen }) }, st.game.shopOpen ? "ร้านเปิดอยู่ (กดเพื่อปิด)" : "ร้านปิดอยู่ (กดเพื่อเปิด)")),
    h("table", { class: "window" }, h("tr", {}, ["ผู้เล่น", "เลเวล", "อาวุธ", "ปลดแล้ว", "เงิน"].map((t) => h("th", {}, t))), rows),
    h("h3", {}, "บันทึกล่าสุด"),
    h("ul", {}, st.log.map((l) => h("li", { class: "muted" }, `${l.ts?.toDate().toLocaleString("th-TH") ?? ""} · ${st.players[l.playerId]?.name ?? l.playerId} · ${l.type} · ${l.detail}`))),
  ];
}

function detail(st, data, id, draw) {
  const p = st.players[id];
  if (!p) return h("p", {}, "ไม่พบผู้เล่น");
  const ref = doc(db, "players", id);
  const f = {}; // ช่องกรอก
  const num = (key, label, val) => h("label", {}, `${label} `, (f[key] = h("input", { type: "number", value: val, style: "width:80px" })));
  const n = (k) => Number(f[k].value);

  const save = async () => {
    await updateDoc(ref, {
      level: n("level"), hp: n("hp"), maxHp: n("maxHp"), ac: n("ac"),
      copper: Math.max(0, Math.trunc(n("copper"))),
      abilities: Object.fromEntries(ABIL.map(([k]) => [k, n(k)])),
      notes: f.notes.value,
    });
    await log(id, "edit", "แก้ชีท");
    draw();
  };

  const weapon = p.path === "weapon" ? data.weapons.find((w) => w.id === p.weaponId) : null;
  const moves = weapon ? weapon.moves : p.path === "unbound" ? data.unbound.ring1 : [];
  const toggle = async (m, on) => {
    await updateDoc(ref, { unlocked: on ? arrayUnion(m.id) : arrayRemove(m.id) });
    await log(id, "unlock", `${m.id} ${on ? "ปลด" : "ล็อกคืน"}`);
  };
  const addItem = async () => {
    const name = f.itemName.value.trim(); const qty = Math.max(1, Math.trunc(Number(f.itemQty.value)));
    if (!name) return;
    await updateDoc(ref, { inventory: [...p.inventory, { itemId: null, name, qty }] });
    await log(id, "edit", `เพิ่มของ ${name} × ${qty}`);
    f.itemName.value = ""; draw();
  };
  const resetWeapon = async () => {
    if (!confirm("รีเซ็ตอาวุธและท่าที่ปลดของคนนี้ใช่ไหม?")) return;
    const b = writeBatch(db);
    if (p.weaponId) b.update(doc(db, "weapons", p.weaponId), { claimedBy: null });
    b.update(ref, { path: null, weaponId: null, unboundCenter: null, unlocked: [] });
    await b.commit();
    await log(id, "edit", "รีเซ็ตอาวุธ");
  };

  return [
    h("a", { href: "#/dm", class: "muted" }, "← กลับ"),
    h("h1", {}, p.name),
    h("section", { class: "window" },
      h("h3", {}, "สถานะ"),
      h("div", { class: "row" }, num("level", "เลเวล", p.level), num("hp", "HP", p.hp), num("maxHp", "HP สูงสุด", p.maxHp), num("ac", "AC", p.ac)),
      h("div", { class: "row" }, ABIL.map(([k, label]) => num(k, label, p.abilities[k]))),
      h("div", { class: "row" }, num("copper", "เงิน (ทองแดง)", p.copper), h("span", { class: "muted" }, `= ${format(p.copper)}`)),
      h("div", {}, (f.notes = h("textarea", { rows: 3, style: "width:100%", placeholder: "หมายเหตุ" }, p.notes ?? ""))),
      h("button", { onclick: save }, "บันทึก")),
    h("section", { class: "window" },
      h("h3", {}, "กระเป๋า"),
      p.inventory.map((it, i) => h("div", { class: "row" }, `${it.name} × ${it.qty}`,
        h("button", { onclick: async () => { await updateDoc(ref, { inventory: p.inventory.filter((_, j) => j !== i) }); draw(); } }, "ลบ"))),
      h("div", { class: "row" }, (f.itemName = h("input", { placeholder: "ชื่อของ" })), (f.itemQty = h("input", { type: "number", value: 1, style: "width:70px" })), h("button", { onclick: addItem }, "เพิ่ม"))),
    h("section", { class: "window" },
      h("h3", {}, "อาวุธและท่า"),
      !p.path ? h("p", { class: "muted" }, "ยังไม่เลือกอาวุธ") : [
        h("p", {}, p.path === "weapon" ? `อาวุธ: ${weapon.name} — ${weapon.fullName}` : "ผู้ไม่ผูกอาวุธ"),
        p.path === "unbound" ? h("div", { class: "row" }, "ท่ากลาง: ",
          h("select", { onchange: (e) => updateDoc(ref, { unboundCenter: e.target.value || null }) },
            h("option", { value: "" }, "— ยังไม่เลือก —"),
            data.unbound.center.map((c) => h("option", { value: c.id, selected: p.unboundCenter === c.id }, c.name)))) : null,
        moves.map((m) => h("label", { class: "row" },
          h("input", { type: "checkbox", checked: p.unlocked.includes(m.id), onchange: (e) => toggle(m, e.target.checked) }),
          `${m.slot}. ${m.secret ? "❓ ท่าลับ (ดูรายละเอียดในไฟล์กติกา)" : m.name} ${m.tier}`)),
        h("button", { onclick: resetWeapon }, "รีเซ็ตอาวุธ"),
      ]),
  ];
}
```

- [ ] **Step 2: รันตรวจ syntax**

Run: `for f in public/js/*.js; do node --check "$f" || echo "FAIL $f"; done` · Expected: ไม่มี `FAIL`

---

### Task 7: สร้างโปรเจกต์ Firebase, deploy และทดสอบมือ

**Files:**
- Modify: `web/public/js/firebase-config.js` (ใส่ค่าจริง)
- ไม่สร้างไฟล์ใหม่ · เก็บ `serviceAccount.json` **นอกโฟลเดอร์ `web/public/`** (ห้าม deploy) เช่น `~/secrets/stage-serviceAccount.json`

- [ ] **Step 1: สร้างโปรเจกต์ใน Firebase Console** (ทำเอง ต้องล็อกอิน Google)

1. console.firebase.google.com → Add project (ชื่อ เช่น `stage-of-the-demon-lord`) ปิด Google Analytics ได้
2. Build → **Authentication** → Get started → Sign-in method เปิด **Anonymous** และ **Email/Password**
3. Build → **Firestore Database** → Create database → **production mode** → เลือกภูมิภาคใกล้ที่สุด (เช่น `asia-southeast1`)
4. Project settings → Your apps → เพิ่ม **Web app** → คัดลอกค่า `firebaseConfig` ไปใส่ `web/public/js/firebase-config.js` (Task 4 ขั้น 2)
5. Project settings → Service accounts → **Generate new private key** เก็บไฟล์ไว้ตามที่ระบุด้านบน

- [ ] **Step 2: ล็อกอิน CLI และผูกโปรเจกต์**

Run (ใน `web/`): `npx firebase login` แล้ว `npx firebase use --add` เลือกโปรเจกต์ที่สร้าง ตั้ง alias `default` · Expected: `Now using project ...`

- [ ] **Step 3: deploy กฎและเว็บ**

Run: `npx firebase deploy --only firestore:rules,hosting` · Expected: `Deploy complete!` พร้อม Hosting URL (`https://<project>.web.app`) ขึ้นเป็นลิงก์ที่ส่งให้ผู้เล่น

- [ ] **Step 4: seed ข้อมูลเริ่มต้นและบัญชี DM**

Run: `node tools/seed.mjs ~/secrets/stage-serviceAccount.json '<รหัสผ่าน DM ที่ตั้งเอง ≥ 6 ตัว>'` · Expected: `seed แล้ว: 6 ผู้เล่น · 6 อาวุธ · บัญชี DM dm@stage.local` · ถ้ารันซ้ำจะล้ม (ตั้งใจ ไม่ทับข้อมูลเดิม)

- [ ] **Step 5: ใส่สถานะจริงของผู้เล่นทั้ง 6 คน**

เปิด `<Hosting URL>/#/dm` → ล็อกอินด้วยรหัสผ่าน DM → กดเข้าแต่ละคน → กรอก เลเวล HP AC ค่าพลัง 6 ตัว เงิน (ทองแดง) → บันทึก (seed ใส่ค่าตั้งต้น level 1 / HP 10 / AC 10 / ค่าพลัง 10 ทั้งหมดไว้ให้แก้)

- [ ] **Step 6: เช็กลิสต์ทดสอบมือ (เปิดสองหน้าต่าง: DM + โหมดไม่ระบุตัวตนสำหรับผู้เล่น)**

- [ ] ผู้เล่นเลือกชื่อ → เห็นสถานะที่ DM กรอก · รีเฟรชหน้า ยังเป็นคนเดิม
- [ ] ผู้เล่นเปิดแท็บ "อาวุธและสกิล" → เลือกดาบ → ยืนยัน → เห็นต้นสกิลดาบ (ท่ากลาง + 10 ท่า ท่าลับขึ้น ❓)
- [ ] ผู้เล่นอีกคน (หน้าต่างอื่น) เห็นดาบเป็นสีเทาและชื่อเจ้าของ กดเลือกไม่ได้
- [ ] DM ติ๊กปลดท่า → **ที่ผู้เล่นขึ้นสีเขียวทันทีโดยไม่ต้องรีเฟรช** · DM ติ๊กท่าลับ → ผู้เล่นเห็น "✨ ท่าลับปลดแล้ว — DM จะแจ้งรายละเอียด"
- [ ] ร้านปิด → ผู้เล่นเห็น "ร้านปิดอยู่" · DM กดเปิดร้าน → ผู้เล่นซื้อ "สมุนไพร" → เงินลด 10 ทองแดงและของขึ้นในกระเป๋า
- [ ] DM ให้เงินเพิ่มและเพิ่มของนอกร้าน (พิมพ์ชื่อ) → ผู้เล่นเห็นทันที
- [ ] ผู้เล่นที่เลือก "ไม่ผูกอาวุธ" → DM เลือกท่ากลางให้ → ผู้เล่นเห็นท่ากลางและวิชา 10 ท่า
- [ ] DM รีเซ็ตอาวุธ → ผู้เล่นกลับไปหน้าเลือกอาวุธ ดาบว่างให้คนอื่นเลือกได้
- [ ] บันทึกล่าสุดที่หน้า DM แสดงรายการ claim / buy / unlock
- [ ] เปิดเว็บบนมือถือ อ่านและกดได้สะดวก (ไม่ต้องเลื่อนแนวนอน)

---

## Self-Review (ทำแล้ว)

**Spec coverage:** ล็อกอินไม่มี PIN → Task 3-4 (กฎ + `firebase.js`/`app.js`) · ชีท D&D และ DM แก้ → Task 5 (`sheetTab`), Task 6 (`save`) · อาวุธห้ามซ้ำ ล็อกหลังเลือก รีเซ็ต → Task 3 (กฎ+เทสต์), Task 5 (`claim`), Task 6 (`resetWeapon`) · ไม่ผูกอาวุธและเส้นทางสกิล → Task 2 (`unbound.json`), Task 5, Task 6 (`unboundCenter`) · DM ปลดท่า → Task 6 (`toggle`) + กฎ · ท่าลับ → Task 2 (`secret`), Task 5 (`node`) · เงินทองแดง → Task 1 · ร้านค้าหักเงินอัตโนมัติ สวิตช์ DM → Task 5 (`buy`), Task 6, กฎ `shopOpen` · เพิ่ม/ลบของ แก้เงิน → Task 6 · log → Task 5-6 + กฎ · ไม่มีข้อมูลลับ → Task 2 (`assertSafe` + เทสต์) · ทดสอบกฎด้วย Emulator → Task 3 · ทดสอบมือ → Task 7
**Placeholder scan:** ค่าที่ผู้ใช้ต้องกรอกมีอย่างเดียวคือ `firebase-config.js` และรหัสผ่าน DM ซึ่งเป็นความลับ/ค่าเฉพาะโปรเจกต์ และระบุขั้นตอนที่ได้มาชัดเจน
**Type consistency:** `renderPlayer/renderDM(root, data, id) => () => void` ตรงกับ `app.js` · ชื่อฟิลด์ `unboundCenter` `weaponId` `unlocked` `inventory[{itemId,name,qty}]` ตรงกันใน `seed.mjs`, กฎ, `player.js`, `dm.js` · id ท่าเป็น `<weaponId>-<slot>` และ `u-<slot>` / ท่ากลางผู้ไม่ผูกอาวุธ `u-c<n>` ตรงกับตัวแปลง
