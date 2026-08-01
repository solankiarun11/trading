import pandas as pd
import requests
import streamlit as st
import yfinance as yf

# ==================== टेलीग्राम सेटिंग्स ====================
TELEGRAM_BOT_TOKEN = "8376242264:AAF8eGE1WiPXdlG1NN9jEfnJ41n7l3fuL74"  # अपना बोट टोकन यहाँ डालें
CHAT_ID = "1626240174"  # अपनी चैट आईडी यहाँ डालें


def send_telegram_alert(message):
  """टेलीग्राम पर मैसेज भेजने का फंक्शन"""
  if (
      TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE"
      or CHAT_ID == "YOUR_CHAT_ID_HERE"
  ):
    return

  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload, timeout=5)
  except Exception as e:
    print(f"Telegram Error: {e}")


# ==================== पेज की सेटिंग ====================
st.set_page_config(
    page_title="Ultimate Pro Trading Command Center", page_icon="🚨", layout="wide"
)

st.title("🚨 Ultimate Trading Command Center (Pro + Sound + RR Calculator)")
st.markdown(
    "Multi-TF Confluence, Smart Money Volume, Risk-to-Reward Calculator और Sound"
    " Alerts के साथ।"
)

col_r1, col_r2 = st.columns([6, 1])
with col_r2:
  if st.button("⚡ Run Full Scan"):
    st.rerun()

assets_to_scan = {
    "Nifty 50": "^NSEI",
    "Bank Nifty": "^NSEBANK",
    "Crude Oil": "CL=F",
    "Gold": "GC=F",
}

scanned_results = []
active_signals_found = []
nifty_change_for_sentiment = 0.0

for name, ticker in assets_to_scan.items():
  try:
    df_daily = yf.download(ticker, period="10d", interval="1d", progress=False)
    df_hourly = yf.download(ticker, period="5d", interval="60m", progress=False)

    if (
        df_daily is not None
        and not df_daily.empty
        and df_hourly is not None
        and not df_hourly.empty
    ):
      if isinstance(df_daily.columns, pd.MultiIndex):
        d_close = float(df_daily.iloc[-1][("Close", ticker)])
        d_prev = float(df_daily.iloc[-2][("Close", ticker)])
        d_vol = float(df_daily.iloc[-1][("Volume", ticker)])
        d_avg_vol = float(df_daily.iloc[-3:-1][("Volume", ticker)].mean())
      else:
        d_close = float(df_daily.iloc[-1]["Close"])
        d_prev = float(df_daily.iloc[-2]["Close"])
        d_vol = float(df_daily.iloc[-1]["Volume"])
        d_avg_vol = float(df_daily.iloc[-3:-1]["Volume"].mean())

      d_change = ((d_close - d_prev) / d_prev) * 100
      d_smart_money = d_vol > (d_avg_vol * 1.2) if d_avg_vol > 0 else False

      if name == "Nifty 50":
        nifty_change_for_sentiment = d_change

      if isinstance(df_hourly.columns, pd.MultiIndex):
        h_close = float(df_hourly.iloc[-1][("Close", ticker)])
        h_prev = float(df_hourly.iloc[-2][("Close", ticker)])
      else:
        h_close = float(df_hourly.iloc[-1]["Close"])
        h_prev = float(df_hourly.iloc[-2]["Close"])

      h_change = ((h_close - h_prev) / h_prev) * 100

      daily_trend = (
          "Bullish 🟢"
          if d_change > 0
          else ("Bearish 🔴" if d_change < 0 else "Neutral ⚪")
      )
      hourly_trend = (
          "Bullish 🟢"
          if h_change > 0
          else ("Bearish 🔴" if h_change < 0 else "Neutral ⚪")
      )

      # --- Risk-to-Reward & Stop Loss / Target Calculation ---
      risk_pips_or_pct = 0.005  # 0.5% Risk
      reward_ratio_1 = 1.0  # 1:1 Target
      reward_ratio_2 = 2.0  # 1:2 Target

      if d_change >= 0:
        stop_loss = round(d_close * (1 - risk_pips_or_pct), 2)
        target_1 = round(
            d_close + ((d_close - stop_loss) * reward_ratio_1), 2
        )
        target_2 = round(
            d_close + ((d_close - stop_loss) * reward_ratio_2), 2
        )
      else:
        stop_loss = round(d_close * (1 + risk_pips_or_pct), 2)
        target_1 = round(
            d_close - ((stop_loss - d_close) * reward_ratio_1), 2
        )
        target_2 = round(
            d_close - ((stop_loss - d_close) * reward_ratio_2), 2
        )

      # Confluence & Signal Logic
      confluence_signal = "⚪ WAIT / NO CONFLUENCE"

      if d_change > 0.3 and h_change > 0.1:
        if d_smart_money:
          confluence_signal = (
              "🚀 **STRONG BULLISH CONFLUENCE (Smart Money + Buy)**"
          )
          active_signals_found.append(
              f"• *{name}*: {confluence_signal}\n  Price: `₹{d_close:,.2f}` | SL:"
              f" `{stop_loss}` | T1: `{target_1}` | T2: `{target_2}`"
          )
        else:
          confluence_signal = "🟢 **BULLISH CONFLUENCE (Buy)**"
      elif d_change < -0.3 and h_change < -0.1:
        if d_smart_money:
          confluence_signal = (
              "🔻 **STRONG BEARISH CONFLUENCE (Smart Money + Sell)**"
          )
          active_signals_found.append(
              f"• *{name}*: {confluence_signal}\n  Price: `₹{d_close:,.2f}` | SL:"
              f" `{stop_loss}` | T1: `{target_1}` | T2: `{target_2}`"
          )
        else:
          confluence_signal = "🔴 **BEARISH CONFLUENCE (Sell)**"

      scanned_results.append({
          "Asset": name,
          "Price": round(d_close, 2),
          "Daily Trend": daily_trend,
          "Hourly Trend": hourly_trend,
          "Stop Loss": stop_loss,
          "Target 1 (1:1)": target_1,
          "Target 2 (1:2)": target_2,
          "Signal": confluence_signal,
      })
  except Exception as e:
    print(f"Error scanning {name}: {e}")

