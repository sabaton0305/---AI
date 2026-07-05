import requests
import config


def send_line_message(message):
    url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Authorization": f"Bearer {config.LINE_TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "to": config.LINE_USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message,
            }
        ],
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print("LINE通知を送信しました。")
    except requests.RequestException as e:
        print("LINE送信エラー")
        print(e)
