# เว็บผู้เล่นและ DM — ย้ายชั้นหน้าเว็บเป็น Next.js + Vercel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** เว็บ Next.js (App Router) ที่ผู้เล่น 6 คนเลือกชื่อแล้วดูชีท เลือกอาวุธ ดูสกิลทรีแบบโหนด และซื้อของ ส่วน DM ดูชีททุกคน กดปลดท่า แก้เงิน/ของ · deploy บน Vercel · ใช้ Firebase (Firestore + Auth) เหมือนเดิม

**Architecture:** แอป Next.js อยู่ใน `web/site/` เป็น client-only (ทุกหน้า `"use client"` ไม่มี SSR data) อ่านเขียน Firestore แบบเรียลไทม์ผ่าน hook เล็กๆ ตรรกะที่มีเงื่อนไข (เงิน ซื้อของ ตำแหน่งวงโหนด) แยกเป็นฟังก์ชันล้วนพร้อมเทสต์ Vitest ส่วน `web/firestore.rules`, `web/tools/*`, `web/test/*` (แผนเดิม งาน 1-3) ใช้ต่อโดยไม่แก้กฎ · ต้นสกิลใช้ React Flow วางโหนดเป็นวงกลม · หน้าตาเริ่มจากการพอร์ต `web/mock/index.html` แล้ว (งาน 10) ค่อยปรับตามดีไซน์จาก Google Stitch

**Tech Stack:** Next.js (App Router, TypeScript strict) · Tailwind CSS · shadcn/ui (เฉพาะ `sonner` สำหรับ toast) · `@xyflow/react` (React Flow) · `firebase` (modular SDK) · Vitest · Vercel

> **สถานะ (2026-09-21): ทำเสร็จแล้วโดยไม่ใช้ subagent** (`web/site/`) · **ต่างจากแผน:** (1) ต้นสกิลเป็น SVG ตามดีไซน์ Stitch แทน React Flow (ไม่มี dependency `@xyflow/react`) (2) toast ใช้ `sonner` ตรงๆ ไม่ผ่าน shadcn (3) ธีมใช้โทเคน Tailwind ของ Stitch (`@theme` ใน `globals.css`) ไม่ได้พอร์ต CSS จาก mock (4) หน้า DM เป็นหน้าเดียว `/dm` (เลือกผู้เล่นในหน้าเดียว) ไม่มี `/dm/[id]` (5) ตัดเนื้อหาที่ Stitch แต่งเองที่ไม่มีในกติกา (โบนัสอาวุธ ตัวนับสไลม์ ข้อมูลปลอมของ DM) · **ยังไม่ได้ทำ:** งาน 9 ขั้น deploy Vercel (ต้องให้ผู้ใช้ล็อกอินเอง)

**Spec:** `docs/superpowers/specs/2026-09-21-player-web-design.md` (ข้อกำหนดด้านข้อมูล/กฎ/หน้าจอยังใช้ทั้งหมด ยกเว้นหัวข้อ "หน้าเว็บเป็น HTML+JS ไม่มีขั้น build" ที่ถูกแทนด้วยแผนนี้) · แผนเดิม `docs/superpowers/plans/2026-09-21-player-web.md` (งาน 1-3 ทำแล้ว คงไว้)

## Global Constraints

- **คงเดิมจากสเปก:** ไม่มี PIN (ผู้เล่น anonymous auth + เลือกชื่อเก็บใน `localStorage` คีย์ `stage.playerId`) · DM = อีเมล `dm@stage.local` เท่านั้น · ผู้เล่น id/ชื่อ: `gun`=กัน · `anvas`=อันวาส · `pongpaeng`=ป๋องแป๋ง · `hong`=หง · `dream`=ดรีม · `phet`=เพชร · เงินเป็นทองแดงจำนวนเต็ม (1 ทอง = 100, 1 เงิน = 10) · อาวุธ 6 ชนิดห้ามซ้ำ เลือกแล้วล็อก DM รีเซ็ตได้ · **DM เท่านั้นที่ปลดท่าและแก้สถานะ** · ข้อมูลฝั่งผู้เล่นไม่มีคำว่า ผนึก / ตื่นพลัง / กลับบ้าน (ตัวแปลงเดิมยังบังคับ) · วงที่ 2-3 ของต้นสกิลไม่มีข้อมูล แสดงเป็นวงจางล็อก
- **โครงเอกสาร Firestore ไม่เปลี่ยน:** `players/{id}` = `{name, level, hp, maxHp, ac, abilities{str,dex,con,int,wis,cha}, notes, copper, inventory[{itemId|null,name,qty}], path: null|"weapon"|"unbound", weaponId, unboundCenter, unlocked[]}` · `weapons/{id}` = `{claimedBy}` · `config/game` = `{shopOpen}` · `log/{auto}` = `{playerId,type,detail,ts}` · id ท่า `<weapon>-<slot>` / `u-<slot>` / ท่ากลางผู้ไม่ผูกอาวุธ `u-c<n>`
- **Stack:** Next.js App Router + TypeScript `strict` · ทุกหน้าและคอมโพเนนต์ที่แตะ Firebase ต้อง `"use client"` และเรียก Firebase ผ่าน `fb()` (init แบบ lazy ภายใน effect/handler เท่านั้น ห้ามเรียกระดับโมดูล เพราะ build ไม่มี env)
- **Env ที่ Vercel/ท้องถิ่นต้องมี:** `NEXT_PUBLIC_FIREBASE_API_KEY` `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` `NEXT_PUBLIC_FIREBASE_PROJECT_ID` `NEXT_PUBLIC_FIREBASE_APP_ID` (ค่าเดียวกับ `web/public/js/firebase-config.js` ที่ใช้อยู่ · โปรเจกต์ `dandd-2c2fc`) · `NEXT_PUBLIC_USE_EMULATOR=1` เฉพาะตอนเทสต์กับ emulator
- **ฟอนต์:** Kanit (หัวข้อ/ตัวเลข) + IBM Plex Sans Thai (เนื้อความ) ผ่าน `next/font/google` · ข้อความ UI เป็นภาษาไทยทั้งหมด
- **CSS:** พอร์ตจาก `web/mock/index.html` เป็น CSS ธรรมดา (คลาส `.win .wt .btn .node ...`) ใน `globals.css` ต่อท้ายส่วนของ Tailwind/shadcn · CSS ที่ไม่อยู่ใน `@layer` ชนะ utility ของ Tailwind เสมอ จึงห้ามใช้ Tailwind utility ไปทับสไตล์ของคลาสเหล่านี้
- **การรัน:** ทุกคำสั่ง `npm`/`npx` ของแอปรันใน `web/site/` · เทสต์กฎ/ตัวแปลงเดิมรันใน `web/` · Node ≥ 20 (เครื่องเป็น v26) · Java 21 สำหรับ emulator
- **git:** `web/` เป็น git repo (สร้างแล้ว) ทุก Task จบด้วย commit เดียว ท้ายข้อความ commit ใส่ `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`
- **ไม่ทำ:** SSR/ISR ดึงข้อมูล · ทอยลูกเต๋า แชต ระบบต่อสู้ น้ำหนักของ รูปโปรไฟล์ · ปุ่มผู้เล่น "ขอปลดท่า" · การตรวจราคาฝั่งเซิร์ฟเวอร์ · ราคาผู้กล้า +20% · ซ่อนข้อความ attribution ของ React Flow

---

## File Structure

```
web/
  firebase.json, firestore.rules, tools/, test/      (คงเดิม; แก้เล็กน้อยใน Task 1 และ 9)
  mock/index.html                                    (ต้นแบบหน้าตา อ่านอย่างเดียว)
  site/                                              ← แอป Next.js ใหม่ (Vercel Root Directory = web/site)
    package.json, vitest.config.ts, .env.example
    src/
      data/{weapons,unbound,items,players}.json      (weapons/unbound สร้างโดย tools/convert.mjs)
      lib/
        types.ts            ชนิดข้อมูลทั้งหมด
        money.ts            toCopper / format
        shop.ts             applyPurchase (ฟังก์ชันล้วน)
        ring.ts             ringPositions (ฟังก์ชันล้วน)
        tiers.ts            tierInfo, abilityMod, iconFor
        firebase.ts         fb() lazy init + DM_EMAIL
        hooks.ts            useAuth, useDoc, useCollection, usePlayerId
        actions.ts          claimWeapon, buyItem, setUnlocked ฯลฯ
      components/
        IconSprite.tsx, Icon.tsx, GlassWindow.tsx, SegBar.tsx, TabBar.tsx
        AbilityGrid.tsx, Bag.tsx, SkillRing.tsx, MoveDetail.tsx, WeaponPicker.tsx
        PlayerProvider.tsx, DmProvider.tsx
      app/
        layout.tsx, globals.css, page.tsx (เลือกชื่อ)
        me/{layout,page}.tsx, me/skill/page.tsx, me/shop/page.tsx
        dm/{layout,page}.tsx, dm/[id]/page.tsx
```

---

### Task 1: สร้างแอป Next.js และย้ายข้อมูลกติกาไป `web/site`

**Files:**
- Create: `web/site/**` (ด้วย create-next-app), `web/site/vitest.config.ts`, `web/site/.env.example`, `web/site/src/lib/firebase.ts`, `web/site/src/data/players.json`
- Modify: `web/tools/convert.mjs` (ที่เขียนไฟล์ผลลัพธ์), `web/tools/seed.mjs` (ที่อ่านไฟล์), `web/site/package.json` (scripts)
- Move: `web/public/data/items.json` → `web/site/src/data/items.json`

**Interfaces:**
- Produces: `fb(): { app, auth, db }` และ `DM_EMAIL` จาก `@/lib/firebase` · ไฟล์ `@/data/weapons.json`, `@/data/unbound.json`, `@/data/items.json`, `@/data/players.json` · script `npm run test`, `npm run typecheck` ใน `web/site`

- [ ] **Step 1: สร้างแอป**

Run (ใน `web/`):
```bash
npx create-next-app@latest site --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --yes
cd site
npm i firebase @xyflow/react
npm i -D vitest
npx shadcn@latest init -d
npx shadcn@latest add sonner
```
Expected: มีโฟลเดอร์ `web/site` ที่ `npm run build` ผ่าน (ถ้า `shadcn init` ถามเพิ่ม ให้เลือกค่าเริ่มต้น) · ตรวจ `git status` ว่า `web/.gitignore` ยังกัน `node_modules/`

- [ ] **Step 2: เพิ่ม script และ vitest config**

ใน `web/site/package.json` เพิ่มใน `"scripts"`:
```json
"test": "vitest run",
"typecheck": "tsc --noEmit"
```
สร้าง `web/site/vitest.config.ts`:
```ts
import { defineConfig } from "vitest/config";
import { fileURLToPath } from "node:url";

export default defineConfig({
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
  test: { include: ["src/**/*.test.ts"] },
});
```

- [ ] **Step 3: ย้ายข้อมูล**

```bash
mkdir -p site/src/data
git mv public/data/items.json site/src/data/items.json
```
สร้าง `web/site/src/data/players.json`:
```json
[
  { "id": "gun", "name": "กัน" },
  { "id": "anvas", "name": "อันวาส" },
  { "id": "pongpaeng", "name": "ป๋องแป๋ง" },
  { "id": "hong", "name": "หง" },
  { "id": "dream", "name": "ดรีม" },
  { "id": "phet", "name": "เพชร" }
]
```

- [ ] **Step 4: ชี้ตัวแปลงและ seed ไปที่ตำแหน่งใหม่**

