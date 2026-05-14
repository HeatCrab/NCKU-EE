# Project 1 — Lab Day 行動清單（v3 重寫版）

Demo: **2026-05-14（四）15:00 SoC Lab**

> **權威來源**：`Docs/Virtualizer for Project 1.pdf` §2.03（10-step 程序）+
> `Docs/Project 1 Descriptions_v3.pdf`（架構、位址、資料流）。
> 本檔是 lab 現場 turn-by-turn 操作；PDF 是教科書。兩者互補，不重複。
>
> 5/5 lab session 的所有產出（DualARMv8_Proj1 workspace、PJ1Bus0 接線、DMA2
> base_ = 0x100000）已全部作廢。新流程從 `mkdir DualA35` 開始。

---

## 📍 當前進度（2026-05-07 深夜，今晚 lab session 結束）

- ✅ **STEP 1 完成** — DualA35 workspace 從 Cortex-A35 Example 開好，
  hierarchy 對、4 UART Dhrystone 跑過、`number_of_cpu` 4→2 後只剩
  UART0/UART1 Dhrystone
- ✅ **STEP 2 完成** — DMA2 library import：
  - `base_ = 0x10000000` ✅
  - Memory Map 8 個 register ✅
  - INT0/INT1 Category = Interrupt（library-side）✅
  - Build success
  - ⚠️ 殘留 2 個 Active Level warning → **老師明確說「不用理會」**
    （LINE 5/7 11:33），不要花時間去修
- ✅ **STEP 3 完成** — vdksys 接線：4 RAM + DMA2 + INT0/INT1 全接好
  - 4 RAM 都按 v3 spec 落位（RAM0/1 各 128MB local，RAM2/3 各 256MB shared）
  - DMA2_1.Ssocket、Msocket0、Msocket1 全接 SharedmemoryMap
  - DMA2_1.INT0 → ARM0.nIRQ0；DMA2_1.INT1 → ARM0.nIRQ1（**注意：是 nIRQ
    不是 nFIQ/nvIRQ/GICV3_x；後者是 GIC 內部 distributor 訊號，動了會壞**）
  - clk → SYSCLK；RST → SYSRST
  - Build success，0 error；剩 2 個 Active Level warning（teacher 說 ignore）
- ✅ **STEP 4 完成** — bare-metal compile：cpu0/cpu1 各自 elf 編出，
  Imageinfo 路徑指對，sim 載入成功
- 🟡 **STEP 5 部分完成** — Run 起來、boot OK 印出來，但 DMA probe
  loop 觸發了一個未解的怪 bug（UART0 狂噴 RAM2 pattern）
- 🟢 **demo 保底 60-70%** 已入袋（架構 20% + compile 20% + run 10% + 部分 run success）

### 🔴 5/11 第一動作：refined DMA probe

cpu0 寫 DMA2 SOURCE/TARGET/SIZE register 之後（**還沒寫 START**），
UART0 開始狂噴 RAM2 的 "0123456789ABCDEF" pattern → DMA 不該觸發卻觸發了。

5/11 開新對話，第一件事：把 `cpu0/main_cpu0.c` probe 改成「**每寫一個
register 印一行**」，讓我們知道是 SRC / DST / SIZE 哪一個觸發的。
這是冷啟動最便宜的 attack 點。詳情看記憶 `project1_v3_rebuild.md`
「Monday 5/11 entry point」段。

### 行程安排

⚠️ 5/8（五）下午 ~ 5/10（日）晚上返鄉。
✅ 5/11（一）~ 5/13（三）= 3 個完整工作天。
🎯 5/14（四）15:00 demo。

---

---

## 工作守則

- 卡關直接停下來問，不瞎猜
- 每完成一個 step 先 Build & Run 一次，確認 Dhrystone 還活著再進下一步
- 不確定的 spec 細節先 flag（見最末「開放問題」），不要自己腦補

---

## 啟動環境（每次 session 開頭）

```csh
cd ~/project1
source setup.csh vze        # vze 後綴必填，吃 license
vs &
```

連線資訊：`192.168.200.13`（備機 `.115`）/ `esl2625` / 工作目錄 `~/project1/`

打開 workspace 後右上角 perspective：
- **TLM Creation** — 建 TLM project / 接線
- **Virtualizer (Simulation)** — Run / 看 transaction / memory view

詳細環境設定（toolchain PATH、Makefile CROSS）見 memory `lab_environment.md`。

---

## STEP 1 — 從 Cortex-A35 Example 開新 workspace ✅ 已完成 (5/7)

