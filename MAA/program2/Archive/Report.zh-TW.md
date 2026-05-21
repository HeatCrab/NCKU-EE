# Metaheuristic Algorithms and Applications: Program Report II-2

第 17 組
- 組長 / 組員： N26140804 張暐俊

## 1. Overview

本次作業要求將 metaheuristic algorithm 應用於 *Early Stage Diabetes Risk Prediction* (UCI dataset 529) 的特徵選取、分群、與分類。在 spec 給出的 II-1（球桿系統控制）與 II-2（糖尿病風險預測）兩個題目，我因為自身學經歷背景因素，選擇實作 II-2。

在本次 program 中我繼續使用 program 1 中選擇的 GA 與 PSO ，並在 16 維二元 mask 空間中搜尋特徵子集，以 Logistic Regression 為分類器、`KMeans` (`n_clusters = 2`) 為分群器。

*Part I* 採用 spec 規定的 `train = test resubstitution` 協定，並額外執行 65,535 個非空 mask 的 exhaustive sweep 以取得「在當前 LR 設定下的真實最佳值」做為參考錨點。*Part II* 採用 10 × 5-fold stratified cross-validation 共 50 個 outer fold，inner 3-fold CV 驅動 GA/PSO 的 fitness 計算，outer test fold 全程不參與搜尋以避免 leakage。所有實驗在同一份預處理資料上跑兩個演算法，數值結果與圖表呈現於後續章節。

## 2. Implementation and Experiment

### 2.1 Dataset and Preprocessing

Spec 引用的 UCI 資料集為 520 筆 × 17 欄（16 個 attribute + 1 個 class label），原始類別 320 Positive / 200 Negative，呈現約 62/38 的類別不平衡。本實驗後續所有 cross-validation 切分一律採 stratified 方式以保留此類別比例。*Age* 在 CSV 中的實際範圍是 16–90，與 spec 文件 Attribute Information 區段標註的 20–65 不一致。同份 spec 的 dataset characteristics 表又寫 Number of Instances = 520，與 CSV 一致。但是考量到
1. 520 列這個數字本身就是 spec 自陳的事實
2. 引用的論文 [1] 也是直接使用 UCI 釋出的版本

本次實驗選擇保留原始 *Age* 不做截斷或過濾等處理，並將此落差記錄於此。

預處理上，所有 Yes/No、Male/Female、Positive/Negative 類別欄位編碼為 0/1。*Age* 維持原始整數，僅對其執行 z-score 標準化。在 *Part I* 由於 `train = test`，scaler 直接 fit 在完整 520 筆資料。在 *Part II* 則嚴格 fit 在每個 outer fold 的 training subset 上，再 apply 到該 fold 的 test subset，以避免 test 資料的統計量洩漏到 search loop。其餘二元欄位不做縮放。

### 2.2 Genetic Algorithm (GA)

Binary chromosome 為 16-bit 編碼，每位對應一個 attribute 是否被選取。各算子的設定概括如下：

- Tournament selection，$k = 3$
- Uniform crossover，每位獨立以 0.5 機率交換
- Bit-flip mutation，每位以 1/16 機率反轉
- Elitism：當代最佳個體保留至下一代 slot 0

初始族群禁止全零 mask。搜尋過程中若 crossover 或 mutation 產出空 mask，fitness 層另以 $-\infty$ 處理。相較於我當初在 Program I 使用的 real-valued GA 來說，這次因為搜尋空間本就是 16 維 binary，binary 編碼比 real-valued 更自然，crossover 與 mutation 也回到二元域的標準形式。

### 2.3 Particle Swarm Optimization (PSO)

Position 為 $[0, 1]^{16}$ 的連續向量，評估時以 0.5 為門檻轉換成二元 mask，然後 pbest 與 gbest 以連續位置儲存，但 `best_pos` 對外回報時必定為門檻化後的 mask。各超參數設定如下：

- 慣性權重 $w$ 自 0.9 線性遞減至 0.4
- Cognitive / social 係數設定為 $c_1 = c_2 = 2$
- Velocity clamp 是 $[-v_{\max}, v_{\max}]$

