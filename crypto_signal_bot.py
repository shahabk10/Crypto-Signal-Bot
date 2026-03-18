import streamlit as st
import yfinance as yf
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import time

# ── Config ─────────────────────────────────────────────────────────────────────
LCW_KEY  = "8be32703-67a3-462b-b161-dd8d6e3e17df"
LCW_BASE = "https://api.livecoinwatch.com"
LCW_HDR  = {"content-type": "application/json", "x-api-key": LCW_KEY}

st.set_page_config(page_title="CryptoSignal", page_icon="📊",
                   layout="wide", initial_sidebar_state="collapsed")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'IBM Plex Sans',sans-serif!important;background:#0B0E11!important;color:#EAECEF!important;}
.main,.block-container{background:#0B0E11!important;padding:0!important;max-width:100%!important;}
section[data-testid="stSidebar"],div[data-testid="stDecoration"],.stDeployButton{display:none!important;}
#MainMenu,footer,header{visibility:hidden!important;}
div[data-testid="stVerticalBlock"]>div{background:transparent!important;}
div[data-testid="stTextInput"] label{display:none!important;}
div[data-testid="stTextInput"] input{background:#1E2329!important;border:1px solid #2B3139!important;border-radius:6px!important;color:#EAECEF!important;font-family:'IBM Plex Mono',monospace!important;font-size:.88rem!important;height:44px!important;box-shadow:none!important;}
div[data-testid="stTextInput"] input:focus{border-color:#F0B90B!important;}
div[data-testid="stTextInput"] input::placeholder{color:#474D57!important;}
div[data-testid="stButton"] button[kind="primary"]{background:#F0B90B!important;color:#1E2329!important;font-weight:700!important;font-size:.85rem!important;border:none!important;border-radius:6px!important;height:44px!important;width:100%!important;}
div[data-testid="stButton"] button[kind="primary"]:hover{background:#FFD35A!important;}
div[data-testid="stSpinner"]>div{border-top-color:#F0B90B!important;}
div[data-testid="stAlert"]{display:none!important;}
/* TF buttons */
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button{background:#1E2329!important;color:#848E9C!important;border:1px solid #2B3139!important;border-radius:4px!important;font-family:'IBM Plex Mono',monospace!important;font-size:.78rem!important;font-weight:600!important;height:32px!important;letter-spacing:.04em!important;padding:0 8px!important;}
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button:hover{border-color:#F0B90B!important;color:#F0B90B!important;background:rgba(240,185,11,0.06)!important;}
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button:disabled{background:rgba(240,185,11,0.12)!important;border-color:#F0B90B!important;color:#F0B90B!important;opacity:1!important;}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:#161A1E;}
::-webkit-scrollbar-thumb{background:#2B3139;border-radius:3px;}
</style>
""", unsafe_allow_html=True)

# ── Symbol Maps ────────────────────────────────────────────────────────────────
# yfinance symbol map — correct IDs for problematic coins
YF_MAP = {
    "BTC":"BTC-USD","ETH":"ETH-USD","SOL":"SOL-USD","BNB":"BNB-USD",
    "XRP":"XRP-USD","ADA":"ADA-USD","AVAX":"AVAX-USD","DOT":"DOT-USD",
    "NEAR":"NEAR-USD","SUI":"SUI20947-USD","APT":"APT21794-USD",
    "LTC":"LTC-USD","TRX":"TRX-USD","MATIC":"MATIC-USD","OP":"OP-USD",
    "ARB":"ARB11841-USD","UNI":"UNI7083-USD","AAVE":"AAVE-USD",
    "LINK":"LINK-USD","INJ":"INJ-USD","CRV":"CRV-USD",
    "DOGE":"DOGE-USD","SHIB":"SHIB-USD","PEPE":"PEPE24478-USD",
    "WIF":"WIF-USD","BONK":"BONK-USD","FLOKI":"FLOKI-USD",
    "MOG":"MOG22421-USD","POPCAT":"POPCAT-USD",
}

META = {
    "BTC":   ("Bitcoin",   "BTC/USDT","Layer-1","₿","#F7931A"),
    "ETH":   ("Ethereum",  "ETH/USDT","Layer-1","Ξ","#627EEA"),
    "SOL":   ("Solana",    "SOL/USDT","Layer-1","◎","#9945FF"),
    "BNB":   ("BNB",       "BNB/USDT","Layer-1","B","#F0B90B"),
    "XRP":   ("XRP",       "XRP/USDT","Layer-1","✕","#00AAE4"),
    "ADA":   ("Cardano",   "ADA/USDT","Layer-1","₳","#0033AD"),
    "AVAX":  ("Avalanche", "AVAX/USDT","Layer-1","A","#E84142"),
    "DOT":   ("Polkadot",  "DOT/USDT","Layer-1","●","#E6007A"),
    "NEAR":  ("NEAR",      "NEAR/USDT","Layer-1","N","#00C08B"),
    "SUI":   ("Sui",       "SUI/USDT","Layer-1","S","#4DA2FF"),
    "APT":   ("Aptos",     "APT/USDT","Layer-1","A","#24D4A8"),
    "LTC":   ("Litecoin",  "LTC/USDT","Layer-1","Ł","#BFBBBB"),
    "TRX":   ("TRON",      "TRX/USDT","Layer-1","T","#FF0013"),
    "MATIC": ("Polygon",   "MATIC/USDT","Layer-2","M","#8247E5"),
    "OP":    ("Optimism",  "OP/USDT","Layer-2","O","#FF0420"),
    "ARB":   ("Arbitrum",  "ARB/USDT","Layer-2","A","#28A0F0"),
    "UNI":   ("Uniswap",   "UNI/USDT","DeFi","🦄","#FF007A"),
    "AAVE":  ("Aave",      "AAVE/USDT","DeFi","A","#B6509E"),
    "LINK":  ("Chainlink", "LINK/USDT","Oracle","⬡","#2A5ADA"),
    "INJ":   ("Injective", "INJ/USDT","DeFi","I","#00B4D8"),
    "CRV":   ("Curve",     "CRV/USDT","DeFi","C","#D7263D"),
    "DOGE":  ("Dogecoin",  "DOGE/USDT","Meme","Ð","#C2A633"),
    "SHIB":  ("Shiba Inu", "SHIB/USDT","Meme","🐕","#F02D21"),
    "PEPE":  ("Pepe",      "PEPE/USDT","Meme","🐸","#00A550"),
    "WIF":   ("dogwifhat", "WIF/USDT","Meme","🎩","#F0A500"),
    "BONK":  ("Bonk",      "BONK/USDT","Meme","🐕","#F5841F"),
    "FLOKI": ("Floki",     "FLOKI/USDT","Meme","F","#F5841F"),
    "MOG":   ("Mog Coin",  "MOG/USDT","Meme","😼","#C850C0"),
    "POPCAT":("Popcat",    "POPCAT/USDT","Meme","🐱","#F7931A"),
}

PICKS = {
    "🔥 Popular":    ["BTC","ETH","SOL","BNB","XRP"],
    "😂 Meme Coins": ["DOGE","SHIB","PEPE","WIF","BONK","FLOKI","MOG"],
    "⚡ DeFi":       ["UNI","AAVE","LINK","INJ","CRV"],
    "🌐 Layer-1/2":  ["ADA","AVAX","NEAR","SUI","ARB","OP"],
}

# Timeframe → (yfinance interval, yfinance period)
TF_YF = {
    "1D":  ("1d",  "3mo"),
    "4H":  ("1h",  "1mo"),   # yfinance has no 4h, use 1h then resample
    "1H":  ("1h",  "7d"),
    "15m": ("15m", "5d"),
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def fmt(p):
    if p is None: return "N/A"
    a = abs(p)
    if a >= 1000:  return f"${p:,.2f}"
    if a >= 1:     return f"${p:.4f}"
    if a >= 0.001: return f"${p:.6f}"
    return f"${p:.8f}"

def fmt_large(n):
    if n >= 1e9: return f"${n/1e9:.2f}B"
    if n >= 1e6: return f"${n/1e6:.2f}M"
    if n >= 1e3: return f"${n/1e3:.2f}K"
    return f"${n:.2f}"

def calc_rsi(series, period=14):
    if len(series) < period+1: return 50.0
    d = series.diff().dropna()
    g = d.clip(lower=0).rolling(period).mean()
    l = (-d.clip(upper=0)).rolling(period).mean()
    rs = g / l.replace(0, np.nan)
    v = (100-(100/(1+rs))).dropna()
    return float(v.iloc[-1]) if len(v) else 50.0

def rsi_series(closes):
    out = []
    for i in range(len(closes)):
        if i < 15: out.append(np.nan)
        else: out.append(calc_rsi(pd.Series(closes[max(0,i-28):i+1])))
    return out

def safe_float(v, default=0.0):
    try:
        if v is None: return default
        f = float(v)
        return default if f != f else f
    except: return default

# ── LCW live price only ────────────────────────────────────────────────────────
def get_live_price(code):
    """Only use LCW for live real-time price — not for history."""
    try:
        r = requests.post(f"{LCW_BASE}/coins/single",
                          headers=LCW_HDR,
                          json={"currency":"USD","code":code.upper(),"meta":False},
                          timeout=8)
        if r.status_code == 200:
            data = r.json()
            delta_raw = data.get("delta") or {}
            return {
                "price": safe_float(data.get("rate"), 0.0),
                "pct":   (safe_float(delta_raw.get("day"), 1.0) - 1) * 100,
                "vol":   safe_float(data.get("volume"), 0.0),
                "cap":   safe_float(data.get("cap"), 0.0),
            }
    except: pass
    return None

# ── yfinance history ───────────────────────────────────────────────────────────
def get_history(code, timeframe="1D"):
    yf_sym = YF_MAP.get(code, code+"-USD")
    interval, period = TF_YF.get(timeframe, ("1d","3mo"))

    df = yf.Ticker(yf_sym).history(period=period, interval=interval)
    if df.empty or len(df) < 10:
        raise ValueError(f"'{code}' ka data nahi mila. Symbol check karein.")

    # For 4H: resample 1H → 4H
    if timeframe == "4H":
        df = df.resample("4h").agg({
            "Open":  "first",
            "High":  "max",
            "Low":   "min",
            "Close": "last",
            "Volume":"sum"
        }).dropna()

    df = df[["Open","High","Low","Close","Volume"]].copy()
    df.dropna(inplace=True)
    return df

# ── Analyze ────────────────────────────────────────────────────────────────────
def analyze(raw, timeframe="1D"):
    code = raw.upper().strip().replace("-USD","").replace("USDT","").strip()
    if not code: return None

    # 1. History from yfinance (reliable OHLCV)
    df = get_history(code, timeframe)

    df["SMA20"] = df["Close"].rolling(20).mean()
    df["STD20"] = df["Close"].rolling(20).std()
    df.dropna(subset=["SMA20","STD20"], inplace=True)

    cp  = float(df["Close"].iloc[-1])
    sma = float(df["SMA20"].iloc[-1])
    std = float(df["STD20"].iloc[-1])
    rsi = calc_rsi(df["Close"])

    # 2. Live price from LCW (real-time)
    lcw = get_live_price(code)
    if lcw and lcw["price"] > 0:
        live = lcw["price"]
        pct  = lcw["pct"]
        vol  = lcw["vol"]
        cap  = lcw["cap"]
    else:
        live = cp
        prev = float(df["Close"].iloc[-2]) if len(df)>1 else cp
        pct  = (cp - prev) / prev * 100 if prev else 0.0
        vol  = float(df["Volume"].iloc[-1])
        cap  = 0.0

    # 3. Signal
    if cp > sma and rsi < 70:
        sig, stype = "LONG / BUY  ▲", "buy"
        sl, tp = cp - 1.5*std, cp + 3.0*std
    elif cp < sma and rsi > 30:
        sig, stype = "SHORT / SELL  ▼", "sell"
        sl, tp = cp + 1.5*std, cp - 3.0*std
    else:
        sig, stype = "HOLD / WAIT  ◆", "hold"
        sl, tp = cp - 1.5*std, cp + 3.0*std

    rr     = abs(tp-cp)/abs(sl-cp) if abs(sl-cp)>0 else 0
    tp_pct = (tp-cp)/cp*100
    sl_pct = (sl-cp)/cp*100
    m = META.get(code, (code, code+"/USDT","Crypto","●","#848E9C"))

    return {
        "code":code,"name":m[0],"pair":m[1],"cat":m[2],"icon":m[3],"color":m[4],
        "live":live,"cp":cp,"pct":pct,"vol":vol,"cap":cap,
        "tp":tp,"sl":sl,"rsi":rsi,"sma":sma,"std":std,
        "sig":sig,"stype":stype,"rr":rr,
        "tp_pct":tp_pct,"sl_pct":sl_pct,
        "trend":"Bullish" if cp>sma else "Bearish",
        "high3m":float(df["High"].max()),
        "low3m": float(df["Low"].min()),
        "df":df, "timeframe":timeframe,
    }

# ── Chart ──────────────────────────────────────────────────────────────────────
def build_chart(d):
    tf     = d.get("timeframe","1D")
    show_n = {"1D":60,"4H":60,"1H":72,"15m":96}.get(tf, 60)
    df     = d["df"].iloc[-show_n:].copy()
    xs     = df.index.tolist()

    UP   = "#26a69a"; DN   = "#ef5350"
    BG   = "#131722"; GRID = "#1c2030"
    MUTED= "#5d6d7e"; GOLD = "#f0b90b"

    mn   = float(df["Low"].min())
    mx   = float(df["High"].max())
    rng  = mx - mn if mx != mn else mn*0.01
    y_lo = mn - rng*0.04
    y_hi = mx + rng*0.12

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        row_heights=[0.65,0.17,0.18],
                        vertical_spacing=0.0)

    # ── Candlestick ──
    fig.add_trace(go.Candlestick(
        x=xs,
        open=df["Open"].values, high=df["High"].values,
        low=df["Low"].values,   close=df["Close"].values,
        increasing=dict(fillcolor=UP, line=dict(color=UP, width=1)),
        decreasing=dict(fillcolor=DN, line=dict(color=DN, width=1)),
        name="Price", showlegend=False,
    ), row=1, col=1)

    # ── SMA ──
    fig.add_trace(go.Scatter(
        x=xs, y=df["SMA20"].values, mode="lines",
        line=dict(color=GOLD, width=1.5, dash="dot"),
        name="MA20", hoverinfo="skip",
    ), row=1, col=1)

    # ── TP / Entry / SL ──
    for yv, col, lbl in [
        (d["tp"], UP,       "TP "    + fmt(d["tp"])),
        (d["cp"], "#848E9C","Entry " + fmt(d["cp"])),
        (d["sl"], DN,       "SL "    + fmt(d["sl"])),
    ]:
        fig.add_trace(go.Scatter(
            x=[xs[0], xs[-1]], y=[yv, yv], mode="lines",
            line=dict(color=col, width=1, dash="dash"),
            showlegend=False, hoverinfo="skip",
        ), row=1, col=1)
        fig.add_annotation(
            x=1, y=yv, xref="paper", yref="y",
            text=lbl, showarrow=False,
            xanchor="left", yanchor="middle",
            font=dict(color=col, size=10, family="IBM Plex Mono"),
            xshift=4,
        )

    # ── Volume ──
    vcol = [UP if float(c)>=float(o) else DN
            for c,o in zip(df["Close"].values, df["Open"].values)]
    fig.add_trace(go.Bar(
        x=xs, y=df["Volume"].values,
        marker_color=vcol, marker_line_width=0,
        opacity=0.7, showlegend=False,
        hovertemplate="Vol: %{y:,.0f}<extra></extra>",
    ), row=2, col=1)

    # ── RSI ──
    rv = rsi_series(df["Close"].values)
    fig.add_trace(go.Scatter(
        x=xs, y=rv, mode="lines",
        line=dict(color="#7b68ee", width=1.5),
        showlegend=False,
        hovertemplate="RSI: %{y:.1f}<extra></extra>",
    ), row=3, col=1)
    fig.add_hrect(y0=70, y1=100, row=3, col=1,
                  fillcolor="rgba(239,83,80,0.07)", line_width=0)
    fig.add_hrect(y0=0,  y1=30,  row=3, col=1,
                  fillcolor="rgba(38,166,154,0.07)", line_width=0)
    for lv, lc in [(70,DN),(50,MUTED),(30,UP)]:
        fig.add_trace(go.Scatter(
            x=[xs[0],xs[-1]], y=[lv,lv], mode="lines",
            line=dict(color=lc, width=0.6, dash="dot"),
            showlegend=False, hoverinfo="skip",
        ), row=3, col=1)

    ax = dict(showgrid=True, gridcolor=GRID, gridwidth=1,
              zeroline=False, linecolor=GRID,
              tickfont=dict(size=9, color=MUTED, family="IBM Plex Mono"),
              showspikes=True, spikecolor=MUTED,
              spikethickness=1, spikedash="dot")

    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color=MUTED, family="IBM Plex Mono", size=10),
        xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(orientation="h", y=1.02, x=0,
                    bgcolor="rgba(0,0,0,0)",
                    font=dict(size=10, color=MUTED)),
        margin=dict(l=0, r=120, t=8, b=0),
        height=580,
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#1e2433", bordercolor=GRID,
                        font=dict(color="#d1d4dc", family="IBM Plex Mono", size=11)),
        dragmode="pan",
    )
    fig.update_xaxes(**ax)
    fig.update_yaxes(**ax)
    fig.update_xaxes(showticklabels=False, row=1, col=1)
    fig.update_xaxes(showticklabels=False, row=2, col=1)
    fig.update_xaxes(showticklabels=True,  row=3, col=1)
    fig.update_yaxes(range=[y_lo, y_hi], tickprefix="$",
                     tickformat=",.4f", exponentformat="none", row=1, col=1)
    fig.update_yaxes(tickformat=".2s", row=2, col=1)
    fig.update_yaxes(range=[0,100], tickvals=[30,50,70], row=3, col=1)
    return fig

# ── Session ────────────────────────────────────────────────────────────────────
for k,v in [("history",[]),("result",None),("skey",0),("error",""),("tf","1D")]:
    if k not in st.session_state: st.session_state[k] = v

def H(html): st.markdown(html, unsafe_allow_html=True)

# ── Navbar ─────────────────────────────────────────────────────────────────────
H("""<div style="background:#161A1E;border-bottom:1px solid #2B3139;padding:0 24px;height:56px;display:flex;align-items:center;position:sticky;top:0;z-index:99">
  <span style="font-size:1.15rem;font-weight:700;color:#F0B90B;margin-right:32px">📊 CryptoSignal</span>
  <span style="font-size:.82rem;font-weight:600;color:#EAECEF;padding:0 16px;height:56px;display:inline-flex;align-items:center;border-bottom:2px solid #F0B90B">Markets</span>
  <span style="font-size:.82rem;color:#474D57;padding:0 16px;height:56px;display:inline-flex;align-items:center">Signals</span>
  <span style="font-size:.82rem;color:#474D57;padding:0 16px;height:56px;display:inline-flex;align-items:center">Portfolio</span>
  <div style="margin-left:auto;display:flex;align-items:center;gap:8px">
    <div style="background:#0ECB8118;border:1px solid #0ECB81;color:#0ECB81;font-size:.7rem;font-weight:600;padding:3px 10px;border-radius:4px">● LIVE</div>
  </div>
</div>""")

H("""<div style="background:#161A1E;border-bottom:1px solid #2B3139;padding:0 24px;height:32px;display:flex;align-items:center;gap:24px;font-size:.7rem;overflow:hidden">
  <span style="color:#474D57">BTC/USDT</span><span style="color:#474D57">ETH/USDT</span>
  <span style="color:#474D57">SOL/USDT</span><span style="color:#474D57">DOGE/USDT</span>
  <span style="color:#474D57">PEPE/USDT</span>
  <span style="margin-left:auto;color:#2B3139;font-size:.65rem">Chart: yfinance &nbsp;|&nbsp; Live Price: LCW &nbsp;|&nbsp; Not financial advice</span>
</div>""")

H('<div style="padding:20px 24px 40px">')

H(f"""<div style="padding-bottom:14px;border-bottom:1px solid #2B3139;margin-bottom:18px;display:flex;align-items:center;justify-content:space-between">
  <div>
    <div style="font-size:1.1rem;font-weight:700;color:#EAECEF">📈 Signal Scanner</div>
    <div style="font-size:.75rem;color:#474D57;margin-top:3px">RSI-14 + SMA-20 &nbsp;·&nbsp; Auto TP/SL &nbsp;·&nbsp; yfinance chart data &nbsp;·&nbsp; LCW live price</div>
  </div>
  <div style="font-size:.7rem;color:#2B3139">{datetime.now().strftime('%d %b %Y  %H:%M')}</div>
</div>""")

# ── Search ─────────────────────────────────────────────────────────────────────
c1, c2 = st.columns([5.5, 1])
with c1:
    sym_inp = st.text_input("s", label_visibility="collapsed",
        placeholder="Symbol likhein:  BTC  •  ETH  •  DOGE  •  PEPE  •  SOL ...",
        key=f"inp_{st.session_state.skey}")
with c2:
    clicked = st.button("Analyze ▶", type="primary", use_container_width=True)

qp = st.query_params
if "chip" in qp and qp["chip"]:
    sym_inp = qp["chip"]; clicked = True

# ── Coin Chips ─────────────────────────────────────────────────────────────────
for cat, coins in PICKS.items():
    H('<div style="font-size:.67rem;color:#474D57;font-weight:600;letter-spacing:.06em;text-transform:uppercase;margin:12px 0 6px">' + cat + '</div>')
    row = '<div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:2px">'
    for coin in coins:
        row += (
            '<a href="?chip=' + coin + '" target="_self" style="display:inline-flex;align-items:center;justify-content:center;background:#1E2329;color:#848E9C;border:1px solid #2B3139;border-radius:4px;font-size:.75rem;font-weight:500;padding:5px 13px;text-decoration:none;white-space:nowrap;font-family:IBM Plex Mono,monospace;cursor:pointer"'
            'onmouseover="this.style.borderColor=\'#F0B90B\';this.style.color=\'#F0B90B\';this.style.background=\'rgba(240,185,11,0.06)\'"'
            'onmouseout="this.style.borderColor=\'#2B3139\';this.style.color=\'#848E9C\';this.style.background=\'#1E2329\'">'
            + coin + '</a>'
        )
    row += "</div>"
    H(row)

H("<div style='height:8px'></div>")
H("<div style='border-top:1px solid #2B3139;margin:4px 0 18px'></div>")

# ── Run Analysis ───────────────────────────────────────────────────────────────
if clicked and sym_inp:
    if "chip" in st.query_params: st.query_params.clear()
    with st.spinner(f"⏳ {sym_inp.upper().strip()} data fetch ho raha hai..."):
        try:
            data = analyze(sym_inp, st.session_state.tf)
            if data:
                st.session_state.result = data
                st.session_state.error  = ""
                st.session_state.history.insert(0, {
                    "pair": data["pair"], "sig": data["stype"],
                    "live": data["live"], "pct": data["pct"],
                    "tp":   data["tp"],   "sl":  data["sl"],
                    "time": datetime.now().strftime("%H:%M:%S"),
                })
                st.session_state.history = st.session_state.history[:8]
                st.session_state.skey += 1
                st.rerun()
        except ValueError as ve:
            st.session_state.error = str(ve); st.session_state.skey += 1; st.rerun()
        except Exception as ex:
            st.session_state.error = str(ex); st.session_state.skey += 1; st.rerun()

if st.session_state.error:
    H('<div style="background:rgba(246,70,93,0.07);border:1px solid rgba(246,70,93,0.3);border-left:3px solid #F6465D;border-radius:6px;padding:11px 16px;color:#F6465D;font-size:.82rem;margin:8px 0 16px;font-family:IBM Plex Mono,monospace">&#10060; &nbsp;' + st.session_state.error + '</div>')

# ── Result ─────────────────────────────────────────────────────────────────────
if st.session_state.result:
    d = st.session_state.result
    if not {"code","stype","live","cp","tp","sl","df"}.issubset(d.keys()):
        st.session_state.result = None; st.session_state.history = []; st.rerun()

    code   = d.get("code","");   name  = d.get("name", code)
    pair   = d.get("pair", "");  cat   = d.get("cat","Crypto")
    icon   = d.get("icon","●");  color = d.get("color","#848E9C")
    live   = d.get("live",0.0);  cp    = d.get("cp",0.0)
    pct    = d.get("pct",0.0);   tp    = d.get("tp",0.0)
    sl     = d.get("sl",0.0);    rsi   = d.get("rsi",50.0)
    sma    = d.get("sma",0.0);   std   = d.get("std",0.0)
    rr     = d.get("rr",0.0);    tp_pct= d.get("tp_pct",0.0)
    sl_pct = d.get("sl_pct",0.0);trend = d.get("trend","-")
    high3m = d.get("high3m",0.0);low3m = d.get("low3m",0.0)
    vol    = d.get("vol",0.0);   cap   = d.get("cap",0.0)
    stype  = d.get("stype","hold"); sig = d.get("sig","HOLD")

    pu  = pct >= 0
    pc  = "#0ECB81" if pu else "#F6465D"
    ps  = ("+" if pu else "") + f"{pct:.2f}%  (24h)"
    sbg = {"buy":"rgba(14,203,129,0.07)","sell":"rgba(246,70,93,0.07)","hold":"rgba(240,185,11,0.07)"}
    sbd = {"buy":"#0ECB81","sell":"#F6465D","hold":"#F0B90B"}
    scl = {"buy":"#0ECB81","sell":"#F6465D","hold":"#F0B90B"}

    # Price header
    H('<div style="background:#161A1E;border:1px solid #2B3139;border-radius:8px;padding:18px 22px;margin-bottom:14px;display:flex;flex-wrap:wrap;gap:20px;align-items:center;justify-content:space-between">'
      '<div style="display:flex;align-items:center;gap:14px">'
      '<div style="width:42px;height:42px;border-radius:50%;background:' + color + '22;color:' + color + ';font-size:1.3rem;display:flex;align-items:center;justify-content:center">' + icon + '</div>'
      '<div><div style="font-size:1.05rem;font-weight:700;color:#EAECEF">' + name + ' <span style="color:#474D57;font-size:.8rem;font-weight:400">' + cat + '</span></div>'
      '<div style="font-size:.76rem;color:#474D57;margin-top:2px">' + pair + '</div></div></div>'
      '<div><div style="font-size:.64rem;color:#474D57;text-transform:uppercase;letter-spacing:.06em;margin-bottom:5px">Current Market Price</div>'
      '<div style="font-size:2rem;font-weight:700;color:#EAECEF;letter-spacing:-.02em;line-height:1">' + fmt(live) + '</div>'
      '<div style="color:' + pc + ';font-size:.86rem;font-weight:500;margin-top:4px">' + ps + '</div></div>'
      '<div><div style="font-size:.64rem;color:#474D57;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px">AI Signal</div>'
      '<div style="background:' + sbg[stype] + ';border:1px solid ' + sbd[stype] + ';color:' + scl[stype] + ';font-size:.84rem;font-weight:700;padding:8px 22px;border-radius:4px;letter-spacing:.04em;display:inline-block">' + sig + '</div>'
      '</div></div>')

    # Stat cards
    rsi_c = "#F0B90B" if 30<=rsi<=70 else ("#0ECB81" if rsi<30 else "#F6465D")
    rr_c  = "#0ECB81" if rr>=2 else ("#F0B90B" if rr>=1 else "#F6465D")
    rsi_l = "Oversold" if rsi<30 else ("Overbought" if rsi>70 else "Neutral")
    sl_s  = ("+" if sl_pct>=0 else "") + f"{sl_pct:.1f}%"

    def sc(label, value, sub, clr="#EAECEF"):
        return ('<div style="background:#161A1E;border:1px solid #2B3139;border-radius:6px;padding:12px 14px">'
                '<div style="font-size:.64rem;color:#474D57;text-transform:uppercase;letter-spacing:.05em;font-weight:600;margin-bottom:6px">' + label + '</div>'
                '<div style="font-size:.88rem;font-weight:600;color:' + clr + ';font-family:IBM Plex Mono,monospace">' + value + '</div>'
                '<div style="font-size:.64rem;color:#474D57;margin-top:3px">' + sub + '</div></div>')

    H('<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:8px">'
      + sc("Entry Price", fmt(cp), "Last close")
      + sc("Take Profit ✦", fmt(tp), "+" + f"{abs(tp_pct):.1f}% from entry", "#0ECB81")
      + sc("Stop Loss ✦", fmt(sl), sl_s + " from entry", "#F6465D")
      + sc("RSI (14)", f"{rsi:.1f}", rsi_l, rsi_c)
      + '</div>'
      '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:14px">'
      + sc("Risk/Reward", f"1 : {rr:.2f}", trend, rr_c)
      + sc("3M High/Low", fmt(high3m), "Low " + fmt(low3m))
      + sc("24h Volume", fmt_large(vol), "LCW real-time")
      + sc("Market Cap", fmt_large(cap), "LCW real-time")
      + '</div>')

    # Insight
    if stype=="buy":
        ins = "Price " + fmt(cp) + " SMA-20 (" + fmt(sma) + ") se upar. RSI " + f"{rsi:.0f}" + " — bullish momentum. TP " + fmt(tp) + " (+" + f"{abs(tp_pct):.1f}" + "%), SL " + fmt(sl) + " rakhen."
    elif stype=="sell":
        ins = "Price " + fmt(cp) + " SMA-20 (" + fmt(sma) + ") se neeche. RSI " + f"{rsi:.0f}" + " — bearish confirm. SL " + fmt(sl) + " pe rakhen. TP: " + fmt(tp) + "."
    else:
        ins = "RSI " + f"{rsi:.0f}" + " neutral (30-70). SMA: " + fmt(sma) + ". Clear direction nahi — wait karen."

    H('<div style="background:#161A1E;border:1px solid #2B3139;border-left:3px solid #F0B90B;border-radius:6px;padding:12px 16px;font-size:.82rem;color:#848E9C;line-height:1.65;margin-bottom:14px">&#128161; &nbsp;' + ins + '</div>')

    # ── Timeframe buttons ──
    cur_tf = st.session_state.get("tf","1D")
    H('<div style="display:flex;align-items:center;gap:6px;margin-bottom:8px"><span style="font-size:.67rem;color:#474D57;text-transform:uppercase;letter-spacing:.06em;margin-right:4px">Timeframe</span></div>')
    tf_cols = st.columns(4)
    for i, (tk, tn) in enumerate([("1D","Daily"),("4H","4 Hour"),("1H","1 Hour"),("15m","15 Min")]):
        with tf_cols[i]:
            if st.button(tn, key=f"tf_{tk}", use_container_width=True, disabled=(cur_tf==tk)):
                st.session_state.tf = tk
                with st.spinner(f"⏳ {code} [{tk}] chart..."):
                    try:
                        nd = analyze(code, tk)
                        if nd:
                            st.session_state.result = nd
                            st.session_state.error  = ""
                            st.rerun()
                    except Exception as ex:
                        st.session_state.error = str(ex); st.rerun()

    # Chart
    st.plotly_chart(build_chart(d), use_container_width=True,
                    config={"displayModeBar":True,"displaylogo":False,
                            "modeBarButtonsToRemove":["lasso2d","select2d"]},
                    theme=None)

# ── History ────────────────────────────────────────────────────────────────────
if st.session_state.history:
    rows = ""
    for h in st.session_state.history:
        pv = h.get("pct",0.0); lv = h.get("live",0.0)
        sv = h.get("sig","hold"); pa = h.get("pair","-"); tv = h.get("time","-")
        pc2 = "#0ECB81" if pv>=0 else "#F6465D"
        sc2 = "#0ECB81" if sv=="buy" else ("#F6465D" if sv=="sell" else "#F0B90B")
        lb  = "BUY ▲" if sv=="buy" else ("SELL ▼" if sv=="sell" else "HOLD ◆")
        rows += ('<div style="padding:9px 16px;display:grid;grid-template-columns:1.3fr 1fr 1fr 1fr 1fr;font-size:.8rem;border-bottom:1px solid rgba(43,49,57,0.5);align-items:center;font-family:IBM Plex Mono,monospace">'
                 '<span style="color:#EAECEF;font-weight:600">' + pa + '</span>'
                 '<span style="color:' + pc2 + '">' + ("+" if pv>=0 else "") + f"{pv:.2f}" + '%</span>'
                 '<span style="color:#848E9C">' + fmt(lv) + '</span>'
                 '<span style="color:' + sc2 + ';font-weight:700">' + lb + '</span>'
                 '<span style="color:#474D57">' + tv + '</span></div>')

    H('<div style="background:#161A1E;border:1px solid #2B3139;border-radius:8px;overflow:hidden;margin-top:20px">'
      '<div style="background:#1E2329;padding:9px 16px;display:grid;grid-template-columns:1.3fr 1fr 1fr 1fr 1fr;font-size:.68rem;font-weight:600;color:#474D57;text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid #2B3139">'
      '<span>Pair</span><span>24h</span><span>Price</span><span>Signal</span><span>Time</span></div>'
      + rows + '</div>')

H('<div style="text-align:center;padding:18px;color:#2B3139;font-size:.7rem;border-top:1px solid #2B3139;margin-top:24px">&#9888; Educational only — not financial advice &nbsp;|&nbsp; Chart: yfinance &nbsp;|&nbsp; Live price: LCW</div>')
H('</div>')