ใน `web/tools/convert.mjs` แก้บรรทัดที่กำหนดโฟลเดอร์ผลลัพธ์ (`const dir = path.join(ROOT, "web", "public", "data");`) เป็น:
```js
  const dir = path.join(ROOT, "web", "site", "src", "data");
```
ใน `web/tools/seed.mjs`: ลบบรรทัด `import { PLAYERS } from "../public/js/players.js";` แล้วเพิ่มหลังบรรทัด `const db = getFirestore();`:
```js
const PLAYERS = JSON.parse(readFileSync(new URL("../site/src/data/players.json", import.meta.url), "utf8"));
```
และเปลี่ยนพาธ weapons เป็น `new URL("../site/src/data/weapons.json", import.meta.url)`

Run (ใน `web/`): `node tools/convert.mjs && git rm -q --cached public/data/weapons.json public/data/unbound.json && rm -f public/data/weapons.json public/data/unbound.json && node --check tools/seed.mjs && node --test test/convert.test.mjs`
Expected: พิมพ์ `weapons 6 · unbound center 12 ring1 10` · มี `site/src/data/weapons.json` และ `unbound.json` · เทสต์ตัวแปลงผ่านทั้งหมด

- [ ] **Step 5: เขียน `web/site/src/lib/firebase.ts`**

```ts
import { getApps, initializeApp, type FirebaseApp } from "firebase/app";
import { connectAuthEmulator, getAuth, type Auth } from "firebase/auth";
import { connectFirestoreEmulator, getFirestore, type Firestore } from "firebase/firestore";

export const DM_EMAIL = "dm@stage.local";

let cache: { app: FirebaseApp; auth: Auth; db: Firestore } | undefined;

/** init แบบ lazy: เรียกเฉพาะใน effect/handler ฝั่ง client (build ไม่มี env) */
export function fb() {
  if (cache) return cache;
  const app =
    getApps()[0] ??
    initializeApp({
      apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
      authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
      projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
      appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
    });
  const auth = getAuth(app);
  const db = getFirestore(app);
  if (process.env.NEXT_PUBLIC_USE_EMULATOR === "1") {
    connectAuthEmulator(auth, "http://127.0.0.1:9099", { disableWarnings: true });
    connectFirestoreEmulator(db, "127.0.0.1", 8080);
  }
  cache = { app, auth, db };
  return cache;
}
```
สร้าง `web/site/.env.example`:
```
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
NEXT_PUBLIC_FIREBASE_APP_ID=
# ตั้งเป็น 1 เฉพาะตอนทดสอบกับ Firebase Emulator
NEXT_PUBLIC_USE_EMULATOR=
```
และสร้าง `web/site/.env.local` โดยคัดลอกค่าจาก `web/public/js/firebase-config.js` (`apiKey`→`NEXT_PUBLIC_FIREBASE_API_KEY`, `authDomain`, `projectId`, `appId`) · `.env.local` ต้องไม่ถูก commit (ตรวจว่า `web/site/.gitignore` มี `.env*`)

- [ ] **Step 6: รันตรวจ**

Run (ใน `web/site`): `npm run typecheck && npm run build` · Expected: ผ่านทั้งคู่ (หน้าเริ่มต้นของ create-next-app ยังอยู่ ไม่เป็นไร)

- [ ] **Step 7: Commit**

```bash
cd .. && git add -A && git commit -m "feat: scaffold Next.js app in web/site, move rules data" -m "Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 2: ชนิดข้อมูลและตรรกะล้วน (พร้อมเทสต์ Vitest)

**Files:**
- Create: `web/site/src/lib/types.ts`, `money.ts`, `shop.ts`, `ring.ts`, `tiers.ts`
- Test: `web/site/src/lib/money.test.ts`, `shop.test.ts`, `ring.test.ts`, `tiers.test.ts`

**Interfaces:**
- Produces: `types.ts` → `Abilities, InvItem, Player, Move, Weapon, Unbound, Item, GameConfig, ClaimedWeapon, LogEntry` · `money.ts` → `toCopper({gold?,silver?,copper?}): number`, `format(total): string` (โยน `RangeError` ถ้าไม่ใช่จำนวนเต็ม ≥ 0) · `shop.ts` → `applyPurchase(me:{copper,inventory}, item: Item): {copper, inventory}` (โยน `Error("เงินไม่พอ")`) · `ring.ts` → `ringPositions(n: number, radius: number): {x:number,y:number}[]` (จุดแรกอยู่บนสุด วนตามเข็ม) · `tiers.ts` → `tierInfo(emoji: string): {label:string, cls:string}`, `abilityMod(score:number): string`, `iconFor(itemId: string|null): string`

- [ ] **Step 1: เขียน `types.ts`**

```ts
export type Abilities = { str: number; dex: number; con: number; int: number; wis: number; cha: number };
export type InvItem = { itemId: string | null; name: string; qty: number };
export type Player = {
  id: string; name: string; level: number; hp: number; maxHp: number; ac: number;
  abilities: Abilities; notes: string; copper: number; inventory: InvItem[];
  path: "weapon" | "unbound" | null; weaponId: string | null; unboundCenter: string | null; unlocked: string[];
};
export type Move = { id: string; slot: number; tier: string; secret?: boolean; name?: string; effect?: string; unlock?: string };
export type Weapon = {
  id: string; name: string; fullName: string; role: string; hitDie: string;
  center: { name: string; effect: string }; moves: Move[];
};
export type UnboundCenter = { id: string; name: string; who: string; effect: string; stat: string };
export type Unbound = { center: UnboundCenter[]; ring1: Move[] };
export type Item = { id: string; name: string; price: number; desc: string; category: string };
export type GameConfig = { shopOpen: boolean };
export type ClaimedWeapon = { id: string; claimedBy: string | null };
export type LogEntry = { playerId: string; type: string; detail: string; ts?: { toDate(): Date } | null };
```

- [ ] **Step 2: เขียนเทสต์ที่ล้ม**

`money.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import { format, toCopper } from "./money";

describe("money", () => {
  it("toCopper: 1 ทอง = 100, 1 เงิน = 10", () => {
    expect(toCopper({ gold: 2, silver: 3, copper: 5 })).toBe(235);
    expect(toCopper({ silver: 1 })).toBe(10);
    expect(toCopper({})).toBe(0);
  });
  it("format: ไม่แสดงหน่วยที่เป็นศูนย์", () => {
    expect(format(235)).toBe("2 ทอง 3 เงิน 5 ทองแดง");
    expect(format(101)).toBe("1 ทอง 1 ทองแดง");
    expect(format(100)).toBe("1 ทอง");
    expect(format(0)).toBe("0 ทองแดง");
  });
  it("format: ค่าติดลบหรือทศนิยมโยน RangeError", () => {
    expect(() => format(-1)).toThrow(RangeError);
    expect(() => format(1.5)).toThrow(RangeError);
  });
});
```
`shop.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import { applyPurchase } from "./shop";
import type { Item } from "./types";

const herb: Item = { id: "herb", name: "สมุนไพร", price: 10, desc: "", category: "วัตถุดิบ" };

describe("applyPurchase", () => {
  it("หักเงินและเพิ่มของใหม่", () => {
    const r = applyPurchase({ copper: 50, inventory: [] }, herb);
    expect(r.copper).toBe(40);
    expect(r.inventory).toEqual([{ itemId: "herb", name: "สมุนไพร", qty: 1 }]);
  });
  it("ซื้อซ้ำเพิ่มจำนวน ไม่แก้ต้นฉบับ", () => {
    const inv = [{ itemId: "herb", name: "สมุนไพร", qty: 2 }];
    const r = applyPurchase({ copper: 10, inventory: inv }, herb);
    expect(r.copper).toBe(0);
    expect(r.inventory[0].qty).toBe(3);
    expect(inv[0].qty).toBe(2);
  });
  it("เงินไม่พอโยน Error", () => {
    expect(() => applyPurchase({ copper: 9, inventory: [] }, herb)).toThrow("เงินไม่พอ");
  });
});
```
`ring.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import { ringPositions } from "./ring";

describe("ringPositions", () => {
  it("จุดแรกอยู่บนสุด (y ติดลบ x ≈ 0)", () => {
    const [p] = ringPositions(10, 100);
    expect(p.x).toBeCloseTo(0, 5);
    expect(p.y).toBeCloseTo(-100, 5);
  });
  it("ทุกจุดห่างจากศูนย์กลางเท่ากับรัศมี และมี n จุด", () => {
    const ps = ringPositions(10, 130);
    expect(ps).toHaveLength(10);
    for (const p of ps) expect(Math.hypot(p.x, p.y)).toBeCloseTo(130, 5);
  });
  it("จุดที่สองอยู่ทางขวาของจุดแรก (วนตามเข็ม)", () => {
    const ps = ringPositions(10, 100);
    expect(ps[1].x).toBeGreaterThan(ps[0].x);
  });
});
```
`tiers.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import { abilityMod, iconFor, tierInfo } from "./tiers";

describe("tiers", () => {
  it("tierInfo แปลงอีโมจิเป็นป้าย", () => {
    expect(tierInfo("🟢")).toEqual({ label: "ง่ายมาก", cls: "t1" });
    expect(tierInfo("🔴")).toEqual({ label: "ยาก", cls: "t4" });
    expect(tierInfo("?")).toEqual({ label: "-", cls: "" });
  });
  it("abilityMod ตามกฎ D&D", () => {
    expect(abilityMod(10)).toBe("+0");
    expect(abilityMod(16)).toBe("+3");
    expect(abilityMod(9)).toBe("-1");
    expect(abilityMod(8)).toBe("-1");
  });
  it("iconFor เลือกไอคอนตามไอเท็ม", () => {
    expect(iconFor("herb")).toBe("leaf");
    expect(iconFor("book-sword")).toBe("codex");
    expect(iconFor("ration")).toBe("bread");
    expect(iconFor(null)).toBe("bag");
  });
});
```

- [ ] **Step 2b: รันให้เห็นว่าล้ม**

Run (ใน `web/site`): `npm test` · Expected: FAIL (ไม่พบโมดูล `./money` ฯลฯ)

- [ ] **Step 3: เขียนโมดูล**

`money.ts`:
```ts
export const toCopper = ({ gold = 0, silver = 0, copper = 0 }: { gold?: number; silver?: number; copper?: number }) =>
  gold * 100 + silver * 10 + copper;

export function format(total: number): string {
  if (!Number.isInteger(total) || total < 0) throw new RangeError("copper must be a non-negative integer");
  const g = Math.floor(total / 100), s = Math.floor((total % 100) / 10), c = total % 10;
  const parts = ([[g, "ทอง"], [s, "เงิน"], [c, "ทองแดง"]] as const).filter(([n]) => n > 0).map(([n, u]) => `${n} ${u}`);
  return parts.length ? parts.join(" ") : "0 ทองแดง";
}
```
`shop.ts`:
```ts
import type { InvItem, Item } from "./types";

export function applyPurchase(me: { copper: number; inventory: InvItem[] }, item: Item) {
  if (me.copper < item.price) throw new Error("เงินไม่พอ");
  const inventory = me.inventory.map((x) => ({ ...x }));
  const row = inventory.find((x) => x.itemId === item.id);
  if (row) row.qty += 1;
  else inventory.push({ itemId: item.id, name: item.name, qty: 1 });
  return { copper: me.copper - item.price, inventory };
}
```
`ring.ts`:
```ts
/** ตำแหน่งจุดบนวงกลมรอบจุด (0,0): จุดแรกอยู่บนสุด วนตามเข็มนาฬิกา */
export function ringPositions(n: number, radius: number): { x: number; y: number }[] {
  return Array.from({ length: n }, (_, i) => {
    const a = ((-90 + (i * 360) / n) * Math.PI) / 180;
    return { x: radius * Math.cos(a), y: radius * Math.sin(a) };
  });
}
```
`tiers.ts`:
```ts
const TIERS: Record<string, { label: string; cls: string }> = {
  "🟢": { label: "ง่ายมาก", cls: "t1" },
  "🟡": { label: "ง่าย", cls: "t2" },
  "🟠": { label: "ปานกลาง", cls: "t3" },
  "🔴": { label: "ยาก", cls: "t4" },
};
export const tierInfo = (emoji: string) => TIERS[emoji] ?? { label: "-", cls: "" };