其中，如果某粒子的連續位置全部低於 0.5 且 threshold 後成為空 mask，fitness 層就會回傳 $-\infty$，讓該粒子無法成為 pbest / gbest，也就是相當於把空 mask 從搜尋空間中排除了。

### 2.4 Fitness Function

本次 program 中使用的 fitness 定義為：

$$\text{fitness}(\text{mask}) = \text{accuracy}(\text{mask}) - 0.005 \times \frac{|\text{selected}|}{16}$$

其中 $\lambda = 0.005$ 故意設得很小，是因為 penalty 的整個動態範圍是 $[0, 0.005]$，每多選一個 feature 只增加 $\lambda / 16 \approx 0.0003$ 的懲罰。相較之下，*Part I* resubstitution 在 520 筆上的 accuracy 最小變動單位是 $1/520 \approx 0.0019$——少分錯一筆樣本帶來的增益，我認為是抵得過約 6 個 feature 的懲罰的。因此除非兩個 mask 的 accuracy 完全相同，penalty 永遠不會主導比較，只在平手時偏好較少 feature。後續實測也驗證了 $\lambda$ 不會把 11-feature 的全域最佳 mask 推離最佳位置。

那在實作上，fitness 物件同時負責 empty-mask 哨兵、integer-mask cache 與 penalty 計算，三件事集中在一個 `__call__` 內

```python
# lib/fitness.py
@dataclass
class FitnessFunction:
    accuracy_fn: Callable[[np.ndarray], float]
    lambda_penalty: float = 0.005
    n_features: int = N_FEATURES
    cache: dict[int, float] = field(default_factory=dict)
    raw_accuracy: dict[int, float] = field(default_factory=dict)
    n_evaluations: int = 0
    n_cache_hits: int = 0

    def __call__(self, bits: np.ndarray) -> float:
        mask = bits_to_int(bits, self.n_features)
        if mask == 0:
            return float("-inf")
        if mask in self.cache:
            self.n_cache_hits += 1
            return self.cache[mask]
        cols = mask_to_columns(mask, self.n_features)
        acc = float(self.accuracy_fn(cols))
        size_ratio = mask.bit_count() / self.n_features
        score = acc - self.lambda_penalty * size_ratio
        self.cache[mask] = score
        self.raw_accuracy[mask] = acc
        self.n_evaluations += 1
        return score
```

`accuracy_fn` 是被注入的函式，依協定不同有不同實作：

- *Part I* 是「以 mask 為特徵子集，對 520 筆做 fit-predict 計算 resubstitution accuracy」
- *Part II* 則是「對 outer training 做 inner 3-fold CV、回傳平均 accuracy」。

這樣的設計讓同一個 fitness/cache/penalty 邏輯能在兩個 Part 共用。Cache 以整數 bitmask 為 key，是因為 GA 與 PSO 在 16 維 binary 空間搜尋時，相同 mask 反覆出現的機率本就很高。

### 2.5 Classifier and Clustering

分類器的部分選擇使用 Logistic Regression（sklearn `LogisticRegression`）原因有以下幾個：
1. 它正是 Islam et al. [1] 採用的分類器之一，用相同模型才能與該文 baseline 直接對照
2. LR 訓練極快，這對需要 fit 65,535 次的 exhaustive sweep、以及 50 個 outer fold 各跑 GA/PSO 內層數千次評估是必要條件
3. 線性模型不引入額外特徵交互作用，能讓 mask 本身的特徵選取訊號保持乾淨。

那除此之外，超參數的部分
- 參數 `solver='lbfgs'`
- L2 penalty、`C=1.0`
- `max_iter=1000`
- `fit_intercept=True`
- threshold 0.5
- 無 class weights。

所有 exhaustive baseline、*Part I*、*Part II* 都使用同一份 LR 設定。這也代表 exhaustive sweep 找到的「最佳 mask」是「在此 LR 配置下的最佳」，並非絕對最佳，換 LR 設定或換分類器後排名可能變動。