# --- MARKET SENTIMENT / FEAR & GREED METER ---
st.subheader("🧭 Market Sentiment Meter")
sentiment_text = "Neutral (शांत बाजार)"
if nifty_change_for_sentiment > 0.8:
  sentiment_text = "🔥 Extreme Greed (अत्यधिक लालच / स्ट्रॉन्ग बुलिश)"
elif nifty_change_for_sentiment > 0.2:
  sentiment_text = "🟢 Greed / Bullish Sentiment (बाजार में तेजी)"
elif nifty_change_for_sentiment < -0.8:
  sentiment_text = "❄️ Extreme Fear (अत्यधिक डर / भारी गिरावट)"
elif nifty_change_for_sentiment < -0.2:
  sentiment_text = "🔴 Fear / Bearish Sentiment (बाजार में मंदी)"

st.metric(
    "Market Mood", sentiment_text, f"{nifty_change_for_sentiment:+.2f}% Nifty"
)
st.markdown("---")

# --- यूआई टेबल ---
st.subheader("📊 Multi-TF Confluence & Risk-to-Reward Matrix")
df_results = pd.DataFrame(scanned_results)
if not df_results.empty:
  st.dataframe(df_results, use_container_width=True)
else:
  st.warning("डेटा लोड होने में समस्या आ रही है।")

# --- ऑटोमैटिक टेलीग्राम अलर्ट और साउंड (Browser Audio Beep) ---
if active_signals_found:
  alert_message = (
      f"🚨 *PRO TRADING SIGNAL & RR ALERT* 🚨\n\n"
      f"🧭 *Market Mood:* {sentiment_text}\n\n"
      f"एक्टिव सिग्नल्स (स्टॉप लॉस और टारگेट के साथ):\n"
      + "\n\n".join(active_signals_found)
      + f"\n\n⚡ अपने जोखिम के हिसाब से ट्रेड मैनेज करें!"
  )

  if "last_final_alert" not in st.session_state:
    st.session_state.last_final_alert = ""

  combined_str = "".join(active_signals_found)
  if st.session_state.last_final_alert != combined_str:
    send_telegram_alert(alert_message)
    st.session_state.last_final_alert = combined_str
    st.success(
        "🚀 सिग्नल्स डिटेक्ट हो गए हैं! टेलीग्राम अलर्ट और साउंड ट्रिगर कर दिया"
        " गया है।"
    )

    # ब्राउज़र में ऑडियो बीप (Sound Alert) बजाने के लिए एचटीएमएल/जावास्क्रिप्ट एम्बेड
    audio_html = """
        <audio autoplay>
          <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
        </audio>
        """
    st.markdown(audio_html, unsafe_allow_html=True)
  else:
    st.info("ℹ️ सिग्नल्स एक्टिव हैं (टेलीग्राम पर पहले ही भेजे जा चुके हैं)।")
else:
  st.success("✅ वर्तमान में कोई नया रिस्क-मैनेज्ड सिग्नल एक्टिव नहीं है।")