export function abilityMod(score: number): string {
  const m = Math.floor((score - 10) / 2);
  return m >= 0 ? `+${m}` : `${m}`;
}

export function iconFor(itemId: string | null): string {
  if (!itemId) return "bag";
  if (itemId.startsWith("book")) return "codex";
  return ({ herb: "leaf", feather: "feather", ration: "bread" } as Record<string, string>)[itemId] ?? "bag";
}
```

- [ ] **Step 4: รันตรวจ**

Run: `npm test && npm run typecheck` · Expected: เทสต์ผ่านทั้ง 13 ข้อ และ typecheck ผ่าน

- [ ] **Step 5: Commit**

```bash
cd .. && git add -A && git commit -m "feat: domain types and pure logic with vitest" -m "Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 3: Firebase hooks และ actions

**Files:**
- Create: `web/site/src/lib/hooks.ts`, `web/site/src/lib/actions.ts`

**Interfaces:**
- Consumes: `fb`, `DM_EMAIL` (Task 1) · `applyPurchase` (Task 2) · ชนิดใน `types.ts`
- Produces (`hooks.ts`): `useAuth(mode: "player"|"dm"): { ready: boolean; isDM: boolean }` · `useDoc<T>(ready: boolean, path: string): T | null | undefined` (`undefined`=กำลังโหลด `null`=ไม่มีเอกสาร; ผลมี `id` ให้) · `useCollection<T>(ready: boolean, path: string, opts?: { orderBy?: string; desc?: boolean; limit?: number }): T[] | undefined` · `usePlayerId(): string | null | undefined` · `signInDM(password: string): Promise<void>` · `signOutAll(): Promise<void>`
- Produces (`actions.ts`, ทั้งหมดคืน `Promise<void>`): `claimWeapon(playerId, weaponId)` · `chooseUnbound(playerId)` · `buyItem(playerId, item: Item)` · `setUnlocked(playerId, moveId, on: boolean)` · `savePlayer(playerId, patch)` · `setInventory(playerId, inventory: InvItem[])` · `setUnboundCenter(playerId, centerId: string|null)` · `resetWeapon(player: Player)` · `setShopOpen(open: boolean)` · `adjustCopper(playerId, delta: number)` · `logEntry(playerId, type, detail)`

- [ ] **Step 1: เขียน `hooks.ts`**

```ts
"use client";
import { useEffect, useState } from "react";
import { onAuthStateChanged, signInAnonymously, signInWithEmailAndPassword, signOut } from "firebase/auth";
import { collection, doc, limit, onSnapshot, orderBy, query } from "firebase/firestore";
import { DM_EMAIL, fb } from "./firebase";

export function useAuth(mode: "player" | "dm") {
  const [state, set] = useState({ ready: false, isDM: false });
  useEffect(() => {
    const { auth } = fb();
    return onAuthStateChanged(auth, (u) => {
      if (!u && mode === "player") {
        signInAnonymously(auth).catch(() => set({ ready: false, isDM: false }));
        return;
      }
      set({ ready: !!u, isDM: u?.email === DM_EMAIL });
    });
  }, [mode]);
  return state;
}

export const signInDM = async (password: string) => {
  await signInWithEmailAndPassword(fb().auth, DM_EMAIL, password);
};
export const signOutAll = () => signOut(fb().auth);

/** undefined = กำลังโหลด · null = ไม่มีเอกสาร */
export function useDoc<T>(ready: boolean, path: string): T | null | undefined {
  const [data, set] = useState<T | null | undefined>(undefined);
  useEffect(() => {
    if (!ready) return;
    return onSnapshot(
      doc(fb().db, path),
      (s) => set(s.exists() ? ({ id: s.id, ...s.data() } as T) : null),
      () => set(null),
    );
  }, [ready, path]);
  return ready ? data : undefined;
}

export function useCollection<T>(
  ready: boolean,
  path: string,
  opts: { orderBy?: string; desc?: boolean; limit?: number } = {},
): T[] | undefined {
  const [data, set] = useState<T[] | undefined>(undefined);
  const { orderBy: ob, desc, limit: lim } = opts;
  useEffect(() => {
    if (!ready) return;
    const c = collection(fb().db, path);
    const q = ob ? query(c, orderBy(ob, desc ? "desc" : "asc"), ...(lim ? [limit(lim)] : [])) : c;
    return onSnapshot(q, (s) => set(s.docs.map((d) => ({ id: d.id, ...d.data() }) as T)), () => set([]));
  }, [ready, path, ob, desc, lim]);
  return ready ? data : undefined;
}

export const PLAYER_KEY = "stage.playerId";
/** undefined = ยังไม่รู้ (SSR/ก่อน mount) · null = ยังไม่เลือกตัวละคร */
export function usePlayerId(): string | null | undefined {
  const [id, set] = useState<string | null | undefined>(undefined);
  useEffect(() => set(localStorage.getItem(PLAYER_KEY)), []);
  return id;
}
```

- [ ] **Step 2: เขียน `actions.ts`**

```ts
"use client";
import {
  addDoc, arrayRemove, arrayUnion, collection, doc, runTransaction, serverTimestamp, updateDoc, writeBatch,
} from "firebase/firestore";
import { fb } from "./firebase";
import { applyPurchase } from "./shop";
import type { InvItem, Item, Player } from "./types";

export const logEntry = async (playerId: string, type: string, detail: string) => {
  await addDoc(collection(fb().db, "log"), { playerId, type, detail, ts: serverTimestamp() });
};

/** จองอาวุธ + ตั้ง path ใน batch เดียว (กฎ getAfter ตรวจว่าจองจริง) */
export async function claimWeapon(playerId: string, weaponId: string) {
  const { db } = fb();
  const b = writeBatch(db);
  b.update(doc(db, "weapons", weaponId), { claimedBy: playerId });
  b.update(doc(db, "players", playerId), { path: "weapon", weaponId });
  await b.commit();
  await logEntry(playerId, "claim", weaponId);
}

export async function chooseUnbound(playerId: string) {
  await updateDoc(doc(fb().db, "players", playerId), { path: "unbound" });
  await logEntry(playerId, "claim", "unbound");
}

export async function buyItem(playerId: string, item: Item) {
  const { db } = fb();
  await runTransaction(db, async (tx) => {
    const ref = doc(db, "players", playerId);
    const me = (await tx.get(ref)).data() as Player;
    tx.update(ref, applyPurchase(me, item));
  });
  await logEntry(playerId, "buy", item.name);
}

export async function setUnlocked(playerId: string, moveId: string, on: boolean) {
  await updateDoc(doc(fb().db, "players", playerId), { unlocked: on ? arrayUnion(moveId) : arrayRemove(moveId) });
  await logEntry(playerId, "unlock", `${moveId} ${on ? "ปลด" : "ล็อกคืน"}`);
}

type Patch = Partial<Pick<Player, "level" | "hp" | "maxHp" | "ac" | "abilities" | "notes" | "copper">>;
export async function savePlayer(playerId: string, patch: Patch) {
  await updateDoc(doc(fb().db, "players", playerId), patch);
  await logEntry(playerId, "edit", "แก้ชีท");
}

export async function setInventory(playerId: string, inventory: InvItem[]) {
  await updateDoc(doc(fb().db, "players", playerId), { inventory });
  await logEntry(playerId, "edit", "แก้กระเป๋า");
}

export async function setUnboundCenter(playerId: string, centerId: string | null) {
  await updateDoc(doc(fb().db, "players", playerId), { unboundCenter: centerId });
}

export async function resetWeapon(p: Player) {
  const { db } = fb();
  const b = writeBatch(db);
  if (p.weaponId) b.update(doc(db, "weapons", p.weaponId), { claimedBy: null });
  b.update(doc(db, "players", p.id), { path: null, weaponId: null, unboundCenter: null, unlocked: [] });
  await b.commit();
  await logEntry(p.id, "edit", "รีเซ็ตอาวุธ");
}

export const setShopOpen = (open: boolean) => updateDoc(doc(fb().db, "config", "game"), { shopOpen: open });

export async function adjustCopper(playerId: string, delta: number) {
  const { db } = fb();
  await runTransaction(db, async (tx) => {
    const ref = doc(db, "players", playerId);
    const cur = ((await tx.get(ref)).data() as Player).copper;
    tx.update(ref, { copper: Math.max(0, cur + delta) });
  });
  await logEntry(playerId, "edit", `เงิน ${delta > 0 ? "+" : ""}${delta} ทองแดง`);
}
```

- [ ] **Step 3: รันตรวจ**

Run (ใน `web/site`): `npm run typecheck && npm run lint` · Expected: ผ่านโดยไม่มี error (lint เตือนได้ ห้าม error)

- [ ] **Step 4: Commit**