分群器使用 `KMeans` (`n_clusters = 2`)，先在 training 資料 fit，再用 training 資料 majority vote 將兩個 cluster 對應到 Positive / Negative 標籤，最後對 evaluation 資料計算 accuracy。Clustering 結果僅在 *Part I/II* 報表中與分類結果並列呈現，不進入 GA/PSO 的 fitness 計算——因為 spec 要求「feature extraction, clustering, and classification」三件事都要做，但沒有要求把 clustering 納入優化目標，把它分離反而能觀察「同一個 mask 在監督與無監督下的差距」。

### 2.6 Baselines and Parameter Settings

為了讓 GA/PSO 的結果有比對基準，本實驗準備了五個 baseline：

- **All-features Logistic Regression**（mask = `0xFFFF`）：不做特徵選取的對照組，是 GA/PSO 必須超越的下限。
- **All-features Random Forest**（sklearn 預設參數，固定 `random_state=0`）：強分類器 reference，在 resubstitution 下會 overfit 到 1.0000，用來顯示「同一份資料若不限制模型，零誤差可達」。
- **Majority-class baseline**：恆預測 Positive，accuracy = 320/520，分類問題的絕對下限。
- **Exhaustive LR sweep**：列舉全部 65,535 個非空 16-bit mask，紀錄每個 mask 的 resubstitution accuracy。其中 tiebreak 規則為 accuracy 遞減、n_features 遞增、mask 遞增，並在此規則下選出 *Part I* 比對用的真實最佳 mask。
- **Islam et al. [1]**：該文 LR 在 10-fold CV 下 accuracy 為 0.9240，參考來供 *Part II* 比對。

實驗的所有參數整理於下表：

| 參數 | GA | PSO | 共用 |
|---|---|---|---|
| Population size | 50 | 50 | — |
| Iterations | 100 | 100 | — |
| Selection / update | Tournament $k = 3$ | $w$: 0.9 → 0.4, $c_1 = c_2 = 2$ | — |
| Crossover | Uniform (per-bit 0.5) | — | — |
| Mutation | Bit-flip (per-bit 1/16) | — | — |
| Elitism | Slot 0 preserved | — | — |
| Representation | Binary 16-bit | $[0, 1]^{16}$ → threshold 0.5 | — |
| $\lambda$ (n_features penalty) | — | — | 0.005 |
| Classifier | — | — | LR (lbfgs, L2, C = 1.0, max_iter = 1000) |
| Cluster | — | — | `KMeans` (`k = 2`) |

實驗環境是 CPU 上以 Python 3.12 + scikit-learn 執行。

最終執行時間的部分：
- *Part I* 全程約 41 秒（GA 32.06 s、PSO 9.10 s）
- *Part II* 全程 179.14 秒。

其中，隨機種子在 *Part I* 為每個 seed 獨立指定，*Part II* 為每個 fold 獨立指定。

## 3. Part 1

### 3.1 Protocol

依 spec 要求採用 `train = test` 的 resubstitution 協定，對完整 520 筆資料同時做特徵選取與分類，模型在訓練資料上的預測即為 test 結果。GA 與 PSO 各跑 30 個獨立 seed，每 run 為 `pop = 50`、`max_iter = 100`。每個 seed 結束後紀錄 best mask、其 raw accuracy、所選特徵數，並對該 seed 的 best mask 在完整資料上計算 spec 規定的五項指標（Accuracy / Sensitivity / Specificity / Precision / F-measure），分類與 `KMeans` clustering 各算一組。30 個 seed 完成後，依前述 tiebreak 規則挑出 best run 做最終呈現。

### 3.2 Results

Exhaustive sweep 在當前 LR 配置下找到的最佳 resubstitution accuracy 為 0.9500，此值由 mask `12239`（11 個特徵）與 mask `61135`（12 個特徵）並列達成。依 tiebreak 規則優先回報 mask `12239`，其特徵組合為 *Age, Gender, Polyuria, Polydipsia, Polyphagia, Genital thrush, visual blurring, Itching, Irritability, delayed healing, muscle stiffness*。

