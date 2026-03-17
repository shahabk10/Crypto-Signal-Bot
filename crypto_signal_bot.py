import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Signal Bot",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

    .main { background: #0a0e1a; }
    .block-container { padding: 1.5rem 2rem; max-width: 1200px; }

    /* Header */
    .hero-title {
        font-size: 2.2rem; font-weight: 700; color: #e2e8f0;
        background: linear-gradient(135deg, #00d4ff, #7c3aed);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }
    .hero-sub { color: #64748b; font-size: 0.95rem; margin-bottom: 1.5rem; }

    /* Signal Badges */
    .badge-buy {
        background: linear-gradient(135deg, #065f46, #059669);
        color: #d1fae5; padding: 8px 20px; border-radius: 20px;
        font-size: 1rem; font-weight: 700; display: inline-block;
    }
    .badge-sell {
        background: linear-gradient(135deg, #7f1d1d, #dc2626);
        color: #fee2e2; padding: 8px 20px; border-radius: 20px;
        font-size: 1rem; font-weight: 700; display: inline-block;
    }
    .badge-hold {
        background: linear-gradient(135deg, #1e293b, #334155);
        color: #cbd5e1; padding: 8px 20px; border-radius: 20px;
        font-size: 1rem; font-weight: 700; display: inline-block;
    }

    /* Metric Cards */
    .metric-card {
        background: #111827; border: 1px solid #1e293b;
        border-radius: 12px; padding: 16px 20px; text-align: center;
    }
    .metric-label { color: #64748b; font-size: 0.78rem; font-weight: 500;
                    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
    .metric-value { font-size: 1.4rem; font-weight: 700; color: #e2e8f0; }
    .metric-value.green { color: #34d399; }
    .metric-value.red { color: #f87171; }
    .metric-value.blue { color: #60a5fa; }

    /* Insight box */
    .insight-box {
        background: #0f172a; border-left: 3px solid #7c3aed;
        border-radius: 8px; padding: 12px 16px;
        color: #94a3b8; font-size: 0.9rem; line-height: 1.6;
        margin-top: 0.5rem;
    }

    /* Quick chip buttons */
    .stButton > button {
        background: #111827 !important; color: #94a3b8 !important;
        border: 1px solid #1e293b !important; border-radius: 20px !important;
        padding: 4px 14px !important; font-size: 0.8rem !important;
        font-weight: 500 !important; transition: all 0.2s !important;
    }
    .stButton > button:hover {
        border-color: #7c3aed !important; color: #e2e8f0 !important;
        background: #1e1b4b !important;
    }

    /* Input */
    .stTextInput > div > div > input {
        background: #111827 !important; color: #e2e8f0 !important;
        border: 1px solid #1e293b !important; border-radius: 10px !important;
        font-size: 1rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #7c3aed !important; box-shadow: 0 0 0 2px rgba(124,58,237,0.2) !important;
    }

    /* History table */
    .hist-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 8px 12px; border-bottom: 1px solid #1e293b;
        font-size: 0.85rem;
    }
    .hist-sym { color: #e2e8f0; font-weight: 600; }
    .hist-price { color: #64748b; }
    .hist-time { color: #475569; font-size: 0.75rem; }

    /* Divider */
    hr { border-color: #1e293b !important; }

    /* Selectbox */
    .stSelectbox > div > div {
        background: #111827 !important; color: #e2e8f0 !important;
        border: 1px solid #1e293b !important; border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── Coin Metadata ─────────────────────────────────────────────────────────────
COIN_META = {
    "BTC-USD":   ("Bitcoin",      "Layer-1",  "🟡"),
    "ETH-USD":   ("Ethereum",     "Layer-1",  "🔵"),
    "SOL-USD":   ("Solana",       "Layer-1",  "🟣"),
    "BNB-USD":   ("BNB",          "Layer-1",  "🟠"),
    "XRP-USD":   ("XRP",          "Layer-1",  "⚫"),
    "ADA-USD":   ("Cardano",      "Layer-1",  "🔵"),
    "AVAX-USD":  ("Avalanche",    "Layer-1",  "🔴"),
    "DOT-USD":   ("Polkadot",     "Layer-1",  "⚪"),
    "NEAR-USD":  ("NEAR",         "Layer-1",  "🟢"),
    "SUI-USD":   ("Sui",          "Layer-1",  "🔵"),
    "APT-USD":   ("Aptos",        "Layer-1",  "🔵"),
    "FTM-USD":   ("Fantom",       "Layer-1",  "🔵"),
    "TRX-USD":   ("TRON",         "Layer-1",  "🔴"),
    "LTC-USD":   ("Litecoin",     "Layer-1",  "⚪"),
    "MATIC-USD": ("Polygon",      "Layer-2",  "🟣"),
    "OP-USD":    ("Optimism",     "Layer-2",  "🔴"),
    "ARB-USD":   ("Arbitrum",     "Layer-2",  "🔵"),
    "UNI-USD":   ("Uniswap",      "DeFi",     "🦄"),
    "AAVE-USD":  ("Aave",         "DeFi",     "🟣"),
    "LINK-USD":  ("Chainlink",    "Oracle",   "🔵"),
    "INJ-USD":   ("Injective",    "DeFi",     "🔵"),
    "CRV-USD":   ("Curve",        "DeFi",     "🔴"),
    "DOGE-USD":  ("Dogecoin",     "Meme 🐕",  "🟡"),
    "SHIB-USD":  ("Shiba Inu",    "Meme 🐕",  "🔴"),
    "PEPE-USD":  ("Pepe",         "Meme 🐸",  "🟢"),
    "WIF-USD":   ("dogwifhat",    "Meme 🎩",  "🟠"),
    "BONK-USD":  ("Bonk",         "Meme 🐕",  "🟡"),
    "FLOKI-USD": ("Floki",        "Meme 🐕",  "🟡"),
    "MOG-USD":   ("Mog Coin",     "Meme 😼",  "🟣"),
    "POPCAT-USD":("Popcat",       "Meme 🐱",  "🟠"),
    "BRETT-USD": ("Brett",        "Meme",     "🔵"),
}

QUICK_PICKS = {
    "🔥 Popular":   ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD"],
    "😂 Meme Coins":["DOGE-USD", "SHIB-USD", "PEPE-USD", "WIF-USD", "BONK-USD", "FLOKI-USD", "MOG-USD"],
    "⚡ DeFi":      ["UNI-USD", "AAVE-USD", "LINK-USD", "INJ-USD", "CRV-USD"],
    "🌐 Layer-1/2": ["ADA-USD", "AVAX-USD", "NEAR-USD", "SUI-USD", "ARB-USD", "OP-USD"],
}

# ─── Helper Functions ──────────────────────────────────────────────────────────
def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    delta = prices.diff()
    gain = delta.where(delta > 0, 0.0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
    rs = gain / loss
    rsi_series = 100 - (100 / (1 + rs))
    return float(rsi_series.iloc[-1]) if not rsi_series.empty else 50.0

def fmt_price(p: float) -> str:
    if p >= 1000:   return f"${p:,.0f}"
    if p >= 1:      return f"${p:.4f}"
    if p >= 0.001:  return f"${p:.6f}"
    return f"${p:.8f}"

def get_signal(price, sma, rsi):
    if price > sma and rsi < 70:
        return "🟢 BUY / LONG", "buy"
    elif price < sma and rsi > 30:
        return "🔴 SELL / SHORT", "sell"
    return "🟡 HOLD / NEUTRAL", "hold"

def fetch_and_analyze(symbol: str):
    symbol = symbol.upper().strip()
    if "-" not in symbol:
        symbol += "-USD"

    ticker = yf.Ticker(symbol)
    df = ticker.history(period="3mo")

    if df.empty or len(df) < 21:
        return None, symbol

    df["SMA_20"]    = df["Close"].rolling(20).mean()
    df["Volatility"]= df["Close"].rolling(20).std()
    df["RSI"]       = calculate_rsi(df["Close"])

    current_price = float(df["Close"].iloc[-1])
    latest_sma    = float(df["SMA_20"].iloc[-1])
    volatility    = float(df["Volatility"].iloc[-1])
    rsi           = float(df["RSI"].iloc[-1])

    signal_text, signal_type = get_signal(current_price, latest_sma, rsi)

    if signal_type == "buy":
        sl = current_price - 1.5 * volatility
        tp = current_price + 3.0 * volatility
    elif signal_type == "sell":
        sl = current_price + 1.5 * volatility
        tp = current_price - 3.0 * volatility
    else:
        sl = current_price - 1.5 * volatility
        tp = current_price + 3.0 * volatility

    rr = abs(tp - current_price) / abs(sl - current_price) if abs(sl - current_price) > 0 else 0
    trend = "Bullish 📈" if current_price > latest_sma else "Bearish 📉"
    tp_pct = (tp - current_price) / current_price * 100
    sl_pct = (sl - current_price) / current_price * 100

    meta = COIN_META.get(symbol, (symbol, "Crypto", "🔵"))

    return {
        "symbol":        symbol,
        "name":          meta[0],
        "category":      meta[1],
        "icon":          meta[2],
        "current_price": current_price,
        "tp":            tp,
        "sl":            sl,
        "rsi":           rsi,
        "sma":           latest_sma,
        "volatility":    volatility,
        "signal_text":   signal_text,
        "signal_type":   signal_type,
        "rr":            rr,
        "trend":         trend,
        "tp_pct":        tp_pct,
        "sl_pct":        sl_pct,
        "df":            df,
    }, symbol

def build_chart(data: dict) -> go.Figure:
    df = data["df"].iloc[-60:]

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.04, row_heights=[0.72, 0.28],
        subplot_titles=("Price Chart", "RSI")
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        increasing_fillcolor="#065f46", increasing_line_color="#34d399",
        decreasing_fillcolor="#7f1d1d", decreasing_line_color="#f87171",
        name="Price"
    ), row=1, col=1)

    # SMA line
    fig.add_trace(go.Scatter(
        x=df.index, y=df["SMA_20"],
        line=dict(color="#f59e0b", width=1.5, dash="dot"),
        name="SMA-20"
    ), row=1, col=1)

    # TP / SL / Entry horizontal lines
    fig.add_hline(y=data["tp"], line_dash="dash", line_color="#34d399",
                  annotation_text=f"TP {fmt_price(data['tp'])}", row=1, col=1,
                  annotation_font_color="#34d399")
    fig.add_hline(y=data["sl"], line_dash="dash", line_color="#f87171",
                  annotation_text=f"SL {fmt_price(data['sl'])}", row=1, col=1,
                  annotation_font_color="#f87171")
    fig.add_hline(y=data["current_price"], line_dash="dot", line_color="#94a3b8",
                  annotation_text="Entry", row=1, col=1,
                  annotation_font_color="#94a3b8")

    # RSI
    fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"],
        line=dict(color="#a78bfa", width=2),
        fill="tozeroy", fillcolor="rgba(124,58,237,0.08)",
        name="RSI"
    ), row=2, col=1)

    fig.add_hrect(y0=30, y1=70, row=2, col=1,
                  fillcolor="rgba(148,163,184,0.05)", line_width=0)
    fig.add_hline(y=30, line_dash="dash", line_color="#34d399",
                  line_width=0.8, row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#f87171",
                  line_width=0.8, row=2, col=1)

    fig.update_layout(
        paper_bgcolor="#0a0e1a",
        plot_bgcolor="#0d1117",
        font=dict(color="#94a3b8", family="Space Grotesk"),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", y=1.02, x=0, font=dict(size=11)),
        margin=dict(l=10, r=10, t=40, b=10),
        height=520,
    )
    for axis in ["xaxis", "xaxis2", "yaxis", "yaxis2"]:
        fig.update_layout(**{axis: dict(
            gridcolor="#1e293b", linecolor="#1e293b",
            tickfont=dict(color="#475569", size=10)
        )})

    return fig

# ─── Session State ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result = None
if "search_key" not in st.session_state:
    st.session_state.search_key = 0

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">📡 Crypto Signal Bot</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Real-time Buy / Sell signals · TP & SL levels · Meme coins, DeFi, Layer-1 sab support</div>', unsafe_allow_html=True)

# ─── Search Bar ────────────────────────────────────────────────────────────────
col_input, col_btn = st.columns([5, 1])
with col_input:
    symbol_input = st.text_input(
        "Search",
        placeholder="Coin likhein: BTC, DOGE, PEPE, SOL...",
        label_visibility="collapsed",
        key=f"search_{st.session_state.search_key}"
    )
with col_btn:
    analyze_clicked = st.button("🔍 Analyze", use_container_width=True)

# ─── Quick Pick Chips ──────────────────────────────────────────────────────────
for category, coins in QUICK_PICKS.items():
    st.markdown(f"<span style='color:#475569;font-size:0.78rem;font-weight:500'>{category}</span>", unsafe_allow_html=True)
    cols = st.columns(len(coins))
    for i, coin in enumerate(coins):
        name = COIN_META.get(coin, (coin,))[0]
        if cols[i].button(name, key=f"chip_{coin}"):
            symbol_input = coin
            analyze_clicked = True

st.markdown("---")

# ─── Analyze Logic ─────────────────────────────────────────────────────────────
if analyze_clicked and symbol_input:
    with st.spinner(f"🔍 {symbol_input.upper()} ka data fetch ho raha hai..."):
        try:
            data, resolved_sym = fetch_and_analyze(symbol_input)
            if data is None:
                st.error(f"❌ '{resolved_sym}' ka data nahi mila. Spelling check karein.")
            else:
                st.session_state.result = data
                st.session_state.history.insert(0, {
                    "sym":    resolved_sym,
                    "signal": data["signal_type"],
                    "price":  data["current_price"],
                    "time":   datetime.now().strftime("%H:%M"),
                })
                if len(st.session_state.history) > 8:
                    st.session_state.history = st.session_state.history[:8]
                # Clear search bar
                st.session_state.search_key += 1
                st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ─── Results Display ───────────────────────────────────────────────────────────
if st.session_state.result:
    d = st.session_state.result

    # Signal Header
    badge_class = f"badge-{d['signal_type']}"
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:16px;margin-bottom:1rem;'>"
        f"  <span style='font-size:1.6rem;font-weight:700;color:#e2e8f0'>{d['icon']} {d['name']}</span>"
        f"  <span style='color:#475569;font-size:0.9rem'>({d['symbol']}) · {d['category']}</span>"
        f"  <span class='{badge_class}'>{d['signal_text']}</span>"
        f"</div>",
        unsafe_allow_html=True
    )

    # Metric Cards
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>Entry Price</div>
        <div class='metric-value blue'>{fmt_price(d['current_price'])}</div>
    </div>""", unsafe_allow_html=True)

    tp_sign = "+" if d['tp_pct'] > 0 else ""
    c2.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>Take Profit (TP)</div>
        <div class='metric-value green'>{fmt_price(d['tp'])}</div>
        <div style='color:#34d399;font-size:0.75rem'>{tp_sign}{d['tp_pct']:.1f}%</div>
    </div>""", unsafe_allow_html=True)

    sl_sign = "+" if d['sl_pct'] > 0 else ""
    c3.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>Stop Loss (SL)</div>
        <div class='metric-value red'>{fmt_price(d['sl'])}</div>
        <div style='color:#f87171;font-size:0.75rem'>{sl_sign}{d['sl_pct']:.1f}%</div>
    </div>""", unsafe_allow_html=True)

    c4.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>RSI</div>
        <div class='metric-value'>{d['rsi']:.1f}</div>
        <div style='color:#64748b;font-size:0.75rem'>{'Oversold' if d['rsi']<30 else 'Overbought' if d['rsi']>70 else 'Neutral'}</div>
    </div>""", unsafe_allow_html=True)

    c5.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>Risk / Reward</div>
        <div class='metric-value'>1 : {d['rr']:.1f}</div>
        <div style='color:#64748b;font-size:0.75rem'>{d['trend']}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Insight
    if d['signal_type'] == 'buy':
        insight = f"RSI {d['rsi']:.0f} hai aur price SMA-20 se upar — bullish momentum dikh raha hai. TP {fmt_price(d['tp'])} pe ({d['tp_pct']:.1f}% upar), SL {fmt_price(d['sl'])} pe rakhen."
    elif d['signal_type'] == 'sell':
        insight = f"RSI {d['rsi']:.0f} hai aur price SMA-20 se neeche — bearish pressure hai. SL {fmt_price(d['sl'])} pe zaroor rakhen, risk manage karein."
    else:
        insight = f"RSI {d['rsi']:.0f} neutral zone mein hai. Abhi clear direction nahi — confirmation ka wait karna better hoga."

    st.markdown(f'<div class="insight-box">💡 {insight}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Chart
    fig = build_chart(d)
    st.plotly_chart(fig, use_container_width=True)

# ─── Search History ────────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown("---")
    st.markdown("<span style='color:#475569;font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em'>Recent Searches</span>", unsafe_allow_html=True)
    for h in st.session_state.history:
        signal_color = "#34d399" if h["signal"]=="buy" else "#f87171" if h["signal"]=="sell" else "#f59e0b"
        signal_label = "BUY" if h["signal"]=="buy" else "SELL" if h["signal"]=="sell" else "HOLD"
        st.markdown(
            f"<div class='hist-row'>"
            f"<span class='hist-sym'>{h['sym']}</span>"
            f"<span style='color:{signal_color};font-size:0.78rem;font-weight:600'>{signal_label}</span>"
            f"<span class='hist-price'>{fmt_price(h['price'])}</span>"
            f"<span class='hist-time'>{h['time']}</span>"
            f"</div>",
            unsafe_allow_html=True
        )
