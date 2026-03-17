import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CryptoSignal Bot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
#  CSS — Binance exact dark theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], [class*="st-"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    background-color: #0B0E11 !important;
    color: #EAECEF !important;
}
.main, .block-container {
    background-color: #0B0E11 !important;
    padding: 0 !important;
    max-width: 100% !important;
}
section[data-testid="stSidebar"]  { display: none !important; }
div[data-testid="stDecoration"]   { display: none !important; }
#MainMenu, footer, header         { visibility: hidden !important; }
.stDeployButton                   { display: none !important; }

/* ── Streamlit element resets ── */
div[data-testid="stVerticalBlock"] > div { background: transparent !important; }
div[data-testid="stHorizontalBlock"] { gap: 6px !important; align-items: flex-start !important; }

/* ── Spinner ── */
div[data-testid="stSpinner"] > div { border-top-color: #F0B90B !important; }

/* ── Alert / error box ── */
div[data-testid="stAlert"] {
    background: #F6465D18 !important;
    border: 1px solid #F6465D !important;
    border-radius: 6px !important;
    color: #F6465D !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
}

/* ── Search input ── */
div[data-testid="stTextInput"] label { display: none !important; }
div[data-testid="stTextInput"] input {
    background: #1E2329 !important;
    border: 1px solid #2B3139 !important;
    border-radius: 6px !important;
    color: #EAECEF !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.88rem !important;
    height: 44px !important;
    box-shadow: none !important;
    transition: border-color .2s !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #F0B90B !important;
    box-shadow: 0 0 0 2px #F0B90B22 !important;
}
div[data-testid="stTextInput"] input::placeholder { color: #474D57 !important; }

/* ── Analyze button (full-width yellow) ── */
div[data-testid="stButton"]:has(button[kind="primary"]) button,
.analyze-btn button {
    background: #F0B90B !important;
    color: #1E2329 !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    border: none !important;
    border-radius: 6px !important;
    height: 44px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    width: 100% !important;
}
div[data-testid="stButton"]:has(button[kind="primary"]) button:hover { background: #FFD35A !important; }

/* ── Coin chip buttons — compact dark ── */
button[kind="secondary"] {
    background: #1E2329 !important;
    color: #848E9C !important;
    border: 1px solid #2B3139 !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    padding: 2px 8px !important;
    height: 30px !important;
    white-space: nowrap !important;
    width: 100% !important;
    transition: all .15s !important;
}
button[kind="secondary"]:hover {
    border-color: #F0B90B !important;
    color: #F0B90B !important;
    background: #F0B90B10 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar            { width: 5px; height: 5px; }
::-webkit-scrollbar-track      { background: #161A1E; }
::-webkit-scrollbar-thumb      { background: #2B3139; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover{ background: #474D57; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  FIX 2 — Correct yfinance symbols for small-cap / meme coins
#  Many meme coins need their yfinance-specific ID (not just TICKER-USD)
# ─────────────────────────────────────────────────────────────────────────────
SYMBOL_MAP = {
    # symbol user sees  →  yfinance symbol
    "BTC-USD":     "BTC-USD",
    "ETH-USD":     "ETH-USD",
    "SOL-USD":     "SOL-USD",
    "BNB-USD":     "BNB-USD",
    "XRP-USD":     "XRP-USD",
    "ADA-USD":     "ADA-USD",
    "AVAX-USD":    "AVAX-USD",
    "DOT-USD":     "DOT-USD",
    "NEAR-USD":    "NEAR-USD",
    "SUI-USD":     "SUI20947-USD",   # SUI correct yfinance ID
    "APT-USD":     "APT21794-USD",   # Aptos correct ID
    "LTC-USD":     "LTC-USD",
    "TRX-USD":     "TRX-USD",
    "MATIC-USD":   "MATIC-USD",
    "OP-USD":      "OP-USD",
    "ARB-USD":     "ARB11841-USD",
    "UNI-USD":     "UNI7083-USD",
    "AAVE-USD":    "AAVE-USD",
    "LINK-USD":    "LINK-USD",
    "INJ-USD":     "INJ-USD",
    "CRV-USD":     "CRV-USD",
    # Meme coins — these need correct IDs
    "DOGE-USD":    "DOGE-USD",
    "SHIB-USD":    "SHIB-USD",
    "PEPE-USD":    "PEPE24478-USD",  # FIX: correct yfinance ID for Pepe
    "WIF-USD":     "WIF-USD",
    "BONK-USD":    "BONK-USD",
    "FLOKI-USD":   "FLOKI-USD",
    "MOG-USD":     "MOG22421-USD",   # FIX: Mog Coin correct ID
    "POPCAT-USD":  "POPCAT-USD",
}

COIN_META = {
    "BTC-USD":    ("Bitcoin",    "BTC/USDT",    "Layer-1",  "₿",  "#F7931A"),
    "ETH-USD":    ("Ethereum",   "ETH/USDT",    "Layer-1",  "Ξ",  "#627EEA"),
    "SOL-USD":    ("Solana",     "SOL/USDT",    "Layer-1",  "◎",  "#9945FF"),
    "BNB-USD":    ("BNB",        "BNB/USDT",    "Layer-1",  "B",  "#F0B90B"),
    "XRP-USD":    ("XRP",        "XRP/USDT",    "Layer-1",  "✕",  "#00AAE4"),
    "ADA-USD":    ("Cardano",    "ADA/USDT",    "Layer-1",  "₳",  "#0033AD"),
    "AVAX-USD":   ("Avalanche",  "AVAX/USDT",   "Layer-1",  "A",  "#E84142"),
    "DOT-USD":    ("Polkadot",   "DOT/USDT",    "Layer-1",  "●",  "#E6007A"),
    "NEAR-USD":   ("NEAR",       "NEAR/USDT",   "Layer-1",  "N",  "#00C08B"),
    "SUI-USD":    ("Sui",        "SUI/USDT",    "Layer-1",  "S",  "#4DA2FF"),
    "APT-USD":    ("Aptos",      "APT/USDT",    "Layer-1",  "A",  "#24D4A8"),
    "LTC-USD":    ("Litecoin",   "LTC/USDT",    "Layer-1",  "Ł",  "#BFBBBB"),
    "TRX-USD":    ("TRON",       "TRX/USDT",    "Layer-1",  "T",  "#FF0013"),
    "MATIC-USD":  ("Polygon",    "MATIC/USDT",  "Layer-2",  "M",  "#8247E5"),
    "OP-USD":     ("Optimism",   "OP/USDT",     "Layer-2",  "O",  "#FF0420"),
    "ARB-USD":    ("Arbitrum",   "ARB/USDT",    "Layer-2",  "A",  "#28A0F0"),
    "UNI-USD":    ("Uniswap",    "UNI/USDT",    "DeFi",     "🦄", "#FF007A"),
    "AAVE-USD":   ("Aave",       "AAVE/USDT",   "DeFi",     "A",  "#B6509E"),
    "LINK-USD":   ("Chainlink",  "LINK/USDT",   "Oracle",   "⬡",  "#2A5ADA"),
    "INJ-USD":    ("Injective",  "INJ/USDT",    "DeFi",     "I",  "#00B4D8"),
    "CRV-USD":    ("Curve",      "CRV/USDT",    "DeFi",     "C",  "#D7263D"),
    "DOGE-USD":   ("Dogecoin",   "DOGE/USDT",   "Meme",     "Ð",  "#C2A633"),
    "SHIB-USD":   ("Shiba Inu",  "SHIB/USDT",   "Meme",     "🐕", "#F02D21"),
    "PEPE-USD":   ("Pepe",       "PEPE/USDT",   "Meme",     "🐸", "#00A550"),
    "WIF-USD":    ("dogwifhat",  "WIF/USDT",    "Meme",     "🎩", "#F0A500"),
    "BONK-USD":   ("Bonk",       "BONK/USDT",   "Meme",     "🐕", "#F5841F"),
    "FLOKI-USD":  ("Floki",      "FLOKI/USDT",  "Meme",     "F",  "#F5841F"),
    "MOG-USD":    ("Mog Coin",   "MOG/USDT",    "Meme",     "😼", "#C850C0"),
    "POPCAT-USD": ("Popcat",     "POPCAT/USDT", "Meme",     "🐱", "#F7931A"),
}

# FIX 2 — Compact rows of chips (not st.columns spread across full width)
QUICK_PICKS = {
    "🔥 Popular":    ["BTC-USD","ETH-USD","SOL-USD","BNB-USD","XRP-USD"],
    "😂 Meme Coins": ["DOGE-USD","SHIB-USD","PEPE-USD","WIF-USD","BONK-USD","FLOKI-USD","MOG-USD"],
    "⚡ DeFi":       ["UNI-USD","AAVE-USD","LINK-USD","INJ-USD","CRV-USD"],
    "🌐 Layer-1/2":  ["ADA-USD","AVAX-USD","NEAR-USD","SUI-USD","ARB-USD","OP-USD"],
}

# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────
def fmt(p: float) -> str:
    if p is None: return "N/A"
    if p >= 1000:  return f"${p:,.2f}"
    if p >= 1:     return f"${p:.4f}"
    if p >= 0.001: return f"${p:.6f}"
    return f"${p:.8f}"

def calc_rsi(series: pd.Series, period: int = 14) -> float:
    if len(series) < period + 1:
        return 50.0
    delta = series.diff().dropna()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, np.nan)
    rsi   = 100 - (100 / (1 + rs))
    v = rsi.dropna()
    return float(v.iloc[-1]) if len(v) > 0 else 50.0

def get_live_price(yf_symbol: str) -> float | None:
    """Try fast_info first, fallback to last close."""
    try:
        fi = yf.Ticker(yf_symbol).fast_info
        lp = getattr(fi, "last_price", None)
        if lp and not np.isnan(float(lp)):
            return float(lp)
    except Exception:
        pass
    return None

def normalize_input(raw: str) -> str:
    """Turn user input like 'btc' or 'PEPE' into canonical key like 'BTC-USD'."""
    s = raw.upper().strip()
    if not s:
        return ""
    if "-USD" not in s:
        s = s + "-USD"
    return s

def fetch_data(canonical: str):
    """
    canonical = key like 'PEPE-USD'
    Returns (df, yf_symbol) or raises ValueError.
    """
    yf_sym = SYMBOL_MAP.get(canonical, canonical)
    df = yf.Ticker(yf_sym).history(period="3mo")
    if df.empty or len(df) < 22:
        # last fallback: try the raw symbol
        if yf_sym != canonical:
            df = yf.Ticker(canonical).history(period="3mo")
            if not df.empty and len(df) >= 22:
                return df, canonical
        raise ValueError(f"Data nahi mila: '{canonical}'. Symbol check karein.")
    return df, yf_sym

def analyze(raw_input: str):
    canonical = normalize_input(raw_input)
    if not canonical:
        return None, ""

    df, yf_sym = fetch_data(canonical)   # raises ValueError on failure

    df["SMA20"] = df["Close"].rolling(20).mean()
    df["STD20"]  = df["Close"].rolling(20).std()
    df.dropna(subset=["SMA20", "STD20"], inplace=True)

    cp   = float(df["Close"].iloc[-1])
    sma  = float(df["SMA20"].iloc[-1])
    std  = float(df["STD20"].iloc[-1])
    rsi  = calc_rsi(df["Close"])

    live = get_live_price(yf_sym) or cp
    prev = float(df["Close"].iloc[-2]) if len(df) > 1 else cp
    pct  = (live - prev) / prev * 100 if prev else 0.0

    if cp > sma and rsi < 70:
        sig, stype = "LONG / BUY  ▲", "buy"
        sl = cp - 1.5 * std;  tp = cp + 3.0 * std
    elif cp < sma and rsi > 30:
        sig, stype = "SHORT / SELL  ▼", "sell"
        sl = cp + 1.5 * std;  tp = cp - 3.0 * std
    else:
        sig, stype = "HOLD / WAIT  ◆", "hold"
        sl = cp - 1.5 * std;  tp = cp + 3.0 * std

    rr     = abs(tp - cp) / abs(sl - cp) if abs(sl - cp) > 0 else 0
    tp_pct = (tp - cp) / cp * 100
    sl_pct = (sl - cp) / cp * 100
    trend  = "Bullish" if cp > sma else "Bearish"
    high3m = float(df["High"].max())
    low3m  = float(df["Low"].min())

    meta = COIN_META.get(canonical, (canonical, canonical, "Crypto", "●", "#848E9C"))
    return {
        "key": canonical, "symbol": yf_sym,
        "name": meta[0], "pair": meta[1], "category": meta[2],
        "icon": meta[3], "color": meta[4],
        "live": live, "cp": cp, "pct": pct, "prev": prev,
        "tp": tp, "sl": sl, "rsi": rsi, "sma": sma, "std": std,
        "sig": sig, "stype": stype,
        "rr": rr, "tp_pct": tp_pct, "sl_pct": sl_pct,
        "trend": trend, "high3m": high3m, "low3m": low3m,
        "df": df,
    }

def rsi_rolling(closes: np.ndarray) -> list:
    out = []
    for i in range(len(closes)):
        if i < 15:
            out.append(np.nan)
        else:
            out.append(calc_rsi(pd.Series(closes[max(0, i-28):i+1])))
    return out

def build_chart(d: dict):
    df   = d["df"].iloc[-60:]
    UP   = "#0ECB81"; DN = "#F6465D"
    BG   = "#0B0E11"; SBG = "#161A1E"; GRID = "#2B3139"

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        vertical_spacing=0.015,
        row_heights=[0.62, 0.19, 0.19],
    )

    # — Candlestick —
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
        (d["tp"], UP,        f"TP  {fmt(d['tp'])}"),
        (d["sl"], DN,        f"SL  {fmt(d['sl'])}"),
        (d["cp"], "#848E9C", f"Entry  {fmt(d['cp'])}"),
    ]:
        fig.add_hline(y=yval, line_dash="dash", line_color=clr, line_width=1,
                      annotation_text=lbl, annotation_font_color=clr,
                      annotation_font_size=10, row=1, col=1)

    # — Volume —
    vol_c = [UP if c >= o else DN for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"],
        marker_color=vol_c, marker_line_width=0,
        name="Volume", opacity=0.55,
    ), row=2, col=1)

    # — RSI —
    fig.add_trace(go.Scatter(
        x=df.index, y=rsi_rolling(df["Close"].values),
        line=dict(color="#C850C0", width=1.5),
        fill="tozeroy", fillcolor="rgba(200,80,192,0.06)",
        name="RSI",
    ), row=3, col=1)
    fig.add_hrect(y0=30, y1=70, row=3, col=1,
                  fillcolor="rgba(255,255,255,0.03)", line_width=0)
    for lvl, c in [(30, UP), (70, DN)]:
        fig.add_hline(y=lvl, line_color=c, line_width=0.8,
                      line_dash="dot", row=3, col=1)

    ax = dict(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID,
              tickfont=dict(size=9, color="#474D57"))
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
    fig.update_xaxes(**ax)
    fig.update_yaxes(**ax)
    fig.update_yaxes(tickprefix="$", row=1, col=1)
    return fig

# ─────────────────────────────────────────────────────────────────────────────
#  Session state
# ─────────────────────────────────────────────────────────────────────────────
for k, v in [("history", []), ("result", None), ("skey", 0)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
#  HTML helpers
# ─────────────────────────────────────────────────────────────────────────────
def H(html): st.markdown(html, unsafe_allow_html=True)

def card(label, value, sub="", vc=""):
    color = {"g":"#0ECB81","r":"#F6465D","y":"#F0B90B"}.get(vc,"#EAECEF")
    return f"""
    <div style="background:#161A1E;border:1px solid #2B3139;border-radius:6px;padding:12px 14px;">
      <div style="font-size:.67rem;color:#474D57;text-transform:uppercase;letter-spacing:.05em;font-weight:600;margin-bottom:6px">{label}</div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:.9rem;font-weight:600;color:{color}">{value}</div>
      <div style="font-size:.65rem;color:#474D57;font-family:'IBM Plex Mono',monospace;margin-top:3px">{sub}</div>
    </div>"""

# ─────────────────────────────────────────────────────────────────────────────
#  NAVBAR
# ─────────────────────────────────────────────────────────────────────────────
H("""
<div style="background:#161A1E;border-bottom:1px solid #2B3139;padding:0 24px;height:56px;display:flex;align-items:center;gap:0;position:sticky;top:0;z-index:99">
  <div style="font-size:1.15rem;font-weight:700;color:#F0B90B;display:flex;align-items:center;gap:8px;margin-right:32px">
    📊 CryptoSignal
  </div>
  <div style="display:flex;height:56px">
    <span style="font-size:.82rem;font-weight:600;color:#EAECEF;padding:0 16px;display:flex;align-items:center;border-bottom:2px solid #F0B90B">Markets</span>
    <span style="font-size:.82rem;color:#474D57;padding:0 16px;display:flex;align-items:center;border-bottom:2px solid transparent">Signals</span>
    <span style="font-size:.82rem;color:#474D57;padding:0 16px;display:flex;align-items:center;border-bottom:2px solid transparent">Portfolio</span>
  </div>
  <div style="margin-left:auto;background:#0ECB8118;border:1px solid #0ECB81;color:#0ECB81;font-size:.7rem;font-weight:600;padding:3px 10px;border-radius:4px;font-family:'IBM Plex Mono',monospace;letter-spacing:.04em">● LIVE DATA</div>
</div>
""")

# ─────────────────────────────────────────────────────────────────────────────
#  TICKER TAPE
# ─────────────────────────────────────────────────────────────────────────────
H("""
<div style="background:#161A1E;border-bottom:1px solid #2B3139;padding:0 24px;height:32px;display:flex;align-items:center;gap:28px;font-family:'IBM Plex Mono',monospace;font-size:.7rem;overflow:hidden">
  <span style="color:#474D57">BTC/USDT</span>
  <span style="color:#474D57">ETH/USDT</span>
  <span style="color:#474D57">SOL/USDT</span>
  <span style="color:#474D57">DOGE/USDT</span>
  <span style="color:#474D57">PEPE/USDT</span>
  <span style="margin-left:auto;color:#2B3139">Data: Yahoo Finance  |  Not financial advice</span>
</div>
""")

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN CONTENT WRAPPER
# ─────────────────────────────────────────────────────────────────────────────
H('<div style="padding:20px 24px 40px">')

# Page header
H(f"""
<div style="padding-bottom:14px;border-bottom:1px solid #2B3139;margin-bottom:18px;display:flex;align-items:center;justify-content:space-between">
  <div>
    <div style="font-size:1.15rem;font-weight:700;color:#EAECEF">📈 Signal Scanner</div>
    <div style="font-size:.76rem;color:#474D57;margin-top:3px">RSI-14 + SMA-20  ·  Auto TP/SL  ·  3-month chart  ·  Real-time price</div>
  </div>
  <div style="font-size:.7rem;color:#2B3139;font-family:'IBM Plex Mono',monospace">{datetime.now().strftime('%d %b %Y  %H:%M')}</div>
</div>
""")

# ─────────────────────────────────────────────────────────────────────────────
#  SEARCH BAR
# ─────────────────────────────────────────────────────────────────────────────
c_inp, c_btn = st.columns([5.5, 1])
with c_inp:
    sym_inp = st.text_input(
        "sym", label_visibility="collapsed",
        placeholder="Symbol likhein:  BTC  •  ETH  •  DOGE  •  PEPE  •  SOL  •  ya koi bhi coin ...",
        key=f"inp_{st.session_state.skey}",
    )
with c_btn:
    clicked = st.button("Analyze ▶", type="primary", use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
#  COIN CHIP BUTTONS — pure HTML flexbox (no st.columns = no forced spacing)
#  Each chip is a Streamlit button inside a tight flex container via CSS inject
# ─────────────────────────────────────────────────────────────────────────────

# Check if a chip was clicked via query params
qp = st.query_params
if "chip" in qp:
    sym_inp = qp["chip"]
    clicked = True

for cat, coins in QUICK_PICKS.items():
    H(f"<div style='font-size:.68rem;color:#474D57;font-weight:600;letter-spacing:.05em;text-transform:uppercase;margin:12px 0 5px'>{cat}</div>")
    # Build all chips as one flex row — pure HTML, no column spreading
    chips_html = "<div style='display:flex;flex-wrap:wrap;gap:6px;margin-bottom:4px'>"
    for coin in coins:
        short = coin.replace("-USD", "")
        chips_html += (
            f"<a href='?chip={coin}' target='_self' "
            f"style='display:inline-flex;align-items:center;justify-content:center;"
            f"background:#1E2329;color:#848E9C;border:1px solid #2B3139;"
            f"border-radius:4px;font-family:IBM Plex Mono,monospace;font-size:.76rem;"
            f"font-weight:500;padding:5px 14px;text-decoration:none;white-space:nowrap;"
            f"transition:all .15s;cursor:pointer' "
            f"onmouseover=\"this.style.borderColor='#F0B90B';this.style.color='#F0B90B';this.style.background='#F0B90B10'\" "
            f"onmouseout=\"this.style.borderColor='#2B3139';this.style.color='#848E9C';this.style.background='#1E2329'\">"
            f"{short}</a>"
        )
    chips_html += "</div>"
    H(chips_html)

H("<div style='height:10px'></div>")
H("<hr style='border:none;border-top:1px solid #2B3139;margin:4px 0 18px'>")

# ─────────────────────────────────────────────────────────────────────────────
#  RUN ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
if clicked and sym_inp:
    sym_inp = sym_inp.strip()
    # clear chip param so back/refresh doesn't re-trigger
    if "chip" in st.query_params:
        st.query_params.clear()
    with st.spinner(f"Fetching {sym_inp.upper()} market data..."):
        try:
            data = analyze(sym_inp)
            if data is None:
                H("<div style='background:#F6465D12;border:1px solid #F6465D40;border-left:3px solid #F6465D;border-radius:6px;padding:11px 16px;color:#F6465D;font-family:IBM Plex Mono,monospace;font-size:.82rem;margin:8px 0'>❌ &nbsp; Symbol empty hai — kuch likhein pehle.</div>")
            else:
                st.session_state.result = data
                st.session_state.history.insert(0, {
                    "pair":  data.get("pair",  data["key"]),
                    "sig":   data.get("stype", "hold"),
                    "live":  data.get("live",  0.0),
                    "pct":   data.get("pct",   0.0),
                    "tp":    data.get("tp",    0.0),
                    "sl":    data.get("sl",    0.0),
                    "time":  datetime.now().strftime("%H:%M:%S"),
                })
                st.session_state.history = st.session_state.history[:8]
                st.session_state.skey += 1
                st.rerun()
        except ValueError as ve:
            H(f"<div style='background:#F6465D12;border:1px solid #F6465D40;border-left:3px solid #F6465D;border-radius:6px;padding:11px 16px;color:#F6465D;font-family:IBM Plex Mono,monospace;font-size:.82rem;margin:8px 0'>❌ &nbsp; {ve}</div>")
        except Exception as ex:
            H(f"<div style='background:#F6465D12;border:1px solid #F6465D40;border-left:3px solid #F6465D;border-radius:6px;padding:11px 16px;color:#F6465D;font-family:IBM Plex Mono,monospace;font-size:.82rem;margin:8px 0'>❌ &nbsp; Error: {ex}</div>")

# ─────────────────────────────────────────────────────────────────────────────
#  RESULT PANEL
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.result:
    d = st.session_state.result
    pu = d["pct"] >= 0
    pct_color = "#0ECB81" if pu else "#F6465D"
    pct_str   = f"{'+'if pu else ''}{d['pct']:.2f}%  (24h)"

    sig_styles = {
        "buy":  ("background:#0ECB8118;border:1px solid #0ECB81;color:#0ECB81",),
        "sell": ("background:#F6465D18;border:1px solid #F6465D;color:#F6465D",),
        "hold": ("background:#F0B90B18;border:1px solid #F0B90B;color:#F0B90B",),
    }
    sig_style = sig_styles.get(d["stype"], sig_styles["hold"])[0]

    # ── Price header ──
    H(f"""
    <div style="background:#161A1E;border:1px solid #2B3139;border-radius:8px;
                padding:18px 22px;margin-bottom:14px;
                display:flex;flex-wrap:wrap;gap:20px;align-items:center;justify-content:space-between">
      <div style="display:flex;align-items:center;gap:14px">
        <div style="width:42px;height:42px;border-radius:50%;background:{d['color']}22;
                    color:{d['color']};font-size:1.3rem;display:flex;align-items:center;justify-content:center">
          {d['icon']}
        </div>
        <div>
          <div style="font-size:1.05rem;font-weight:700;color:#EAECEF">
            {d['name']} <span style="color:#474D57;font-size:.8rem;font-weight:400">{d['category']}</span>
          </div>
          <div style="font-size:.76rem;color:#474D57;font-family:'IBM Plex Mono',monospace">{d['pair']}</div>
        </div>
      </div>
      <div>
        <div style="font-size:.64rem;color:#474D57;font-family:'IBM Plex Mono',monospace;
                    text-transform:uppercase;letter-spacing:.06em;margin-bottom:5px">Current Market Price</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:2rem;font-weight:700;
                    color:#EAECEF;letter-spacing:-.02em;line-height:1">{fmt(d['live'])}</div>
        <div style="color:{pct_color};font-size:.86rem;font-family:'IBM Plex Mono',monospace;
                    font-weight:500;margin-top:4px">{pct_str}</div>
      </div>
      <div>
        <div style="font-size:.64rem;color:#474D57;font-family:'IBM Plex Mono',monospace;
                    text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px">AI Signal</div>
        <div style="{sig_style};font-size:.84rem;font-weight:700;padding:8px 22px;border-radius:4px;
                    letter-spacing:.04em;font-family:'IBM Plex Mono',monospace;display:inline-block">{d['sig']}</div>
      </div>
    </div>
    """)

    # ── Stat cards ──
    rsi_c = "y" if 30 <= d["rsi"] <= 70 else ("g" if d["rsi"] < 30 else "r")
    rr_c  = "g" if d["rr"] >= 2 else ("y" if d["rr"] >= 1 else "r")
    rsi_lbl = "Oversold ↑" if d["rsi"] < 30 else ("Overbought ↓" if d["rsi"] > 70 else "Neutral zone")

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.markdown(card("Entry Price",    fmt(d["cp"]),          "Last close"),            unsafe_allow_html=True)
    c2.markdown(card("Take Profit ✦",  fmt(d["tp"]),          f"+{abs(d['tp_pct']):.1f}% from entry", "g"), unsafe_allow_html=True)
    c3.markdown(card("Stop Loss ✦",    fmt(d["sl"]),          f"{d['sl_pct']:+.1f}% from entry",  "r"), unsafe_allow_html=True)
    c4.markdown(card("RSI (14)",       f"{d['rsi']:.1f}",     rsi_lbl,  rsi_c),        unsafe_allow_html=True)
    c5.markdown(card("Risk / Reward",  f"1 : {d['rr']:.2f}", d["trend"], rr_c),        unsafe_allow_html=True)
    c6.markdown(card("3M High / Low",  fmt(d["high3m"]),      f"Low {fmt(d['low3m'])}"), unsafe_allow_html=True)

    H("<div style='height:10px'></div>")

    # ── Insight ──
    if d["stype"] == "buy":
        ins = (f"Price <b>{fmt(d['cp'])}</b> SMA-20 (<b>{fmt(d['sma'])}</b>) se upar hai. "
               f"RSI <b>{d['rsi']:.0f}</b> — overbought nahi, bullish momentum strong. "
               f"TP target <b>{fmt(d['tp'])}</b> (+{abs(d['tp_pct']):.1f}%), "
               f"SL <b>{fmt(d['sl'])}</b> ({abs(d['sl_pct']):.1f}% neeche) pe rakhen.")
    elif d["stype"] == "sell":
        ins = (f"Price <b>{fmt(d['cp'])}</b> SMA-20 (<b>{fmt(d['sma'])}</b>) se neeche. "
               f"RSI <b>{d['rsi']:.0f}</b> — bearish structure confirm. "
               f"SL <b>{fmt(d['sl'])}</b> pe lazmi rakhen. TP: <b>{fmt(d['tp'])}</b>.")
    else:
        ins = (f"RSI <b>{d['rsi']:.0f}</b> neutral zone (30–70) mein, price SMA (<b>{fmt(d['sma'])}</b>) ke paas. "
               f"Clear direction nahi — confirmation ka wait karen. Volatility: <b>{fmt(d['std'])}</b>.")

    H(f"""<div style="background:#161A1E;border:1px solid #2B3139;border-left:3px solid #F0B90B;
                      border-radius:6px;padding:12px 16px;font-size:.82rem;color:#848E9C;
                      line-height:1.65;margin-bottom:14px">
        💡 &nbsp; {ins}
      </div>""")

    # ── Chart ──
    st.plotly_chart(build_chart(d), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
#  HISTORY TABLE
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.history:
    rows = ""
    for h in st.session_state.history:
        # FIX 1 — safe .get() so old history entries without 'pct' don't crash
        pct_val  = h.get("pct", 0.0)
        live_val = h.get("live", 0.0)
        tp_val   = h.get("tp",   0.0)
        sl_val   = h.get("sl",   0.0)
        sig_val  = h.get("sig",  "hold")
        pair_val = h.get("pair", "—")
        time_val = h.get("time", "—")

        pu  = pct_val >= 0
        pc  = "#0ECB81" if pu else "#F6465D"
        sc  = "#0ECB81" if sig_val=="buy" else "#F6465D" if sig_val=="sell" else "#F0B90B"
        lbl = "BUY ▲"   if sig_val=="buy" else "SELL ▼"  if sig_val=="sell" else "HOLD ◆"

        rows += f"""
        <div style="padding:9px 16px;display:grid;grid-template-columns:1.3fr 1fr 1fr 1fr 1fr;
                    font-size:.8rem;border-bottom:1px solid #2B313940;align-items:center;
                    font-family:'IBM Plex Mono',monospace">
          <span style="color:#EAECEF;font-weight:600">{pair_val}</span>
          <span style="color:{pc}">{pct_val:+.2f}%</span>
          <span style="color:#848E9C">{fmt(live_val)}</span>
          <span style="color:{sc};font-weight:700">{lbl}</span>
          <span style="color:#474D57">{time_val}</span>
        </div>"""

    H(f"""
    <div style="background:#161A1E;border:1px solid #2B3139;border-radius:8px;overflow:hidden;margin-top:20px">
      <div style="background:#1E2329;padding:9px 16px;font-size:.68rem;font-weight:600;color:#474D57;
                  text-transform:uppercase;letter-spacing:.06em;
                  display:grid;grid-template-columns:1.3fr 1fr 1fr 1fr 1fr;border-bottom:1px solid #2B3139">
        <span>Pair</span><span>24h</span><span>Price</span><span>Signal</span><span>Time</span>
      </div>
      {rows}
    </div>""")

H("""
<div style="text-align:center;padding:18px;color:#2B3139;font-size:.7rem;
            border-top:1px solid #2B3139;margin-top:24px;font-family:'IBM Plex Mono',monospace">
  ⚠ &nbsp; Educational purposes only — not financial advice &nbsp;|&nbsp;
  Data: Yahoo Finance &nbsp;|&nbsp; Strategy: RSI-14 + SMA-20
</div>
""")

H('</div>')  # close page-wrap