對應 PDF §2.03 step 1–8。目標：跑出 4 UART Dhrystone，再降到 2 cores 只剩 UART0/UART1。

### 1.1 開新 workspace

```csh
cd ~/project1
mkdir DualA35
vs -d DualA35 &
```

### 1.2 建 VDK Project from Example

1. File → New → VDK Project
2. 選 **VDK Example**（不是 vdkzip）
3. Template 搜尋 `A35` → 進入
   `Arm FM QuickRef Examples → CortexA_v8 → Arm Cortex-A35 Example`
4. Project name 填 `DualA35`（跟資料夾同名）
5. Finish

### 1.3 預期 default hierarchy

- 1× ARM0（Cortex-A35，4 cores）
- MEM + MEM2
- SharedMemoryMap + Bridge
- 4× UART（UART_0/UART_PHY_0 ~ UART_3/UART_PHY_3）

ARM0 內建的 `.axf` 檔在 `ARM0 Parameters → Imageinfo`，路徑在 `DualA35` workspace 裡面。

### 1.4 第一次 Build & Run（驗證 example）

1. Build
2. Run（VPConfig 用 example 預設那個）
3. 4 UART console 都應該開始跑 Dhrystone
4. Resume → 4 UART 都動

✅ 看到 4 UART Dhrystone = example 本身 OK，可以動 cores 數。

### 1.5 把 number_of_cpu 從 4 降成 2

1. 停 simulation
2. ARM0 → Parameters → 拉到底找 `number_of_cpu`
3. **Design Value** 改 `2`、**Runtime Value** 也改 `2`（兩個都要改）
4. Save
5. Build & Run 再一次
6. 這次只剩 UART0 / UART1 跑 Dhrystone，UART2/UART3 安靜

✅ 卡點：如果 UART2/UART3 還在跑 → Runtime Value 沒改。

---

## STEP 2 — Import DMA2（PDF §1.02，從零建）✅ 已完成 (5/7)

> 結果：library 建立成功、Build success、3 個 fix points 全做對。
> 殘留 INT0/INT1 Active Level warning，**老師說不用理會**（LINE 5/7 11:33）。
>

DMA2 source 已經在 Mac 端 `my_works/SystemC/dma2/{DMA2.h, DMA2.cpp}`，FileZilla
傳到 superdome3。

5/5 漏掉的 3 件事這次必須一次做對：

### 2.1 base_ = 0x10000000（**重要：8 個 0**）

1. New TLM Project → Module 名 `DMA2`
2. Vendor 填 `ESL Class, EE NCKU`（跟以前一致）
3. Constructor Parameters → `base_` 初始值 **`0x10000000`**
   - 5/5 填了 `0x100000`（少 2 個 0）→ 整個 memory map 對不上 v3 spec

### 2.2 Memory Map 手動加 8 個 register（Module.tlmc）

Virtualizer 不會自動偵測，必須手填。Module.tlmc → Memory Map：

| Offset | Name    | Size |
|--------|---------|------|
| 0x00   | SOURCE0 | 4    |
| 0x04   | TARGET0 | 4    |
| 0x08   | SIZE0   | 4    |
| 0x0C   | START0  | 4    |
| 0x10   | SOURCE1 | 4    |
| 0x14   | TARGET1 | 4    |
| 0x18   | SIZE1   | 4    |
| 0x1C   | START1  | 4    |

第 1 組（0x00~0x0C）= ARMv8_0、第 2 組（0x10~0x1C）= ARMv8_1。

### 2.3 INT Category = Interrupt（library-side，**不是 instance-side**）

Module.tlmc → Interface tab → 把 INT0、INT1 的 Category 從 Default 改成
**Interrupt**，type 選 `interrupt-signal`。

- ⚠️ 這個改在 **library 端**（Module.tlmc），改完整個 module 一次到位
- 5/5 是改在 vdksys instance 端 → 只要 module re-import 就會被吃掉，要一直重做
- library-side 改完之後，vdksys 那邊用到的 instance 自動繼承，不用再改

### 2.4 Build library

Build TLM Project → 沒 error。叉叉應該變鉛筆，library OK。

---

## STEP 3 — 加 2× Memory_Generic + 接線（v3 Figure 1）✅ 已完成 (5/7)

### 完成記錄（5/7 evening lab session）

實際做法跟下面寫的計畫**有差**，記下來免得 5/11 回來忘了：

**SharedmemoryMap memory map**（最終值，Build success）：

