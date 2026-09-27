# พรอมต์ออกแบบ UI ด้วย Google Stitch

> ใช้ที่ stitch.withgoogle.com (ตรวจหน้าเครื่องมือปัจจุบันเองอีกครั้ง เพราะเมนูและโหมดเปลี่ยนได้) · เขียนเป็นภาษาอังกฤษเพราะ Stitch ตอบสนองได้ดีกว่า แต่ให้ข้อความบนหน้าจอเป็นภาษาไทยตามที่กำกับ · ทำทีละหน้าจอ อย่าสั่งหลายหน้าในครั้งเดียว · อัปโหลดภาพหน้าจอของ `web/mock/index.html` เป็นภาพอ้างอิงได้ถ้า Stitch รองรับการแนบภาพ

## วิธีใช้
1. เลือกโหมด **Mobile** (ความกว้าง ~390px) วางพรอมต์หลัก (A) ตามด้วยพรอมต์ของหน้าจอ (B1)
2. ได้หน้าแรกแล้ว สั่งหน้าถัดไปโดยเริ่มด้วยประโยค "Keep the exact same visual style as the previous screen." แล้ววางพรอมต์ของหน้านั้น
3. ปรับด้วยพรอมต์ปรับแต่ง (C) ทีละข้อ
4. หน้า DM (B6) ให้เลือกโหมด Desktop/Tablet
5. ส่งออกภาพหน้าจอและโค้ด (HTML/CSS หรือ Figma) เก็บที่ `web/mock/stitch/` แล้วให้เอเจนต์ทำตามงาน 10 ของแผน `2026-09-21-player-web-nextjs.md`

## A. พรอมต์หลัก (วางก่อนทุกหน้า)

```
Design a mobile-first (390px wide) web app: a game-style character sheet for a 6-player tabletop RPG campaign that feels like the "status window" system of an anime isekai online RPG (Rising of the Shield Hero / Sword Art Online system menus). The players were summoned into another world and each holds an ancient weapon with a skill tree.

VISUAL LANGUAGE
- Translucent glass panels (frosted, subtle backdrop blur) with a thin 1px cyan-blue border (#8fd3ff at ~55% opacity) and small gold (#ffd27a) L-shaped corner brackets on the top-left and bottom-right of every window. Angular, slightly clipped corners; NOT rounded pill cards, NOT identical stacked SaaS cards.
- Background: deep night sky gradient from #0a1338 to #060a1c with a soft blue glow top-right (#2f5cb4) and violet glow top-left (#3b2b7e), a few faint stars. No photos, no stock illustrations.
- Palette: night #060a1c, deep blue #0f1c4d, glass cyan #8fd3ff, text #eaf6ff, muted text #9db7d6, gold #ffd27a (level, currency, selection), mint #7cf7d4 (unlocked / active / glow), rose #ff6f8e (HP / danger). Avoid purple-to-pink gradients and neon overload. Glow is used sparingly: only for unlocked nodes and the selected item.
- Typography: Kanit for headings and numbers, IBM Plex Sans Thai for body text. ALL UI text is Thai. Comfortable Thai line height (1.6+), minimum 16px body text, text contrast at least 4.5:1 on the glass panels. Do not use all-caps eyebrow labels.
- Icons: simple 1.6px-stroke line icons (sword, shield, bow, open spellbook, guitar, staff, leaf, feather, bread, coin, user, tree-of-nodes, bag, eye).
- Bottom tab bar (game HUD style, fixed) with three tabs: "สถานะ" (user icon), "สกิล" (node-tree icon), "ร้านค้า" (bag icon). The active tab is gold with a gold underline.
- Motion is functional only: an unlock produces a single mint ring pulse on the node. Respect reduced motion. Keep it accessible: visible focus rings, large touch targets (min 44px).

TONE OF COPY: short, plain Thai game UI wording. No marketing text.
```

## B. พรอมต์รายหน้าจอ