GA 30 個 seed 全部收斂到 mask `12239`，raw accuracy 30/30 為 0.9500。PSO 9/30 達到 0.9500，其餘 21 個 seed 落在 0.9365–0.9481 之間，raw accuracy 平均 0.9451 ± 0.0045。值得注意的是，PSO 那 9 個達到 0.9500 的 seed，全部命中 exhaustive 列舉出的兩個 global optima（mask `12239` 4 個 seed、mask `61135` 5 個 seed），無一例外，亦無在 exhaustive 之外發現新的 0.9500 mask。GA 與 PSO 的 best run 依 tiebreak 都落在 mask `12239`，因此後續五項指標完全相同。

**表 3.1：*Part I* best-mask 分類與分群指標（GA 與 PSO 的 best run 均落在 mask `12239`）**

| 指標 | Classification | Clustering (`KMeans`) |
|---|---|---|
| Accuracy | 0.9500 | 0.6154 |
| Sensitivity | 0.9500 | 1.0000 |
| Specificity | 0.9500 | 0.0000 |
| Precision | 0.9682 | 0.6154 |
| F-measure | 0.9590 | 0.7619 |

為了界定這個 0.9500 落在什麼位置，下表列出 *Part I* 的幾個參考點：

**表 3.2：*Part I* 參考數據**

| 參考 | Accuracy |
|---|---|
| Exhaustive best（mask `12239` / `61135` 並列）| 0.9500 |
| All-features Logistic Regression | 0.9308 |
| All-features Random Forest | 1.0000 |
| Majority-class baseline | 0.6154 |

### 3.3 Observations

*Part I* 最直接的觀察是 GA 完整收斂到全域最佳。從下圖可以看到，GA 的標準差帶在第 30 個 iteration 之後幾乎消失成一條線。可見在 16 維 mask 空間（搜尋空間 $2^{16} \approx 65\mathrm{k}$）上，pop = 50、iter = 100 的 GA 對這樣子的尺度顯然綽綽有餘，elitism 與 tournament k = 3 提供的選擇壓力足以在 ~30 代內鎖定全域最佳。

![Part I convergence curves](Pics/part1_convergence.png)

**圖 3.1：** *Part I* raw accuracy 收斂曲線，30 seeds 的平均 ± 1 標準差。虛線為 exhaustive optimum 0.9500。

相對於 GA 的全員到位，PSO 則很有意思。命中 global optimum 的 seed 是少數，其餘卡在 local optima，這是 PSO 在離散搜尋空間上典型的失敗模式。由於 position 是連續的、threshold 是硬切的，一旦 swarm 的 gbest 對應到某個 mask、隨後個別粒子在其鄰域內擾動產出的多半都是同一個 mask。

這點從 cache hit rate 高達 91.7%（GA 為 68.6%）也看得出來。值得讓人重新思考的是，那批達到 0.9500 的 PSO seed 裡，有一部分落在 mask `61135` 而非 tiebreak 偏好的 `12239`。我在想，或許 PSO 的成功路徑不見得會落在 GA 收斂到的同一點，但兩者落在的點都是 exhaustive 標記出的真實最佳，沒有「異常解」。從這個對比可以推斷，PSO 未達標的那些 seed 並不是找到「不同但同等好」的解，而是確實沒收斂。

從下圖可以更準確地閱讀， GA 的選取頻率精確落在 mask `12239` 的 11 個特徵上，PSO 則因部分 seed 落在 `61135` 或其他 local optima，而在若干特徵上散開。

![Part I feature frequency](Pics/part1_feature_freq.png)

**圖 3.2：** *Part I* 各 attribute 被 best mask 選中的次數（max = 30）。粗體 y-軸標籤為 exhaustive best mask `12239` 包含的 11 個特徵。