| Name | Start | End | Size |
|---|---|---|---|
| MEM (RAM0, ARMv8_0 local) | 0x0000_0000 | 0x07ff_ffff | 0x0800_0000 (128MB) |
| MEM2 (RAM1, ARMv8_1 local) | 0x0800_0000 | 0x0fff_ffff | 0x0800_0000 (128MB) |
| DMA2_1.Ssocket | 0x1000_0000 | 0x1000_001f | 0x0000_0020 (32B) |
| MEM3 (RAM2, shared) | 0x2000_0000 | 0x2fff_ffff | 0x1000_0000 (256MB) |
| MEM4 (RAM3, shared) | 0x3000_0000 | 0x3fff_ffff | 0x1000_0000 (256MB) |
| UART_0~3（template default 沒動）| 0x4000_0000~0x4000_3000 | 0x4000_0fff~0x4000_3fff | 0x1000 each |

**踩過的坑**（lessons learned，lab 才會撞到）：

- `Inconsistent information` error 來自 Memory_Generic instance 的 size
  parameter 跟 bus-mapped range 不一致 → 必須 **兩邊同步改**（Memory_Generic
  的 Parameters → size，跟 SharedmemoryMap 的 row Range，要互相吻合）。
  template 預設 256MB，縮成 128MB 必須兩邊都改。
- `Address Conflict` error 通常是改 row 的 Start/End 沒一次改完整。
  改某個 row 的位址範圍時，**Start 跟 End 一起改、一次儲存**。
- DMA2 的 slave port 是 **Ssocket**（在 Memory Target 分類下），不是
  「Tslave」。Memory Initiator 是 Msocket0 + Msocket1（DMA 自己的 master
  port，給它讀 source / 寫 target 用）。**Ssocket + Msocket0 + Msocket1
  都要連 SharedmemoryMap**，三條都要。

**INT0/INT1 接法**（這個容易接錯）：

- 目標：DMA2_1.INT0 → ARMv8_0、DMA2_1.INT1 → ARMv8_1
- 從 ARM0 端發起連線：左邊 Design Hierarchy 點 ARM0 → 中間切 Interfaces
  tab → 展開 **Interrupt Input** → 雙擊 **nIRQ0**（cpu0 用）或 **nIRQ1**
  （cpu1 用）→ External Connections 加 peer，找 DMA2_1.INT0 / INT1
- ARM0 預設 `number_of_cpu = 4` 所以會看到 nIRQ0~3，nFIQ0~3 等等。我們只
  接 nIRQ0 跟 nIRQ1（CPU0 跟 CPU1），nIRQ2/3 留 stub model（cpu2/3 不存在）
- **千萬不要碰**：nFIQ、nvIRQ、nvFIQ（hypervisor virtual IRQ）、REI/SEI/VSEI
  （RAS error report）、GICV3_0~3（GIC distributor inter-CPU 通訊）。
  GICV3_x 動了會把 GIC 弄壞，CPU 收不到任何中斷
- ⚠️ Active Level Mandatory 警告 2 個 → **teacher LINE 5/7 11:33 說 ignore**

---

## STEP 3 — 計畫（保留歷史參考）

### 起手式（每次 session 開頭）

```csh
cd ~/project1
source setup.csh vze        # 必須跟 vs & 同一個 shell
vs -d DualA35 &
```

GUI 起來後右上角 perspective 切到 **TLM Creation**。確認左邊 Project Explorer
看到 `DualA35`（vdksys）跟 `DMA2`（library）兩個 project，DMA2 圖示乾淨無叉叉。


對應 PDF §2.03 step 9–10。目標：example 的 MEM/MEM2 + 新加 2× Memory_Generic =
共 4 RAM，按 v3 Figure 1 接成共享 bus 架構。

### 3.1 確認 v3 RAM 規劃

| RAM   | Range                    | Size   | 角色                |
|-------|--------------------------|--------|---------------------|
| RAM0  | `0x00000000~0x07FFFFFF`  | 128 MB | ARMv8_0 local       |
| RAM1  | `0x08000000~0x0FFFFFFF`  | 128 MB | ARMv8_1 local       |
| RAM2  | `0x20000000~0x2FFFFFFF`  | 256 MB | shared (含 sync flag) |
| RAM3  | `0x30000000~0x3FFFFFFF`  | 256 MB | shared              |

DMA2: `0x10000000~0x1000001F`（32 bytes）
Bus: `0x10000000~0x4FFFFFFF`（單一 shared bus）
UART: 沒給位址 — 先沿用 example 既有的（見「開放問題」）

