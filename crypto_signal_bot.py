import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Signal Bot | Binance Style",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Binance-Exact CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background: #0B0E11 !important;
    color: #EAECEF;
}
.main { background: #0B0E11 !important; }
.block-container { padding: 0 !important; max-width: 100% !important; background: #0B0E11; }
section[data-testid="stSidebar"] { display: none; }

.navbar {
    background: #161A1E; border-bottom: 1px solid #2B3139;
    padding: 0 24px; height: 56px;
    display: flex; align-items: center; gap: 32px;
}
.navbar-logo { font-size: 1.2rem; font-weight: 700; color: #F0B90B; display: flex; align-items: center; gap: 8px; }
.navbar-link { font-size: 0.82rem; font-weight: 500; color: #848E9C; padding: 0 14px; height: 56px; display: inline-flex; align-items: center; border-bottom: 2px solid transparent; }
.navbar-link.active { color: #EAECEF; border-bottom-color: #F0B90B; }
.live-badge { background: #0ECB8120; border: 1px solid #0ECB81; color: #0ECB81; font-size: 0.7rem; font-weight: 600; padding: 3px 10px; border-radius: 4px; letter-spacing: 0.04em; font-family: 'IBM Plex Mono', monospace; margin-left: auto; }

.ticker-tape { background: #161A1E; border-bottom: 1px solid #2B3139; padding: 0 24px; height: 34px; display: flex; align-items: center; gap: 28px; overflow: hidden; font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; }
.ticker-item { display: flex; gap: 6px; align-items: center; white-space: nowrap; }
.ticker-sym { color: #474D57; }
.ticker-up { color: #0ECB81; }
.ticker-dn { color: #F6465D; }

.page-wrap { padding: 20px 24px 40px; }
.section-title { font-size: 0.7rem; font-weight: 600; color: #474D57; text-transform: uppercase; letter-spacing: 0.06em; margin: 12px 0 6px; }

.stTextInput > div > div > input {
    background: #1E2329 !important; border: 1px solid #2B3139 !important;
    box-shadow: none !important; color: #EAECEF !important;
    font-size: 0.9rem !important; font-family: 'IBM Plex Mono', monospace !important;
    border-radius: 6px !important; height: 44px !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus { border-color: #F0B90B !important; }
.stTextInput > div > div > input::placeholder { color: #474D57 !important; }
.stTextInput > label { display: none !important; }

.stButton > button {
    background: #F0B90B !important; color: #1E2329 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 700 !important; font-size: 0.85rem !important;
    border: none !important; border-radius: 6px !important;
    height: 44px !important; width: 100% !important;
}
.stButton > button:hover { background: #FFD35A !important; }

div[data-testid="column"] .stButton > button {
    background: #1E2329 !important; color: #848E9C !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.76rem !important; font-weight: 500 !important;
    border: 1px solid #2B3139 !important; border-radius: 4px !important;
    height: 30px !important; letter-spacing: 0.02em !important;
}
div[data-testid="column"] .stButton > button:hover {
    border-color: #F0B90B !important; color: #F0B90B !important; background: #F0B90B10 !important;
}

.price-header {
    background: #161A1E; border: 1px solid #2B3139; border-radius: 8px;
    padding: 18px 22px; margin-bottom: 14px;
    display: flex; flex-wrap: wrap; gap: 20px; align-items: center; justify-content: space-between;
}
.ph-icon { width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; }
.coin-name-big { font-size: 1.1rem; font-weight: 700; color: #EAECEF; }
.coin-pair-txt { font-size: 0.78rem; color: #474D57; font-family: 'IBM Plex Mono', monospace; }
.live-price-num { font-family: 'IBM Plex Mono', monospace; font-size: 2rem; font-weight: 700; color: #EAECEF; letter-spacing: -0.02em; line-height: 1; }
.price-up { color: #0ECB81; font-size: 0.88rem; font-family: 'IBM Plex Mono', monospace; font-weight: 500; margin-top: 4px; }
.price-dn { color: #F6465D; font-size: 0.88rem; font-family: 'IBM Plex Mono', monospace; font-weight: 500; margin-top: 4px; }
.sig-buy { background: #0ECB8118; border: 1px solid #0ECB81; color: #0ECB81; font-size: 0.85rem; font-weight: 700; padding: 8px 22px; border-radius: 4px; letter-spacing: 0.04em; font-family: 'IBM Plex Mono', monospace; display: inline-block; }
.sig-sell { background: #F6465D18; border: 1px solid #F6465D; color: #F6465D; font-size: 0.85rem; font-weight: 700; padding: 8px 22px; border-radius: 4px; letter-spacing: 0.04em; font-family: 'IBM Plex Mono', monospace; display: inline-block; }
.sig-hold { background: #F0B90B18; border: 1px solid #F0B90B; color: #F0B90B; font-size: 0.85rem; font-weight: 700; padding: 8px 22px; border-radius: 4px; letter-spacing: 0.04em; font-family: 'IBM Plex Mono', monospace; display: inline-block; }
.sig-label { font-size: 0.68rem; color: #474D57; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }

.stat-row { display: grid; grid-template-columns: repeat(6,1fr); gap: 8px; margin-bottom: 14px; }
.stat-card { background: #161A1E; border: 1px solid #2B3139; border-radius: 6px; padding: 12px 14px; }
.stat-lbl { font-size: 0.68rem; color: #474D57; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
.stat-num { font-family: 'IBM Plex Mono', monospace; font-size: 0.88rem; font-weight: 600; color: #EAECEF; }
.stat-num.g { color: #0ECB81; }
.stat-num.r { color: #F6465D; }
.stat-num.y { color: #F0B90B; }
.stat-sub { font-size: 0.66rem; color: #474D57; font-family: 'IBM Plex Mono', monospace; margin-top: 3px; }

.insight-box { background: #161A1E; border: 1px solid #2B3139; border-left: 3px solid #F0B90B; border-radius: 6px; padding: 12px 16px; font-size: 0.82rem; color: #848E9C; line-height: 1.65; margin-bottom: 14px; }
.insight-box b { color: #EAECEF; font-weight: 600; }

.hist-wrap { background: #161A1E; border: 1px solid #2B3139; border-radius: 8px; overflow: hidden; margin-top: 20px; }
.hist-head { background: #1E2329; padding: 9px 16px; font-size: 0.68rem; font-weight: 600; color: #474D57; text-transform: uppercase; letter-spacing: 0.06em; display: grid; grid-template-columns: 1.2fr 1fr 1fr 1fr 1fr; border-bottom: 1px solid #2B3139; }
.hist-row-item { padding: 9px 16px; display: grid; grid-template-columns: 1.2fr 1fr 1fr 1fr 1fr; font-size: 0.8rem; border-bottom: 1px solid #2B313940; align-items: center; font-family: 'IBM Plex Mono', monospace; }
.hist-row-item:last-child { border-bottom: none; }
.hist-row-item:hover { background: #1E2329; }

.footer { text-align: center; padding: 18px; color: #474D57; font-size: 0.7rem; border-top: 1px solid #2B3139; margin-top: 24px; font-family: 'IBM Plex Mono', monospace; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #161A1E; }
::-webkit-scrollbar-thumb { background: #2B3139; border-radius: 3px; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
div[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Coin Metadata ──────────────────────────────────────────────────────────────
COIN_META = {
    "BTC-USD":    ("Bitcoin",     "BTC/USDT",   "Layer-1",  "₿",  "#F7931A"),
    "ETH-USD":    ("Ethereum",    "ETH/USDT",   "Layer-1",  "Ξ",  "#627EEA"),
    "SOL-USD":    ("Solana",      "SOL/USDT",   "Layer-1",  "◎",  "#9945FF"),
    "BNB-USD":    ("BNB",         "BNB/USDT",   "Layer-1",  "B",  "#F0B90B"),
    "XRP-USD":    ("XRP",         "XRP/USDT",   "Layer-1",  "✕",  "#00AAE4"),
    "ADA-USD":    ("Cardano",     "ADA/USDT",   "Layer-1",  "₳",  "#0033AD"),
    "AVAX-USD":   ("Avalanche",   "AVAX/USDT",  "Layer-1",  "A",  "#E84142"),
    "DOT-USD":    ("Polkadot",    "DOT/USDT",   "Layer-1",  "●",  "#E6007A"),
    "NEAR-USD":   ("NEAR",        "NEAR/USDT",  "Layer-1",  "N",  "#00C08B"),
    "SUI-USD":    ("Sui",         "SUI/USDT",   "Layer-1",  "S",  "#4DA2FF"),
    "APT-USD":    ("Aptos",       "APT/USDT",   "Layer-1",  "A",  "#24D4A8"),
    "LTC-USD":    ("Litecoin",    "LTC/USDT",   "Layer-1",  "Ł",  "#BFBBBB"),
    "TRX-USD":    ("TRON",        "TRX/USDT",   "Layer-1",  "T",  "#FF0013"),
    "MATIC-USD":  ("Polygon",     "MATIC/USDT", "Layer-2",  "M",  "#8247E5"),
    "OP-USD":     ("Optimism",    "OP/USDT",    "Layer-2",  "O",  "#FF0420"),
    "ARB-USD":    ("Arbitrum",    "ARB/USDT",   "Layer-2",  "A",  "#28A0F0"),
    "UNI-USD":    ("Uniswap",     "UNI/USDT",   "DeFi",     "🦄", "#FF007A"),
    "AAVE-USD":   ("Aave",        "AAVE/USDT",  "DeFi",     "A",  "#B6509E"),
    "LINK-USD":   ("Chainlink",   "LINK/USDT",  "Oracle",   "⬡",  "#2A5ADA"),
    "INJ-USD":    ("Injective",   "INJ/USDT",   "DeFi",     "I",  "#00B4D8"),
    "CRV-USD":    ("Curve",       "CRV/USDT",   "DeFi",     "C",  "#D7263D"),
    "DOGE-USD":   ("Dogecoin",    "DOGE/USDT",  "Meme",     "Ð",  "#C2A633"),
    "SHIB-USD":   ("Shiba Inu",   "SHIB/USDT",  "Meme",     "🐕", "#F02D21"),
    "PEPE-USD":   ("Pepe",        "PEPE/USDT",  "Meme",     "🐸", "#00A550"),
    "WIF-USD":    ("dogwifhat",   "WIF/USDT",   "Meme",     "🎩", "#F0A500"),
    "BONK-USD":   ("Bonk",        "BONK/USDT",  "Meme",     "🐕", "#F5841F"),
    "FLOKI-USD":  ("Floki",       "FLOKI/USDT", "Meme",     "F",  "#F5841F"),
    "MOG-USD":    ("Mog Coin",    "MOG/USDT",   "Meme",     "😼", "#C850C0"),
    "POPCAT-USD": ("Popcat",      "POPCAT/USDT","Meme",     "🐱", "#F7931A"),
}

QUICK_PICKS = {
    "🔥 Popular":   ["BTC-USD","ETH-USD","SOL-USD","BNB-USD","XRP-USD"],
    "😂 Meme Coins":["DOGE-USD","SHIB-USD","PEPE-USD","WIF-USD","BONK-USD","FLOKI-USD","MOG-USD"],
    "⚡ DeFi":      ["UNI-USD","AAVE-USD","LINK-USD","INJ-USD","CRV-USD"],
    "🌐 Layer-1/2": ["ADA-USD","AVAX-USD","NEAR-USD","SUI-USD","ARB-USD","OP-USD"],
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def fmt(p: float) -> str:
    if p >= 1000:  return f"${p:,.2f}"
    if p >= 1:     return f"${p:.4f}"
    if p >= 0.001: return f"${p:.6f}"
    return f"${p:.8f}"

def calc_rsi(series: pd.Series, period=14) -> float:
    delta = series.diff()
    gain  = delta.where(delta > 0, 0.0).rolling(period).mean()
    loss  = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
    rs    = gain / loss
    val   = 100 - (100 / (1 + rs))
    return float(val.iloc[-1]) if len(val) > 0 else 50.0

def get_live_price(symbol: str):
    try:
        info = yf.Ticker(symbol).fast_info
        lp = getattr(info, "last_price", None)
        if lp: return float(lp)
    except:
        pass
    return None

def analyze(symbol: str):
    symbol = symbol.upper().strip()
    if "-" not in symbol:
        symbol += "-USD"

    df = yf.Ticker(symbol).history(period="3mo")
    if df.empty or len(df) < 22:
        return None, symbol

    df["SMA20"] = df["Close"].rolling(20).mean()
    df["STD20"] = df["Close"].rolling(20).std()
    df.dropna(subset=["SMA20", "STD20"], inplace=True)

    cp  = float(df["Close"].iloc[-1])
    sma = float(df["SMA20"].iloc[-1])
    std = float(df["STD20"].iloc[-1])
    rsi = calc_rsi(df["Close"])

    live       = get_live_price(symbol) or cp
    prev_close = float(df["Close"].iloc[-2]) if len(df) > 1 else live
    pct_change = (live - prev_close) / prev_close * 100 if prev_close else 0

    if cp > sma and rsi < 70:
        sig, sig_type = "LONG / BUY ▲", "buy"
        sl = cp - 1.5 * std;  tp = cp + 3.0 * std
    elif cp < sma and rsi > 30:
        sig, sig_type = "SHORT / SELL ▼", "sell"
        sl = cp + 1.5 * std;  tp = cp - 3.0 * std
    else:
        sig, sig_type = "HOLD / WAIT ◆", "hold"
        sl = cp - 1.5 * std;  tp = cp + 3.0 * std

    rr     = abs(tp - cp) / abs(sl - cp) if abs(sl - cp) > 0 else 0
    tp_pct = (tp - cp) / cp * 100
    sl_pct = (sl - cp) / cp * 100
    trend  = "Bullish" if cp > sma else "Bearish"
    high3m = float(df["High"].max())
    low3m  = float(df["Low"].min())

    meta = COIN_META.get(symbol, (symbol, symbol, "Crypto", "●", "#848E9C"))
    return {
        "symbol": symbol, "name": meta[0], "pair": meta[1],
        "category": meta[2], "icon": meta[3], "color": meta[4],
        "live": live, "cp": cp, "pct_change": pct_change,
        "prev_close": prev_close,
        "tp": tp, "sl": sl, "rsi": rsi, "sma": sma, "std": std,
        "sig": sig, "sig_type": sig_type, "rr": rr,
        "tp_pct": tp_pct, "sl_pct": sl_pct, "trend": trend,
        "high3m": high3m, "low3m": low3m,
        "df": df,
    }, symbol

def rsi_series(closes):
    vals = []
    for i in range(len(closes)):
        if i < 15:
            vals.append(np.nan)
        else:
            sub = pd.Series(closes[max(0, i-28):i+1])
            vals.append(calc_rsi(sub))
    return vals

def build_chart(d):
    df    = d["df"].iloc[-60:]
    UP    = "#0ECB81"; DN = "#F6465D"; BG = "#0B0E11"; SBG = "#161A1E"; GRID = "#2B3139"

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        vertical_spacing=0.015, row_heights=[0.62, 0.19, 0.19],
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        increasing_fillcolor=UP, increasing_line_color=UP,
        decreasing_fillcolor=DN, decreasing_line_color=DN,
        name="Price", line_width=1,
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["SMA20"],
        line=dict(color="#F0B90B", width=1.5, dash="dot"),
        name="SMA-20",
    ), row=1, col=1)

    for yval, clr, lbl in [
        (d["tp"], UP,       f"TP {fmt(d['tp'])}"),
        (d["sl"], DN,       f"SL {fmt(d['sl'])}"),
        (d["cp"], "#848E9C",f"Entry {fmt(d['cp'])}"),
    ]:
        fig.add_hline(y=yval, line_dash="dash", line_color=clr, line_width=1,
                      annotation_text=lbl, annotation_font_color=clr,
                      annotation_font_size=10, row=1, col=1)

    # Volume
    vol_colors = [UP if c >= o else DN for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"], marker_color=vol_colors,
        marker_line_width=0, name="Volume", opacity=0.55,
    ), row=2, col=1)

    # RSI
    rsi_vals = rsi_series(df["Close"].values)
    fig.add_trace(go.Scatter(
        x=df.index, y=rsi_vals,
        line=dict(color="#C850C0", width=1.5),
        fill="tozeroy", fillcolor="rgba(200,80,192,0.06)",
        name="RSI",
    ), row=3, col=1)
    fig.add_hrect(y0=30, y1=70, row=3, col=1,
                  fillcolor="rgba(255,255,255,0.03)", line_width=0)
    for lvl, c in [(30, UP), (70, DN)]:
        fig.add_hline(y=lvl, line_color=c, line_width=0.8,
                      line_dash="dot", row=3, col=1)

    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=SBG,
        font=dict(color="#848E9C", family="IBM Plex Mono", size=10),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", y=1.03, x=0,
                    bgcolor="rgba(0,0,0,0)",
                    font=dict(size=10, color="#848E9C")),
        margin=dict(l=0, r=72, t=8, b=0),
        height=550,
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#1E2329", bordercolor="#2B3139",
                        font=dict(color="#EAECEF", family="IBM Plex Mono")),
    )
    ax = dict(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID,
              tickfont=dict(size=9, color="#474D57"))
    fig.update_xaxes(**ax)
    fig.update_yaxes(**ax)
    fig.update_yaxes(tickprefix="$", row=1, col=1)
    return fig

# ── Session ────────────────────────────────────────────────────────────────────
for k, v in [("history", []), ("result", None), ("skey", 0)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── NavBar ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
  <div class="navbar-logo">📊 CryptoSignal</div>
  <div class="navbar-link active" style="margin-left:16px">Markets</div>
  <div class="navbar-link">Signals</div>
  <div class="navbar-link">Portfolio</div>
  <span class="live-badge">● LIVE DATA</span>
</div>
""", unsafe_allow_html=True)

# ── Ticker ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ticker-tape">
  <div class="ticker-item"><span class="ticker-sym">BTC/USDT</span><span class="ticker-up">Loading...</span></div>
  <div class="ticker-item"><span class="ticker-sym">ETH/USDT</span></div>
  <div class="ticker-item"><span class="ticker-sym">SOL/USDT</span></div>
  <div class="ticker-item"><span class="ticker-sym">DOGE/USDT</span></div>
  <div class="ticker-item"><span class="ticker-sym">PEPE/USDT</span></div>
  <div style="margin-left:auto;color:#2B3139;font-size:0.68rem">⚠ Not financial advice &nbsp;|&nbsp; Data: Yahoo Finance</div>
</div>
""", unsafe_allow_html=True)

# ── Main Content ───────────────────────────────────────────────────────────────
st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

# Header
st.markdown("""
<div style="padding:16px 0 14px;border-bottom:1px solid #2B3139;margin-bottom:18px;display:flex;align-items:center;justify-content:space-between;">
  <div>
    <div style="font-size:1.2rem;font-weight:700;color:#EAECEF">📈 Signal Scanner</div>
    <div style="font-size:0.78rem;color:#474D57;margin-top:3px">RSI + SMA-20 strategy · Auto TP/SL · 3-month chart · Real-time price</div>
  </div>
  <div style="font-size:0.72rem;color:#474D57;font-family:IBM Plex Mono,monospace">{}</div>
</div>
""".format(datetime.now().strftime("%d %b %Y  %H:%M")), unsafe_allow_html=True)

# Search
c1, c2 = st.columns([5.5, 1])
with c1:
    sym_inp = st.text_input(
        "sym", label_visibility="collapsed",
        placeholder="Coin name ya symbol likhein:  BTC  •  ETH  •  DOGE  •  PEPE  •  SOL...",
        key=f"inp_{st.session_state.skey}"
    )
with c2:
    clicked = st.button("Analyze ▶", use_container_width=True)

# Quick Picks
for cat, coins in QUICK_PICKS.items():
    st.markdown(f'<div class="section-title">{cat}</div>', unsafe_allow_html=True)
    cols = st.columns(len(coins))
    for i, coin in enumerate(coins):
        short = coin.replace("-USD", "")
        if cols[i].button(short, key=f"q_{coin}"):
            sym_inp = coin; clicked = True

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
st.markdown("<hr style='border-color:#2B3139'>", unsafe_allow_html=True)

# ── Run Analysis ───────────────────────────────────────────────────────────────
if clicked and sym_inp:
    with st.spinner(f"Fetching {sym_inp.upper()} data..."):
        try:
            data, rsym = analyze(sym_inp)
            if data is None:
                st.markdown(
                    f"<div style='background:#F6465D18;border:1px solid #F6465D;border-radius:6px;"
                    f"padding:12px 16px;color:#F6465D;font-size:0.84rem;font-family:IBM Plex Mono,monospace'>"
                    f"❌  &nbsp; <b>{rsym}</b> ka data nahi mila. "
                    f"Sahi symbol likhein jaise BTC, DOGE-USD, SOL</div>",
                    unsafe_allow_html=True)
            else:
                st.session_state.result = data
                st.session_state.history.insert(0, {
                    "pair": data["pair"], "sym": rsym,
                    "sig": data["sig_type"], "live": data["live"],
                    "pct": data["pct_change"],
                    "tp": data["tp"], "sl": data["sl"],
                    "time": datetime.now().strftime("%H:%M:%S"),
                })
                st.session_state.history = st.session_state.history[:8]
                st.session_state.skey += 1
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# ── Show Result ────────────────────────────────────────────────────────────────
if st.session_state.result:
    d = st.session_state.result
    pu       = d["pct_change"] >= 0
    pct_str  = f"{'+'if pu else ''}{d['pct_change']:.2f}%  (24h)"
    pct_cls  = "price-up" if pu else "price-dn"
    sig_cls  = {"buy": "sig-buy", "sell": "sig-sell", "hold": "sig-hold"}[d["sig_type"]]

    # Price Header
    st.markdown(f"""
    <div class="price-header">
      <div style="display:flex;align-items:center;gap:14px">
        <div class="ph-icon" style="background:{d['color']}22;color:{d['color']}">{d['icon']}</div>
        <div>
          <div class="coin-name-big">{d['name']} <span style="color:#474D57;font-size:0.8rem;font-weight:400">{d['category']}</span></div>
          <div class="coin-pair-txt">{d['pair']}</div>
        </div>
      </div>
      <div>
        <div style="font-size:0.65rem;color:#474D57;font-family:IBM Plex Mono,monospace;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:5px">Current Market Price</div>
        <div class="live-price-num">{fmt(d['live'])}</div>
        <div class="{pct_cls}">{pct_str}</div>
      </div>
      <div>
        <div style="font-size:0.65rem;color:#474D57;font-family:IBM Plex Mono,monospace;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px">AI Signal</div>
        <div class="{sig_cls}">{d['sig']}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    rsi_c = "y" if 30<=d['rsi']<=70 else ("g" if d['rsi']<30 else "r")
    rr_c  = "g" if d['rr']>=2 else ("y" if d['rr']>=1 else "r")
    tp_c  = "g"; sl_c = "r"

    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-card">
        <div class="stat-lbl">Entry Price</div>
        <div class="stat-num">{fmt(d['cp'])}</div>
        <div class="stat-sub">Last close</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Take Profit ✦</div>
        <div class="stat-num {tp_c}">{fmt(d['tp'])}</div>
        <div class="stat-sub">+{abs(d['tp_pct']):.1f}% from entry</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Stop Loss ✦</div>
        <div class="stat-num {sl_c}">{fmt(d['sl'])}</div>
        <div class="stat-sub">{d['sl_pct']:+.1f}% from entry</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">RSI (14)</div>
        <div class="stat-num {rsi_c}">{d['rsi']:.1f}</div>
        <div class="stat-sub">{'Oversold ↑' if d['rsi']<30 else 'Overbought ↓' if d['rsi']>70 else 'Neutral zone'}</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Risk / Reward</div>
        <div class="stat-num {rr_c}">1 : {d['rr']:.2f}</div>
        <div class="stat-sub">{d['trend']} trend</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">3M High / Low</div>
        <div class="stat-num" style="font-size:0.78rem">{fmt(d['high3m'])}</div>
        <div class="stat-sub">{fmt(d['low3m'])} low</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Insight
    if d["sig_type"] == "buy":
        ins = (f"Price <b>{fmt(d['cp'])}</b> SMA-20 (<b>{fmt(d['sma'])}</b>) se upar hai. "
               f"RSI <b>{d['rsi']:.0f}</b> — overbought nahi, bullish momentum strong hai. "
               f"TP target <b>{fmt(d['tp'])}</b> (+{abs(d['tp_pct']):.1f}%), "
               f"SL <b>{fmt(d['sl'])}</b> ({abs(d['sl_pct']):.1f}% neeche) pe rakhen.")
    elif d["sig_type"] == "sell":
        ins = (f"Price <b>{fmt(d['cp'])}</b> SMA-20 (<b>{fmt(d['sma'])}</b>) se neeche hai. "
               f"RSI <b>{d['rsi']:.0f}</b> — bearish structure confirm. "
               f"SL <b>{fmt(d['sl'])}</b> pe lazmi rakhen. TP: <b>{fmt(d['tp'])}</b>.")
    else:
        ins = (f"RSI <b>{d['rsi']:.0f}</b> neutral zone (30–70) mein hai aur price "
               f"SMA-20 (<b>{fmt(d['sma'])}</b>) ke paas hai. Clear direction abhi nahi — "
               f"confirmation ka wait karen. Daily close dekh ke entry lena safer hoga.")

    st.markdown(f'<div class="insight-box">💡 &nbsp; {ins}</div>', unsafe_allow_html=True)

    # Chart
    st.plotly_chart(build_chart(d), use_container_width=True)

# ── History ────────────────────────────────────────────────────────────────────
if st.session_state.history:
    rows = ""
    for h in st.session_state.history:
        pu   = h["pct"] >= 0
        pc   = "#0ECB81" if pu else "#F6465D"
        sc   = "#0ECB81" if h["sig"]=="buy" else "#F6465D" if h["sig"]=="sell" else "#F0B90B"
        slbl = "BUY ▲" if h["sig"]=="buy" else "SELL ▼" if h["sig"]=="sell" else "HOLD ◆"
        rows += (
            f"<div class='hist-row-item'>"
            f"<span style='color:#EAECEF;font-weight:600'>{h['pair']}</span>"
            f"<span style='color:{pc}'>{h['pct']:+.2f}%</span>"
            f"<span style='color:#848E9C'>{fmt(h['live'])}</span>"
            f"<span style='color:{sc};font-weight:700'>{slbl}</span>"
            f"<span style='color:#474D57'>{h['time']}</span>"
            f"</div>"
        )
    st.markdown(
        f"<div class='hist-wrap'>"
        f"<div class='hist-head'><span>Pair</span><span>24h</span><span>Price</span><span>Signal</span><span>Time</span></div>"
        f"{rows}</div>",
        unsafe_allow_html=True
    )

st.markdown("""
<div class="footer">
  ⚠ &nbsp; Educational purposes only — not financial advice &nbsp;|&nbsp; Data: Yahoo Finance &nbsp;|&nbsp; Strategy: RSI-14 + SMA-20
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