可以看到， Clustering accuracy 0.6154 恰好等於 majority-class baseline，這是個刻意保留下來的負面結果。`KMeans` 在純無監督的情況下，對 11 個多為二元、加上一個被標準化的 *Age* 構成的特徵空間，找出的兩個 cluster 與真實 Positive/Negative 標籤幾乎沒有對應關係。換句話說，`KMeans` 的兩群剛好以「全部歸到 Positive」的方式被 majority-vote 對應上，與 majority baseline 行為等價。這一點攤成五項指標會看得更直接
1. sensitivity 1.0
2. specificity 0.0
3. precision 0.6154
4. F-measure 0.7619
5. sensitivity 滿分而 specificity 掛零

這些恰好就是「全部猜 Positive」在指標上的樣子。這個現象在 *Part II* 的 CV 環境下則會略有不同。

## 4. Part 2

### 4.1 Protocol

依 spec 要求進行 10 次重複的 5-fold stratified cross-validation，共 50 個 outer fold。整個流程的核心設計是「outer test 不參與任何 model selection 決策」，避免特徵選取階段的選擇偏差混入 test accuracy。最外層 `main()` 的迴圈骨架負責切 50 個 outer fold 與「每 fold 重新 fit *Age* scaler」這件事：

```python
# run_part2.py: main()
# ... dataset load omitted
outer = RepeatedStratifiedKFold(
    n_splits=N_FOLDS, n_repeats=N_REPEATS, random_state=0
)
# ... timer / folds list setup omitted

for fold_i, (tr_idx, te_idx) in enumerate(outer.split(X_raw, y)):
    X_tr_raw, X_te_raw = X_raw[tr_idx], X_raw[te_idx]
    y_tr, y_te = y[tr_idx], y[te_idx]
    mean, std = fit_age_scaler(X_tr_raw)
    X_tr = apply_age_scaler(X_tr_raw, mean, std)
    X_te = apply_age_scaler(X_te_raw, mean, std)

    fold_out = run_one_fold(X_tr, y_tr, X_te, y_te, fold_seed=fold_i)
    # ... progress print / aggregation omitted
```

`run_one_fold` 內部把 GA 與 PSO 各跑一次，每個搜尋結束後立刻用 best mask 在 outer training 上重新 fit LR 並評估 outer test：

```python
def run_one_fold(X_tr, y_tr, X_te, y_te, fold_seed):
    fold = {}
    for name, algo in (("ga", ga_maximize), ("pso", pso_maximize)):
        f = make_cv_fitness(X_tr, y_tr, seed=fold_seed)
        r = algo(f, pop_size=POP_SIZE, max_iter=MAX_ITER, seed=fold_seed)
        mask = bits_to_int(r["best_pos"])
        # ... convergence bookkeeping omitted
        train_m, test_m, clust = evaluate_mask(mask, X_tr, y_tr, X_te, y_te)
        fold[name] = {
            "mask": int(mask),
            # ... other fields omitted
        }
    return fold
```

真正讓 outer test 隔離的關鍵在 `make_cv_fitness`。它在 outer training 上再切一次 3-fold StratifiedKFold，所有 GA/PSO 的 fitness 計算都只看這個內層切分，outer test 從未進入 fitness 評估：

```python
def make_cv_fitness(X_train, y_train, seed):
    skf = StratifiedKFold(n_splits=INNER_FOLDS, shuffle=True, random_state=seed)
    splits = list(skf.split(X_train, y_train))

    def accuracy_fn(cols):
        accs = [
            fit_predict_accuracy(
                X_train[tr][:, cols], y_train[tr],
                X_train[te][:, cols], y_train[te],
            )
            for tr, te in splits
        ]
        return float(np.mean(accs))

    return FitnessFunction(accuracy_fn=accuracy_fn, lambda_penalty=LAMBDA)
```

`KMeans` clustering 也在 `evaluate_mask` 內以同一份 best mask 在 outer training 與 test 上各評估一組五項指標。GA 與 PSO 在每個 outer fold 各自獨立執行一次（共 50 + 50 個搜尋），每 fold 種子獨立指定。

### 4.2 Results

