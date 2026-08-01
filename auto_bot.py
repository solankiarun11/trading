import time
import pandas as pd
import requests
import yfinance as yf

# ==================== टेलीग्राम सेटिंग्स ====================
TELEGRAM_BOT_TOKEN = "8376242264:AAF8eGE1WiPXdlG1NN9jEfnJ41n7l3fuL74"  # अपना बोट टोकन यहाँ डालें
CHAT_ID = "1626240174"  # अपनी चैट आईडी यहाँ डालें


def send_telegram_alert(message):
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload, timeout=5)
  except Exception as e:
    print(f"Telegram Error: {e}")


def check_market():
  print("Market scanning started...")
  assets = {
      "Nifty 50": "^NSEI",
      "Bank Nifty": "^NSEBANK",
      "Crude Oil": "CL=F",
      "Gold": "GC=F",
  }

  for name, ticker in assets.items():
    try:
      df = yf.download(ticker, period="5d", interval="1d", progress=False)
      if df is not None and not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
          close = float(df.iloc[-1][("Close", ticker)])
          prev = float(df.iloc[-2][("Close", ticker)])
        else:
          close = float(df.iloc[-1]["Close"])
          prev = float(df.iloc[-2]["Close"])

        change = ((close - prev) / prev) * 100

        # अगर बड़ा मूव या सिग्नल मिला
        if change > 0.4:
          msg = (
              f"🚨 *AUTO BOT ALERT* 🚨\n• *{name}*: Bullish Breakout!\n  Price:"
              f" `₹{close:,.2f}` (+{change:.2f}%)"
          )
          send_telegram_alert(msg)
        elif change < -0.4:
          msg = (
              f"🚨 *AUTO BOT ALERT* 🚨\n• *{name}*: Bearish Breakdown!\n  Price:"
              f" `₹{close:,.2f}` ({change:.2f}%)"
          )
          send_telegram_alert(msg)
    except Exception as e:
      print(f"Error for {name}: {e}")


# 24/7 चलने के लिए लूप (हर 15 मिनट में चेक करेगा)
if __name__ == "__main__":
  print("Auto Bot is running 24/7...")
  while True:
    check_market()
    time.sleep(900)  # 900 सेकंड = 15 मिनट