```bash
cd .. && git add -A && git commit -m "feat: firebase hooks and actions" -m "Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 4: ธีม ฟอนต์ ไอคอน และคอมโพเนนต์พื้นฐาน

**Files:**
- Modify: `web/site/src/app/globals.css`, `web/site/src/app/layout.tsx`
- Create: `web/site/src/components/{IconSprite,Icon,GlassWindow,SegBar,TabBar}.tsx`

**Interfaces:**
- Produces: `<Icon id="sword" className? />` (id ที่มี: `sword shield bow codex guitar staff leaf feather bread coin user tree bag eye`) · `<GlassWindow title?>` · `<SegBar hp maxHp />` · `<TabBar items={{href,label,icon}[]} />` · คลาส CSS: `win wt muted lv btn btn gold chip coins ab slot node tag detail item ico price sw prow tabbar tab wgrid wc toast` (ตามที่พอร์ตจาก mock) และคลาสของ React Flow: `rf-node rf-orbit ring-flow`

- [ ] **Step 1: พอร์ต CSS**

เปิด `web/mock/index.html` คัดลอกเนื้อหาทั้งหมดระหว่าง `<style>` และ `</style>` ไปต่อท้าย `web/site/src/app/globals.css` (หลัง `@import`/`@layer` ของ Tailwind และ shadcn) แล้วแก้ 3 จุด:
1. ในบล็อก `:root{...}` เปลี่ยนสองบรรทัดฟอนต์เป็น:
   `--display:var(--font-kanit),system-ui,sans-serif; --body:var(--font-plex),system-ui,sans-serif;`
2. ลบกฎ `.over`, `.over.on` และ `.toast`, `.toast.on` ออก (ไม่ใช้ในแอปจริง ใช้ sonner)
3. ต่อท้ายไฟล์เพิ่มสไตล์ของต้นสกิลแบบ React Flow (แทนกฎ `.ring ...` ที่ใช้กับ SVG เดิม; กฎ `.ring ...` ของ mock ปล่อยไว้ได้ ไม่ทำอะไร):
```css
/* ---------- ต้นสกิล (React Flow) ---------- */
.ring-flow{height:440px;background:transparent}
.ring-flow .react-flow__pane{cursor:grab}
.ring-flow .react-flow__attribution{background:transparent;color:#7f9fc9}
.ring-flow .react-flow__edge-path{stroke:#5b8fd0;stroke-opacity:.35;stroke-width:1}
.ring-flow .react-flow__edge.lit .react-flow__edge-path{stroke:var(--mint);stroke-opacity:.95;stroke-width:1.8;filter:drop-shadow(0 0 3px var(--mint))}
.rf-node{width:46px;height:46px;border-radius:50%;display:grid;place-items:center;cursor:pointer;
  background:#08123a;border:1.5px solid #5b8fd0;color:#b9d2f0;font:500 14px var(--display);position:relative}
.rf-node.center{width:64px;height:64px;background:#0d3a47;border:2px solid var(--gold);color:var(--gold);box-shadow:0 0 12px #ffd27a88}
.rf-node.center svg{width:30px;height:30px}
.rf-node.on{background:#0d3a47;border-color:var(--mint);border-width:2px;color:var(--mint);box-shadow:0 0 12px #7cf7d4aa}
.rf-node.sec{border-style:dashed}
.rf-node.sel::after{content:"";position:absolute;inset:-6px;border-radius:50%;border:2px solid var(--gold)}
.rf-node.flash::before{content:"";position:absolute;inset:0;border-radius:50%;border:2px solid var(--mint);animation:rfburst .8s ease-out forwards}
@keyframes rfburst{from{transform:scale(1);opacity:.95}to{transform:scale(2.3);opacity:0}}
.rf-orbit{border-radius:50%;border:1px solid #5b8fd0;opacity:.35;pointer-events:none}
.rf-orbit.far{border-style:dashed;opacity:.2}
```

- [ ] **Step 2: เขียน `layout.tsx`**

```tsx
import type { Metadata, Viewport } from "next";
import { IBM_Plex_Sans_Thai, Kanit } from "next/font/google";
import { Toaster } from "@/components/ui/sonner";
import { IconSprite } from "@/components/IconSprite";
import "./globals.css";

const kanit = Kanit({ subsets: ["thai", "latin"], weight: ["400", "500", "600"], variable: "--font-kanit" });
const plex = IBM_Plex_Sans_Thai({ subsets: ["thai", "latin"], weight: ["400", "500", "600"], variable: "--font-plex" });

export const metadata: Metadata = { title: "ม่านเวทีของจอมมาร — สถานะผู้กล้า" };
export const viewport: Viewport = { width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="th" className={`${kanit.variable} ${plex.variable}`}>
      <body>
        <IconSprite />
        <main className="app">{children}</main>
        <Toaster theme="dark" position="bottom-center" />
      </body>
    </html>
  );
}
```
(ถ้า shadcn สร้าง `layout.tsx` เดิมที่มี provider อื่น ให้คงของ shadcn ที่จำเป็นและใช้โครงข้างบนเป็นหลัก)

- [ ] **Step 3: เขียน `IconSprite.tsx` และ `Icon.tsx`**

`IconSprite.tsx` (พอร์ตจาก `<symbol>` ใน mock: แปลงแอตทริบิวต์เป็น camelCase):
```tsx
const S = { fill: "none", stroke: "currentColor", strokeWidth: 1.6, strokeLinecap: "round", strokeLinejoin: "round" } as const;

export function IconSprite() {
  return (
    <svg width="0" height="0" style={{ position: "absolute" }} aria-hidden="true">
      <defs>
        <symbol id="i-sword" viewBox="0 0 24 24"><g {...S}><path d="M20 4l-9.5 9.5M20 4h-4.5M20 4v4.5M7.5 11l5.5 5.5M11 14l-5.5 5.5M4 20.5l1.5-1.5" /></g></symbol>
        <symbol id="i-shield" viewBox="0 0 24 24"><g {...S}><path d="M12 3l7 3v5.5c0 4.5-3 7.5-7 9.5-4-2-7-5-7-9.5V6z" /><path d="M12 3v18" opacity=".5" /></g></symbol>
        <symbol id="i-bow" viewBox="0 0 24 24"><g {...S}><path d="M6 3c9 1 15 7 15 15M6 3l15 15M4 21l10-10" /></g></symbol>
        <symbol id="i-codex" viewBox="0 0 24 24"><g {...S}><path d="M5 4h10.5A2.5 2.5 0 0118 6.5V20H7.5A2.5 2.5 0 015 17.5z" /><path d="M8 4v13.5M11.5 9l1.2 2.2 2.3.3-1.7 1.6.4 2.3-2.2-1.2-2.2 1.2.4-2.3L8 11.5l2.3-.3z" opacity=".8" /></g></symbol>
        <symbol id="i-guitar" viewBox="0 0 24 24"><g {...S}><circle cx="9" cy="15" r="4.6" /><circle cx="9" cy="15" r="1.2" /><path d="M12.4 11.6L19.5 4.5M17.5 3l3.5 3.5" /></g></symbol>
        <symbol id="i-staff" viewBox="0 0 24 24"><g {...S}><path d="M5 20l9-9" /><circle cx="17.5" cy="6.5" r="3.3" /><path d="M17.5 3.2V1.5M20.8 6.5h1.7M14.2 6.5h-1.7" opacity=".7" /></g></symbol>
        <symbol id="i-leaf" viewBox="0 0 24 24"><g {...S}><path d="M5 19C5 10 11 5 19 5c0 8-5 14-14 14zM5 19l8-8" /></g></symbol>
        <symbol id="i-feather" viewBox="0 0 24 24"><g {...S}><path d="M20 4c-8 0-14 6-14 14M6 18c6 0 12-4 14-14M4 20l2-2M9 15h6" /></g></symbol>
        <symbol id="i-bread" viewBox="0 0 24 24"><g {...S}><path d="M4 16c0-4 3-7.5 8-7.5s8 3.5 8 7.5v2H4z" /><path d="M9 13l1 2M13 12.5l1 2" opacity=".7" /></g></symbol>
        <symbol id="i-coin" viewBox="0 0 24 24"><g {...S}><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="5.5" opacity=".6" /></g></symbol>
        <symbol id="i-user" viewBox="0 0 24 24"><g {...S}><circle cx="12" cy="8" r="4" /><path d="M4 21c1-5 4-7 8-7s7 2 8 7" /></g></symbol>
        <symbol id="i-tree" viewBox="0 0 24 24"><g {...S}><circle cx="12" cy="13" r="3" /><circle cx="12" cy="4" r="1.7" /><circle cx="4.5" cy="18.5" r="1.7" /><circle cx="19.5" cy="18.5" r="1.7" /><path d="M12 10V5.7M9.5 14.7L6 17.2M14.5 14.7L18 17.2" /></g></symbol>
        <symbol id="i-bag" viewBox="0 0 24 24"><g {...S}><path d="M6 8h12l1 12H5zM9 8V6.5a3 3 0 016 0V8" /></g></symbol>
        <symbol id="i-eye" viewBox="0 0 24 24"><g {...S}><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z" /><circle cx="12" cy="12" r="3" /></g></symbol>
      </defs>
    </svg>
  );
}
```
`Icon.tsx`:
```tsx
export function Icon({ id, className }: { id: string; className?: string }) {
  return (
    <svg className={className} aria-hidden="true">
      <use href={`#i-${id}`} />
    </svg>
  );
}
```

- [ ] **Step 4: เขียน `GlassWindow.tsx`, `SegBar.tsx`, `TabBar.tsx`**

```tsx
// GlassWindow.tsx
export function GlassWindow({ title, className = "", children }: { title?: string; className?: string; children: React.ReactNode }) {
  return (
    <section className={`win ${className}`}>
      {title && <div className="wt">{title}</div>}
      {children}
    </section>
  );
}
```
```tsx
// SegBar.tsx
export function SegBar({ hp, maxHp, segments = 14 }: { hp: number; maxHp: number; segments?: number }) {
  const filled = maxHp > 0 ? Math.round((Math.max(0, Math.min(hp, maxHp)) / maxHp) * segments) : 0;
  return (
    <div className="segbar" role="meter" aria-valuemin={0} aria-valuemax={maxHp} aria-valuenow={hp} aria-label="พลังชีวิต">
      {Array.from({ length: segments }, (_, i) => <i key={i} className={i < filled ? "f" : ""} />)}
    </div>
  );
}
```
```tsx
// TabBar.tsx
"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Icon } from "./Icon";

export type TabItem = { href: string; label: string; icon: string };

export function TabBar({ items }: { items: TabItem[] }) {
  const path = usePathname();
  return (
    <nav className="tabbar" aria-label="เมนูหลัก">
      <div className="in" style={{ gridTemplateColumns: `repeat(${items.length}, 1fr)` }}>
        {items.map((t) => (
          <Link key={t.href} href={t.href} className="tab" aria-current={path === t.href ? "page" : undefined} aria-selected={path === t.href}>
            <Icon id={t.icon} />
            {t.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}
```
เพิ่มใน `globals.css`: `.tab[aria-current=page]{color:var(--gold);box-shadow:inset 0 -2px 0 var(--gold);background:#ffd27a14}` และ `a.tab{text-decoration:none}`

- [ ] **Step 5: รันตรวจ**

Run: `npm run typecheck && npm run build` · Expected: ผ่าน · แล้ว `npm run dev` เปิด `http://localhost:3000` ต้องเห็นพื้นหลังท้องฟ้ายามค่ำ (ฟอนต์และสีตรงกับ mock) หน้าเริ่มต้นเดิมของ create-next-app จะถูกแทนใน Task 5

- [ ] **Step 6: Commit**

```bash
cd .. && git add -A && git commit -m "feat: theme, fonts, icon sprite and base components" -m "Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 5: หน้าเลือกชื่อ ตัวห่อผู้เล่น และหน้าสถานะ

**Files:**
- Create: `web/site/src/components/{PlayerProvider,AbilityGrid,Bag}.tsx`, `web/site/src/app/me/layout.tsx`, `web/site/src/app/me/page.tsx`
- Modify: `web/site/src/app/page.tsx` (แทนที่ทั้งไฟล์)

**Interfaces:**
- Consumes: hooks/actions (Task 3), ตรรกะ (Task 2), คอมโพเนนต์ (Task 4)
- Produces: `usePlayerCtx(): { id: string; me: Player; weapons: Record<string, ClaimedWeapon>; game: GameConfig }` จาก `@/components/PlayerProvider` (ใช้ใน Task 6-7) · `<AbilityGrid abilities />` · `<Bag inventory />`

- [ ] **Step 1: `page.tsx` (เลือกชื่อ)**

```tsx
"use client";
import { useRouter } from "next/navigation";
import players from "@/data/players.json";
import { PLAYER_KEY } from "@/lib/hooks";

export default function Picker() {
  const router = useRouter();
  return (
    <>
      <h1 style={{ fontSize: "1.8rem", margin: "24px 0 14px" }}>เลือกตัวละครของคุณ</h1>
      <div className="wgrid" style={{ gridTemplateColumns: "repeat(auto-fit,minmax(140px,1fr))" }}>
        {players.map((p) => (
          <button key={p.id} className="wc" onClick={() => { localStorage.setItem(PLAYER_KEY, p.id); router.push("/me"); }}>
            <b>{p.name}</b>
          </button>
        ))}
      </div>
      <p style={{ marginTop: 24 }}><a className="linkbtn" href="/dm">สำหรับ DM</a></p>
    </>
  );
}
```

- [ ] **Step 2: `PlayerProvider.tsx`**

```tsx
"use client";
import { createContext, useContext, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useAuth, useCollection, useDoc, usePlayerId } from "@/lib/hooks";
import type { ClaimedWeapon, GameConfig, Player } from "@/lib/types";

type Ctx = { id: string; me: Player; weapons: Record<string, ClaimedWeapon>; game: GameConfig };
const PlayerCtx = createContext<Ctx | null>(null);

export function usePlayerCtx(): Ctx {
  const v = useContext(PlayerCtx);
  if (!v) throw new Error("usePlayerCtx ต้องอยู่ใน PlayerProvider");
  return v;
}

export function PlayerProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const id = usePlayerId();
  const { ready } = useAuth("player");
  const on = ready && !!id;
  const me = useDoc<Player>(on, `players/${id}`);
  const list = useCollection<ClaimedWeapon>(on, "weapons");
  const game = useDoc<GameConfig>(on, "config/game");
  const weapons = useMemo(() => Object.fromEntries((list ?? []).map((w) => [w.id, w])), [list]);

  useEffect(() => { if (id === null) router.replace("/"); }, [id, router]);

  if (id === undefined || id === null || me === undefined || list === undefined || game === undefined)
    return <p className="muted" style={{ padding: 24 }}>กำลังโหลด…</p>;
  if (me === null)
    return <p style={{ padding: 24 }}>ยังไม่มีข้อมูลตัวละครนี้ ให้ DM รัน seed ก่อน · <a className="linkbtn" href="/">เปลี่ยนตัวละคร</a></p>;
  return <PlayerCtx.Provider value={{ id, me, weapons, game: game ?? { shopOpen: false } }}>{children}</PlayerCtx.Provider>;
}
```

- [ ] **Step 3: `me/layout.tsx`**

```tsx
"use client";
import Link from "next/link";
import { PlayerProvider, usePlayerCtx } from "@/components/PlayerProvider";
import { TabBar } from "@/components/TabBar";
import { PLAYER_KEY } from "@/lib/hooks";

function Header() {
  const { me } = usePlayerCtx();
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, margin: "8px 0" }}>
      <h1 style={{ fontSize: "1.6rem" }}>{me.name}</h1>
      <span className="lv" style={{ marginLeft: 0 }}>Lv.{me.level}</span>
      <Link href="/" className="linkbtn" style={{ marginLeft: "auto" }} onClick={() => localStorage.removeItem(PLAYER_KEY)}>เปลี่ยนตัวละคร</Link>
    </div>
  );
}

export default function MeLayout({ children }: { children: React.ReactNode }) {
  return (
    <PlayerProvider>
      <Header />
      {children}
      <TabBar items={[
        { href: "/me", label: "สถานะ", icon: "user" },
        { href: "/me/skill", label: "สกิล", icon: "tree" },
        { href: "/me/shop", label: "ร้านค้า", icon: "bag" },
      ]} />
    </PlayerProvider>
  );
}
```

- [ ] **Step 4: `AbilityGrid.tsx`, `Bag.tsx`**

```tsx
// AbilityGrid.tsx
import { abilityMod } from "@/lib/tiers";
import type { Abilities } from "@/lib/types";

const ORDER: [keyof Abilities, string][] = [["str", "STR"], ["dex", "DEX"], ["con", "CON"], ["int", "INT"], ["wis", "WIS"], ["cha", "CHA"]];

export function AbilityGrid({ abilities }: { abilities: Abilities }) {
  return (
    <div className="abil">
      {ORDER.map(([k, label]) => (
        <div key={k} className={`ab ${abilities[k] >= 15 ? "hi" : ""}`}>
          <small>{label}</small>
          <b>{abilityMod(abilities[k])}</b>
          <em>{abilities[k]}</em>
        </div>
      ))}
    </div>
  );
}
```
```tsx
// Bag.tsx
import { iconFor } from "@/lib/tiers";
import type { InvItem } from "@/lib/types";
import { Icon } from "./Icon";

export function Bag({ inventory, slots = 15 }: { inventory: InvItem[]; slots?: number }) {
  const empty = Math.max(0, slots - inventory.length);
  return (
    <div className="bag">
      {inventory.map((it, i) => (
        <button key={`${it.itemId ?? it.name}-${i}`} className="slot has" aria-label={`${it.name} ${it.qty} ชิ้น`}>
          <Icon id={iconFor(it.itemId)} />
          <span className="q">{it.qty}</span>
          <span className="tip">{it.name}</span>
        </button>
      ))}
      {Array.from({ length: empty }, (_, i) => <div key={`e${i}`} className="slot" aria-hidden="true" />)}
    </div>
  );
}
```

- [ ] **Step 5: `me/page.tsx` (สถานะ)**

```tsx
"use client";
import { AbilityGrid } from "@/components/AbilityGrid";
import { Bag } from "@/components/Bag";
import { GlassWindow } from "@/components/GlassWindow";
import { Icon } from "@/components/Icon";
import { usePlayerCtx } from "@/components/PlayerProvider";
import { SegBar } from "@/components/SegBar";
import weaponsData from "@/data/weapons.json";
import { format } from "@/lib/money";
import type { Weapon } from "@/lib/types";

export default function StatusPage() {
  const { me } = usePlayerCtx();
  const weapon = (weaponsData as Weapon[]).find((w) => w.id === me.weaponId);
  const sub = me.path === "weapon" && weapon ? `ผู้ถืออาวุธ · ${weapon.name} ${weapon.fullName}` : me.path === "unbound" ? "ผู้ไม่ผูกอาวุธ" : "ยังไม่ได้เลือกอาวุธ";
  return (
    <>
      <GlassWindow>
        <div className="hero">
          <div className="emblem"><Icon id={me.path === "weapon" && weapon ? weapon.id : "user"} /></div>
          <div><p className="sub">{sub}</p></div>
        </div>
        <div className="vitals">
          <div className="hp">
            <small>พลังชีวิต</small>
            <div className="hpnum">{me.hp} <span>/ {me.maxHp}</span></div>
            <SegBar hp={me.hp} maxHp={me.maxHp} />
          </div>
          <div className="chip"><small>เกราะ</small><b>{me.ac}</b></div>
          <div className="chip"><small>เงิน</small><b style={{ color: "var(--gold)", fontSize: "1rem" }}>{format(me.copper)}</b></div>
        </div>
        {me.notes && <p className="muted" style={{ marginTop: 10 }}>{me.notes}</p>}
      </GlassWindow>
      <GlassWindow title="ค่าพลัง"><AbilityGrid abilities={me.abilities} /></GlassWindow>
      <GlassWindow title="กระเป๋า"><Bag inventory={me.inventory} /></GlassWindow>
    </>
  );
}
```

- [ ] **Step 6: รันตรวจ**

Run: `npm run typecheck && npm run build` · Expected: ผ่าน · ทดสอบมือ (Task 9 มีเช็กลิสต์เต็ม): `npm run dev` เปิด `/` เลือกชื่อ → `/me` ต้องเห็นสถานะที่ DM กรอกไว้จาก Firestore จริง (ต้องมี `.env.local`)

- [ ] **Step 7: Commit**

```bash
cd .. && git add -A && git commit -m "feat: player picker, provider and status page" -m "Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 6: หน้าสกิล (วงโหนด React Flow · รายละเอียดท่า · เลือกอาวุธ)

**Files:**
- Create: `web/site/src/components/{SkillRing,MoveDetail,WeaponPicker}.tsx`, `web/site/src/app/me/skill/page.tsx`

**Interfaces:**
- Consumes: `usePlayerCtx` (Task 5) · `ringPositions`, `tierInfo` (Task 2) · `claimWeapon`, `chooseUnbound` (Task 3)
- Produces: `<SkillRing moves unlocked selected onSelect centerIcon />` โดย `moves: Move[]`, `unlocked: string[]`, `selected: number` (0 = ท่ากลาง), `onSelect(slot: number)`, `centerIcon: string` — ใช้ซ้ำในหน้า DM (Task 8) · `<MoveDetail selected moves unlocked center />` · `<WeaponPicker />`

- [ ] **Step 1: `SkillRing.tsx`**

```tsx
"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import { Handle, Position, ReactFlow, type Edge, type Node, type NodeProps } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { ringPositions } from "@/lib/ring";
import type { Move } from "@/lib/types";
import { Icon } from "./Icon";

const R1 = 130;
type SkillData = { label: string; on: boolean; secret: boolean; selected: boolean; flash: boolean; icon?: string; center?: boolean };
type OrbitData = { r: number; far: boolean };

const hidden = { left: "50%", top: "50%", transform: "translate(-50%,-50%)", opacity: 0, pointerEvents: "none" } as const;

function SkillNode({ data }: NodeProps<Node<SkillData>>) {
  const cls = ["rf-node", data.center && "center", data.on && "on", data.secret && "sec", data.selected && "sel", data.flash && "flash"].filter(Boolean).join(" ");
  return (
    <div className={cls} role="button" aria-label={data.label}>
      <Handle type="target" position={Position.Top} style={hidden} isConnectable={false} />
      <Handle type="source" position={Position.Top} style={hidden} isConnectable={false} />
      {data.icon ? <Icon id={data.icon} /> : data.label}
    </div>
  );
}
function Orbit({ data }: NodeProps<Node<OrbitData>>) {
  return <div className={`rf-orbit ${data.far ? "far" : ""}`} style={{ width: data.r * 2, height: data.r * 2 }} />;
}
const nodeTypes = { skill: SkillNode, orbit: Orbit };

export function SkillRing({ moves, unlocked, selected, onSelect, centerIcon }: {
  moves: Move[]; unlocked: string[]; selected: number; onSelect: (slot: number) => void; centerIcon: string;
}) {
  // วงวาบเมื่อท่าเพิ่งถูกปลด (เทียบกับค่าก่อนหน้า)
  const prev = useRef<Set<string> | null>(null);
  const [flash, setFlash] = useState<string | null>(null);
  useEffect(() => {
    const now = new Set(unlocked);
    if (prev.current) {
      const added = [...now].find((id) => !prev.current!.has(id));
      if (added) { setFlash(added); const t = setTimeout(() => setFlash(null), 900); prev.current = now; return () => clearTimeout(t); }
    }
    prev.current = now;
  }, [unlocked]);

  const { nodes, edges } = useMemo(() => {
    const on = new Set(unlocked);
    const pos = ringPositions(moves.length, R1);
    const orbit = (id: string, r: number, far: boolean): Node<OrbitData> => ({
      id, type: "orbit", position: { x: -r, y: -r }, data: { r, far },
      draggable: false, selectable: false, focusable: false, zIndex: -1, style: { pointerEvents: "none" },
    });
    const ns: Node[] = [orbit("o1", R1, false), orbit("o2", R1 + 40, true), orbit("o3", R1 + 80, true)];
    ns.push({
      id: "c", type: "skill", position: { x: -32, y: -32 }, draggable: false,
      data: { label: "ท่ากลาง", on: true, secret: false, selected: selected === 0, flash: false, icon: centerIcon, center: true } satisfies SkillData,
    });
    const es: Edge[] = [];
    moves.forEach((m, i) => {
      const lit = on.has(m.id);
      const label = m.secret && !lit ? "?" : String(m.slot);
      ns.push({
        id: `m${m.slot}`, type: "skill", position: { x: pos[i].x - 23, y: pos[i].y - 23 }, draggable: false,
        data: { label, on: lit, secret: !!m.secret, selected: selected === m.slot, flash: flash === m.id } satisfies SkillData,
      });
      es.push({ id: `e${m.slot}`, source: "c", target: `m${m.slot}`, type: "straight", className: lit ? "lit" : "", selectable: false, focusable: false });
    });
    return { nodes: ns, edges: es };
  }, [moves, unlocked, selected, flash, centerIcon]);

  return (
    <div className="ring-flow">
      <ReactFlow
        nodes={nodes} edges={edges} nodeTypes={nodeTypes} colorMode="dark"
        fitView fitViewOptions={{ padding: 0.12 }} minZoom={0.5} maxZoom={1.6}
        nodesDraggable={false} nodesConnectable={false} zoomOnScroll={false} preventScrolling={false}
        onNodeClick={(_, n) => { if (n.id === "c") onSelect(0); else if (n.id.startsWith("m")) onSelect(Number(n.id.slice(1))); }}
      />
    </div>
  );
}
```

- [ ] **Step 2: `MoveDetail.tsx`**

```tsx
import { tierInfo } from "@/lib/tiers";
import type { Move } from "@/lib/types";
import { GlassWindow } from "./GlassWindow";

export function MoveDetail({ selected, moves, unlocked, center }: {
  selected: number; moves: Move[]; unlocked: string[]; center: { name: string; effect: string } | null;
}) {
  if (selected === 0)
    return (
      <GlassWindow className="detail">
        <h3>{center?.name ?? "ท่ากลาง"}</h3>
        <div className="row"><span className={`tag ${center ? "on" : ""}`}>{center ? "ท่ากลาง ปลดแล้ว" : "รอ DM เลือกให้"}</span></div>
        <p>{center?.effect ?? "DM จะเลือกท่ากลางให้คุณ"}</p>
      </GlassWindow>
    );
  const m = moves.find((x) => x.slot === selected);
  if (!m) return null;
  const on = unlocked.includes(m.id);
  const t = tierInfo(m.tier);
  return (
    <GlassWindow className="detail">
      <h3>{m.secret ? (on ? "ท่าลับปลดแล้ว" : "ท่าลับ") : m.name}</h3>
      <div className="row">
        <span className={`tag ${on ? "on" : ""}`}>{on ? "ปลดแล้ว" : "ยังล็อก"}</span>
        <span className={`tag ${t.cls}`}>{t.label}</span>
      </div>
      {m.secret ? (
        <p className="muted">{on ? "DM จะแจ้งรายละเอียดของท่านี้ให้" : "ยังไม่มีข้อมูล ท่านี้จะเผยเมื่อถึงเวลา"}</p>
      ) : (
        <dl>
          <dt>ผล</dt><dd>{m.effect}</dd>
          <dt>วิธีปลด</dt><dd>{m.unlock}</dd>
        </dl>
      )}
    </GlassWindow>
  );
}
```

- [ ] **Step 3: `WeaponPicker.tsx`**

```tsx
"use client";
import { useState } from "react";
import { toast } from "sonner";
import players from "@/data/players.json";
import weaponsData from "@/data/weapons.json";
import { chooseUnbound, claimWeapon } from "@/lib/actions";
import type { Weapon } from "@/lib/types";
import { GlassWindow } from "./GlassWindow";
import { Icon } from "./Icon";
import { usePlayerCtx } from "./PlayerProvider";

const nameOf = (id: string) => players.find((p) => p.id === id)?.name ?? id;

export function WeaponPicker() {
  const { id, weapons } = usePlayerCtx();
  const [pick, setPick] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const run = async (fn: () => Promise<void>, fail: string) => {
    setBusy(true);
    try { await fn(); } catch { toast.error(fail); } finally { setBusy(false); }
  };
  return (
    <GlassWindow title="เลือกอาวุธโบราณ">
      <p className="muted" style={{ marginBottom: 12 }}>เลือกได้ครั้งเดียว และแต่ละอาวุธมีเจ้าของได้คนเดียว</p>
      <div className="wgrid">
        {(weaponsData as Weapon[]).map((w) => {
          const owner = weapons[w.id]?.claimedBy;
          return (
            <button key={w.id} className={`wc ${owner ? "taken" : ""} ${pick === w.id ? "pick" : ""}`} disabled={!!owner || busy} onClick={() => setPick(w.id)}>
              <Icon id={w.id} />
              <b>{w.name}</b>
              <small>{w.role}</small>
              {owner && <span className="own">เจ้าของ: {nameOf(owner)}</span>}
            </button>
          );
        })}
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap", marginTop: 14 }}>
        <button className="linkbtn" disabled={busy} onClick={() => run(() => chooseUnbound(id), "เลือกไม่ได้ ลองใหม่")}>ไม่ผูกอาวุธ</button>
        <button className="btn gold" disabled={!pick || busy}
          onClick={() => pick && run(() => claimWeapon(id, pick), "เลือกไม่ได้ อาจมีคนเลือกอาวุธนี้ไปแล้ว")}>ยืนยันเลือก</button>
      </div>
    </GlassWindow>
  );
}
```
(ข้อความยืนยัน: ปุ่ม "ยืนยันเลือก" เป็นขั้นยืนยันแล้ว จึงไม่ใช้ `confirm()`)

- [ ] **Step 4: `me/skill/page.tsx`**

```tsx
"use client";
import { useState } from "react";
import { GlassWindow } from "@/components/GlassWindow";
import { MoveDetail } from "@/components/MoveDetail";
import { usePlayerCtx } from "@/components/PlayerProvider";
import { SkillRing } from "@/components/SkillRing";
import { WeaponPicker } from "@/components/WeaponPicker";
import unboundData from "@/data/unbound.json";
import weaponsData from "@/data/weapons.json";
import type { Unbound, Weapon } from "@/lib/types";

export default function SkillPage() {
  const { me } = usePlayerCtx();
  const [selected, setSelected] = useState(1);
  if (!me.path) return <WeaponPicker />;

  const unbound = unboundData as Unbound;
  const weapon = me.path === "weapon" ? (weaponsData as Weapon[]).find((w) => w.id === me.weaponId) : undefined;
  const moves = weapon ? weapon.moves : unbound.ring1;
  const centerUnbound = unbound.center.find((c) => c.id === me.unboundCenter);
  const center = weapon ? weapon.center : centerUnbound ? { name: centerUnbound.name, effect: centerUnbound.effect } : null;
  const title = weapon ? `${weapon.name} ${weapon.fullName}` : "ผู้ไม่ผูกอาวุธ";

  return (
    <>
      <GlassWindow title={title}>
        <SkillRing moves={moves} unlocked={me.unlocked} selected={selected} onSelect={setSelected} centerIcon={weapon ? weapon.id : "user"} />
        <p className="muted" style={{ fontSize: ".85rem", textAlign: "center", marginTop: 6 }}>วงที่ 2 และ 3 ยังปิดอยู่ ปลดได้เมื่อเรื่องดำเนินไปถึง</p>
      </GlassWindow>
      <MoveDetail selected={selected} moves={moves} unlocked={me.unlocked} center={center} />
    </>
  );
}
```

- [ ] **Step 5: รันตรวจ**

Run: `npm run typecheck && npm run build` · Expected: ผ่าน · ตรวจด้วยตา: เปิดหน้า `/me/skill` ของผู้เล่นที่เลือกดาบแล้ว ต้องเห็นท่ากลางที่กลาง 10 โหนดเป็นวงรอบ เส้นเชื่อมจากกลางไปทุกโหนด (เส้นสว่างเฉพาะท่าที่ปลด) และวงที่ 2-3 เป็นเงาจาง · ถ้าเส้นเชื่อมไปออกที่ขอบโหนดไม่ใช่ศูนย์กลาง ให้ตรวจ `style` ของ `Handle` (`hidden`) ว่าอยู่กลางโหนด

- [ ] **Step 6: Commit**

```bash
cd .. && git add -A && git commit -m "feat: skill ring (React Flow), move detail and weapon picker" -m "Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 7: หน้าร้านค้า

**Files:**
- Create: `web/site/src/app/me/shop/page.tsx`

**Interfaces:**
- Consumes: `usePlayerCtx` · `buyItem` (Task 3) · `format` · `iconFor` · `@/data/items.json`

- [ ] **Step 1: เขียน `me/shop/page.tsx`**

```tsx
"use client";
import { toast } from "sonner";
import { GlassWindow } from "@/components/GlassWindow";
import { Icon } from "@/components/Icon";
import { usePlayerCtx } from "@/components/PlayerProvider";
import itemsData from "@/data/items.json";
import { buyItem } from "@/lib/actions";
import { format } from "@/lib/money";
import { iconFor } from "@/lib/tiers";
import type { Item } from "@/lib/types";

export default function ShopPage() {
  const { id, me, game } = usePlayerCtx();
  const buy = async (it: Item) => {
    try { await buyItem(id, it); toast.success(`ซื้อแล้ว: ${it.name}`); }
    catch (e) { toast.error(e instanceof Error && e.message === "เงินไม่พอ" ? "เงินไม่พอ" : "ซื้อไม่ได้ ร้านอาจปิดแล้ว"); }
  };
  return (
    <GlassWindow>
      <div className="shophead">
        <div className="wt" style={{ margin: 0, flex: 1, minWidth: 120 }}>ร้านของทั่วไป</div>
        <span className={`open ${game.shopOpen ? "" : "closed"}`}>{game.shopOpen ? "เปิดอยู่" : "ปิดอยู่"}</span>
      </div>
      <div className="coins" style={{ margin: "10px 0 6px" }}><Icon id="coin" /><span>{format(me.copper)}</span></div>
      {game.shopOpen ? (
        (itemsData as Item[]).map((it) => (
          <div key={it.id} className="item">
            <div className="ico"><Icon id={iconFor(it.id)} /></div>
            <div><b>{it.name}</b><small>{it.desc}</small></div>
            <div className="price">
              <span>{format(it.price)}</span>
              <button className="btn" disabled={me.copper < it.price} onClick={() => buy(it)}>ซื้อ</button>
            </div>
          </div>
        ))
      ) : (
        <p className="muted">ร้านปิดอยู่ ผู้ควบคุมเกมยังไม่เปิดร้าน</p>
      )}
    </GlassWindow>
  );
}
```

- [ ] **Step 2: รันตรวจ**

Run: `npm run typecheck && npm run build` · Expected: ผ่าน

- [ ] **Step 3: Commit**

```bash
cd .. && git add -A && git commit -m "feat: shop page" -m "Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 8: หน้า DM (ล็อกอิน · ภาพรวม · รายละเอียดผู้เล่น)

**Files:**
- Create: `web/site/src/components/DmProvider.tsx`, `web/site/src/app/dm/layout.tsx`, `web/site/src/app/dm/page.tsx`, `web/site/src/app/dm/[id]/page.tsx`

**Interfaces:**
- Consumes: hooks (`useAuth("dm")`, `useCollection`, `useDoc`, `signInDM`, `signOutAll`), actions ทั้งหมด (Task 3), `SkillRing`/`MoveDetail` (Task 6), `format`, `AbilityGrid` ไม่ใช้
- Produces: `useDmCtx(): { players: Player[]; game: GameConfig; log: LogEntry[] }` จาก `@/components/DmProvider`

- [ ] **Step 1: `DmProvider.tsx`**

```tsx
"use client";
import { createContext, useContext, useState } from "react";
import { signInDM, signOutAll, useAuth, useCollection, useDoc } from "@/lib/hooks";
import type { GameConfig, LogEntry, Player } from "@/lib/types";
import { GlassWindow } from "./GlassWindow";

type Ctx = { players: Player[]; game: GameConfig; log: LogEntry[] };
const DmCtx = createContext<Ctx | null>(null);
export function useDmCtx(): Ctx {
  const v = useContext(DmCtx);
  if (!v) throw new Error("useDmCtx ต้องอยู่ใน DmProvider");
  return v;
}

function Login() {
  const [pw, setPw] = useState("");
  const [err, setErr] = useState("");
  const go = async () => { try { await signInDM(pw); setErr(""); } catch { setErr("รหัสผ่านไม่ถูกต้อง"); } };
  return (
    <GlassWindow title="เข้าสู่ระบบ DM">
      <form onSubmit={(e) => { e.preventDefault(); go(); }} style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <input type="password" value={pw} onChange={(e) => setPw(e.target.value)} placeholder="รหัสผ่าน DM" autoComplete="current-password" />
        <button className="btn" type="submit">เข้าสู่ระบบ</button>
      </form>
      {err && <p role="alert" style={{ color: "var(--rose)", marginTop: 8 }}>{err}</p>}
      <p style={{ marginTop: 12 }}><a className="linkbtn" href="/">กลับหน้าผู้เล่น</a></p>
    </GlassWindow>
  );
}

export function DmProvider({ children }: { children: React.ReactNode }) {
  const { ready, isDM } = useAuth("dm");
  const on = ready && isDM;
  const players = useCollection<Player>(on, "players", { orderBy: "name" });
  const game = useDoc<GameConfig>(on, "config/game");
  const log = useCollection<LogEntry>(on, "log", { orderBy: "ts", desc: true, limit: 30 });
  if (!on) return <Login />;
  if (!players || game === undefined || !log) return <p className="muted" style={{ padding: 24 }}>กำลังโหลด…</p>;
  return (
    <DmCtx.Provider value={{ players, game: game ?? { shopOpen: false }, log }}>
      <div style={{ display: "flex", justifyContent: "flex-end" }}>
        <button className="linkbtn" onClick={() => signOutAll()}>ออกจากระบบ</button>
      </div>
      {children}
    </DmCtx.Provider>
  );
}
```
หมายเหตุ: `useAuth("dm")` ไม่ล็อกอินแบบ anonymous ให้ (`mode === "dm"`) จึงขึ้นหน้าเข้าสู่ระบบเมื่อยังไม่ได้ล็อกอิน · ถ้าเบราว์เซอร์นั้นมี session anonymous ค้างจากหน้าผู้เล่น `ready` จะเป็น true แต่ `isDM` false ก็ยังขึ้นหน้าเข้าสู่ระบบ ซึ่งถูกต้อง

- [ ] **Step 2: `dm/layout.tsx` และ `dm/page.tsx`**

```tsx
// dm/layout.tsx
"use client";
import { DmProvider } from "@/components/DmProvider";
export default function DmLayout({ children }: { children: React.ReactNode }) {
  return <DmProvider>{children}</DmProvider>;
}
```
```tsx
// dm/page.tsx
"use client";
import Link from "next/link";
import { useDmCtx } from "@/components/DmProvider";
import { GlassWindow } from "@/components/GlassWindow";
import { Icon } from "@/components/Icon";
import { setShopOpen } from "@/lib/actions";
import { format } from "@/lib/money";

export default function DmHome() {
  const { players, game, log } = useDmCtx();
  const name = (id: string) => players.find((p) => p.id === id)?.name ?? id;
  return (
    <>
      <GlassWindow title="ผู้ควบคุมเกม">
        <div className="switch" style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <button className="sw" role="switch" aria-checked={game.shopOpen} aria-label="เปิดร้านค้า" onClick={() => setShopOpen(!game.shopOpen)} />
          <span>เปิดร้านค้าให้ผู้เล่น</span>
        </div>
      </GlassWindow>
      <GlassWindow title="ผู้เล่น">
        <div className="plist">
          {players.map((p) => (
            <Link key={p.id} href={`/dm/${p.id}`} className="prow">
              <span className="mini">{p.path === "weapon" && p.weaponId ? <Icon id={p.weaponId} /> : null}</span>
              <span>{p.name} <span className="muted">Lv.{p.level}</span></span>
              <span className="muted">{p.unlocked.length} ท่า · {format(p.copper)}</span>
            </Link>
          ))}
        </div>
      </GlassWindow>
      <GlassWindow title="บันทึกล่าสุด">
        <ul style={{ listStyle: "none", padding: 0 }}>
          {log.map((l, i) => (
            <li key={i} className="muted" style={{ fontSize: ".9rem" }}>
              {l.ts?.toDate().toLocaleString("th-TH") ?? ""} · {name(l.playerId)} · {l.type} · {l.detail}
            </li>
          ))}
        </ul>
      </GlassWindow>
    </>
  );
}
```
เพิ่มใน `globals.css`: `a.prow{color:inherit;text-decoration:none}` และให้ `.prow .mini svg{width:30px;height:30px}`

- [ ] **Step 3: `dm/[id]/page.tsx` (รายละเอียดผู้เล่น)**

```tsx
"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { useDmCtx } from "@/components/DmProvider";
import { GlassWindow } from "@/components/GlassWindow";
import { MoveDetail } from "@/components/MoveDetail";
import { SkillRing } from "@/components/SkillRing";
import unboundData from "@/data/unbound.json";
import weaponsData from "@/data/weapons.json";
import { adjustCopper, resetWeapon, savePlayer, setInventory, setUnboundCenter, setUnlocked } from "@/lib/actions";
import { format } from "@/lib/money";
import type { Abilities, Player, Unbound, Weapon } from "@/lib/types";

const ABIL: [keyof Abilities, string][] = [["str", "STR"], ["dex", "DEX"], ["con", "CON"], ["int", "INT"], ["wis", "WIS"], ["cha", "CHA"]];
const num = (v: string) => Number(v) || 0;

function Editor({ p }: { p: Player }) {
  // ค่าเริ่มต้นจากเอกสารตอนเปิดหน้า: การอัปเดตสดจากผู้เล่นจะไม่ทับสิ่งที่ DM กำลังพิมพ์ (remount ด้วย key เมื่อกดบันทึก)
  const [f, setF] = useState({
    level: String(p.level), hp: String(p.hp), maxHp: String(p.maxHp), ac: String(p.ac), copper: String(p.copper), notes: p.notes ?? "",
    ...Object.fromEntries(ABIL.map(([k]) => [k, String(p.abilities[k])])),
  } as Record<string, string>);
  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => setF({ ...f, [k]: e.target.value });
  const field = (k: string, label: string) => (
    <label key={k}>{label}{" "}<input type="number" value={f[k]} onChange={set(k)} style={{ width: 80 }} /></label>
  );
  const save = async () => {
    await savePlayer(p.id, {
      level: num(f.level), hp: num(f.hp), maxHp: num(f.maxHp), ac: num(f.ac),
      copper: Math.max(0, Math.trunc(num(f.copper))), notes: f.notes,
      abilities: Object.fromEntries(ABIL.map(([k]) => [k, num(f[k])])) as Abilities,
    });
    toast.success("บันทึกแล้ว");
  };
  return (
    <GlassWindow title="สถานะ">
      <div className="row" style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>{field("level", "เลเวล")}{field("hp", "HP")}{field("maxHp", "HP สูงสุด")}{field("ac", "AC")}</div>
      <div className="row" style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>{ABIL.map(([k, l]) => field(k, l))}</div>
      <div className="row" style={{ display: "flex", gap: 10, alignItems: "center" }}>{field("copper", "เงิน (ทองแดง)")}<span className="muted">= {format(Math.max(0, Math.trunc(num(f.copper))))}</span></div>
      <textarea rows={3} style={{ width: "100%", marginTop: 8 }} placeholder="หมายเหตุ" value={f.notes} onChange={set("notes")} />
      <button className="btn" style={{ marginTop: 8 }} onClick={save}>บันทึก</button>
    </GlassWindow>
  );
}

export default function DmPlayer() {
  const { id } = useParams<{ id: string }>();
  const { players } = useDmCtx();
  const p = players.find((x) => x.id === id);
  const [sel, setSel] = useState(1);
  const [item, setItem] = useState({ name: "", qty: "1" });
  if (!p) return <p className="muted">ไม่พบผู้เล่น · <Link className="linkbtn" href="/dm">กลับ</Link></p>;

  const unbound = unboundData as Unbound;
  const weapon = p.path === "weapon" ? (weaponsData as Weapon[]).find((w) => w.id === p.weaponId) : undefined;
  const moves = weapon ? weapon.moves : p.path === "unbound" ? unbound.ring1 : [];
  const cu = unbound.center.find((c) => c.id === p.unboundCenter);
  const center = weapon ? weapon.center : cu ? { name: cu.name, effect: cu.effect } : null;
  const toggle = (slot: number) => {
    setSel(slot);
    const m = moves.find((x) => x.slot === slot);
    if (m) setUnlocked(p.id, m.id, !p.unlocked.includes(m.id)).then(() => toast(p.unlocked.includes(m.id) ? "ล็อกท่าคืนแล้ว" : "ปลดท่าแล้ว — ผู้เล่นเห็นทันที"));
  };
  const addItem = async () => {
    const name = item.name.trim();
    const qty = Math.max(1, Math.trunc(Number(item.qty)) || 1);
    if (!name) return;
    await setInventory(p.id, [...p.inventory, { itemId: null, name, qty }]);
    setItem({ name: "", qty: "1" });
  };

  return (
    <>
      <Link className="linkbtn" href="/dm">← กลับ</Link>
      <h1 style={{ fontSize: "1.8rem", margin: "6px 0" }}>{p.name}</h1>
      <Editor key={p.id} p={p} />

      <GlassWindow title="กระเป๋าและเงิน">
        {p.inventory.map((it, i) => (
          <div key={i} style={{ display: "flex", gap: 8, alignItems: "center", margin: "4px 0" }}>
            {it.name} × {it.qty}
            <button className="btn" onClick={() => setInventory(p.id, p.inventory.filter((_, j) => j !== i))}>ลบ</button>
          </div>
        ))}
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 8 }}>
          <input placeholder="ชื่อของ" value={item.name} onChange={(e) => setItem({ ...item, name: e.target.value })} />
          <input type="number" style={{ width: 70 }} value={item.qty} onChange={(e) => setItem({ ...item, qty: e.target.value })} />
          <button className="btn" onClick={addItem}>เพิ่ม</button>
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 12 }}>
          <button className="btn" onClick={() => adjustCopper(p.id, -100)}>−1 ทอง</button>
          <button className="btn gold" onClick={() => adjustCopper(p.id, 100)}>+1 ทอง</button>
          <button className="btn" onClick={() => adjustCopper(p.id, 10)}>+1 เงิน</button>
        </div>
      </GlassWindow>

      <GlassWindow title="อาวุธและท่า (แตะโหนดเพื่อปลดหรือล็อกคืน)">
        {!p.path ? <p className="muted">ยังไม่เลือกอาวุธ</p> : (
          <>
            <p>{weapon ? `อาวุธ: ${weapon.name} ${weapon.fullName}` : "ผู้ไม่ผูกอาวุธ"}</p>
            {p.path === "unbound" && (
              <label>ท่ากลาง{" "}
                <select value={p.unboundCenter ?? ""} onChange={(e) => setUnboundCenter(p.id, e.target.value || null)}>
                  <option value="">— ยังไม่เลือก —</option>
                  {unbound.center.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </label>
            )}
            <SkillRing moves={moves} unlocked={p.unlocked} selected={sel} onSelect={toggle} centerIcon={weapon ? weapon.id : "user"} />
            <button className="btn" onClick={() => confirm("รีเซ็ตอาวุธและท่าที่ปลดของคนนี้ใช่ไหม?") && resetWeapon(p)}>รีเซ็ตอาวุธ</button>
          </>
        )}
      </GlassWindow>
      {p.path && <MoveDetail selected={sel} moves={moves} unlocked={p.unlocked} center={center} />}
    </>
  );
}
```
หมายเหตุ: โหนดท่าลับที่ DM ปลดแล้ว แสดงในหน้า DM เป็น "ท่าลับ" (รายละเอียดจริงอยู่ในไฟล์กติกา `weapon-trees.md` ที่ DM มีอยู่แล้ว)

- [ ] **Step 2b: เพิ่มสไตล์ลิงก์ในหน้า DM**

ต่อท้าย `globals.css`: `a.prow{color:inherit;text-decoration:none} .prow .mini svg{width:30px;height:30px}` (ถ้ายังไม่ได้เพิ่มในขั้นก่อน)

- [ ] **Step 3: รันตรวจ**

Run: `npm run typecheck && npm run lint && npm run build` · Expected: ผ่าน

- [ ] **Step 4: Commit**

```bash
cd .. && git add -A && git commit -m "feat: DM login, overview and player detail" -m "Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 9: ตรวจกับ emulator, deploy ไป Vercel และลบชุดเก่า

**Files:**
- Modify: `web/firebase.json` (ตัดส่วน hosting), `web/package.json` (script test), `web/site/README.md` (คำสั่งสั้นๆ)
- Delete: `web/public/**` (ชุด HTML/JS เดิม), `web/test/money.test.mjs`

- [ ] **Step 1: ทดสอบกับ Firebase Emulator (ก่อนแตะของจริง)**

เปิดเทอร์มินัล A (ใน `web/`): `npx firebase emulators:start --only auth,firestore --project stage-test` (ถ้า `firebase.json` ยังไม่มี emulator `auth` ให้เพิ่ม `"auth": { "port": 9099 }` ใน `emulators`)
เทอร์มินัล B: seed ลง emulator ด้วยสคริปต์ชั่วคราวหรือเพิ่มเอกสารผ่าน Emulator UI ให้ครบตามโครงเอกสาร (players 6 คน, weapons 6, config/game) แล้วสร้างผู้ใช้ `dm@stage.local` ใน Auth emulator
เทอร์มินัล C (ใน `web/site`): `NEXT_PUBLIC_USE_EMULATOR=1 NEXT_PUBLIC_FIREBASE_PROJECT_ID=stage-test NEXT_PUBLIC_FIREBASE_API_KEY=x NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=x NEXT_PUBLIC_FIREBASE_APP_ID=x npm run dev`
ทำเช็กลิสต์ใน Step 4 ให้ครบกับ emulator ก่อน

- [ ] **Step 2: deploy ไป Vercel (ทำเอง ต้องล็อกอิน)**

1. สร้างที่เก็บ GitHub (private ได้) แล้ว push โฟลเดอร์ `web/` เป็นรากของที่เก็บ (`git remote add origin ...` แล้ว `git push -u origin main`) · ห้าม push `.env.local` หรือไฟล์ `serviceAccount*.json`
2. vercel.com → Add New → Project → เลือกที่เก็บ → **Root Directory = `site`** → Framework: Next.js
3. Environment Variables (ทั้ง Production และ Preview): `NEXT_PUBLIC_FIREBASE_API_KEY`, `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`, `NEXT_PUBLIC_FIREBASE_PROJECT_ID`, `NEXT_PUBLIC_FIREBASE_APP_ID` (ค่าจากโปรเจกต์ `dandd-2c2fc`) · **ไม่**ตั้ง `NEXT_PUBLIC_USE_EMULATOR`
4. Deploy → ได้ URL `https://<ชื่อ>.vercel.app`
5. Firebase Console → Authentication → Settings → **Authorized domains** → เพิ่มโดเมนของ Vercel (และโดเมน preview ถ้าจะทดสอบ) · ไม่เพิ่มก็ล็อกอิน anonymous ไม่ได้

- [ ] **Step 3: ลบชุดหน้าเว็บเก่าและปรับสคริปต์**

ใน `web/`:
```bash
git rm -r -q public test/money.test.mjs
```
แก้ `web/firebase.json`: ลบคีย์ `"hosting"` ทั้งก้อน (เหลือ `firestore` และ `emulators`) · ใน `web/package.json` เปลี่ยน script `"test"` เป็น `"node --test test/convert.test.mjs"` และลบ script `"serve"` · สร้าง `web/site/README.md` สั้นๆ ระบุคำสั่ง: `npm run dev`, `npm test`, `npm run build`, การตั้ง env และการ seed (`cd .. && node tools/seed.mjs <key> <รหัส>`)
Run (ใน `web/`): `npm test && npm run test:rules` · Expected: เทสต์ตัวแปลงผ่าน และเทสต์กฎ 11 ข้อผ่าน · ใน `web/site`: `npm test && npm run build` ผ่าน

- [ ] **Step 4: เช็กลิสต์ทดสอบมือ (ทำกับเว็บบน Vercel จริง เปิด 2 หน้าต่าง: DM + โหมดไม่ระบุตัวตนสำหรับผู้เล่น)**

- [ ] ผู้เล่นเลือกชื่อ → เห็นสถานะที่ DM กรอก · รีเฟรชแล้วยังเป็นคนเดิม · "เปลี่ยนตัวละคร" กลับหน้าเลือกชื่อ
- [ ] แท็บสกิลของผู้ที่ยังไม่เลือกอาวุธ → เห็นการ์ดอาวุธ 6 ใบ เลือกดาบ → กด "ยืนยันเลือก" → เห็นวงโหนดของดาบ (ท่ากลาง + 10 โหนด ท่าลับเป็น "?")
- [ ] ผู้เล่นอีกคน (หน้าต่างอื่น) เห็นดาบจางและมีชื่อเจ้าของ กดเลือกไม่ได้ · ปุ่ม "ไม่ผูกอาวุธ" พาเข้าเส้นทางผู้ไม่ผูกอาวุธ
- [ ] DM แตะโหนดในหน้า `/dm/<id>` → **ที่ผู้เล่นโหนดสว่างเป็นสีเขียวทันทีโดยไม่รีเฟรช** มีวงวาบ · DM แตะท่าลับ → ผู้เล่นเห็น "ท่าลับปลดแล้ว"
- [ ] ร้านปิด → ผู้เล่นเห็น "ร้านปิดอยู่" · DM เปิดสวิตช์ร้าน → ผู้เล่นซื้อ "สมุนไพร" → เงินลด 10 ทองแดง ของขึ้นในกระเป๋าและมี toast
- [ ] DM +1 ทอง / เพิ่มของนอกร้าน → ผู้เล่นเห็นทันที · DM รีเซ็ตอาวุธ → ผู้เล่นกลับไปหน้าเลือกอาวุธ ดาบว่างให้คนอื่น
- [ ] บันทึกล่าสุดที่หน้า DM แสดง claim / buy / unlock
- [ ] ผู้เล่นเปิด `/dm` → เห็นหน้าเข้าสู่ระบบ ไม่เห็นข้อมูลใดๆ (ทดสอบรหัสผิดขึ้นข้อความ "รหัสผ่านไม่ถูกต้อง")
- [ ] มือถือ: ใช้งานได้ ไม่ต้องเลื่อนแนวนอน วงโหนดแตะได้และเลื่อนหน้าได้ปกติ (ไม่ถูกวงโหนดแย่งการเลื่อน)

- [ ] **Step 5: Commit**

```bash
cd .. && git add -A && git commit -m "chore: remove vanilla site, finalize Vercel deploy config" -m "Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 10: ปรับหน้าตาตามดีไซน์จาก Google Stitch

> ทำหลังจากได้ภาพหน้าจอ/โค้ดจาก Stitch (พรอมต์อยู่ใน `docs/superpowers/specs/2026-09-21-stitch-ui-prompt.md`) · งานนี้แก้ **เฉพาะหน้าตา** ห้ามแตะ `lib/`, `actions.ts`, กฎ หรือข้อมูล

**Files:**
- Modify: `web/site/src/app/globals.css`, ไฟล์ `components/*.tsx` และ `app/**/page.tsx` เฉพาะ `className`/โครง JSX
- Reference: ไฟล์ส่งออกจาก Stitch (ภาพ + HTML/CSS) เก็บไว้ที่ `web/mock/stitch/` (สร้างโฟลเดอร์นี้)

- [ ] **Step 1: เก็บผลงานจาก Stitch** — บันทึกภาพหน้าจอของแต่ละหน้าและโค้ดที่ส่งออก (Copy code / export) ไว้ที่ `web/mock/stitch/<ชื่อหน้า>.png` และ `.html`
- [ ] **Step 2: ดึงโทเคนออกแบบ** — จากดีไซน์เขียนรายการสี ฟอนต์ ระยะห่าง รัศมีมุม และเงา แล้วแก้ตัวแปรใน `:root` ของ `globals.css` (`--night --edge --gold --mint --rose --glass` ฯลฯ) ให้ตรง · ถ้า Stitch เลือกฟอนต์ไทยอื่น ให้เปลี่ยนใน `layout.tsx` ผ่าน `next/font/google`
- [ ] **Step 3: ปรับทีละหน้า** ตามลำดับ สถานะ → สกิล → ร้านค้า → หน้าเลือกอาวุธ → DM: แก้ CSS ของคลาสที่เกี่ยวข้องและ JSX ให้โครงตรงกับดีไซน์ (ห้ามเปลี่ยนชื่อ prop/ฟังก์ชันที่ Task 5-8 ใช้ร่วมกัน) · ต้นสกิลต้องยังเป็นวงกลมที่มีท่ากลางอยู่กลาง 10 โหนดรอบ และวงที่ 2-3 จาง
- [ ] **Step 4: ตรวจ** — `npm run typecheck && npm test && npm run build` ผ่าน · เปิดหน้าจอเทียบกับภาพจาก Stitch ที่ความกว้าง 390px และ 1024px ทีละหน้า แล้วรายงานความต่างที่เหลือ · ตรวจการเข้าถึง: ตัวอักษรอ่านได้ชัด (ตัดกันพอ) มี focus ที่มองเห็นเมื่อกด Tab และปิดแอนิเมชันเมื่อผู้ใช้ตั้ง `prefers-reduced-motion`
- [ ] **Step 5: Commit**

```bash
cd .. && git add -A && git commit -m "style: apply Stitch design" -m "Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Self-Review

**Spec coverage:** ล็อกอินไม่มี PIN → Task 3 (`useAuth`), 5 (`PlayerProvider`), 8 (`DmProvider`) · ชีท D&D → Task 5, 8 (`Editor`) · อาวุธห้ามซ้ำ/ล็อก/รีเซ็ต → Task 3 (`claimWeapon`, `resetWeapon`), 6 (`WeaponPicker`), 8 · ไม่ผูกอาวุธ + DM เลือกท่ากลาง → Task 3, 6, 8 · DM เท่านั้นที่ปลดท่า → Task 8 (`toggle`) และกฎเดิม · ท่าลับ → Task 6 (`MoveDetail`, `SkillRing`) · เงินทองแดง/ร้านค้า/สวิตช์ร้าน → Task 2, 3, 7, 8 · log → Task 3, 8 · ไม่มีข้อมูลลับ → ตัวแปลงเดิม (Task 1 ย้ายพาธ ยังรันเทสต์) · ทดสอบ → Task 2 (Vitest), Task 9 (กฎเดิม + emulator + เช็กลิสต์ 9 ข้อ) · Vercel → Task 9
**Placeholder scan:** ไม่มี TBD · ส่วนที่ผู้ใช้ต้องทำเองระบุชัด (สร้างที่เก็บ GitHub, ตั้ง env บน Vercel, เพิ่ม authorized domain) · Task 10 ขึ้นกับผลงาน Stitch จึงเป็นขั้นตอนพร้อมเกณฑ์ตรวจ ไม่มีโค้ดตายตัว
**Type consistency:** `usePlayerCtx()` = `{id, me, weapons, game}` ตรงกับที่ Task 6-7 ใช้ · `SkillRing` props (`moves, unlocked, selected, onSelect, centerIcon`) ตรงกับการเรียกใน Task 6 และ 8 · ชื่อ action ตรงกับ Task 3 ทุกตัว · id ท่ารูปแบบเดียวกับข้อมูลที่ตัวแปลงสร้าง · `Icon id` = id อาวุธ (`sword shield bow codex guitar staff`) ตรงกับ `weapons.json`
**ความเสี่ยงที่ควรรู้:** (1) API ของ `@xyflow/react` และ shadcn CLI เปลี่ยนตามเวอร์ชัน ถ้าคำสั่งใน Task 1 หรือชนิดใน Task 6 ไม่ตรง ให้ปรับตามเอกสารเวอร์ชันที่ติดตั้ง แล้วบันทึกการเปลี่ยนในรายงาน · (2) ตำแหน่งปลายเส้นของ React Flow ต้องตรวจด้วยตาใน Task 6 ขั้น 5