整段 50 outer fold 流程 elapsed 179.14 秒。下方分別列出 GA 與 PSO 的 training 與 testing 指標，皆為 50 個 fold 的 mean ± std。

**表 4.1：*Part II* GA 結果（50 outer folds, mean ± std）**

| 指標 | Train | Test |
|---|---|---|
| Accuracy | 0.9380 ± 0.0091 | 0.9177 ± 0.0267 |
| Sensitivity | 0.9429 ± 0.0100 | 0.9275 ± 0.0359 |
| Specificity | 0.9301 ± 0.0203 | 0.9020 ± 0.0487 |
| Precision | 0.9559 ± 0.0122 | 0.9390 ± 0.0280 |
| F-measure | 0.9493 ± 0.0073 | 0.9326 ± 0.0223 |
| n_features | — | 10.12 ± 1.83 |

**表 4.2：*Part II* PSO 結果（50 outer folds, mean ± std）**

| 指標 | Train | Test |
|---|---|---|
| Accuracy | 0.9356 ± 0.0101 | 0.9160 ± 0.0269 |
| Sensitivity | 0.9420 ± 0.0092 | 0.9272 ± 0.0333 |
| Specificity | 0.9254 ± 0.0206 | 0.8980 ± 0.0458 |
| Precision | 0.9530 ± 0.0124 | 0.9364 ± 0.0268 |
| F-measure | 0.9474 ± 0.0081 | 0.9313 ± 0.0223 |
| n_features | — | 10.48 ± 1.88 |

分群（`KMeans`）的五項指標另列於下表，同樣為 training 與 testing 兩側。

**表 4.3：*Part II* 分群（`KMeans`）五項指標（50 outer folds, mean ± std）**

| 指標 | GA Train | GA Test | PSO Train | PSO Test |
|---|---|---|---|---|
| Accuracy | 0.6946 ± 0.0880 | 0.6900 ± 0.0874 | 0.6987 ± 0.0907 | 0.7006 ± 0.0902 |
| Sensitivity | 0.8536 ± 0.1429 | 0.8503 ± 0.1524 | 0.8487 ± 0.1432 | 0.8559 ± 0.1381 |
| Specificity | 0.4402 ± 0.4338 | 0.4335 ± 0.4284 | 0.4586 ± 0.4334 | 0.4520 ± 0.4313 |
| Precision | 0.7583 ± 0.1518 | 0.7533 ± 0.1481 | 0.7638 ± 0.1510 | 0.7631 ± 0.1517 |
| F-measure | 0.7782 ± 0.0380 | 0.7735 ± 0.0456 | 0.7796 ± 0.0428 | 0.7825 ± 0.0392 |

**表 4.4：*Part II* 參考 baseline**

| 參考 | Test accuracy |
|---|---|
| Islam et al. [1], LR, 10-fold CV | 0.9240 |
| GA test accuracy（本作業）| 0.9177 ± 0.0267 |
| PSO test accuracy（本作業）| 0.9160 ± 0.0269 |

GA test accuracy 在 50 fold 上的範圍為 [0.8558, 0.9712]、PSO 亦為 [0.8558, 0.9712]，兩者四分位距重疊。50 fold 中 GA 共出現 48 種不同的 best mask、PSO 49 種，幾乎每個 fold 都選到不同 mask。

### 4.3 Observations

*Part II* 的 test accuracy 與 Islam et al. [1] 的 LR 10-fold CV 結果（0.9240）落在了同一個區間無誤，且兩者均略低於 [1] 的數字。差距合理。其中，在 program2 中選擇採用 50 outer fold 的較嚴格切分、且每 fold 都重新進行特徵選取，相對於 [1] 僅使用全部 16 features 與 10-fold CV，我們的流程 test 的期望值本就會被 fold 切分變異拉高 std。Train → test 落差約 2 個百分點（GA 0.9380 → 0.9177、PSO 0.9356 → 0.9160），泛化 gap 健康、沒有明顯 overfit 跡象。圖 4.1 的 box plot 也顯示 GA 與 PSO 的 outer test accuracy 都密集落在 [1] 的 baseline 0.9240 上下。

