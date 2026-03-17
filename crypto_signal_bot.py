import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="CryptoSignal", page_icon="📊",
                   layout="wide", initial_sidebar_state="collapsed")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

html,body,[class*="css"]{font-family:'IBM Plex Sans',sans-serif!important;
  background:#0B0E11!important;color:#EAECEF!important;}
.main,.block-container{background:#0B0E11!important;padding:0!important;max-width:100%!important;}
section[data-testid="stSidebar"],div[data-testid="stDecoration"],
.stDeployButton{display:none!important;}
#MainMenu,footer,header{visibility:hidden!important;}

div[data-testid="stVerticalBlock"]>div{background:transparent!important;}

/* search input */
div[data-testid="stTextInput"] label{display:none!important;}
div[data-testid="stTextInput"] input{
  background:#1E2329!important;border:1px solid #2B3139!important;
  border-radius:6px!important;color:#EAECEF!important;
  font-family:'IBM Plex Mono',monospace!important;font-size:.88rem!important;
  height:44px!important;box-shadow:none!important;}
div[data-testid="stTextInput"] input:focus{border-color:#F0B90B!important;}
div[data-testid="stTextInput"] input::placeholder{color:#474D57!important;}

/* analyze button */
div[data-testid="stButton"] button[kind="primary"]{
  background:#F0B90B!important;color:#1E2329!important;font-weight:700!important;
  font-size:.85rem!important;border:none!important;border-radius:6px!important;
  height:44px!important;width:100%!important;}
div[data-testid="stButton"] button[kind="primary"]:hover{background:#FFD35A!important;}

/* spinner */
div[data-testid="stSpinner"]>div{border-top-color:#F0B90B!important;}

/* hide streamlit alerts completely — we use custom HTML */
div[data-testid="stAlert"]{display:none!important;}

::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:#161A1E;}
::-webkit-scrollbar-thumb{background:#2B3139;border-radius:3px;}
</style>
""", unsafe_allow_html=True)

# ── Coin data ──────────────────────────────────────────────────────────────────
SYMBOL_MAP = {
    "BTC-USD":"BTC-USD","ETH-USD":"ETH-USD","SOL-USD":"SOL-USD",
    "BNB-USD":"BNB-USD","XRP-USD":"XRP-USD","ADA-USD":"ADA-USD",
    "AVAX-USD":"AVAX-USD","DOT-USD":"DOT-USD","NEAR-USD":"NEAR-USD",
    "SUI-USD":"SUI20947-USD","APT-USD":"APT21794-USD",
    "LTC-USD":"LTC-USD","TRX-USD":"TRX-USD",
    "MATIC-USD":"MATIC-USD","OP-USD":"OP-USD","ARB-USD":"ARB11841-USD",
    "UNI-USD":"UNI7083-USD","AAVE-USD":"AAVE-USD","LINK-USD":"LINK-USD",
    "INJ-USD":"INJ-USD","CRV-USD":"CRV-USD",
    "DOGE-USD":"DOGE-USD","SHIB-USD":"SHIB-USD",
    "PEPE-USD":"PEPE24478-USD","WIF-USD":"WIF-USD","BONK-USD":"BONK-USD",
    "FLOKI-USD":"FLOKI-USD","MOG-USD":"MOG22421-USD","POPCAT-USD":"POPCAT-USD",
}

META = {
    "BTC-USD":  ("Bitcoin",   "BTC/USDT", "Layer-1","₿","#F7931A"),
    "ETH-USD":  ("Ethereum",  "ETH/USDT", "Layer-1","Ξ","#627EEA"),
    "SOL-USD":  ("Solana",    "SOL/USDT", "Layer-1","◎","#9945FF"),
    "BNB-USD":  ("BNB",       "BNB/USDT", "Layer-1","B","#F0B90B"),
    "XRP-USD":  ("XRP",       "XRP/USDT", "Layer-1","✕","#00AAE4"),
    "ADA-USD":  ("Cardano",   "ADA/USDT", "Layer-1","₳","#0033AD"),
    "AVAX-USD": ("Avalanche", "AVAX/USDT","Layer-1","A","#E84142"),
    "DOT-USD":  ("Polkadot",  "DOT/USDT", "Layer-1","●","#E6007A"),
    "NEAR-USD": ("NEAR",      "NEAR/USDT","Layer-1","N","#00C08B"),
    "SUI-USD":  ("Sui",       "SUI/USDT", "Layer-1","S","#4DA2FF"),
    "APT-USD":  ("Aptos",     "APT/USDT", "Layer-1","A","#24D4A8"),
    "LTC-USD":  ("Litecoin",  "LTC/USDT", "Layer-1","Ł","#BFBBBB"),
    "TRX-USD":  ("TRON",      "TRX/USDT", "Layer-1","T","#FF0013"),
    "MATIC-USD":("Polygon",   "MATIC/USDT","Layer-2","M","#8247E5"),
    "OP-USD":   ("Optimism",  "OP/USDT",  "Layer-2","O","#FF0420"),
    "ARB-USD":  ("Arbitrum",  "ARB/USDT", "Layer-2","A","#28A0F0"),
    "UNI-USD":  ("Uniswap",   "UNI/USDT", "DeFi",  "🦄","#FF007A"),
    "AAVE-USD": ("Aave",      "AAVE/USDT","DeFi",  "A","#B6509E"),
    "LINK-USD": ("Chainlink", "LINK/USDT","Oracle","⬡","#2A5ADA"),
    "INJ-USD":  ("Injective", "INJ/USDT", "DeFi",  "I","#00B4D8"),
    "CRV-USD":  ("Curve",     "CRV/USDT", "DeFi",  "C","#D7263D"),
    "DOGE-USD": ("Dogecoin",  "DOGE/USDT","Meme",  "Ð","#C2A633"),
    "SHIB-USD": ("Shiba Inu", "SHIB/USDT","Meme",  "🐕","#F02D21"),
    "PEPE-USD": ("Pepe",      "PEPE/USDT","Meme",  "🐸","#00A550"),
    "WIF-USD":  ("dogwifhat", "WIF/USDT", "Meme",  "🎩","#F0A500"),
    "BONK-USD": ("Bonk",      "BONK/USDT","Meme",  "🐕","#F5841F"),
    "FLOKI-USD":("Floki",     "FLOKI/USDT","Meme", "F","#F5841F"),
    "MOG-USD":  ("Mog Coin",  "MOG/USDT", "Meme",  "😼","#C850C0"),
    "POPCAT-USD":("Popcat",   "POPCAT/USDT","Meme","🐱","#F7931A"),
}

PICKS = {
    "🔥 Popular":    ["BTC-USD","ETH-USD","SOL-USD","BNB-USD","XRP-USD"],
    "😂 Meme Coins": ["DOGE-USD","SHIB-USD","PEPE-USD","WIF-USD","BONK-USD","FLOKI-USD","MOG-USD"],
    "⚡ DeFi":       ["UNI-USD","AAVE-USD","LINK-USD","INJ-USD","CRV-USD"],
    "🌐 Layer-1/2":  ["ADA-USD","AVAX-USD","NEAR-USD","SUI-USD","ARB-USD","OP-USD"],
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def fmt(p):
    if p is None: return "N/A"
    if p >= 1000:  return f"${p:,.2f}"
    if p >= 1:     return f"${p:.4f}"
    if p >= 0.001: return f"${p:.6f}"
    return f"${p:.8f}"

def calc_rsi(s, period=14):
    if len(s) < period+1: return 50.0
    d = s.diff().dropna()
    g = d.clip(lower=0).rolling(period).mean()
    l = (-d.clip(upper=0)).rolling(period).mean()
    rs = g / l.replace(0, np.nan)
    v = (100-(100/(1+rs))).dropna()
    return float(v.iloc[-1]) if len(v) else 50.0

def get_live(sym):
    try:
        fi = yf.Ticker(sym).fast_info
        lp = getattr(fi,"last_price",None)
        if lp and not np.isnan(float(lp)): return float(lp)
    except: pass
    return None

def normalize(raw):
    s = raw.upper().strip()
    if not s: return ""
    return s if "-USD" in s else s+"-USD"

def analyze(raw):
    key = normalize(raw)
    if not key: return None
    yf_sym = SYMBOL_MAP.get(key, key)
    df = yf.Ticker(yf_sym).history(period="3mo")
    if df.empty or len(df) < 22:
        if yf_sym != key:
            df = yf.Ticker(key).history(period="3mo")
        if df.empty or len(df) < 22:
            raise ValueError(f"'{key}' ka data nahi mila. Symbol check karein.")
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["STD20"] = df["Close"].rolling(20).std()
    df.dropna(subset=["SMA20","STD20"], inplace=True)
    cp  = float(df["Close"].iloc[-1])
    sma = float(df["SMA20"].iloc[-1])
    std = float(df["STD20"].iloc[-1])
    rsi = calc_rsi(df["Close"])
    live = get_live(yf_sym) or cp
    prev = float(df["Close"].iloc[-2]) if len(df)>1 else cp
    pct  = (live-prev)/prev*100 if prev else 0.0
    if cp > sma and rsi < 70:
        sig,stype = "LONG / BUY  ▲","buy"
        sl,tp = cp-1.5*std, cp+3.0*std
    elif cp < sma and rsi > 30:
        sig,stype = "SHORT / SELL  ▼","sell"
        sl,tp = cp+1.5*std, cp-3.0*std
    else:
        sig,stype = "HOLD / WAIT  ◆","hold"
        sl,tp = cp-1.5*std, cp+3.0*std
    rr     = abs(tp-cp)/abs(sl-cp) if abs(sl-cp)>0 else 0
    tp_pct = (tp-cp)/cp*100
    sl_pct = (sl-cp)/cp*100
    m = META.get(key,(key,key,"Crypto","●","#848E9C"))
    return {"key":key,"yf_sym":yf_sym,
            "name":m[0],"pair":m[1],"cat":m[2],"icon":m[3],"color":m[4],
            "live":live,"cp":cp,"pct":pct,"prev":prev,
            "tp":tp,"sl":sl,"rsi":rsi,"sma":sma,"std":std,
            "sig":sig,"stype":stype,"rr":rr,
            "tp_pct":tp_pct,"sl_pct":sl_pct,
            "trend":"Bullish" if cp>sma else "Bearish",
            "high3m":float(df["High"].max()),"low3m":float(df["Low"].min()),
            "df":df}

def rsi_arr(closes):
    out=[]
    for i in range(len(closes)):
        if i<15: out.append(np.nan)
        else: out.append(calc_rsi(pd.Series(closes[max(0,i-28):i+1])))
    return out

def build_chart(d):
    df = d["df"].iloc[-60:]
    UP="#0ECB81"; DN="#F6465D"; BG="#0B0E11"; SBG="#161A1E"; GR="#2B3139"
    fig = make_subplots(rows=3,cols=1,shared_xaxes=True,
                        vertical_spacing=0.015,row_heights=[0.62,0.19,0.19])
    fig.add_trace(go.Candlestick(x=df.index,open=df["Open"],high=df["High"],
        low=df["Low"],close=df["Close"],
        increasing_fillcolor=UP,increasing_line_color=UP,
        decreasing_fillcolor=DN,decreasing_line_color=DN,
        name="Price",line_width=1),row=1,col=1)
    fig.add_trace(go.Scatter(x=df.index,y=df["SMA20"],
        line=dict(color="#F0B90B",width=1.5,dash="dot"),name="SMA-20"),row=1,col=1)
    for yv,c,lb in [(d["tp"],UP,f"TP {fmt(d['tp'])}"),(d["sl"],DN,f"SL {fmt(d['sl'])}"),(d["cp"],"#848E9C",f"Entry {fmt(d['cp'])}")]:
        fig.add_hline(y=yv,line_dash="dash",line_color=c,line_width=1,
                      annotation_text=lb,annotation_font_color=c,
                      annotation_font_size=10,row=1,col=1)
    vol_c=[UP if c>=o else DN for c,o in zip(df["Close"],df["Open"])]
    fig.add_trace(go.Bar(x=df.index,y=df["Volume"],marker_color=vol_c,
        marker_line_width=0,name="Volume",opacity=0.55),row=2,col=1)
    fig.add_trace(go.Scatter(x=df.index,y=rsi_arr(df["Close"].values),
        line=dict(color="#C850C0",width=1.5),fill="tozeroy",
        fillcolor="rgba(200,80,192,0.06)",name="RSI"),row=3,col=1)
    fig.add_hrect(y0=30,y1=70,row=3,col=1,fillcolor="rgba(255,255,255,0.03)",line_width=0)
    for lv,c in [(30,UP),(70,DN)]:
        fig.add_hline(y=lv,line_color=c,line_width=0.8,line_dash="dot",row=3,col=1)
    ax=dict(gridcolor=GR,linecolor=GR,zerolinecolor=GR,tickfont=dict(size=9,color="#474D57"))
    fig.update_layout(paper_bgcolor=BG,plot_bgcolor=SBG,
        font=dict(color="#848E9C",family="IBM Plex Mono",size=10),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h",y=1.03,x=0,bgcolor="rgba(0,0,0,0)",
                    font=dict(size=10,color="#848E9C")),
        margin=dict(l=0,r=72,t=8,b=0),height=550,hovermode="x unified",
        hoverlabel=dict(bgcolor="#1E2329",bordercolor="#2B3139",
                        font=dict(color="#EAECEF",family="IBM Plex Mono")))
    fig.update_xaxes(**ax); fig.update_yaxes(**ax)
    fig.update_yaxes(tickprefix="$",row=1,col=1)
    return fig

# ── Session ────────────────────────────────────────────────────────────────────
for k,v in [("history",[]),("result",None),("skey",0),("error","")]:
    if k not in st.session_state: st.session_state[k]=v

def H(html): st.markdown(html, unsafe_allow_html=True)

# ── NAVBAR ─────────────────────────────────────────────────────────────────────
H("""<div style="background:#161A1E;border-bottom:1px solid #2B3139;
  padding:0 24px;height:56px;display:flex;align-items:center;
  position:sticky;top:0;z-index:99">
  <span style="font-size:1.15rem;font-weight:700;color:#F0B90B;margin-right:32px">📊 CryptoSignal</span>
  <span style="font-size:.82rem;font-weight:600;color:#EAECEF;padding:0 16px;
    height:56px;display:inline-flex;align-items:center;
    border-bottom:2px solid #F0B90B">Markets</span>
  <span style="font-size:.82rem;color:#474D57;padding:0 16px;height:56px;
    display:inline-flex;align-items:center">Signals</span>
  <span style="font-size:.82rem;color:#474D57;padding:0 16px;height:56px;
    display:inline-flex;align-items:center">Portfolio</span>
  <div style="margin-left:auto;background:#0ECB8118;border:1px solid #0ECB81;
    color:#0ECB81;font-size:.7rem;font-weight:600;padding:3px 10px;
    border-radius:4px;letter-spacing:.04em">● LIVE DATA</div>
</div>""")

# ── TICKER ─────────────────────────────────────────────────────────────────────
H("""<div style="background:#161A1E;border-bottom:1px solid #2B3139;
  padding:0 24px;height:32px;display:flex;align-items:center;gap:24px;
  font-size:.7rem;overflow:hidden">
  <span style="color:#474D57">BTC/USDT</span>
  <span style="color:#474D57">ETH/USDT</span>
  <span style="color:#474D57">SOL/USDT</span>
  <span style="color:#474D57">DOGE/USDT</span>
  <span style="color:#474D57">PEPE/USDT</span>
  <span style="margin-left:auto;color:#2B3139;font-size:.68rem">
    Data: Yahoo Finance &nbsp;|&nbsp; Not financial advice</span>
</div>""")

# ── PAGE WRAP ──────────────────────────────────────────────────────────────────
H('<div style="padding:20px 24px 40px">')

H(f"""<div style="padding-bottom:14px;border-bottom:1px solid #2B3139;
  margin-bottom:18px;display:flex;align-items:center;justify-content:space-between">
  <div>
    <div style="font-size:1.1rem;font-weight:700;color:#EAECEF">📈 Signal Scanner</div>
    <div style="font-size:.75rem;color:#474D57;margin-top:3px">
      RSI-14 + SMA-20 &nbsp;·&nbsp; Auto TP/SL &nbsp;·&nbsp; 3-month chart &nbsp;·&nbsp; Real-time price
    </div>
  </div>
  <div style="font-size:.7rem;color:#2B3139">{datetime.now().strftime('%d %b %Y  %H:%M')}</div>
</div>""")

# ── SEARCH ─────────────────────────────────────────────────────────────────────
c1, c2 = st.columns([5.5, 1])
with c1:
    sym_inp = st.text_input("s", label_visibility="collapsed",
        placeholder="Symbol likhein:  BTC  •  ETH  •  DOGE  •  PEPE  •  SOL ...",
        key=f"inp_{st.session_state.skey}")
with c2:
    clicked = st.button("Analyze ▶", type="primary", use_container_width=True)

# ── COIN CHIPS — pure HTML anchor tags, tight flex layout ──────────────────────
# Query param se chip click detect karo
qp = st.query_params
if "chip" in qp and qp["chip"]:
    sym_inp = qp["chip"]
    clicked = True

for cat, coins in PICKS.items():
    H(f"""<div style="font-size:.67rem;color:#474D57;font-weight:600;
      letter-spacing:.06em;text-transform:uppercase;margin:12px 0 6px">{cat}</div>""")
    # Build one flex row — chips naturally stay close together
    chip_row = '<div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:2px">'
    for coin in coins:
        short = coin.replace("-USD","")
        chip_row += (
            f'<a href="?chip={coin}" target="_self" style="'
            f'display:inline-flex;align-items:center;justify-content:center;'
            f'background:#1E2329;color:#848E9C;'
            f'border:1px solid #2B3139;border-radius:4px;'
            f'font-size:.75rem;font-weight:500;padding:5px 13px;'
            f'text-decoration:none;white-space:nowrap;'
            f'font-family:IBM Plex Mono,monospace;cursor:pointer"'
            f'onmouseover="this.style.borderColor=\'#F0B90B\';'
            f'this.style.color=\'#F0B90B\';this.style.background=\'rgba(240,185,11,0.06)\'"'
            f'onmouseout="this.style.borderColor=\'#2B3139\';'
            f'this.style.color=\'#848E9C\';this.style.background=\'#1E2329\'">'
            f'{short}</a>'
        )
    chip_row += "</div>"
    H(chip_row)

H("<div style='height:8px'></div>")
H("<div style='border-top:1px solid #2B3139;margin:4px 0 18px'></div>")

# ── RUN ANALYSIS ───────────────────────────────────────────────────────────────
if clicked and sym_inp:
    if "chip" in st.query_params:
        st.query_params.clear()
    with st.spinner(f"Fetching {sym_inp.upper().strip()} data..."):
        try:
            data = analyze(sym_inp)
            if data:
                st.session_state.result = data
                st.session_state.error  = ""
                st.session_state.history.insert(0, {
                    "pair": data["pair"],
                    "sig":  data["stype"],
                    "live": data["live"],
                    "pct":  data["pct"],
                    "tp":   data["tp"],
                    "sl":   data["sl"],
                    "time": datetime.now().strftime("%H:%M:%S"),
                })
                st.session_state.history = st.session_state.history[:8]
                st.session_state.skey += 1
                st.rerun()
        except ValueError as ve:
            st.session_state.error = str(ve)
            st.session_state.skey += 1
            st.rerun()
        except Exception as ex:
            st.session_state.error = f"Unexpected error: {ex}"
            st.session_state.skey += 1
            st.rerun()

# ── ERROR BOX (custom HTML, no st.error) ───────────────────────────────────────
if st.session_state.error:
    H(f"""<div style="background:rgba(246,70,93,0.07);border:1px solid rgba(246,70,93,0.3);
      border-left:3px solid #F6465D;border-radius:6px;padding:11px 16px;
      color:#F6465D;font-size:.82rem;margin:8px 0 16px;
      font-family:IBM Plex Mono,monospace">
      &#10060; &nbsp; {st.session_state.error}
    </div>""")

# ── RESULT ─────────────────────────────────────────────────────────────────────
if st.session_state.result:
    d = st.session_state.result
    pu = d["pct"] >= 0
    pct_col = "#0ECB81" if pu else "#F6465D"
    pct_str = ("+" if pu else "") + f"{d['pct']:.2f}%  (24h)"

    sig_bg  = {"buy":"rgba(14,203,129,0.07)","sell":"rgba(246,70,93,0.07)","hold":"rgba(240,185,11,0.07)"}
    sig_bdr = {"buy":"#0ECB81","sell":"#F6465D","hold":"#F0B90B"}
    sig_clr = {"buy":"#0ECB81","sell":"#F6465D","hold":"#F0B90B"}
    st_key  = d["stype"]

    # Price header
    H(f"""<div style="background:#161A1E;border:1px solid #2B3139;border-radius:8px;
      padding:18px 22px;margin-bottom:14px;
      display:flex;flex-wrap:wrap;gap:20px;align-items:center;justify-content:space-between">
      <div style="display:flex;align-items:center;gap:14px">
        <div style="width:42px;height:42px;border-radius:50%;
          background:{d['color']}22;color:{d['color']};font-size:1.3rem;
          display:flex;align-items:center;justify-content:center">{d['icon']}</div>
        <div>
          <div style="font-size:1.05rem;font-weight:700;color:#EAECEF">
            {d['name']}
            <span style="color:#474D57;font-size:.8rem;font-weight:400;margin-left:6px">{d['cat']}</span>
          </div>
          <div style="font-size:.76rem;color:#474D57;margin-top:2px">{d['pair']}</div>
        </div>
      </div>
      <div>
        <div style="font-size:.64rem;color:#474D57;text-transform:uppercase;
          letter-spacing:.06em;margin-bottom:5px">Current Market Price</div>
        <div style="font-size:2rem;font-weight:700;color:#EAECEF;
          letter-spacing:-.02em;line-height:1">{fmt(d['live'])}</div>
        <div style="color:{pct_col};font-size:.86rem;font-weight:500;margin-top:4px">{pct_str}</div>
      </div>
      <div>
        <div style="font-size:.64rem;color:#474D57;text-transform:uppercase;
          letter-spacing:.06em;margin-bottom:8px">AI Signal</div>
        <div style="background:{sig_bg[st_key]};border:1px solid {sig_bdr[st_key]};
          color:{sig_clr[st_key]};font-size:.84rem;font-weight:700;
          padding:8px 22px;border-radius:4px;letter-spacing:.04em;display:inline-block">
          {d['sig']}
        </div>
      </div>
    </div>""")

    # Stat cards — build all HTML as one string to avoid f-string nesting issues
    rsi_c = "#F0B90B" if 30<=d["rsi"]<=70 else ("#0ECB81" if d["rsi"]<30 else "#F6465D")
    rr_c  = "#0ECB81" if d["rr"]>=2 else ("#F0B90B" if d["rr"]>=1 else "#F6465D")
    rsi_lbl = "Oversold" if d["rsi"]<30 else ("Overbought" if d["rsi"]>70 else "Neutral")

    def stat_card(label, value, sub, color="#EAECEF"):
        return (
            '<div style="background:#161A1E;border:1px solid #2B3139;'
            'border-radius:6px;padding:12px 14px">'
            '<div style="font-size:.67rem;color:#474D57;text-transform:uppercase;'
            'letter-spacing:.05em;font-weight:600;margin-bottom:6px">' + label + '</div>'
            '<div style="font-size:.9rem;font-weight:600;color:' + color + '">' + value + '</div>'
            '<div style="font-size:.65rem;color:#474D57;margin-top:3px">' + sub + '</div>'
            '</div>'
        )

    cards_html = (
        '<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-bottom:14px">'
        + stat_card("Entry Price", fmt(d["cp"]), "Last close")
        + stat_card("Take Profit", fmt(d["tp"]), "+" + f"{abs(d['tp_pct']):.1f}% from entry", "#0ECB81")
        + stat_card("Stop Loss",   fmt(d["sl"]), f"{d['sl_pct']:+.1f}% from entry", "#F6465D")
        + stat_card("RSI (14)",    f"{d['rsi']:.1f}", rsi_lbl, rsi_c)
        + stat_card("Risk/Reward", f"1 : {d['rr']:.2f}", d["trend"], rr_c)
        + stat_card("3M High/Low", fmt(d["high3m"]), "Low " + fmt(d["low3m"]))
        + '</div>'
    )
    H(cards_html)

    # Insight
    if d["stype"] == "buy":
        ins = (f"Price {fmt(d['cp'])} SMA-20 ({fmt(d['sma'])}) se upar hai. "
               f"RSI {d['rsi']:.0f} — overbought nahi, bullish momentum strong. "
               f"TP {fmt(d['tp'])} (+{abs(d['tp_pct']):.1f}%), SL {fmt(d['sl'])} rakhen.")
    elif d["stype"] == "sell":
        ins = (f"Price {fmt(d['cp'])} SMA-20 ({fmt(d['sma'])}) se neeche. "
               f"RSI {d['rsi']:.0f} — bearish confirm. "
               f"SL {fmt(d['sl'])} pe rakhen. TP: {fmt(d['tp'])}.")
    else:
        ins = (f"RSI {d['rsi']:.0f} neutral (30-70). Price SMA ({fmt(d['sma'])}) ke paas. "
               f"Clear direction nahi — confirmation ka wait karen.")

    H('<div style="background:#161A1E;border:1px solid #2B3139;border-left:3px solid #F0B90B;'
      'border-radius:6px;padding:12px 16px;font-size:.82rem;color:#848E9C;'
      'line-height:1.65;margin-bottom:14px">&#128161; &nbsp; ' + ins + '</div>')

    st.plotly_chart(build_chart(d), use_container_width=True)

# ── HISTORY TABLE ──────────────────────────────────────────────────────────────
if st.session_state.history:
    # Build all rows as plain string concatenation — NO f-string with inner quotes
    rows_html = ""
    for h in st.session_state.history:
        pct_v  = h.get("pct",  0.0)
        live_v = h.get("live", 0.0)
        sig_v  = h.get("sig",  "hold")
        pair_v = h.get("pair", "-")
        time_v = h.get("time", "-")
        pc = "#0ECB81" if pct_v >= 0 else "#F6465D"
        sc = "#0ECB81" if sig_v=="buy" else ("#F6465D" if sig_v=="sell" else "#F0B90B")
        lb = "BUY" if sig_v=="buy" else ("SELL" if sig_v=="sell" else "HOLD")
        ar = "▲" if sig_v=="buy" else ("▼" if sig_v=="sell" else "◆")
        pct_sign = "+" if pct_v >= 0 else ""
        rows_html += (
            '<div style="padding:9px 16px;display:grid;'
            'grid-template-columns:1.3fr 1fr 1fr 1fr 1fr;'
            'font-size:.8rem;border-bottom:1px solid rgba(43,49,57,0.5);'
            'align-items:center">'
            '<span style="color:#EAECEF;font-weight:600">' + pair_v + '</span>'
            '<span style="color:' + pc + '">' + pct_sign + f"{pct_v:.2f}" + '%</span>'
            '<span style="color:#848E9C">' + fmt(live_v) + '</span>'
            '<span style="color:' + sc + ';font-weight:700">' + lb + ' ' + ar + '</span>'
            '<span style="color:#474D57">' + time_v + '</span>'
            '</div>'
        )

    table_html = (
        '<div style="background:#161A1E;border:1px solid #2B3139;'
        'border-radius:8px;overflow:hidden;margin-top:20px">'
        '<div style="background:#1E2329;padding:9px 16px;'
        'display:grid;grid-template-columns:1.3fr 1fr 1fr 1fr 1fr;'
        'font-size:.68rem;font-weight:600;color:#474D57;'
        'text-transform:uppercase;letter-spacing:.06em;'
        'border-bottom:1px solid #2B3139">'
        '<span>Pair</span><span>24h</span><span>Price</span>'
        '<span>Signal</span><span>Time</span>'
        '</div>'
        + rows_html +
        '</div>'
    )
    H(table_html)

H('<div style="text-align:center;padding:18px;color:#2B3139;font-size:.7rem;'
  'border-top:1px solid #2B3139;margin-top:24px">'
  '&#9888; Educational only — not financial advice &nbsp;|&nbsp;'
  ' Data: Yahoo Finance &nbsp;|&nbsp; Strategy: RSI-14 + SMA-20'
  '</div>')

H('</div>')
