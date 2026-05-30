# 2026-05-25 MAA 課堂要問的問題

篩選自 `OPEN_QUESTIONS.md`，刪掉可由 spec 推導或慣例決定的，只留真正會卡住動工的。

---

## 必問

### Q1. Part II：「all the even-numbered cities are not connected」是什麼意思？

Spec 原文（p.1 Part II）：

> Only the first 30 cities are considered; determine the shortest route path if all the even-numbered cities are not connected. Note that the fitness function is different from that in Part I.

不確定的兩件事，請老師澄清其一即可：

**(a) 編號從 0 還是從 1？**
- 1-indexed → 受限城市是 `2, 4, 6, ..., 30`
- 0-indexed → 受限城市是 `0, 2, 4, ..., 28`

**(b)「not connected」的意思？**
可能讀法：

1. 把偶數城市整個拿掉 → 變成 ~15 個奇數城市的 TSP
2. 保留 30 城市，只禁止「偶-偶」之間的邊（偶-奇仍可走）
3. 禁止所有「碰到偶數城市」的邊（會無解，不太可能是這個意思）
4. 把禁邊設成無限大懲罰 / 距離矩陣設成 ∞
5. 其他

順帶可以一起問：spec 寫「fitness function is different from Part I」是老師有特定形式（例如要求 penalty term 寫出來），還是可以自行設計然後在報告 justify？

> 這題不問下去整個 Part II 沒辦法開始寫。Q1 答案出來，fitness function 的形式自然就跟著確定。

#### 老師回答（2026-05-25 課堂）

1. **老師理解的慣例：從 1 開始**（即 1-indexed → 受限城市是 `2, 4, 6, ..., 30`）。
2. **"even" 通常表示為 0、其他有數值**（疑似指距離矩陣中禁邊填 0、其他填實際距離）；另有「什麼從 0 開始」這句，現場記述片段不完整、語意待補。
3. **老師整體立場**：不違反事實性錯誤即可，怎麼定義由我們自己決定，**重點是報告寫清楚**。

→ 結論：Q1 在「老師授權自決」的意義下已解封。我們有裁量權，PLAN.md 可以開始寫。
→ 待補語意已補（2026-05-25 對話）：使用者補述「老師說起點的 even 是 0」。
  解讀為「在距離矩陣中，第一個（起點）even city 對應的位置填 0」——也就是
  reinforce「禁邊用 0 當 sentinel」的設計，剛好跟對角線 `d(i,i)=0` 一致。
  這個推敲會寫進 PLAN.md 的設計理由區。

→ **Part II 語意決定（2026-05-25 對齊）：採 (d) penalty / matrix-0 sentinel**——
  保留 30 城市結構不變，把所有「碰到偶數城市」（或更窄：偶-偶）的邊在距離矩陣中
  設成 0 當禁邊 sentinel，演算法在 fitness 評估時把 0 sentinel 視為 forbidden。
  最終 fitness 形式（penalty term 還是 hard reject）寫 PLAN 時決定。

---

## 機會問

### Q5. 重複跑幾次 / 幾個 seed 有班級統一標準嗎？

- Program I 用 30 次、Program II 用 30 seeds。
- spec 沒提，沒問到的話就沿用 30 次。
- 影響到「Average Distance」跨組可比性，順口問一下就好。

---

## 不必問（自己決定，理由寫進報告）

| 項目 | 決定 | 依據 |
|---|---|---|
| Part II 是 open path 還是 roundtrip？ | Roundtrip | Discussion (II) 明寫 "for Parts I **and II**" |
| 「first 12/30/52」按哪個順序？ | spec p.2 `city_coordinates` list 順序 | spec 已內嵌座標 |
| 演算法選哪兩種？ | GA + ACO | PSO 在 permutation 上不自然 |
| Average Distance 對什麼平均？ | 對 repeated runs 平均 | TSP 慣例 |
| Computation Time 怎麼量？ | 單次 run wall-clock，回報平均 | 慣例 |
| 停止條件 | 固定 iterations + 收斂門檻 | 自行 justify |
| `Best_Route` 欄要不要用？ | 不用 | 是分類標籤，跟最佳化任務無關 |

---

## 課後動作

把 Q1（+ 可能的 Q5）的答案直接回填到本檔，**不要刪題目**，保留問題＋答案兩段，方便寫報告時引用。然後再寫 `Codebase/PLAN.md`。