![Part II test boxplot](Pics/part2_test_boxplot.png)

**圖 4.1：** *Part II* outer test accuracy 分布。虛線為 [1] 的 LR 10-fold CV baseline 0.9240。

GA 與 PSO 在 *Part II* 的差距不大，但 PSO 的 `n_features` 平均比 GA 多 0.36 個（10.48 vs 10.12）、specificity 略低（0.8980 vs 0.9020）。不過這個「PSO 多選一點 feature」並不是跨 Part 穩定的傾向，*Part I* 的 PSO 平均特徵數 10.93 反而比 GA 的 11.00 略少，所以這裡比較像 *Part II* CV 設定下的偶發差異，而非演算法本質。下圖的收斂曲線也看得出兩者在 inner CV 上幾乎貼合、標準差帶持續偏寬，反映每個 fold 的 inner-CV 最佳本就不同。

![Part II convergence](Pics/part2_convergence.png)

**圖 4.2：** *Part II* inner 3-fold CV accuracy 收斂曲線，50 個 fold 的平均 ± 1 標準差。

Clustering accuracy 在 *Part II* 反而明顯高於 *Part I* 的 0.6154（GA 0.6900、PSO 0.7006），這是因為 *Part II* 的 outer test 與 training 並非同一份資料，`KMeans` 在 fold 間有更多機會把 cluster 對應到真實標籤。但即便如此，clustering 仍遠低於 classification，再次印證 `KMeans` 在這個半二元特徵空間上單靠無監督結構難以分離 Positive 與 Negative。

那可以發現，根據 clustering 的五項指標，*Part II* 還浮現一個 *Part I* 看不到的現象，specificity 的跨 fold 變異大得異常（GA 0.4335 ± 0.4284、PSO 0.4520 ± 0.4313），標準差幾乎和平均一樣大。這代表 `KMeans` 對負類的辨識在 fold 間時好時壞，好的 fold 兩群剛好對上真實標籤、specificity 拉得很高，壞的 fold 又塌回 *Part I* 那種全猜 Positive 的狀態。accuracy 的 0.69 / 0.70 把這個雙峰分布平滑掉了，這也是把五項指標一起看會比單看 accuracy 更有資訊量的地方。

但最值得關注的是下圖中顯示的「*Part I* 最佳特徵集」與「*Part II* CV 穩定特徵集」之間的落差。

![Part II feature frequency](Pics/part2_feature_freq.png)

**圖 4.3：** *Part II* 各 attribute 被選中的次數（max = 50）。粗體 y-軸標籤為 *Part I* exhaustive best mask `12239` 包含的 11 個特徵，可看出 *Part I* 「真實最佳」特徵集與 *Part II* 「CV 穩定」特徵集存在落差。

對比 *Part I* exhaustive 認定的最佳 11 特徵與 *Part II* 50 fold 的選取頻率，可以分成三組：

- **兩演算法在 *Part II* 都極穩定的核心**：*Gender*（GA/PSO 各 50/50）、*Polydipsia*（50/50）、*Polyuria*（GA 50/50、PSO 48/50），皆為無爭議的核心特徵。
- ***Part I* 必選、*Part II* 飄移**：*Age*（30/50）、*visual blurring*（GA 20、PSO 28）。在 resubstitution 下必選的特徵，在 CV 下未必每 fold 都最有效。
- ***Part I* 完全不選、*Part II* 反而常見**：*Alopecia*（28–29/50）、*partial paresis*（21–25/50）、*sudden weight loss*（17–24/50）。這些「*Part I* 多餘」的特徵，在 CV 下提供穩定性。

這些分組與比較的意義在於，*Part I* 的「全域最佳 mask」是針對「特定一份 520 筆資料」過擬合出來的結果，當資料切分改變、評估的是泛化能力時，原本看似多餘的特徵反而提供穩定性、原本必選的特徵則未必每 fold 都最有效。