### B1. สถานะ (Status)
```
Screen: player Status. Top: a window with a large circular weapon emblem (sword icon, mint glow) on the left; character name "กัน" in large Kanit (32px) with a small gold level badge "Lv.3"; below it the line "ผู้ถืออาวุธ · ดาบ ออเรลิส ดาบแห่งรุ่งแสง" in muted text. Under that, a vitals row: a segmented HP bar (14 slanted segments, rose colour, 34 of 42 filled) with the number "34 / 42" above it; two compact stat chips "เกราะ 16" and "เงิน 3 ทอง 2 เงิน" (gold).
Second window titled "ค่าพลัง": a 3x2 grid of ability tiles with clipped corners. Each tile shows the label (STR, DEX, CON, INT, WIS, CHA), a very large modifier number (+3, +1, +2, -1, +0, +0) and the raw score small underneath (16, 13, 14, 9, 11, 10). Highlight tiles with score 15 or more in gold.
Third window titled "กระเป๋า": an inventory grid of 5 columns x 3 rows of square slots. Four slots hold line icons with a small gold quantity in the bottom-right corner (leaf x3, feather x1, bread x2, spellbook x1); the rest are empty dim slots. Tooltip style label on hover.
```

### B2. สกิล (Skill tree) — ชิ้นสำคัญที่สุดของแอป
```
Screen: Skill tree. One window titled "ดาบ ออเรลิส ดาบแห่งรุ่งแสง" containing a RADIAL skill tree, this is the memorable centrepiece of the whole app: a large gold-rimmed circular node in the centre (sword icon) for the free base skill, and exactly 10 round nodes evenly spaced on a ring around it, numbered 1 to 10 clockwise from the top. Thin lines connect the centre to each node. Unlocked nodes (3, 8 and 10) glow mint with a mint number and their connecting line glows; locked nodes are dim outlined circles; node 6 is a secret skill shown with a dashed outline and a "?" instead of a number. Node 1 is currently selected (gold ring). Around the ring, two more faint dashed concentric rings labelled "วงที่ 2" and "วงที่ 3" suggest future tiers that are still locked. Under the tree, a small caption: "วงที่ 2 และ 3 ยังปิดอยู่ ปลดได้เมื่อเรื่องดำเนินไปถึง".
Below the tree, a second window with the selected skill's detail: title "ดาบสวนกลับ", two small tags "ยังล็อก" and a difficulty tag "ปานกลาง" (orange), then two labelled lines: "ผล" — "การตอบโต้ (1 แต้ม): เมื่อศัตรูโจมตีคุณพลาด โจมตีตอบ 1 ครั้ง"; "วิธีปลด" — "ภารกิจล่าสไลม์ 10 ตัว และภารกิจเฉพาะตัวของดาบ". Difficulty tags use four colours: ง่ายมาก (green), ง่าย (yellow), ปานกลาง (orange), ยาก (rose).
```

### B3. เลือกอาวุธ (Weapon picker)
```
Screen: choose your ancient weapon (shown when the player has none yet). Window titled "เลือกอาวุธโบราณ" with helper text "เลือกได้ครั้งเดียว และแต่ละอาวุธมีเจ้าของได้คนเดียว". A 2-column grid of six weapon cards, each with a large line icon, the weapon name and a one-line role: ดาบ "นักดวลโจมตีจุดเดียว", โล่ "ผู้ปกป้องทีม", ธนู "ระยะไกล + สอดแนม", คัมภีร์ "เวทโจมตี + ความรู้", กีต้าร์ "เสริมพลังด้วยดนตรี", คฑา "ผู้รักษา + ผู้ปกป้อง". Three cards are already taken: dimmed to 40% with a rose line "เจ้าของ: หง" (ดาบ is taken by กัน, โล่ by หง, คัมภีร์ by ดรีม). One free card (ธนู) is selected with a gold border and gold glow. At the bottom: a text link "ไม่ผูกอาวุธ" on the left and a gold primary button "ยืนยันเลือก" on the right.
```

