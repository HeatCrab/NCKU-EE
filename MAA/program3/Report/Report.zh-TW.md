# Metaheuristic Algorithms and Applications: Program Report III

第 17 組
- 組員： N26140804 張暐俊

## 1. Introduction

這次作業要把 metaheuristic algorithm 套到 Traveling Salesman Problem 上。spec 只需要任選至少兩個演算法即可，我延續前兩次 program 的選擇，繼續用 **Genetic Algorithm (GA)** 與 **Particle Swarm Optimization (PSO)**。一方面這兩個演算法我已經連續實作兩次、比較熟悉，另一方面沿用同一組演算法也能讓我把焦點放在「同樣的 GA 與 PSO，換到組合最佳化問題上會怎麼表現」這件事上，而不是又從頭認識一個新方法。

資料集就是遵照 spec 要求，使用指定的 TSPLIB Kaggle dataset，使用其中 `instance_id == 24` 這一筆。這裡有一個我一開始看 spec 時的小困惑，就是 spec 的 About Dataset 段落寫整個資料集是「2,783 個 instance、每個 20 城」，但同一頁下方的表格又明確標出 instance 24 有 52 城，兩處數字對不上。我最後以「instance 24 = 52 城」為準，因為這是 spec 真正要我處理的那一筆，實際讀進來的座標也確實是 52 筆。後面所有實驗都建立在這 52 城之上。

那一樣根據 spec 的要求，實驗分成兩部分。*Part I* 在前 12、30、52 城三個子集上跑 GA 與 PSO，用 spec 要求的四個指標比較。*Part II* 只取前 30 城，額外加上「偶數編號城市彼此不可相連」的限制，fitness 也因此和 *Part I* 不同。

最後的 Discussion 也一樣因應 spec 的兩個小題，分別交代所有參數設定，以及把兩個 Part 的最佳路徑畫出來。

## 2. Program design (Discussion (i))

首先在這邊除了展示一些程式碼上的設計外，也一並先說明 spec 中要求的 Discussion (i) 。從兩個演算法各自的解編碼、fitness、selection、crossover、mutation 到停止條件。最後關於實際的數值參數部分，為了不要失焦，我將他們集中放在後面 Parameter Settings 區塊下的那張對照表。

### 2.1 Data Pipeline

原始 CSV 約 226 MB，一列就是一個 TSP instance。我的做法是讀進來之後直接以 `instance_id == 24` 篩出那一列，再用 `ast.literal_eval` 把 `city_coordinates` 與 `distance_matrix` 兩個字串欄位還原成數值陣列。這裡我刻意沒有直接信任 CSV 附的 `distance_matrix`，而是從座標自己重算一份歐式距離矩陣，並要求自算版本與 CSV 版本的最大差異小於 `1e-6` 才放行，實測這個檢查通過（最大差異為 0）。之所以多這一步，是因為 CSV 裡的距離是被序列化成字串再讀回來的，可能帶有浮點截斷誤差，所以與其讓這種誤差悄悄滲進每一次 fitness 計算，不如用座標重算的乾淨版本當作唯一的距離來源。後續 GA 與 PSO 看到的距離矩陣都是這個自算版本。

### 2.2 Genetic Algorithm (GA)

GA 這邊直接用 permutation 編碼，一個個體就是 `0` 到 `n-1` 的一個排列，代表造訪城市的順序。這個編碼最大的好處是，只要每個算子都維持「輸入是排列、輸出也是排列」，整個搜尋過程就不需要任何修復步驟。各算子設定如下。

- Selection：tournament，$k = 3$
- Crossover：order crossover (OX)，rate $= 0.8$
- Mutation：swap，每個非菁英子代固定做一次對調
- Elitism：每代保留 2 個最佳個體

選 OX 而不是前兩次用過的數值型 crossover，是因為 permutation 不能像實數那樣逐維混合，否則會產生重複或缺漏的城市。OX 的做法是保留一個父代的一段連續片段，其餘位置再依另一個父代的相對順序補滿，天生保證子代仍是合法排列。

```python
# lib/ga.py
def _order_crossover(p1, p2, rng):
    """OX: keep a random segment of one parent, fill the rest from the other."""
    a, b = np.sort(rng.choice(len(p1), size=2, replace=False))
    b += 1  # half-open segment [a, b)
    return _ox_child(p1, p2, a, b), _ox_child(p2, p1, a, b)


def _ox_child(donor, filler, a, b):
    n = len(donor)
    child = np.full(n, -1, dtype=donor.dtype)
    child[a:b] = donor[a:b]
    taken = set(donor[a:b].tolist())

    fill = [city for city in np.roll(filler, -b) if city not in taken]
    positions = [(b + k) % n for k in range(n - (b - a))]
    for pos, city in zip(positions, fill):
        child[pos] = city
    return child
```