## 5. Questions

### 5.1 Do you have to use all the attributes?

在做完以上實驗後驗證明確不用。因為在本資料集與本 program 中 LR 的配置下，使用全部 16 個 attribute 的 resubstitution accuracy 為 0.9308，但僅使用 11 個 attribute（mask `12239`）的 resubstitution accuracy 為 0.9500。這表示了，更少的特徵反而給出更高的準確率，差距約 2 個百分點。

*Part II* 的 CV 結果也支持這個結論。GA 在 50 fold 中平均選出 10.12 個 feature、test accuracy 0.9177。PSO 平均選出 10.48 個 feature、test accuracy 0.9160。兩者皆在 all-features 之下顯著減少特徵數，仍能維持與 [1] 的 baseline 同一水準的 test accuracy。

更具體地說，*sudden weight loss / weakness / partial paresis / Alopecia / Obesity* 五個特徵在 *Part I* exhaustive 認定的最佳 mask `12239` 中皆未被選。不過其中 *Alopecia* 與 *Obesity* 其實出現在另一個並列最佳的 mask `61135`（它用這兩者換掉 *visual blurring*，一樣達到 0.9500），可見它們並非無用，而是可與其他特徵互換。真正在兩個全域最佳 mask 中都缺席的只有 *sudden weight loss / weakness / partial paresis*，這三者才真正對 LR 在這份資料上做 Positive/Negative 分類並無正向幫助，甚至會引入噪音。從臨床角度而言，這個結果並非否定這些症狀的醫學意義，而是指出在 16 個徵兆同時可得的條件下，11 個主要特徵足以承載絕大部分的分類資訊。

### 5.2 Is it possible to find the best combination of attributes to make the highest classification Accuracy rates?

在本作業中對「最佳」的操作型定義是「在固定 LR 配置（lbfgs、L2、C = 1.0、max_iter = 1000、threshold 0.5）下，使 resubstitution accuracy 最高的 mask」。在此定義下，65,535 個非空 mask 的 exhaustive sweep 可在 ~80 秒內完成，並明確找到 accuracy = 0.9500 的兩個並列最佳 mask（`12239` 與 `61135`）。GA 在 30 個獨立 seed 下 30/30 收斂到其中之一，PSO 9/30 命中，兩者的成功皆與 exhaustive 結果一致，沒有發現 exhaustive 之外的更佳解。換言之，對 16 個 attribute 的這個尺度，metaheuristic 搜尋找得到全域最佳，exhaustive sweep 則進一步保證這個全域最佳的存在性。所以是可以找到的，但需要對「最佳」的定義取得共識，因為「最佳」這件事是會隨評估協定與分類器設定而改變的。

*Part II* 的 CV 結果顯示，每個 outer fold 選出的 best mask 幾乎都不一樣（GA 48/50 種、PSO 49/50 種），也就是說存在一個「對所有 fold 都最佳」的單一 mask 並不切實際，因為不同 fold 的 training 資料統計分布不同，各自最適的特徵組合本就不同。所以如果我們把「最佳」定義改為「對未見資料泛化最好」，那麼存在的不是單一最佳 mask，而是一群高頻穩定特徵加上一組可替換的次要特徵。前者以 *Gender, Polyuria, Polydipsia, Irritability, Itching* 為代表，五者在 GA/PSO 兩演算法的 *Part II* 中皆有 40+/50 的選取率。換 LR 設定、換分類器、換評估協定，「最佳組合」的具體成員會跟著漂移。所以結論是，在固定設定下、單份資料、resubstitution 評估上，最佳 combination 存在且可被 metaheuristic 找到。放寬到泛化意義上，「最佳」更應理解為「一個高頻穩定子集加上若干互換的次要特徵」而非單一答案。

## 6. References

[1] Islam, MM Faniqul, et al. "Likelihood prediction of diabetes at early stage using data mining techniques." Computer Vision and Machine Intelligence in Medical Image Analysis: International Symposium, ISCMM 2019. Singapore: Springer Singapore, 2019.