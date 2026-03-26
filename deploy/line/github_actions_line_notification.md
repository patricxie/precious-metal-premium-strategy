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

## 最短路徑：怎麼拿到 LINE_TO_ID

如果你是要通知你自己的 LINE，最短流程是：

1. 在 LINE Developers Console 建立 Messaging API channel
2. 讓你的 LINE 帳號先加這個官方帳號為好友
3. 先把 Webhook URL 指到一個能看到原始 request 的地方
4. 用你的 LINE 帳號傳一則訊息給官方帳號
5. 從收到的 webhook JSON 裡找 `events[0].source.userId`
6. 把這個值設成 GitHub secret `LINE_TO_ID`

如果你要發到群組：

1. 把官方帳號加入群組
2. 在群組內發一則訊息
3. 從 webhook JSON 裡找 `events[0].source.groupId`
4. 把這個值設成 `LINE_TO_ID`

如果你要發到多人聊天室：

1. 把官方帳號加入聊天室
2. 在聊天室內發一則訊息
3. 從 webhook JSON 裡找 `events[0].source.roomId`
4. 把這個值設成 `LINE_TO_ID`

你只需要三種 ID 其中一種，不需要全部都有。

## 你會看到的 webhook JSON 重點

使用者私訊時，`source` 會像這樣：

```json
{
  "type": "user",
  "userId": "Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

群組訊息時，`source` 會像這樣：

```json
{
  "type": "group",
  "groupId": "Cxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

多人聊天室訊息時，`source` 會像這樣：

```json
{
  "type": "room",
  "roomId": "Rxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

## 手動測試 LINE Push

在把 GitHub secret 設上去之前，你可以先在本機手動測一次：

```bash
curl -X POST https://api.line.me/v2/bot/message/push \
  -H "Authorization: Bearer <YOUR_LINE_CHANNEL_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "<YOUR_LINE_TO_ID>",
    "messages": [
      {
        "type": "text",
        "text": "Precious Metal ETL LINE notification test"
      }
    ]
  }'
```

如果這一步成功，再把同一組 token 和 ID 放進 GitHub secrets，之後每日更新就會直接通知。

## 測試方式

1. 在 GitHub repository 設好 `LINE_CHANNEL_ACCESS_TOKEN` 與 `LINE_TO_ID`
2. 手動觸發 `Daily ETL Update`
3. 確認 LINE 收到成功或失敗通知

## 可選方案

如果你之後還想做多平台通知、條件分流或訊息格式加工，repo 內也保留了一份可匯入 n8n 的範本：

- [`deploy/n8n/line_daily_update_notification.workflow.json`](/Users/patric/Desktop/資料工程師/Precious_Metal_ETL/deploy/n8n/line_daily_update_notification.workflow.json)

## 官方文件

- [LINE Messaging API getting started](https://developers.line.biz/en/docs/messaging-api/getting-started/)
- [Send push message](https://developers.line.biz/en/reference/messaging-api/nojs/#send-push-message)
- [Group chats and multi-person chats](https://developers.line.biz/en/docs/messaging-api/group-chats/)