Mutation 則用最單純的 swap，隨機挑兩個位置對調，同樣不會破壞排列結構。值得一提的是這裡的 swap 不是「以某機率發生」，而是每個非菁英子代都固定做一次，等於給整個族群一個穩定的擾動量。Elitism 保留當代最好的 2 個個體，確保好不容易找到的短路徑不會被下一代的 crossover 或 mutation 改掉，讓收斂不會退步。停止條件就是固定跑滿 500 代，沒有額外的早停判斷。

### 2.3 Particle Swarm Optimization (PSO)

那相較於 GA 來說，PSO 麻煩的點在於它本來是為連續空間設計的，而 TSP 的解是離散排列。最終決定沿用前一次 program 的 random-keys 想法，讓每個粒子的位置是一個連續向量（初始化在 $[0, 1]^n$），要評估 fitness 時才用 `argsort` 把這個向量轉成一個排列，也就是「把連續鍵值由小到大排序，得到的索引順序就是造訪順序」。這樣速度更新可以完全留在連續空間、套用標準 PSO 公式，不需要為離散空間另設規則。

```python
# lib/pso.py: pso_minimize()
def evaluate(position: np.ndarray) -> float:
    return fitness_fn(np.argsort(position))

# ... swarm / pbest / gbest initialization omitted
for t in range(1, max_iter + 1):
    w = w_max - (w_max - w_min) * (t - 1) / (max_iter - 1) if max_iter > 1 else w_min
    for i in range(pop_size):
        r1 = rng.random(n)
        r2 = rng.random(n)
        vel[i] = (
            w * vel[i]
            + c1 * r1 * (pbest_pos[i] - pos[i])
            + c2 * r2 * (gbest_pos - pos[i])
        )
        vel[i] = np.clip(vel[i], -v_clamp, v_clamp)
        pos[i] = pos[i] + vel[i]
        # ... evaluate + pbest / gbest update omitted
```

慣性權重 $\omega$ 從 0.9 線性遞減到 0.4，前期保留較多舊速度偏向探索、後期收斂。這裡用 $(t-1)/(\text{max\_iter}-1)$ 而非 $t/\text{max\_iter}$，是為了讓最後一代精確落在 $\omega_{\min} = 0.4$。認知與社會係數設為 $c_1 = c_2 = 1.5$，速度則 clip 在 $[-0.5, 0.5]$ 之間。比較特別的是位置本身不做任何 clip 或修復，因為 `argsort` 只在乎鍵值之間的相對大小，粒子位置飄出 $[0, 1]$ 也不影響轉出來的排列，反而硬把它拉回範圍會干擾搜尋。停止條件同樣是固定跑滿 500 代。

### 2.4 Fitness Function

*Part I* 的 fitness 就是純粹的 roundtrip 長度，也就是把整條封閉路徑（含從最後一個城市回到起點的那條邊）的距離加總，目標是讓它越小越好。

*Part II* 因為多了「偶數城市不可相連」的限制，fitness 改成在 roundtrip 長度上，對每用到一條被禁止的邊就加一筆懲罰：

$$f_{\text{II}}(\text{tour}) = \text{roundtrip}(\text{tour}) + \lambda \cdot (\text{使用到的禁止邊數})$$

其中 $\lambda = 2n\max(D)$，以 30 城這個子集算出來是 6611.81。我把 $\lambda$ 設得這麼大是刻意的，因為一條禁止邊帶來的懲罰（$\ge \lambda$）就足以超過任何一條完整可行路徑的總長（這個子集的可行解大約落在 1200 上下），所以只要存在可行解，帶懲罰的不可行解永遠比它差。這等於用一個「軟性」的懲罰達到「硬性」排除的效果，搜尋會被自然推向可行區域，但又不需要在算子層面去硬擋，保留了實作上的單純。

實作上我讓距離矩陣 `D` 維持原樣、不去改寫它，而是另外維護一個獨立的布林遮罩 `forbidden_mask`，標記哪些 (i, j) 是偶-偶邊（以 1-indexed 判斷）。這樣可行路徑的幾何長度始終是真實的，懲罰只是額外疊加的一項，兩者分開比較不容易混淆。

## 3. Parameter Settings

