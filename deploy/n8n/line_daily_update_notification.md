# n8n + LINE 每日更新通知

這個專案現在會在 `Daily ETL Update` GitHub Actions 結束後，額外 POST 一份 JSON payload 到你設定的 n8n webhook。

## GitHub 端設定

在 GitHub repository secrets 新增：

- `N8N_DAILY_UPDATE_WEBHOOK_URL`

內容填你的 n8n **production webhook URL**。

## GitHub 傳給 n8n 的 payload

GitHub Actions 會送出類似這樣的 JSON：

```json
{
  "job_status": "success",
  "changes_pushed": true,
  "repository": "patricxie/precious-metal-premium-strategy",
  "workflow": "Daily ETL Update",
  "ref_name": "main",
  "event_name": "workflow_dispatch",
  "run_id": "123456789",
  "run_url": "https://github.com/patricxie/precious-metal-premium-strategy/actions/runs/123456789",
  "head_sha": "431a797...",
  "last_update": {
    "last_update_time": "2026-03-26 08:00:21",
    "status": "success",
    "message": "每日資料更新完成"
  }
}
```

## 建議的 n8n 流程

1. `Webhook` node
2. `Code` node 或 `Edit Fields` node
3. `HTTP Request` node 呼叫 LINE Messaging API push endpoint

## Webhook Node

- Method: `POST`
- Authentication: 視你的 n8n 環境而定
- 使用 **Production URL**

## Code Node 範例

```javascript
const p = $json;
const ok = p.job_status === 'success';
const icon = ok ? '✅' : '❌';
const updateTime = p.last_update?.last_update_time || 'N/A';
const updateMessage = p.last_update?.message || 'N/A';

return [
  {
    json: {
      lineText:
        `${icon} Precious Metal ETL ${p.job_status}\n` +
        `Last Update: ${updateTime}\n` +
        `Message: ${updateMessage}\n` +
        `Changes Pushed: ${p.changes_pushed}\n` +
        `Run: ${p.run_url}`,
    },
  },
];
```

## LINE HTTP Request Node 設定

- Method: `POST`
- URL: `https://api.line.me/v2/bot/message/push`
- Send Headers: `true`
- Header `Authorization`: `Bearer <YOUR_CHANNEL_ACCESS_TOKEN>`
- Header `Content-Type`: `application/json`
- Send Body: `JSON`

Body 範例：

```json
{
  "to": "<YOUR_LINE_USER_ID>",
  "messages": [
    {
      "type": "text",
      "text": "{{ $json.lineText }}"
    }
  ]
}
```

## LINE 端需要準備的資料

- `Channel access token`
- 要接收通知的 `userId`、`groupId` 或 `roomId`

若你是要通知你自己的 LINE，一般最簡單是：

1. 建一個 LINE Official Account / Messaging API channel
2. 讓你的 LINE 帳號先加這個官方帳號為好友
3. 從 LINE webhook event 取得自己的 `userId`
4. 在 n8n 的 LINE push request 中把 `to` 設成這個 `userId`

## 測試方式

1. 在 GitHub repository 設好 `N8N_DAILY_UPDATE_WEBHOOK_URL`
2. 在 n8n 啟用 workflow
3. 手動觸發 `Daily ETL Update`
4. 確認 n8n 有收到 payload
5. 確認 LINE 收到成功或失敗通知