### 3.2 加 2× Memory_Generic instance

vdksys → 從 library 拖兩個 Memory_Generic 到 design hierarchy，命名先用 `RAM2`、`RAM3`。
原本 example 的 MEM、MEM2 改名（或重用）成 RAM0、RAM1。

🚧 **未確認**：example template 哪個對應 RAM0、哪個對應 RAM1，要在 lab 看
hierarchy 的 default address window 才能決定。先進 lab 再說，不在這邊腦補。

### 3.3 改 size

Memory_Generic instance → Parameters → `mem_size`：
- RAM0 / RAM1 → `0x08000000`（128 MB）
- RAM2 / RAM3 → `0x10000000`（256 MB）

### 3.4 加 DMA2 instance

vdksys → 從 library 拖 DMA2 進來，命名 `DMA2_0`（單一 instance，1 slave + 2 master + 2 INT）。

### 3.5 接線（每接一條，過幾條就 Build & Run 一次驗 Dhrystone 還活著）

按 v3 Figure 1：
- ARMv8_0、ARMv8_1 → shared bus（master）
- shared bus → RAM0、RAM1、RAM2、RAM3（slave，配對應 address window）
- shared bus → DMA2_0.slave port（window `0x10000000`, size `0x20`）
- DMA2_0.M0、DMA2_0.M1 → shared bus（master）
- DMA2_0.INT0 → ARMv8_0 中斷腳
- DMA2_0.INT1 → ARMv8_1 中斷腳
- clk / rst 接 example 既有的 CPU_SS.Clock / SYSRST.RST

🚧 **未確認**：example template 的 shared bus 名字、ARMv8 的中斷腳名字（GIC 有沒有
nLEGACYIRQ_x、還是 GICD by-port）→ lab 看 hierarchy 才知道，不腦補。

### 3.6 中途驗證

每接 2~3 條就 Build → Run，UART0/UART1 Dhrystone 還在跑 = 沒接歪。
壞了立刻退回上一步比較容易。

---

## STEP 4 — 改 bare-metal source ✅ 已完成 (5/7)

### 完成記錄

bare-metal 在 Mac 改完、FileZilla 上傳、lab 編成 elf 並透過 Imageinfo 載入成功。
詳細的 source 內容跟 trampoline 設計見記憶 `project1_v3_rebuild.md`「Bare-metal
source state」段。

**最重要的 5 個發現**（5/11 回來別忘了）：

1. **兩個 CPU 都從 PC=0x0 啟動**，必須在 cpu0.elf 開頭放 MPIDR_EL1
   trampoline，把 cpu1（MPIDR Aff0=1）路由到 0x08000000（cpu1.elf 入口）。
   這個結論是 disasm dhrystone_aa64_cpu0.axf 前 24 byte 學來的（教材沒講）。
2. **vector_table 不能放在 0x0**，否則 reset PC=0 會撞上第一個 sync vector
   的 `b .` 無窮迴圈。要把 `_start` 放在 .vectors section（被 linker 強制
   放 0x0），vector_table 移到 `_start` 之後並 `.balign 2048`，再 msr
   vbar_el3 接上去。
3. **UART 是 PL011**（disasm `Setup_UART` 確認）：必須先寫 IBRD/FBRD/LCR_H/CR
   才能用，不然 DR 寫入全部被吞。CR=0x301（UARTEN | TXE | RXE）是關鍵。
4. **UART base**：cpu0 寫 0x40000000（UART_0），cpu1 寫 0x40001000（UART_1），
   per-cpu 透過 `#define UART_BASE` 在 main 開頭覆蓋 write.h 的 default。
5. **cpu0/cpu1 的 link 位址不一樣**：cpu0 連到 0x0（RAM0），cpu1 連到
   0x08000000（RAM1）。Makefile 拆 `LDFLAGS_CPU0` / `LDFLAGS_CPU1`，
   兩個各用自己的 linker script。stack 也要分（cpu0 sp=0x100000，
   cpu1 sp=0x08100000）。

### 現在 source 狀態

- `common/write.h`：含 `uart_init()` (PL011 init) + `_write` (poll FR.TXFF
  + 寫 DR) + `print_str` + `print_hex32` debug helpers
- `common/DMA2_regs.h`：v3 位址（DMA2_BASE=0x10000000、RAM2_BASE=0x20000000、
  RAM3_BASE=0x30000000、FLAG_ADDR=0x20000800）