兩個演算法的完整參數整理如下表。

| Parameter | GA | PSO |
|---|---|---|
| Population / swarm size | 100 | 50 |
| Max iterations | 500 | 500 |
| Number of runs (seeds) | 30 | 30 |
| Selection | Tournament ($k = 3$) | — |
| Crossover | OX (rate $= 0.8$) | — |
| Mutation | Swap（一次 / 子代） | — |
| Elitism | 2 | — |
| Encoding | Permutation | Random-keys $[0, 1]^n$ → `argsort` |
| Inertia weight $\omega$ | — | 0.9 → 0.4 (linear) |
| Cognitive / social $c_1, c_2$ | — | 1.5 / 1.5 |
| Velocity clamp | — | $[-0.5, 0.5]$ |
| Velocity init | — | uniform $[-0.1, 0.1]$ |
| Fitness | Part I 純 roundtrip。Part II 加 $\lambda \cdot$ 禁止邊數，$\lambda = 2n\max(D)$ | 同左（共用） |

有一點需要先講明。GA 的族群大小是 100、PSO 的 swarm 是 50，兩者並不相等。這個差異來自我沿用各自在前幾次 program 的預設值，而不是針對這次刻意調的。它的直接後果是 GA 每代會做 100 次 fitness 評估、PSO 每代只做 50 次，所以後面比較 computation time 時要記得，GA 偏慢有一部分單純是因為它每代算了兩倍的次數，並不全是單次評估比較貴。

實驗環境是在 CPU 上以 Python 3.12 搭配 NumPy 執行。計時用 `time.perf_counter()` 包住演算法主體（含族群 / 粒子群的初始化，但不含資料載入），每個 cell 回報的是 30 次 run 的平均時間。隨機種子固定為 0 到 29，GA 與 PSO 跑相同的種子編號，讓實驗可重現。不過這只是種子層級的一致，初始解並不相同，因為 GA 初始化的是排列、PSO 初始化的是連續向量，本來就不在同一個空間。

## 4. Part I

### 4.1 Protocol

*Part I* 在前 12、30、52 城三個子集上，各跑 GA 與 PSO，合計 6 個 cell，每個 cell 用種子 0–29 獨立執行 30 次、每次 500 代。每個 cell 的代表 run 取「fitness 最低」的那一次，Best Distance 與 Best fitness 都來自這同一條路徑，避免兩個指標來自不同 run 而對不上。要注意的是，*Part I* 的 fitness 定義就是純 roundtrip 距離，所以 spec 要求的 Best fitness value 在這裡會等於 Best Distance，兩欄數值相同。Average Distance 是 30 次 run 的距離平均，Computation Time 則是每次 run 的平均牆鐘時間。

### 4.2 Results

下表是 6 個 cell 的四項指標。Best Distance 與 Best Fitness 同值，如前述。

| Case | Algo | Best Distance | Best Fitness | Avg Distance | Comp Time (s) |
|---|---|---:|---:|---:|---:|
| 12 cities | GA | 209.47 | 209.47 | 209.47 | 0.753 |
| 12 cities | PSO | 209.47 | 209.47 | 227.14 | 0.208 |
| 30 cities | GA | 444.86 | 444.86 | 522.80 | 0.796 |
| 30 cities | PSO | 494.12 | 494.12 | 604.80 | 0.218 |
| 52 cities | GA | 850.38 | 850.38 | 943.79 | 0.881 |
| 52 cities | PSO | 1019.25 | 1019.25 | 1237.96 | 0.233 |

### 4.3 Observations

在最小的 12 城上，GA 與 PSO 都找到了同一個最短值 209.47，可以合理當作這個子集的全域最佳。差別在穩定度。GA 的 30 次 run 全部收斂到 209.47，PSO 則只有 15 次達標、其餘落在稍長的路徑上，因此它的 Avg Distance（227.14）被拉高。這說明在搜尋空間還小的時候，兩者都找得到最佳解，但 GA 找得比較可靠。

城市數一拉大，GA 的優勢就同時體現在 Best 和 Avg 兩欄。30 城時 GA 的最佳 444.86 明顯短於 PSO 的 494.12，52 城時更拉開到 850.38 對 1019.25。平均距離的差距更大，52 城時 GA 平均 943.79、PSO 平均 1237.96。我的理解是，GA 的 OX 與 swap 直接在排列結構上操作，能保留並重組「好的子路徑片段」。PSO 透過連續鍵值間接控制排列，城市一多，鍵值的微小擾動就可能讓 `argsort` 出來的順序大幅跳動，較難穩定地累積局部結構。

