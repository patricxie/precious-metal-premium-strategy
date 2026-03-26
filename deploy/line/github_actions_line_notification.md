# GitHub Actions 直接推送 LINE 每日更新通知

這個專案現在可以在 `Daily ETL Update` GitHub Actions 結束後，直接呼叫 LINE Messaging API 發送通知，不需要經過 n8n。

## GitHub 端設定

在 GitHub repository secrets 新增：

- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_TO_ID`

`LINE_CHANNEL_ACCESS_TOKEN` 是 LINE Messaging API channel access token。  
`LINE_TO_ID` 可以是要接收通知的 `userId`、`groupId` 或 `roomId`。

## workflow 會送出的 LINE 訊息內容

通知內容會包含：

- workflow 成功或失敗狀態
- `last_update.json` 的更新時間
- `last_update.json` 的狀態與訊息
- 這次是否有推送變更
- GitHub Actions run 連結

## LINE 端需要準備的資料

1. 建立 LINE Official Account / Messaging API channel
2. 取得 `Channel access token`
3. 讓接收通知的對象先成為好友，或把官方帳號加入群組
4. 從 webhook event 取得自己的 `userId`、`groupId` 或 `roomId`
5. 把這個 ID 存成 GitHub secret `LINE_TO_ID`

## 測試方式

1. 在 GitHub repository 設好 `LINE_CHANNEL_ACCESS_TOKEN` 與 `LINE_TO_ID`
2. 手動觸發 `Daily ETL Update`
3. 確認 LINE 收到成功或失敗通知

## 可選方案

如果你之後還想做多平台通知、條件分流或訊息格式加工，repo 內也保留了一份可匯入 n8n 的範本：

- [`deploy/n8n/line_daily_update_notification.workflow.json`](/Users/patric/Desktop/資料工程師/Precious_Metal_ETL/deploy/n8n/line_daily_update_notification.workflow.json)
