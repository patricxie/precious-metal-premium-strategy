# 面試風格 Canva 生成提示詞

請幫我製作一份 **中文、16:9、8 頁、5 分鐘面試簡報**，主題是 **貴金屬市場分析 ETL 專案**。

這份簡報不是課堂型報告，而是 **資料工程面試作品集風格**。請強調：
- 我解決了什麼資料問題
- 我如何設計 ETL pipeline
- 我做了哪些工程決策
- 這個專案如何展現資料工程能力

整體視覺方向：
- 風格：專業、俐落、偏金融科技 / Data Engineering
- 配色：深藍、金色、米白
- 版面：乾淨、大標題、少字、高資訊密度
- 元素：流程圖、KPI 卡片、雙欄對照、資料標籤
- 不要太像課堂作業，不要卡通化，不要過多裝飾

請依照以下內容生成：

## 第 1 頁｜封面
標題：貴金屬市場分析 ETL 專案
副標：從多來源市場資料到可查詢交易訊號的資料流程實作
小字：Gold / Silver Futures + Spot Data / ETL / Premium / Z-score / SQLite

## 第 2 頁｜我想解決的問題
標題：Why This Project
- 市場資料來自不同來源，格式與日期不一致
- 我希望不只做分析，而是驗證自己能否落地一套 ETL pipeline
- 專案核心問題是：期貨相對現貨的偏離，能否轉成可量化的交易訊號
- 重點不是預測市場，而是建立可重複、可驗證的資料流程

## 第 3 頁｜我實作了什麼
標題：What I Built
- Extract：抓取黃金與白銀期貨、現貨資料
- Transform：標準化欄位、對齊日期、計算 Premium 與 Z-score
- Load：輸出 CSV 並寫入 SQLite
- Output：可接回測、圖表、報表與 dashboard
- 技術：Python、Pandas、SQLite、Matplotlib、Streamlit

## 第 4 頁｜資料與分析邏輯
標題：Data + Signal Logic
- 資料來源：Yahoo Finance 期貨資料 + 現貨 API 資料
- Premium (%) = (Futures - Spot) / Spot × 100
- 用 rolling Z-score 判斷目前偏離是否異常
- Z-score < -2：BUY
- Z-score > 2：SELL
- 其餘：HOLD
- 重點是把主觀判斷轉成可解釋的統計規則

## 第 5 頁｜工程上的挑戰與處理方式
標題：Engineering Challenges
左欄：遇到的問題
- 欄位名稱不一致
- 日期需要對齊
- API 可能有缺值或格式異常
- 流程若過度耦合會難以維護

右欄：我的做法
- schema normalization
- 統一日期格式與 join 邏輯
- 在 transform 階段處理缺值
- 拆成 extract / transform / load 模組

## 第 6 頁｜專案成果
標題：Results
- 成功建立可重複執行的 ETL pipeline
- 原始價格資料已轉成 premium、z-score 與 signal
- 結果可輸出成 CSV，也可存進 SQLite
- 可延伸到回測、圖表報告與前端展示

請加入 KPI 卡：
- 最佳策略：Silver BUY 20D
- 總報酬：317.02%
- 勝率：83.33%
- Gold BUY 20D：73.65%

## 第 7 頁｜這個專案如何對應資料工程職位
標題：Why It Matters For Data Engineering
- 我不只寫分析邏輯，也處理資料品質、流程拆分與結果落地
- 我把資料從 raw source 轉成可查詢、可維護的資料資產
- 這個專案展示的是資料工程思維，而不只是 notebook 分析
- 後續能接排程、自動化、監控與雲端部署

## 第 8 頁｜下一步與結尾
標題：Next Step
- 加入排程自動化
- 補上交易成本與更完整回測
- 部署到雲端並加上 dashboard
- 延伸成更完整的資料產品與研究平台

最後一句請收在：
這個專案讓我完整走過一次資料工程流程，也更確認自己想往資料工程方向發展

請用 **面試簡報語氣**，讓內容看起來更像作品集展示，而不是一般上課報告。