![Part I convergence curves for the six cells](Pics/convergence_part1.png)

**圖 1.** *Part I* 六個 cell 的收斂曲線，每條為 30 次 run 的平均 best-so-far fitness，陰影為 ± 1 標準差。

收斂曲線也呼應了上面的觀察。三個子集裡 GA 的曲線都壓在 PSO 之下，而且標準差帶在 12 城幾乎收成一條線，對應它 30/30 全數收斂。30 城與 52 城的標準差帶則明顯變寬，反映不同種子之間的結果落差變大，這在 GA 與 PSO 上都看得到，只是 GA 的整體水位較低。

至於 Computation Time，PSO 每個子集都比 GA 快上大約 3.5 到 4 倍。不過如同第 3 節提醒的，GA 的族群是 100、PSO 只有 50，GA 每代做了兩倍的 fitness 評估，所以這個時間差有相當一部分是族群大小造成的，不能單純解讀成 PSO 的單次迭代比較省。把這點納入考量後，比較公允的結論是，GA 用較多的計算換到了更短也更穩定的路徑。

## 5. Part II

### 5.1 Protocol

*Part II* 只取前 30 城，並加上「偶數編號城市彼此不可相連」的限制。以 1-indexed 來看，前 30 城裡有 15 個偶數城，它們兩兩之間共構成 105 條禁止邊。fitness 改用第 2.4 節的懲罰式，$\lambda = 6611.81$。一樣是 GA 與 PSO 各跑 30 個種子、每次 500 代，代表 run 取 fitness 最低者。

除了四項基本指標，*Part II* 另外回報三個和可行性有關的數字，分別是代表路徑用到的禁止邊數 `forbidden_edge_count`、所有 run 中最短的純距離 `min_pure_distance`（不論可行與否），以及一個 `infeasibility_flag` 標記代表路徑是否仍踩到禁止邊。我刻意不做任何修復或重試，一旦出現不可行就如實標記、照常回報，而不是把它藏起來。

### 5.2 Results

| Algo | Best Distance | Best Fitness | Avg Distance | Comp Time (s) | Forbidden Edges | Min Pure Distance | Infeasible |
|---|---:|---:|---:|---:|---:|---:|:---:|
| GA | 1190.74 | 1190.74 | 1216.89 | 0.881 | 0 | 1190.74 | No |
| PSO | 1372.62 | 1372.62 | 1400.70 | 0.250 | 0 | 1201.77 | No |

兩個演算法的代表路徑都是可行的（禁止邊數為 0），所以 Best Fitness 沒有被加上任何懲罰，仍然等於 Best Distance。要特別留意 PSO 那列。它的 `min_pure_distance`（1201.77）比自己的 Best Distance（1372.62）還短，這不是矛盾，而是因為這個最短純距離來自一條雖然較短、但其實踩到禁止邊的不可行路徑，幾何上短卻不合法，所以沒有被選為代表。

### 5.3 Observations

兩個演算法的代表路徑都可行，代表那個很大的 $\lambda$ 確實達到了預期效果。只要族群裡存在可行解，它的 fitness 就一定壓過所有不可行解，代表 run 自然會落在最短的可行路徑上。

不過把 30 次 run 攤開來看，GA 與 PSO 的可靠度差很多。GA 的 30 次 run 全部都找到了可行路徑，沒有任何一次以踩線收場。PSO 則有 15 次、整整一半的 run 最終的 gbest 仍帶著一條禁止邊。由於懲罰高達 6611，一條帶禁止邊的路徑 fitness 會直接衝到 7800 以上，這代表那 15 次 run 不是「找到比較差的可行解」，而是從頭到尾沒能湊出任何一條完全合法的路徑。這和 *Part I* 看到的趨勢一致，PSO 的 random-keys 編碼在這種帶硬性鄰接限制的問題上明顯吃力。

這裡也要把 Avg Distance 這欄講清楚，免得誤讀。它是 30 次 run 的純距離平均，而且是「不分可行與否」全部一起平均的。對 PSO 來說，這 1400.70 裡混進了那些不可行 run 的純距離，所以它並不是「可行解的平均長度」。同樣地 PSO 的 `min_pure_distance`（1201.77）來自一條不可行路徑。換句話說，*Part II* 的 PSO 數字一定要搭配 Infeasible 欄一起看，只看距離會低估它違反限制的程度。GA 因為全數可行，這個問題不存在，它的平均 1216.89 就是貨真價實的可行解平均。