- `common/linker.ld`（cpu0 用，`. = 0x0`）/ `common/linker_cpu1.ld`
  （cpu1 用，`. = 0x08000000`）
- `cpu0/init.S`：MPIDR trampoline + cpu0 init flow + vector_table + irq_handler
- `cpu1/init.S`：cpu1 init flow（無 trampoline）+ vector_table + irq_handler
- `cpu0/main_cpu0.c`：**目前是 DMA probe 版**（不是 spec 的 repeat-3 sync 流程）
- `cpu1/main_cpu1.c`：**目前是 halt 版**（boot OK + halt 等 cpu0）
- `Makefile`：拆 LDFLAGS_CPU0 / LDFLAGS_CPU1
- `common/init.S`：**孤兒檔，Makefile 沒用**，留著當參考，要清就刪

⚠️ main 還是 probe / halt 版，**5/14 demo 前必須恢復成 spec §4 資料流版**
（fill RAM2/3 → 等同步旗標 → DMA → 印 message × 3 cycle）。但**先解 DMA mystery
再恢復**，否則恢復也是噴亂碼。

---

## STEP 4 計畫 — 保留歷史參考

bare-metal source 在 Mac 端 `my_works/ARMv8/`。先在 Mac 改、FileZilla 上傳、
lab 上 `make`。也可以直接在 superdome3 上改。

### 4.1 必改項

- `common/DMA2_regs.h` 的 `DMA2_BASE` → `0x10000000`
- cpu0 / cpu1 各自的 stack / code 區段 → 落在自己的 local RAM（cpu0: 0~0x07FF_FFFF；cpu1: 0x0800_0000~0x0FFF_FFFF）
- 共享 buffer / sync flag 位址：
  - RAM2 ARMv8_0 init pattern：`0x20000400~0x200007FF`（"0123456789ABCDEF" × 64，1KB）
  - RAM3 ARMv8_1 init pattern：`0x30000400~0x300007FF`（"FEDCBA9876543210" × 64，1KB）
  - sync flag：`0x20000800`（1 byte，0/1 切換）
- linker.ld → 對應 RAM0/RAM1 的 entry point

### 4.2 UART_BASE — **暫定不改**

5/5 改成 `0x400000` 是 Package 1 的 UART 位址，跟 v3 example 不見得一樣。
example template 的 UART 沒給位址也跑得起來（teacher LINE 04:24 確認）→
先沿用 source code 原本的 UART base，lab 跑起來看 console 有沒有東西出。
有 → 不動；沒有 → 看 example 的 UART instance parameters 找實際 base，再改。

### 4.3 Make

```csh
cd ~/project1/my_works/ARMv8
make
```

`cpu0/DualARMv8_SW0.elf`、`cpu1/DualARMv8_SW1.elf` 應該各 ~70 KB。

### 4.4 把 ELF 指到 ARM0 Parameters

ARM0 → Parameters → Imageinfo（雙擊 `initial_image` 那一格 → Configure
Parameter 對話框 → Value 欄填**絕對路徑**，不要 `~/`）：
- cpu0 `initial_image` → `/home/user1/esl26/esl2625/project1/.../cpu0/DualARMv8_SW0.elf`
- cpu1 `initial_image` → `/home/user1/esl26/esl2625/project1/.../cpu1/DualARMv8_SW1.elf`
- cpu2、cpu3 不設（number_of_cpu = 2 之後它們本來就不啟動）

⚠️ 路徑格式為 `/home/user1/esl26/esl2625/...`（u-s-e-r-1，不是 `usr1`）—
較舊的 lab_environment.md 寫 `usr1`，但 5/7 lab session 的 PuTTY prompt
顯示是 `user1`。lab 上用 `pwd` 確認當下實際路徑。

🚧 **未確認**：v3 example 是否還是用 vpcfg + Images tab，還是 ARM0 Parameters
直接吃 ELF。lab 看就知道。

---

## STEP 5 — Run + Bus Transaction View（demo 必看）

### 5.1 Run

1. Perspective → Virtualizer (Simulation)
2. Build → Run
3. UART0 / UART1 console 應該各印 cpu0 / cpu1 的進度訊息
4. spec §4 資料流跑 3 次 → 每邊各 3 行 = 共 6 行 output

### 5.2 Bus transaction view

VDK Creator manual ch5 「Instance Connectivity Diagram」 — demo 必開。

