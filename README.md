# 📊 Crypto Signal Bot

> Real-time cryptocurrency trading signals powered by **Yahoo Finance** + **LiveCoinWatch API**, built with Python & Streamlit.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![yfinance](https://img.shields.io/badge/yfinance-Data-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 🚀 Live Demo
👉 **[Click here to open the app]([YOUR_STREAMLIT_URL_HERE](https://crypto-signal-bot-by-shahab.streamlit.app/))**

---

## 📸 Preview

![App Screenshot](<img width="1600" height="510" alt="image" src="https://github.com/user-attachments/assets/18430bc1-0793-4a28-a1be-66bac9ed0172" />
)

---

## ✨ Features

- 🟢 **BUY / SELL / HOLD signals** — based on RSI-14 + SMA-20 strategy
- 💰 **Real-time live price** — powered by LiveCoinWatch API
- 🎯 **Auto TP & SL** — Take Profit and Stop Loss calculated automatically
- 📈 **Interactive Candlestick Chart** — with Volume & RSI panels (Binance dark style)
- ⏱️ **Multiple Timeframes** — Daily, 4H, 1H, 15 Min
- 😂 **30+ Coins supported** — BTC, ETH, SOL, DOGE, PEPE, WIF, BONK and more
- 📋 **Search History** — track your last 8 analyzed coins
- 📊 **Market Cap & Volume** — live data from LiveCoinWatch

---

## 🧠 Signal Logic

| Condition | Signal |
|-----------|--------|
| Price > SMA-20 AND RSI < 70 | 🟢 **BUY / LONG** |
| Price < SMA-20 AND RSI > 30 | 🔴 **SELL / SHORT** |
| Neutral zone | 🟡 **HOLD / WAIT** |

**TP** = Entry + (3.0 × Volatility)  
**SL** = Entry − (1.5 × Volatility)  
**Risk/Reward Ratio** = 1 : 2

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Charts | Plotly |
| Chart Data | yfinance |
| Live Price | LiveCoinWatch API |
| Indicators | Pandas, NumPy |
| Language | Python 3.10+ |

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/Crypto-Signal-Bot.git
cd Crypto-Signal-Bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run crypto_signal_bot.py
```

---

## 📦 Requirements

```
streamlit>=1.35.0
yfinance>=0.2.40
requests>=2.31.0
plotly>=5.22.0
pandas>=2.2.0
numpy>=1.26.0
```

---

## 🔑 API Key Setup

This app uses the **LiveCoinWatch API** for real-time prices.

Get your free API key from 👉 [livecoinwatch.com](https://www.livecoinwatch.com/tools/api)

Then replace in `crypto_signal_bot.py`:
```python
LCW_KEY = "your-api-key-here"
```

Or for Streamlit Cloud, add to `secrets.toml`:
```toml
LCW_KEY = "your-api-key-here"
```

---

## 📁 Project Structure

```
Crypto-Signal-Bot/
│
├── crypto_signal_bot.py   # Main application
├── requirements.txt       # Dependencies
├── README.md              # This file
└── screenshot.png         # App preview
```

---

## ⚠️ Disclaimer

> This tool is built for **educational purposes only**.  
> I personally tested 4 signals — **3 out of 4 were highly accurate**.  
> However, crypto markets are volatile and unpredictable.  
> **If you use these signals for trading, you do so at your own risk.**  
> The developer is not responsible for any financial losses.  
> Always do your own research (DYOR) before investing. 🙏

---

## 👨‍💻 Developer

**Shahab Ullah Khattak**  
🎓 Bachelor's in Artificial Intelligence  
📧 shahabkhattak0000@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/shahab-ullah-khattak-5136a1246/)  


---

## ⭐ Support

If you found this project useful, please consider giving it a **star** ⭐  
It motivates me to build more cool projects!

---