就路徑品質本身而言，GA 的可行最短路徑（1190.74）也短於 PSO 的（1372.62），所以 *Part II* 不論從可行率還是路徑長度來看，GA 都比較好。

## 6. Discussion (ii)

這一節對應 spec 的 Discussion (ii)，把兩個 Part 的最佳 roundtrip 路徑畫出來。所有圖的城市標號都是 1-indexed，和前面的敘述一致。

*Part I* 三個子集、兩個演算法的最佳路徑如下。

![Part I best route, GA, 12 cities](Pics/route_part1_ga_12.png)

**圖 2.** *Part I* GA，12 城最佳路徑。

![Part I best route, PSO, 12 cities](Pics/route_part1_pso_12.png)

**圖 3.** *Part I* PSO，12 城最佳路徑。

![Part I best route, GA, 30 cities](Pics/route_part1_ga_30.png)

**圖 4.** *Part I* GA，30 城最佳路徑。

![Part I best route, PSO, 30 cities](Pics/route_part1_pso_30.png)

**圖 5.** *Part I* PSO，30 城最佳路徑。

![Part I best route, GA, 52 cities](Pics/route_part1_ga_52.png)

**圖 6.** *Part I* GA，52 城最佳路徑。

![Part I best route, PSO, 52 cities](Pics/route_part1_pso_52.png)

**圖 7.** *Part I* PSO，52 城最佳路徑。

12 城的兩條路徑幾乎一樣，都收成同一個沒有交叉的環，符合它們同樣達到 209.47 的結果。城市數變多後，GA 的 30、52 城路徑看起來比 PSO 的更「收斂」，交叉與繞遠的邊比較少，這和表上 GA 路徑較短是一致的。PSO 的路徑則還看得到幾條明顯把環撐開的長邊。

*Part II* 的兩條最佳路徑如下，圖中同時把偶數城與奇數城用不同顏色標出，被禁止的偶-偶邊若有使用會以紅色虛線呈現。

![Part II best route, GA](Pics/route_part2_ga.png)

**圖 8.** *Part II* GA 最佳路徑（長度 1190.74，禁止邊 0）。

![Part II best route, PSO](Pics/route_part2_pso.png)

**圖 9.** *Part II* PSO 最佳路徑（長度 1372.62，禁止邊 0）。

兩張圖裡都看不到任何紅色虛線，直接印證了代表路徑的可行性。整條環在相鄰位置上都成功避開了偶數城彼此相連。對照之下也能看出路徑為了繞開這些禁止鄰接，在偶數城密集的區域多走了一些轉折，這正是限制帶來的代價。

![Part II convergence curves](Pics/convergence_part2.png)

**圖 10.** *Part II* 收斂曲線，GA 與 PSO 各 30 次 run 的平均 best-so-far fitness，陰影為 ± 1 標準差。

*Part II* 的收斂曲線補充了一個前面提過的現象。GA 的曲線平滑地降到可行解的水位，標準差帶很窄。PSO 的標準差帶則一直偏寬，正是那 15 次始終卡在不可行區域的 run 把它撐開的。

## 7. Conclusion

這次把同一組 GA 與 PSO 換到 TSP 上，得到的結論其實相當一致。在這個問題上，GA 全面比 PSO 穩。*Part I* 三個尺度，GA 的最佳與平均路徑都較短，城市越多差距越大。*Part II* 加上禁止邊的限制後，GA 不只路徑較短，30 次 run 還全數可行，而 PSO 有一半的 run 連一條合法路徑都湊不出來。PSO 在牆鐘時間上看起來快了幾倍，但其中一大半要歸因於它的 swarm 只有 GA 族群的一半、每代少算一倍的 fitness，所以這個「快」不能直接當成效率優勢。

我認為差距的根源在解的表示法。GA 的 permutation 編碼配上 OX 與 swap，所有操作都直接落在排列結構上，既不需修復也能保留好的子路徑。PSO 的 random-keys 是透過連續鍵值間接控制排列，城市一多、又遇上硬性鄰接限制時，這層間接就成了負擔。所以如果要在這類帶限制的組合最佳化問題上挑一個，我會選 GA。PSO 並非不能用，但它原生是為連續空間設計的，套到離散排列上終究是借道而行。

## References

[1] ZIYA. *Traveling Salesman Problem (TSPLIB Dataset)*. Kaggle. https://www.kaggle.com/datasets/ziya07/traveling-salesman-problem-tsplib-dataset