1. 切到 Connectivity / Transaction view
2. 應看到：
   - cpu0 / cpu1 寫各自 local RAM（0x0~0x07FF_FFFF / 0x0800_0000~）
   - cpu0 / cpu1 寫 DMA2 reg（0x10000000~0x1000001F）
   - DMA2 讀 RAM2/3、寫 RAM3/2
   - sync flag `0x20000800` 在 0/1 之間切 3 次

### 5.3 Memory view 驗證

- RAM2 `0x20000400` 起：先 `"0123..."`，第 2 輪後變 `"FEDC..."`
- RAM3 `0x30000400` 起：先 `"FEDC..."`，第 2 輪後變 `"0123..."`
- `0x20000800`：0 → 1 → 0 → 1 → 0 → 1（3 個 cycle）

---

## STEP 6 — Debug branches（卡住時的對策表）

| 症狀 | 可能原因 | 對策 |
|---|---|---|
| Build 失敗（DMA2 library） | base_ 沒填 / Memory Map 沒手加 / INT category 沒改 | STEP 2 三件事重檢 |
| Run elaboration abort（address width） | RAM size 沒設 / address window 全範圍 | STEP 3.3 + 3.5 接線時帶 window |
| Run 起來但 cpu 不動 | ELF 沒指到 ARM0 Parameters | STEP 4.4 |
| Console 沒輸出 | UART base 不對 | 看 example UART instance parameter，改 source 重 make |
| 只 cpu0 動 | cpu1 ELF 沒指 / number_of_cpu 沒設 2 | STEP 1.5 + STEP 4.4 |
| DMA reg 寫不進 | bus address window 沒覆蓋 0x10000000 | STEP 3.5 重檢 DMA2 slave 那條 |
| DMA 跑但 ISR 沒觸發 | INT category 在 instance side 沒繼承 / GIC 沒 init | STEP 2.3 確認 library-side；GIC 看 ARM CORTEX A35 TLM2 LT PSP manual |
| **DMA 自動跑（沒寫 START 也搬資料）** | TLM Memory Map vs SystemC b_transport 解碼不一致；或 INT active level；或 RST polarity | 5/11 用 finer probe 定位（每寫一個 reg 印一行）；可能要動 TLM Project Memory Map 設定或 DMA2.h 的 reset_signal_is |
| **UART 狂噴 RAM2 pattern** | DMA 在跑（見上條），且 master port 接到 UART 路徑（待驗）| 看 sim console 是否有 DMA2.cpp 的 std::cout 輸出（b_transport / dma_process0） |
| 任何看不懂 error | 截圖 + console log | 停下來問，不瞎修 |

---

## STEP 7 — Demo 前準備

- [ ] Bus transaction view 預設打開
- [ ] Memory view 預設打開（RAM2 0x20000400、RAM3 0x30000400、0x20000800）
- [ ] Reset → Run 一次完整跑通（6 行 UART output）
- [ ] Instance Connectivity Diagram 能切出來
- [ ] 5-page report 寫完
- [ ] 整個 DualA35 workspace 打包

口頭講解可以準備：
- Cortex-A35 example 的選擇理由（v3 spec 直接點名）
- 4 RAM 規劃（2 local + 2 shared）對應 v3 Figure 1
- DMA2 8 reg 的兩組分工（set 1 = ARMv8_0、set 2 = ARMv8_1）
- DMA2 INT0/INT1 → ARMv8_0/ARMv8_1 的中斷路由
- 為什麼用 library-side INT category（一次到位、不會被 re-import 蓋掉）

---

## 開放問題（lab 現場決定 / 問老師）

1. **v3 spec §4C vs §2 矛盾**：§2 說「first set used by ARMv8_0」，§4C 說
   「ARMv8_0 monitors... ARMv8_**1** programs DMA2's 1st set」。應該是 §4C typo，
   照 §2 走（ARMv8_0 程式自己的 set 1），但要跟老師 confirm 一句。
2. **ARMv8_2 不存在**：score row 寫「ISR of ARMv8_1 and ARMv8_2」，project 只有 0、1。Cosmetic typo。
3. **UART 沒位址**：teacher 已 acknowledge，先沿用 example 既有 UART 跑得起來就好。
4. **RAM0/RAM1 對應 example 的 MEM/MEM2 哪一個**：lab 看 default address window 決定。
5. **cpu1/cpu2/cpu3 在 Cortex-A35 Example 的 ELF 怎麼指**：v3 是 1 cluster × 2 cpu，跟以前 2 cluster × 4 cpu 結構不一樣，UI 操作要 lab 才知。