### B4. ร้านค้า (Shop)
```
Screen: Shop. One window with a header row: title "ร้านของทั่วไป" on the left and a small mint status tag "เปิดอยู่" on the right. Under it a coin icon with the player's money "3 ทอง 2 เงิน" in gold. Then a list of items, separated by thin lines, each row: a square icon tile, the item name with a muted one-line note, and on the right the price in gold and a compact blue "ซื้อ" button. Items: ตำราท่าดาบพื้นฐานฉบับชาวบ้าน (500 ทองแดง = 5 ทอง), ตำราป้องกันตัว (5 ทอง), ตำรายิงธนูมือใหม่ (2 ทอง), คู่มือมอนสเตอร์ (ย่อ) (1 ทอง), สมุนไพร "ต่อชนิด" (1 เงิน), ขนนก "ต่อเส้น" (1 เงิน), เสบียงติดตัว "ต่อวัน" (5 เงิน). Buttons for items the player cannot afford are disabled at 40% opacity.
```

### B5. ร้านปิด (สถานะว่าง)
```
Same Shop screen in its closed state: the tag reads "ปิดอยู่" in rose and the list is replaced by one line "ร้านปิดอยู่ ผู้ควบคุมเกมยังไม่เปิดร้าน" in muted text.
```

### B6. หน้า DM (Desktop/Tablet 1024px)
```
Screen: Game Master dashboard, for tablet/desktop (1024px). Same glass-window visual language. Left column: window "ผู้ควบคุมเกม" with a toggle switch "เปิดร้านค้าให้ผู้เล่น" (mint when on), and window "ผู้เล่น" listing six rows (กัน, อันวาส, ป๋องแป๋ง, หง, ดรีม, เพชร), each with a small weapon icon, name, level, number of unlocked skills and money; the selected row (กัน) has a gold border. Right column: window "ปลดท่าของกัน (แตะโหนดเพื่อปลดหรือล็อกคืน)" containing the same radial skill tree as the player view but interactive, with three buttons under it "−1 ทอง", "+1 ทอง" (gold), "+1 เงิน"; below it a window "บันทึกล่าสุด" with a compact chronological list of events like "กัน · ซื้อ · สมุนไพร" and "กัน · ปลดท่า · sword-3". Dense but calm; this is a working tool, so clarity beats decoration.
```

### B7. เลือกตัวละคร (หน้าแรก)
```
Screen: player picker (first screen). Large heading "เลือกตัวละครของคุณ", then a grid of six large tappable tiles with the names กัน, อันวาส, ป๋องแป๋ง, หง, ดรีม, เพชร (glass tiles with gold corner brackets). A small text link at the bottom "สำหรับ DM".
```

## C. พรอมต์ปรับแต่ง (ใช้หลังได้หน้าแรก)
- `Make the glass panels more transparent and the borders thinner; the background should show through.`
- `Increase the contrast of muted text and make all Thai text at least 16px.`
- `Reduce glow. Only the unlocked skill nodes and the selected item may glow.`
- `Make the radial skill tree larger and give each node a 44px minimum touch target.`
- `Replace the rounded corners with clipped (chamfered) corners on windows and buttons.`
- `Show the same screen at 1024px wide with the two-column layout.`
- `Show the empty state of the inventory and the state where a skill was just unlocked (mint pulse ring around the node).`

## D. สิ่งที่ห้ามเปลี่ยน (เพื่อให้พอร์ตเข้าแอปได้)
- ต้นสกิลต้องเป็นวงกลม: ท่ากลาง 1 ท่า + 10 โหนดรอบ + วงจาง 2 วง
- แท็บล่าง 3 แท็บ: สถานะ / สกิล / ร้านค้า · ข้อความไทยตามที่ระบุ
- ค่าพลัง 6 ตัวแบบ D&D (STR DEX CON INT WIS CHA) และ HP แบบแบ่งช่อง

## E. พรอมต์เดียวครบทุกหน้า

> วางพรอมต์นี้ครั้งเดียวใน Stitch (ถ้าสร้างหลายหน้าไม่ได้ ใช้ A + B แยกหน้าด้านบนแทน) · ตัวเต็มถูกส่งให้ผู้ใช้ในแชทเมื่อ 2026-09-21 ประกอบจากพรอมต์หลัก (A) และหน้าจอ B1-B7 ที่รวมเป็น 7 หน้า: เลือกตัวละคร, สถานะ, สกิลทรี, เลือกอาวุธ, ร้านค้าเปิด, ร้านค้าปิด, DM
