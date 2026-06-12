import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io, re, urllib.request, json as pyjson, uuid
from datetime import datetime

# NEW
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest, proportion_confint

# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="BI Dashboard Builder",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0f1117; }

section[data-testid="stSidebar"] {
    background: #151820 !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* ── Metric card glassmorphism ── */
.metric-card {
    background: rgba(21, 24, 32, 0.6);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 20px 16px 16px 16px;
    text-align: center;
    position: relative; overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,0.35),
                inset 0 1px 0 rgba(255,255,255,0.07);
    transition: transform .18s ease, box-shadow .18s ease;
}
.metric-card::before {
    content:'';
    position:absolute; top:0; left:0; right:0; height:1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.13), transparent);
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(92,124,250,0.16),
                inset 0 1px 0 rgba(255,255,255,0.09);
}
.metric-value {
    font-size:2rem; font-weight:700; color:#4fc3f7; line-height:1; letter-spacing:-0.02em;
}
.metric-label {
    font-size:0.68rem; color:#8892a4; margin-top:7px; text-transform:uppercase; letter-spacing:0.07em;
}
.metric-delta { font-size:0.8rem; font-weight:600; margin-top:5px; }
.metric-delta.up   { color:#81c784; }
.metric-delta.down { color:#f06292; }
.metric-delta.flat { color:#5a6072; }

/* ── Module headers ── */
.module-header {
    background: linear-gradient(90deg, rgba(26,42,26,0.6), rgba(15,17,23,0));
    backdrop-filter: blur(8px);
    border-left: 3px solid #4caf50;
    border-radius: 0 10px 10px 0;
    padding: 10px 16px; margin: 8px 0 16px 0;
    font-weight: 600; font-size: 1rem; color: #e0e0e0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}
.module-header-blue {
    border-left-color:#5c7cfa;
    background: linear-gradient(90deg, rgba(26,26,54,0.6), rgba(15,17,23,0));
}
.module-header-teal {
    border-left-color:#26c6da;
    background: linear-gradient(90deg, rgba(10,40,42,0.6), rgba(15,17,23,0));
}
.module-header-purple {
    border-left-color:#ba68c8;
    background: linear-gradient(90deg, rgba(44,20,58,0.60), rgba(15,17,23,0));
}

/* ── Badges ── */
.badge-warn {
    display:inline-block; background:rgba(255,152,0,0.1); border:1px solid #ff9800;
    border-radius:6px; padding:3px 10px; font-size:0.8rem; color:#ffb74d; margin:3px;
}
.badge-ok {
    display:inline-block; background:rgba(76,175,80,0.1); border:1px solid #4caf50;
    border-radius:6px; padding:3px 10px; font-size:0.8rem; color:#81c784; margin:3px;
}
.badge-info {
    display:inline-block; background:rgba(92,124,250,0.10); border:1px solid #5c7cfa;
    border-radius:6px; padding:3px 10px; font-size:0.8rem; color:#9fb2ff; margin:3px;
}

/* ── Log entries ── */
.log-entry {
    background:rgba(17,19,24,0.9); border-left:2px solid #4caf50;
    border-radius:0 6px 6px 0; padding:5px 12px; margin:3px 0;
    font-size:0.82rem; color:#9ca3af; font-family:monospace;
}

/* ── Chart glass card ── */
.chart-card {
    background: rgba(21,24,32,0.55);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 14px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.28);
    margin-bottom: 16px;
}

/* ── Executive summary ── */
.exec-summary {
    background: rgba(92,124,250,0.07);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(92,124,250,0.22);
    border-radius: 14px; padding:20px 24px; margin:8px 0 20px 0;
    box-shadow: 0 4px 24px rgba(92,124,250,0.08);
}
.exec-summary h4 {
    color:#7c9dfa; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:10px;
}
.exec-summary p  {
    color:#c9d1d9; font-size:0.95rem; line-height:1.75; margin:0;
}

/* ── Analysis cards ── */
.analysis-box {
    background: rgba(186,104,200,0.08);
    border: 1px solid rgba(186,104,200,0.20);
    border-radius: 14px;
    padding: 18px 20px;
    margin: 10px 0 16px 0;
    box-shadow: 0 4px 18px rgba(186,104,200,0.08);
}
.analysis-box h4 {
    color:#d2a5ef;
    font-size:0.82rem;
    text-transform:uppercase;
    letter-spacing:0.08em;
    margin-bottom:10px;
}
.analysis-box p, .analysis-box li {
    color:#c9d1d9;
    font-size:0.92rem;
    line-height:1.7;
}
.result-ok {
    background: rgba(76,175,80,0.10);
    border: 1px solid rgba(76,175,80,0.35);
    border-radius: 12px;
    padding: 14px 16px;
    color:#b8efc0;
    margin: 10px 0;
}
.result-warn {
    background: rgba(255,152,0,0.10);
    border: 1px solid rgba(255,152,0,0.35);
    border-radius: 12px;
    padding: 14px 16px;
    color:#ffd08a;
    margin: 10px 0;
}
.result-bad {
    background: rgba(240,98,146,0.10);
    border: 1px solid rgba(240,98,146,0.35);
    border-radius: 12px;
    padding: 14px 16px;
    color:#ffb3ca;
    margin: 10px 0;
}

/* ── Step badge in sidebar ── */
.step-row { display:flex; align-items:center; gap:10px; padding:5px 0; }
.step-dot  { width:8px; height:8px; border-radius:50%; flex-shrink:0; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(21,24,32,0.8);
    backdrop-filter: blur(6px);
    border-radius:10px; padding:4px; gap:4px;
}
.stTabs [data-baseweb="tab"] { border-radius:7px; color:#8892a4; font-weight:500; }
.stTabs [aria-selected="true"] { background:#1e2235 !important; color:#e0e0e0 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  PLOTLY THEME
# ══════════════════════════════════════════════════════════════
PLOTLY_THEME = dict(
    paper_bgcolor='#151820',
    plot_bgcolor='#151820',
    font=dict(family='Inter', color='#c9d1d9', size=11),
    colorway=['#5c7cfa','#4fc3f7','#81c784','#ffb74d','#f06292','#ba68c8','#4dd0e1','#ff8a65'],
    xaxis=dict(
        gridcolor='#1e2235', linecolor='#2a2d3a', zerolinecolor='#2a2d3a',
        title_font=dict(size=11, color='#5a6072'),
        tickfont=dict(size=10, color='#8892a4')
    ),
    yaxis=dict(
        gridcolor='#1e2235', linecolor='#2a2d3a', zerolinecolor='#2a2d3a',
        title_font=dict(size=11, color='#5a6072'),
        tickfont=dict(size=10, color='#8892a4')
    ),
    title=dict(font=dict(size=16, color='#e0e0e0', family='Inter'), x=0.02, xanchor='left'),
    legend=dict(
        bgcolor='rgba(21,24,32,0.8)',
        bordercolor='#2a2d3a',
        borderwidth=1,
        font=dict(size=11)
    ),
    margin=dict(l=50, r=30, t=55, b=50),
    hoverlabel=dict(
        bgcolor='#1e2235',
        bordercolor='#5c7cfa',
        font=dict(color='#e0e0e0', size=12)
    ),
)

def style_fig(fig):
    if fig is None:
        return None
    fig.update_layout(**PLOTLY_THEME)
    fig.update_xaxes(
        showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.04)',
        zeroline=False, showline=False, tickcolor='rgba(0,0,0,0)'
    )
    fig.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.04)',
        zeroline=False, showline=False, tickcolor='rgba(0,0,0,0)'
    )
    return fig

def get_df():
    if st.session_state.df_clean is not None:
        return st.session_state.df_clean
    return st.session_state.df_raw

# ══════════════════════════════════════════════════════════════
#  HELPERS — ANALYSIS
# ══════════════════════════════════════════════════════════════
def safe_numeric(s):
    return pd.to_numeric(s, errors='coerce')

def format_p_value(p):
    if pd.isna(p):
        return "—"
    if p < 0.0001:
        return "< 0.0001"
    return f"{p:.4f}"

def significance_label(p, alpha=0.05):
    if pd.isna(p):
        return "Не удалось оценить"
    return "Статистически значимо" if p < alpha else "Недостаточно оснований считать различие значимым"

def calc_relative_uplift(a, b):
    if a == 0 or pd.isna(a) or pd.isna(b):
        return np.nan
    return (b - a) / a * 100

def cohen_d(x, y):
    x = pd.Series(x).dropna()
    y = pd.Series(y).dropna()
    if len(x) < 2 or len(y) < 2:
        return np.nan
    nx, ny = len(x), len(y)
    vx, vy = x.var(ddof=1), y.var(ddof=1)
    pooled = np.sqrt(((nx - 1) * vx + (ny - 1) * vy) / (nx + ny - 2))
    if pooled == 0 or np.isnan(pooled):
        return np.nan
    return (y.mean() - x.mean()) / pooled

def eta_interpretation(val):
    if pd.isna(val):
        return "—"
    av = abs(val)
    if av < 0.2:
        return "очень слабый эффект"
    if av < 0.5:
        return "слабый эффект"
    if av < 0.8:
        return "средний эффект"
    return "сильный эффект"

def render_metric_card(value, label, delta="", delta_cls="flat"):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {f'<div class="metric-delta {delta_cls}">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════
_defaults = {
    'df_raw': None,
    'df_clean': None,
    'clean_log': [],
    'clean_done': False,
    'charts': [],
    'exec_summary': '',
    'file_name': '',
    'analysis_result': None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📊 BI Dashboard Builder")
    st.markdown("---")

    steps = [
        ("📁", "Данные загружены",  st.session_state.df_raw is not None),
        ("🧹", "Очистка применена", st.session_state.clean_done),
        ("📐", "Анализ доступен",   get_df() is not None),
        ("🤖", "Графики готовы",    len(st.session_state.charts) > 0),
        ("📦", "Экспорт доступен",  len(st.session_state.charts) > 0 or get_df() is not None),
    ]
    for icon, label, done in steps:
        dot_color = "#4caf50" if done else "#2a2d3a"
        txt_color = "#e0e0e0" if done else "#5a5f72"
        st.markdown(f"""
        <div class="step-row">
            <div class="step-dot" style="background:{dot_color};
                 box-shadow:{'0 0 6px #4caf5099' if done else 'none'}"></div>
            <span style="font-size:0.85rem;color:{txt_color};
                  font-weight:{'500' if done else '400'}">{icon} {label}</span>
        </div>""", unsafe_allow_html=True)

    if st.session_state.file_name:
        st.markdown(
            f'<small style="color:#5a6072;padding-left:18px">📄 {st.session_state.file_name}</small>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("**🔑 Groq API**")
    st.markdown(
        '<a href="https://console.groq.com" target="_blank" '
        'style="font-size:0.78rem;color:#4fc3f7">→ Получить бесплатно</a>',
        unsafe_allow_html=True
    )
    api_key = st.text_input("API Key", type="password", placeholder="gsk_...")

    if api_key:
        if st.button("🔍 Проверить подключение", use_container_width=True):
            try:
                p = pyjson.dumps({
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role":"user","content":"ping"}],
                    "max_tokens": 3
                }).encode()
                req = urllib.request.Request(
                    "https://api.groq.com/openai/v1/chat/completions",
                    data=p,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0"
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as r:
                    pyjson.loads(r.read())
                st.session_state['api_status'] = 'ok'
            except Exception as e:
                err = str(e)
                st.session_state['api_status'] = (
                    'invalid' if '401' in err else
                    'forbidden' if '403' in err else
                    'limit' if '429' in err else f'error:{err[:50]}'
                )

        _s = st.session_state.get('api_status')
        _msg = {
            'ok':        ("✅ Подключён", "#81c784", "rgba(76,175,80,0.1)",  "#4caf50"),
            'invalid':   ("❌ Неверный ключ", "#ef9a9a", "rgba(244,67,54,0.1)",  "#f44336"),
            'forbidden': ("⚠️ Доступ закрыт", "#ffb74d", "rgba(255,152,0,0.1)",  "#ff9800"),
            'limit':     ("⏳ Лимит запросов", "#ffb74d", "rgba(255,152,0,0.1)",  "#ff9800"),
        }.get(_s)

        if _msg:
            txt, tc, bg, bc = _msg
        elif _s and _s.startswith('error'):
            txt, tc, bg, bc = _s, "#ef9a9a", "rgba(244,67,54,0.1)", "#f44336"
        else:
            txt = None

        if txt:
            st.markdown(f"""<div style="background:{bg};border:1px solid {bc};
                border-radius:8px;padding:7px 12px;font-size:0.8rem;
                color:{tc};margin-top:4px">{txt}</div>""", unsafe_allow_html=True)

    GROQ_MODELS = {
        "⚡ Llama 3.3 70B (лучший)":  "llama-3.3-70b-versatile",
        "🚀 Llama 3.1 8B (быстрый)":  "llama-3.1-8b-instant",
        "🧠 Llama 3.1 70B":           "llama-3.1-70b-versatile",
        "🔥 Mixtral 8x7B":            "mixtral-8x7b-32768",
        "💎 Gemma 2 9B":              "gemma2-9b-it",
        "🌟 DeepSeek R1 70B":         "deepseek-r1-distill-llama-70b",
    }
    model_label = st.selectbox("Модель ИИ", list(GROQ_MODELS.keys()))
    llm_model   = GROQ_MODELS[model_label]
    st.markdown(
        '<small style="color:#5a5f72">Без ключа — встроенный генератор</small>',
        unsafe_allow_html=True
    )

    _df = get_df()
    if _df is not None:
        st.markdown("---")
        st.markdown("**📋 Датасет**")
        st.markdown(f"""<div style="font-size:0.82rem;color:#8892a4;line-height:2">
        Строк: <b style="color:#4fc3f7">{len(_df):,}</b><br>
        Колонок: <b style="color:#4fc3f7">{len(_df.columns)}</b><br>
        Числовых: <b style="color:#81c784">{len(_df.select_dtypes(include='number').columns)}</b><br>
        Текстовых: <b style="color:#ffb74d">{len(_df.select_dtypes(include='object').columns)}</b>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "  📁 Загрузка  ",
    "  🧹 Очистка  ",
    "  📐 Анализ  ",
    "  🤖 ИИ + Графики  ",
    "  📦 Экспорт  "
])

# ══════════════════════════════════════════════════════════════
#  TAB 1 — ЗАГРУЗКА
# ══════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="module-header">📁 Загрузка данных</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Загрузите CSV или Excel файл",
        type=["csv", "xlsx", "xls"],
        help="Поддерживаются разделители: запятая, точка с запятой, табуляция, | "
    )

    if uploaded is not None:
        try:
            raw_bytes = uploaded.read()
            fname = uploaded.name

            if fname.lower().endswith(".csv"):
                df_loaded = None
                for sep in [',', ';', '\t', '|']:
                    try:
                        df_loaded = pd.read_csv(io.BytesIO(raw_bytes), sep=sep, encoding='utf-8', low_memory=False)
                        if len(df_loaded.columns) > 1:
                            break
                    except Exception:
                        continue
                if df_loaded is None or len(df_loaded.columns) <= 1:
                    for sep in [',', ';', '\t', '|']:
                        try:
                            df_loaded = pd.read_csv(io.BytesIO(raw_bytes), sep=sep, encoding='latin-1', low_memory=False)
                            if len(df_loaded.columns) > 1:
                                break
                        except Exception:
                            continue
            else:
                df_loaded = pd.read_excel(io.BytesIO(raw_bytes))

            if fname != st.session_state.file_name:
                st.session_state.df_raw = df_loaded.copy()
                st.session_state.df_clean = None
                st.session_state.clean_done = False
                st.session_state.clean_log = []
                st.session_state.charts = []
                st.session_state.exec_summary = ''
                st.session_state.analysis_result = None
                st.session_state.file_name = fname

        except Exception as e:
            st.error(f"❌ Ошибка чтения файла: {e}")

    if st.session_state.df_raw is not None:
        df = st.session_state.df_raw
        st.success(
            f"✅ Файл загружен: **{st.session_state.file_name}** — "
            f"{len(df):,} строк × {len(df.columns)} колонок"
        )
        st.markdown("---")

        nulls_n = int(df.isnull().sum().sum())
        dupes_n = int(df.duplicated().sum())
        c1, c2, c3, c4 = st.columns(4)
        with c1: render_metric_card(f"{len(df):,}", "Строк")
        with c2: render_metric_card(f"{len(df.columns)}", "Колонок")
        with c3: render_metric_card(
            f"{nulls_n:,}",
            "Пропусков",
            "▲ требуют внимания" if nulls_n > 0 else "✓ Чисто",
            "down" if nulls_n > 0 else "up"
        )
        with c4: render_metric_card(
            f"{dupes_n:,}",
            "Дубликатов",
            "▲ есть дубли" if dupes_n > 0 else "✓ Уникальные",
            "down" if dupes_n > 0 else "up"
        )

        st.markdown("#### Предпросмотр данных")
        st.dataframe(df.head(20), use_container_width=True, height=320)

        with st.expander("📋 Схема колонок (типы, пропуски, уникальные значения)"):
            schema = pd.DataFrame({
                'Колонка': df.columns,
                'Тип': df.dtypes.astype(str).values,
                'Пропусков': df.isnull().sum().values,
                '% пропусков': (df.isnull().mean() * 100).round(1).values,
                'Уникальных': df.nunique().values,
                'Пример': [
                    str(df[c].dropna().iloc[0]) if df[c].notna().any() else '—'
                    for c in df.columns
                ],
            })
            st.dataframe(schema, use_container_width=True, height=280)

        with st.expander("📊 Базовая статистика числовых колонок"):
            num_df = df.select_dtypes(include='number')
            if not num_df.empty:
                st.dataframe(num_df.describe().round(2), use_container_width=True)
            else:
                st.info("Числовых колонок нет")

        st.markdown("---")
        st.info("👉 Перейдите на вкладку **🧹 Очистка** или **📐 Анализ**")

    else:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#5a6072">
            <div style="font-size:3rem;margin-bottom:16px">📂</div>
            <div style="font-size:1.1rem;font-weight:500;color:#8892a4;margin-bottom:8px">
                Загрузите CSV или Excel файл выше
            </div>
            <div style="font-size:0.85rem">
                Поддерживаются форматы: .csv, .xlsx, .xls
            </div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TAB 2 — ОЧИСТКА
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="module-header">🧹 Очистка данных</div>', unsafe_allow_html=True)

    if st.session_state.df_raw is None:
        st.info("👆 Сначала загрузите файл на вкладке 📁")
    else:
        src = st.session_state.df_raw
        nulls = src.isnull().sum()
        null_cols = nulls[nulls > 0]
        dupes_n = int(src.duplicated().sum())
        num_cols = src.select_dtypes(include='number').columns.tolist()
        cat_cols = src.select_dtypes(include='object').columns.tolist()

        if st.session_state.clean_done:
            df_c = st.session_state.df_clean
            dc1, dc2 = st.columns(2)
            dc1.success(f"✅ Очистка применена: {len(df_c):,} строк × {len(df_c.columns)} колонок")
            if dc2.button("🔄 Сбросить и переделать", use_container_width=True):
                st.session_state.df_clean = None
                st.session_state.clean_done = False
                st.session_state.clean_log = []
                st.rerun()

            if st.session_state.clean_log:
                with st.expander("📋 Лог выполненных действий"):
                    for entry in st.session_state.clean_log:
                        st.markdown(f'<div class="log-entry">{entry}</div>', unsafe_allow_html=True)

        else:
            st.markdown("#### 🔍 Диагностика")
            dg = st.columns(4)
            for cw, cond, txt in [
                (dg[0], len(null_cols) > 0, f"⚠️ Пропуски: {len(null_cols)} кол."),
                (dg[1], dupes_n > 0, f"⚠️ Дубликатов: {dupes_n}"),
                (dg[2], len(num_cols) > 0, f"📊 Числовых: {len(num_cols)}"),
                (dg[3], len(cat_cols) > 0, f"🔤 Текстовых: {len(cat_cols)}"),
            ]:
                cls = "badge-warn" if cond else "badge-ok"
                cw.markdown(f'<span class="{cls}">{txt}</span>', unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### ⚙️ Настройки очистки")
            cl, cr = st.columns(2)
            actions = {}

            with cl:
                st.markdown("**1. Пропущенные значения**")
                if len(null_cols):
                    for col in null_cols.index:
                        pct = null_cols[col] / len(src) * 100
                        is_num = pd.api.types.is_numeric_dtype(src[col])
                        st.markdown(
                            f'<small style="color:#8892a4">*{col}* — {null_cols[col]} ({pct:.0f}%)</small>',
                            unsafe_allow_html=True
                        )
                        opts = (
                            ["Оставить","Удалить строки","Заполнить медианой","Заполнить нулём","Заполнить средним"]
                            if is_num else
                            ["Оставить","Удалить строки","Заполнить модой",'Заполнить "Unknown"']
                        )
                        sel = st.selectbox("", opts, key=f"null_{col}")
                        actions[f'null_{col}'] = (col, sel)
                else:
                    st.markdown('<span class="badge-ok">✓ Пропусков нет</span>', unsafe_allow_html=True)

                st.markdown("<br>**2. Дубликаты**", unsafe_allow_html=True)
                if dupes_n > 0:
                    actions['dupes'] = st.radio(
                        f"Найдено {dupes_n} дублирующихся строк:",
                        ["Оставить","Удалить (оставить первый)","Удалить все копии"],
                        key="dup_act"
                    )
                else:
                    st.markdown('<span class="badge-ok">✓ Дубликатов нет</span>', unsafe_allow_html=True)

            with cr:
                st.markdown("**3. Выбросы (правило 3σ)**")
                if num_cols:
                    out_act = st.selectbox(
                        "Действие:",
                        ["Оставить","Пометить флагом","Удалить строки","Заменить медианой"],
                        key="out_act"
                    )
                    out_cols = st.multiselect(
                        "В колонках:",
                        num_cols,
                        default=num_cols[:min(3, len(num_cols))]
                    )
                    if out_act != "Оставить":
                        actions['outliers'] = (out_act, out_cols)
                else:
                    st.markdown('<span class="badge-ok">✓ Числовых колонок нет</span>', unsafe_allow_html=True)

                st.markdown("<br>**4. Конвертировать в дату**", unsafe_allow_html=True)
                auto_dates = [
                    c for c in src.columns
                    if any(k in c.lower() for k in ['date','time','дата','год','year'])
                ]
                date_sel = st.multiselect(
                    "Выбрать колонки:",
                    src.columns.tolist(),
                    default=auto_dates
                )
                if date_sel:
                    actions['dates'] = date_sel

                st.markdown("<br>**5. Удалить ненужные колонки**", unsafe_allow_html=True)
                drop_sel = st.multiselect("Выбрать:", src.columns.tolist(), key="drop_cols")
                if drop_sel:
                    actions['drop'] = drop_sel

            st.markdown("---")
            if st.button("✅ Применить очистку", type="primary", use_container_width=True, key="apply_clean"):
                df2 = src.copy()
                log = []

                if 'drop' in actions:
                    df2 = df2.drop(columns=actions['drop'], errors='ignore')
                    log.append(f"🗑 Удалены колонки: {actions['drop']}")

                for k, (col, action) in [(k, v) for k, v in actions.items() if k.startswith('null_')]:
                    if col not in df2.columns or action == "Оставить":
                        continue
                    if action == "Удалить строки":
                        b = len(df2)
                        df2 = df2.dropna(subset=[col])
                        log.append(f"🗑 [{col}] удалено {b - len(df2)} строк")
                    elif "медиан" in action:
                        m = df2[col].median()
                        df2[col] = df2[col].fillna(m)
                        log.append(f"📊 [{col}] nulls → медиана {m:.2f}")
                    elif "средним" in action:
                        m = df2[col].mean()
                        df2[col] = df2[col].fillna(m)
                        log.append(f"📊 [{col}] nulls → среднее {m:.2f}")
                    elif "нулём" in action:
                        df2[col] = df2[col].fillna(0)
                        log.append(f"📊 [{col}] nulls → 0")
                    elif "модой" in action:
                        m = df2[col].mode()
                        m = m.iloc[0] if not m.empty else "Unknown"
                        df2[col] = df2[col].fillna(m)
                        log.append(f"📊 [{col}] nulls → '{m}'")
                    elif "Unknown" in action:
                        df2[col] = df2[col].fillna("Unknown")
                        log.append(f"📊 [{col}] nulls → 'Unknown'")

                if 'dupes' in actions:
                    act = actions['dupes']
                    if "первый" in act:
                        b = len(df2)
                        df2 = df2.drop_duplicates(keep='first')
                        log.append(f"🔄 Дубли удалены: {b - len(df2)} строк")
                    elif "копии" in act:
                        b = len(df2)
                        df2 = df2.drop_duplicates(keep=False)
                        log.append(f"🔄 Все копии удалены: {b - len(df2)} строк")

                if 'outliers' in actions:
                    act, cols = actions['outliers']
                    for col in cols:
                        if col not in df2.columns:
                            continue
                        srs = safe_numeric(df2[col])
                        m, s = srs.mean(), srs.std()
                        if pd.isna(s) or s == 0:
                            continue
                        mask = (srs - m).abs() > 3 * s
                        n_out = int(mask.sum())
                        if n_out == 0:
                            continue
                        if "флаг" in act:
                            df2[f'{col}_outlier'] = mask.astype(int)
                            log.append(f"🚩 [{col}] помечено {n_out} выбросов")
                        elif "Удалить" in act:
                            df2 = df2.loc[~mask].copy()
                            log.append(f"🗑 [{col}] удалено {n_out} строк-выбросов")
                        elif "медиан" in act:
                            med = srs.median()
                            df2.loc[mask, col] = med
                            log.append(f"📊 [{col}] {n_out} выбросов → медиана {med:.2f}")

                if 'dates' in actions:
                    for col in actions['dates']:
                        if col not in df2.columns:
                            continue
                        try:
                            df2[col] = pd.to_datetime(df2[col], errors='coerce')
                            log.append(f"📅 [{col}] конвертирован в datetime")
                        except Exception as ex:
                            log.append(f"⚠️ [{col}] не удалось: {ex}")

                if not log:
                    log.append("✓ Данные чистые — настройки не изменились")

                st.session_state.df_clean = df2
                st.session_state.clean_log = log
                st.session_state.clean_done = True
                st.session_state.analysis_result = None
                st.rerun()

# ══════════════════════════════════════════════════════════════
#  TAB 3 — АНАЛИЗ
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="module-header module-header-purple">📐 A/B-тестирование и статистический анализ</div>', unsafe_allow_html=True)

    df_work = get_df()

    if df_work is None:
        st.info("👆 Сначала загрузите файл на вкладке 📁")
    else:
        if not st.session_state.clean_done:
            st.warning("💡 Очистка не применена — анализ выполняется по текущему рабочему датасету.")

        st.markdown("""
        <div class="analysis-box">
            <h4>Что умеет вкладка</h4>
            <p>
                Здесь можно сравнивать две группы A/B: проверять различие конверсии,
                сравнивать средние значения метрик, строить доверительные интервалы
                и получать краткую интерпретацию результата.
            </p>
        </div>
        """, unsafe_allow_html=True)

        cat_cols = df_work.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
        num_cols = df_work.select_dtypes(include='number').columns.tolist()

        c0, c00 = st.columns([2, 1])
        group_col = c0.selectbox(
            "Колонка группировки (A/B-группы)",
            options=cat_cols if cat_cols else df_work.columns.tolist(),
            help="Например: variant, group, test_group, cohort"
        )

        if group_col:
            group_values = df_work[group_col].dropna().astype(str).unique().tolist()
            group_values = sorted(group_values)

            if len(group_values) < 2:
                st.error("В выбранной колонке меньше двух уникальных групп.")
            else:
                mode = c00.radio(
                    "Тип анализа",
                    ["Конверсия (0/1)", "Сравнение средних"],
                    index=0,
                    horizontal=False
                )

                c1, c2 = st.columns(2)
                group_a = c1.selectbox("Группа A", group_values, index=0)
                idx_b = 1 if len(group_values) > 1 else 0
                group_b = c2.selectbox("Группа B", group_values, index=idx_b)

                if group_a == group_b:
                    st.warning("Выберите разные группы A и B.")
                else:
                    alpha = st.slider("Уровень значимости α", 0.01, 0.10, 0.05, 0.01)

                    subset = df_work[df_work[group_col].astype(str).isin([group_a, group_b])].copy()
                    subset['_ab_group_'] = subset[group_col].astype(str)

                    base_info = subset['_ab_group_'].value_counts().rename_axis('group').reset_index(name='n')
                    st.markdown("#### 📋 Размеры групп")
                    bi1, bi2 = st.columns(2)
                    a_n = int((subset['_ab_group_'] == group_a).sum())
                    b_n = int((subset['_ab_group_'] == group_b).sum())
                    with bi1:
                        render_metric_card(f"{a_n:,}", f"Размер {group_a}")
                    with bi2:
                        render_metric_card(f"{b_n:,}", f"Размер {group_b}")

                    if mode == "Конверсия (0/1)":
                        binary_candidates = []
                        for c in subset.columns:
                            uniq = set(pd.Series(subset[c]).dropna().astype(str).str.lower().unique().tolist())
                            if uniq and uniq.issubset({'0', '1', 'true', 'false', 'yes', 'no'}):
                                binary_candidates.append(c)

                        metric_col = st.selectbox(
                            "Бинарная метрика конверсии",
                            options=binary_candidates if binary_candidates else subset.columns.tolist(),
                            help="Ожидается 0/1, True/False, Yes/No"
                        )

                        if st.button("🚀 Рассчитать A/B тест", type="primary", use_container_width=True):
                            dfa = subset[subset['_ab_group_'] == group_a].copy()
                            dfb = subset[subset['_ab_group_'] == group_b].copy()

                            def to_binary(s):
                                mapping = {
                                    '1': 1, '0': 0,
                                    'true': 1, 'false': 0,
                                    'yes': 1, 'no': 0
                                }
                                return s.astype(str).str.lower().map(mapping)

                            xa = to_binary(dfa[metric_col]).dropna()
                            xb = to_binary(dfb[metric_col]).dropna()

                            if len(xa) == 0 or len(xb) == 0:
                                st.error("Не удалось привести выбранную колонку к бинарной метрике 0/1.")
                            else:
                                succ = np.array([int(xa.sum()), int(xb.sum())])
                                obs = np.array([int(xa.count()), int(xb.count())])

                                try:
                                    z_stat, p_val = proportions_ztest(count=succ, nobs=obs)
                                except Exception:
                                    z_stat, p_val = np.nan, np.nan

                                conv_a = succ[0] / obs[0] if obs[0] else np.nan
                                conv_b = succ[1] / obs[1] if obs[1] else np.nan
                                uplift = calc_relative_uplift(conv_a, conv_b)
                                abs_diff = (conv_b - conv_a) * 100 if pd.notna(conv_a) and pd.notna(conv_b) else np.nan

                                ci_a_low, ci_a_high = proportion_confint(succ[0], obs[0], alpha=alpha, method='wilson')
                                ci_b_low, ci_b_high = proportion_confint(succ[1], obs[1], alpha=alpha, method='wilson')

                                k1, k2, k3, k4 = st.columns(4)
                                with k1:
                                    render_metric_card(f"{conv_a*100:.2f}%", f"CR {group_a}")
                                with k2:
                                    render_metric_card(f"{conv_b*100:.2f}%", f"CR {group_b}")
                                with k3:
                                    render_metric_card(
                                        f"{abs_diff:.2f} п.п." if pd.notna(abs_diff) else "—",
                                        "Абс. разница",
                                        f"{uplift:.2f}% uplift" if pd.notna(uplift) else "",
                                        "up" if pd.notna(uplift) and uplift >= 0 else "down"
                                    )
                                with k4:
                                    render_metric_card(format_p_value(p_val), "p-value")

                                res_class = "result-ok" if pd.notna(p_val) and p_val < alpha else "result-warn"
                                direction = (
                                    f"Группа **{group_b}** лучше по конверсии."
                                    if pd.notna(conv_a) and pd.notna(conv_b) and conv_b > conv_a
                                    else f"Группа **{group_a}** лучше по конверсии."
                                )

                                st.markdown(f"""
                                <div class="{res_class}">
                                    <b>Вывод:</b> {significance_label(p_val, alpha)}.
                                    {direction}
                                </div>
                                """, unsafe_allow_html=True)

                                result_tbl = pd.DataFrame({
                                    'Группа': [group_a, group_b],
                                    'Наблюдений': [obs[0], obs[1]],
                                    'Конверсий': [succ[0], succ[1]],
                                    'Конверсия %': [round(conv_a * 100, 3), round(conv_b * 100, 3)],
                                    f'CI {100*(1-alpha):.0f}% low': [round(ci_a_low * 100, 3), round(ci_b_low * 100, 3)],
                                    f'CI {100*(1-alpha):.0f}% high': [round(ci_a_high * 100, 3), round(ci_b_high * 100, 3)],
                                })
                                st.dataframe(result_tbl, use_container_width=True)

                                fig_conv = go.Figure()
                                fig_conv.add_trace(go.Bar(
                                    x=[group_a, group_b],
                                    y=[conv_a * 100, conv_b * 100],
                                    marker_color=['#5c7cfa', '#ba68c8'],
                                    text=[f"{conv_a*100:.2f}%", f"{conv_b*100:.2f}%"],
                                    textposition='outside'
                                ))
                                fig_conv.update_layout(title=f"A/B тест конверсии: {metric_col}", yaxis_title="Конверсия, %")
                                st.plotly_chart(style_fig(fig_conv), use_container_width=True)

                    else:
                        metric_col = st.selectbox(
                            "Числовая метрика",
                            options=num_cols if num_cols else subset.columns.tolist(),
                            help="Например: revenue, check, duration, margin"
                        )
                        equal_var = st.checkbox("Предполагать равенство дисперсий", value=False)

                        if st.button("🚀 Рассчитать статистику", type="primary", use_container_width=True):
                            dfa = subset.loc[subset['_ab_group_'] == group_a, metric_col]
                            dfb = subset.loc[subset['_ab_group_'] == group_b, metric_col]

                            xa = safe_numeric(dfa).dropna()
                            xb = safe_numeric(dfb).dropna()

                            if len(xa) < 2 or len(xb) < 2:
                                st.error("Для t-test нужно минимум по 2 наблюдения в каждой группе.")
                            else:
                                try:
                                    t_stat, p_val = stats.ttest_ind(xa, xb, equal_var=equal_var, nan_policy='omit')
                                except Exception:
                                    t_stat, p_val = np.nan, np.nan

                                mean_a, mean_b = xa.mean(), xb.mean()
                                med_a, med_b = xa.median(), xb.median()
                                uplift = calc_relative_uplift(mean_a, mean_b)
                                diff = mean_b - mean_a
                                eff = cohen_d(xa, xb)

                                k1, k2, k3, k4 = st.columns(4)
                                with k1:
                                    render_metric_card(f"{mean_a:,.2f}", f"Mean {group_a}")
                                with k2:
                                    render_metric_card(f"{mean_b:,.2f}", f"Mean {group_b}")
                                with k3:
                                    render_metric_card(
                                        f"{diff:,.2f}",
                                        "Разница mean",
                                        f"{uplift:.2f}% uplift" if pd.notna(uplift) else "",
                                        "up" if pd.notna(diff) and diff >= 0 else "down"
                                    )
                                with k4:
                                    render_metric_card(format_p_value(p_val), "p-value")

                                res_class = "result-ok" if pd.notna(p_val) and p_val < alpha else "result-warn"
                                better = group_b if mean_b > mean_a else group_a

                                st.markdown(f"""
                                <div class="{res_class}">
                                    <b>Вывод:</b> {significance_label(p_val, alpha)}.
                                    По средней метрике <b>{metric_col}</b> лучше выглядит группа <b>{better}</b>.
                                    Эффект Cohen's d = {eff:.3f} ({eta_interpretation(eff)}).
                                </div>
                                """, unsafe_allow_html=True)

                                result_tbl = pd.DataFrame({
                                    'Показатель': ['N', 'Mean', 'Median', 'Std', 'Min', 'Max'],
                                    group_a: [len(xa), round(mean_a, 4), round(med_a, 4), round(xa.std(ddof=1), 4), round(xa.min(), 4), round(xa.max(), 4)],
                                    group_b: [len(xb), round(mean_b, 4), round(med_b, 4), round(xb.std(ddof=1), 4), round(xb.min(), 4), round(xb.max(), 4)],
                                })
                                st.dataframe(result_tbl, use_container_width=True)

                                fig_box = px.box(
                                    subset[subset['_ab_group_'].isin([group_a, group_b])],
                                    x='_ab_group_',
                                    y=metric_col,
                                    color='_ab_group_',
                                    title=f"Сравнение распределений: {metric_col}",
                                    color_discrete_sequence=['#5c7cfa', '#ba68c8']
                                )
                                st.plotly_chart(style_fig(fig_box), use_container_width=True)

                                agg_means = pd.DataFrame({
                                    'Группа': [group_a, group_b],
                                    'Среднее': [mean_a, mean_b]
                                })
                                fig_bar = px.bar(
                                    agg_means,
                                    x='Группа',
                                    y='Среднее',
                                    text_auto='.2f',
                                    color='Группа',
                                    color_discrete_sequence=['#5c7cfa', '#ba68c8'],
                                    title=f"Среднее значение метрики: {metric_col}"
                                )
                                st.plotly_chart(style_fig(fig_bar), use_container_width=True)

        with st.expander("📘 Подсказка по интерпретации"):
            st.markdown("""
- **p-value < α** — различие считаем статистически значимым.
- **Uplift** показывает относительное изменение группы B к группе A.
- Для конверсии лучше использовать бинарную колонку 0/1.
- Для средних значений используется t-test между двумя независимыми группами.
            """)

        st.markdown("---")
        st.markdown('<div class="module-header module-header-teal">📊 Продакт-аналитика</div>', unsafe_allow_html=True)

        prod_tab1, prod_tab2, prod_tab3, prod_tab4 = st.tabs([
            "🔄 Когортный анализ",
            "📉 Воронка продаж",
            "🔁 Retention",
            "📦 RFM-сегментация"
        ])

        # ── КОГОРТНЫЙ АНАЛИЗ ──
        with prod_tab1:
            st.markdown("#### 🔄 Когортный анализ по периоду")
            num_cols_p = df_work.select_dtypes(include='number').columns.tolist()
            cat_cols_p = df_work.select_dtypes(include='object').columns.tolist()
            date_cols  = [c for c in df_work.columns if 'date' in c.lower() or 'time' in c.lower() or 'дата' in c.lower()]

            if not date_cols and not num_cols_p:
                st.info("Для когортного анализа нужна колонка с датой и числовая метрика.")
            else:
                ca1, ca2, ca3 = st.columns(3)
                cohort_date  = ca1.selectbox("Колонка даты", date_cols or df_work.columns.tolist(), key="coh_date")
                cohort_group = ca2.selectbox("Группировка (когорта)", cat_cols_p or df_work.columns.tolist(), key="coh_group")
                cohort_metric= ca3.selectbox("Метрика", num_cols_p or df_work.columns.tolist(), key="coh_metric")
                period       = st.radio("Период агрегации", ["Месяц","Квартал","Год"], horizontal=True, key="coh_period")

                if st.button("📊 Построить когорты", use_container_width=True, key="btn_cohort"):
                    try:
                        dfc = df_work[[cohort_date, cohort_group, cohort_metric]].copy()
                        dfc[cohort_date] = pd.to_datetime(dfc[cohort_date], errors='coerce')
                        dfc = dfc.dropna(subset=[cohort_date])
                        freq = 'ME' if period=="Месяц" else ('QE' if period=="Квартал" else 'YE')
                        dfc['_period_'] = dfc[cohort_date].dt.to_period(freq[0]).astype(str)
                        cohort_pivot = dfc.groupby(['_period_', cohort_group])[cohort_metric].sum().unstack(fill_value=0)
                        st.markdown(f"**Матрица: {cohort_metric} по {period.lower()}ам и {cohort_group}**")
                        st.dataframe(cohort_pivot.style.background_gradient(cmap='Blues', axis=None), use_container_width=True)
                        fig_coh = px.bar(
                            dfc.groupby(['_period_', cohort_group])[cohort_metric].sum().reset_index(),
                            x='_period_', y=cohort_metric, color=cohort_group,
                            title=f"Динамика {cohort_metric} по {period.lower()}ам",
                            color_discrete_sequence=['#5c7cfa','#4fc3f7','#81c784','#ffb74d','#f06292','#ba68c8']
                        )
                        st.plotly_chart(style_fig(fig_coh), use_container_width=True)
                    except Exception as e:
                        st.error(f"Ошибка: {e}")

        # ── ВОРОНКА ПРОДАЖ ──
        with prod_tab2:
            st.markdown("#### 📉 Воронка конверсии")
            st.markdown('<small style="color:#8892a4">Укажите этапы и число пользователей на каждом</small>', unsafe_allow_html=True)

            n_stages = st.slider("Количество этапов воронки", 2, 8, 4, key="funnel_n")
            stage_names, stage_vals = [], []
            default_stages = ["Посещение","Регистрация","Корзина","Оплата","Повторная покупка","Retention"]
            fcols = st.columns(2)
            for i in range(n_stages):
                with fcols[i % 2]:
                    sname = st.text_input(f"Этап {i+1}", value=default_stages[i] if i < len(default_stages) else f"Этап {i+1}", key=f"fn_{i}")
                    sval  = st.number_input(f"Пользователей", min_value=0, value=max(1000 - i*180, 50), key=f"fv_{i}")
                    stage_names.append(sname)
                    stage_vals.append(sval)

            if st.button("📉 Построить воронку", use_container_width=True, key="btn_funnel"):
                conversions = []
                for i in range(len(stage_vals)):
                    cr = stage_vals[i] / stage_vals[0] * 100 if stage_vals[0] > 0 else 0
                    conversions.append(round(cr, 1))

                fig_funnel = go.Figure(go.Funnel(
                    y=stage_names,
                    x=stage_vals,
                    textinfo="value+percent initial+percent previous",
                    marker=dict(
                        color=['#5c7cfa','#4fc3f7','#81c784','#ffb74d','#f06292','#ba68c8','#ff8a65','#4dd0e1'][:n_stages],
                        line=dict(color='#151820', width=2)
                    ),
                    connector=dict(line=dict(color='#2a2d3a', width=1))
                ))
                fig_funnel.update_layout(title="Воронка конверсии", funnelmode="stack")
                st.plotly_chart(style_fig(fig_funnel), use_container_width=True)

                funnel_df = pd.DataFrame({
                    'Этап': stage_names,
                    'Пользователей': stage_vals,
                    '% от старта': conversions,
                    'Отвалилось': [0] + [stage_vals[i-1] - stage_vals[i] for i in range(1, len(stage_vals))],
                })
                st.dataframe(funnel_df, use_container_width=True)

        # ── RETENTION ──
        with prod_tab3:
            st.markdown("#### 🔁 Retention — удержание пользователей")
            ret_cols = df_work.select_dtypes(include='number').columns.tolist()
            date_cols_r = [c for c in df_work.columns if 'date' in c.lower() or 'time' in c.lower() or 'дата' in c.lower()]
            user_cols = [c for c in df_work.columns if any(k in c.lower() for k in ['user','id','клиент','customer','uid'])]

            if len(date_cols_r) < 1 or len(user_cols) < 1:
                st.info("Для Retention нужна колонка с датой события и колонка user_id/клиент.")
                st.markdown("""**Пример структуры данных:**
| user_id | event_date |
|---|---|
| 101 | 2024-01-05 |
| 101 | 2024-02-12 |
| 102 | 2024-01-03 |""")
            else:
                rc1, rc2 = st.columns(2)
                ret_user = rc1.selectbox("Колонка user_id", user_cols, key="ret_user")
                ret_date = rc2.selectbox("Колонка даты события", date_cols_r, key="ret_date")

                if st.button("🔁 Рассчитать Retention", use_container_width=True, key="btn_retention"):
                    try:
                        dfr = df_work[[ret_user, ret_date]].copy()
                        dfr[ret_date] = pd.to_datetime(dfr[ret_date], errors='coerce')
                        dfr = dfr.dropna()
                        dfr['cohort_month'] = dfr.groupby(ret_user)[ret_date].transform('min').dt.to_period('M')
                        dfr['event_month']  = dfr[ret_date].dt.to_period('M')
                        dfr['period_num']   = (dfr['event_month'] - dfr['cohort_month']).apply(lambda x: x.n if hasattr(x,'n') else 0)
                        cohort_sizes = dfr.groupby('cohort_month')[ret_user].nunique()
                        ret_matrix   = dfr.groupby(['cohort_month','period_num'])[ret_user].nunique().unstack()
                        ret_pct      = ret_matrix.divide(cohort_sizes, axis=0).round(3) * 100
                        st.markdown("**Retention matrix (%) по месячным когортам:**")
                        st.dataframe(
                            ret_pct.style.background_gradient(cmap='RdYlGn', vmin=0, vmax=100, axis=None).format("{:.1f}%"),
                            use_container_width=True
                        )
                        avg_ret = ret_pct.mean()
                        fig_ret = px.line(
                            x=avg_ret.index, y=avg_ret.values,
                            title="Средний Retention по периодам",
                            labels={'x': 'Период (месяц)', 'y': 'Retention %'},
                            markers=True, color_discrete_sequence=['#4fc3f7']
                        )
                        fig_ret.update_traces(line_width=2.5, marker_size=8)
                        st.plotly_chart(style_fig(fig_ret), use_container_width=True)
                    except Exception as e:
                        st.error(f"Ошибка расчёта: {e}")

        # ── RFM ──
        with prod_tab4:
            st.markdown("#### 📦 RFM-сегментация клиентов")
            st.markdown('<small style="color:#8892a4">Recency · Frequency · Monetary — стандарт продакт и CRM аналитики</small>', unsafe_allow_html=True)

            date_cols_rfm = [c for c in df_work.columns if 'date' in c.lower() or 'time' in c.lower() or 'дата' in c.lower()]
            user_cols_rfm = [c for c in df_work.columns if any(k in c.lower() for k in ['user','id','клиент','customer','uid'])]
            num_cols_rfm  = df_work.select_dtypes(include='number').columns.tolist()

            if not date_cols_rfm or not user_cols_rfm or not num_cols_rfm:
                st.info("Для RFM нужны: колонка user_id, дата транзакции, числовая сумма.")
                st.markdown("""**Пример структуры:**
| customer_id | order_date | revenue |
|---|---|---|
| C001 | 2024-03-15 | 1500 |
| C002 | 2024-01-08 | 800 |""")
            else:
                rf1, rf2, rf3 = st.columns(3)
                rfm_user   = rf1.selectbox("User ID", user_cols_rfm, key="rfm_user")
                rfm_date   = rf2.selectbox("Дата транзакции", date_cols_rfm, key="rfm_date")
                rfm_amount = rf3.selectbox("Сумма (Monetary)", num_cols_rfm, key="rfm_amount")

                if st.button("📦 Рассчитать RFM", type="primary", use_container_width=True, key="btn_rfm"):
                    try:
                        dfm = df_work[[rfm_user, rfm_date, rfm_amount]].copy()
                        dfm[rfm_date] = pd.to_datetime(dfm[rfm_date], errors='coerce')
                        dfm = dfm.dropna()
                        snapshot = dfm[rfm_date].max() + pd.Timedelta(days=1)

                        rfm = dfm.groupby(rfm_user).agg(
                            Recency  = (rfm_date,   lambda x: (snapshot - x.max()).days),
                            Frequency= (rfm_date,   'count'),
                            Monetary = (rfm_amount, 'sum')
                        ).reset_index()

                        rfm['R'] = pd.qcut(rfm['Recency'],   q=5, labels=[5,4,3,2,1], duplicates='drop').astype(int)
                        rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=5, labels=[1,2,3,4,5]).astype(int)
                        rfm['M'] = pd.qcut(rfm['Monetary'].rank(method='first'),  q=5, labels=[1,2,3,4,5]).astype(int)
                        rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)
                        rfm['RFM_Total'] = rfm['R'] + rfm['F'] + rfm['M']

                        def rfm_segment(row):
                            if row['R'] >= 4 and row['F'] >= 4 and row['M'] >= 4: return '👑 Champions'
                            if row['R'] >= 3 and row['F'] >= 3:                    return '💚 Loyal'
                            if row['R'] >= 4 and row['F'] <= 2:                    return '🆕 New'
                            if row['R'] >= 3 and row['M'] >= 4:                    return '💰 Big Spenders'
                            if row['R'] <= 2 and row['F'] >= 3:                    return '😴 At Risk'
                            if row['R'] <= 2 and row['F'] <= 2:                    return '💀 Lost'
                            return '🔄 Regular'

                        rfm['Сегмент'] = rfm.apply(rfm_segment, axis=1)

                        seg_counts = rfm['Сегмент'].value_counts().reset_index()
                        seg_counts.columns = ['Сегмент', 'Клиентов']

                        mc1, mc2, mc3, mc4 = st.columns(4)
                        with mc1: render_metric_card(f"{len(rfm):,}", "Всего клиентов")
                        with mc2: render_metric_card(f"{rfm['Recency'].median():.0f}д", "Медиана Recency")
                        with mc3: render_metric_card(f"{rfm['Frequency'].median():.0f}", "Медиана частоты")
                        with mc4: render_metric_card(f"{rfm['Monetary'].median():,.0f}", "Медиана чека")

                        fig_rfm_pie = px.pie(
                            seg_counts, names='Сегмент', values='Клиентов',
                            title="Распределение RFM-сегментов", hole=0.42,
                            color_discrete_sequence=['#5c7cfa','#4fc3f7','#81c784','#ffb74d','#f06292','#ba68c8','#ff8a65']
                        )
                        fig_rfm_pie.update_traces(textposition='outside', textfont_size=12)
                        st.plotly_chart(style_fig(fig_rfm_pie), use_container_width=True)

                        fig_rfm_scatter = px.scatter(
                            rfm, x='Recency', y='Monetary', size='Frequency',
                            color='Сегмент', title="RFM: Recency vs Monetary (размер = Frequency)",
                            opacity=0.75,
                            color_discrete_sequence=['#5c7cfa','#4fc3f7','#81c784','#ffb74d','#f06292','#ba68c8','#ff8a65']
                        )
                        st.plotly_chart(style_fig(fig_rfm_scatter), use_container_width=True)

                        st.markdown("**📋 Таблица RFM (топ-100)**")
                        st.dataframe(
                            rfm.sort_values('RFM_Total', ascending=False).head(100),
                            use_container_width=True, height=300
                        )

                        csv_rfm = rfm.to_csv(index=False).encode('utf-8')
                        st.download_button("⬇️ Скачать полный RFM-файл CSV", csv_rfm, "rfm_segments.csv", "text/csv")

                    except Exception as e:
                        st.error(f"Ошибка RFM: {e}")

# ══════════════════════════════════════════════════════════════
#  TAB 4 — ИИ + ГРАФИКИ
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="module-header module-header-blue">🤖 ИИ генерация графиков</div>', unsafe_allow_html=True)

    df_work = get_df()

    if df_work is None:
        st.info("👆 Сначала загрузите файл на вкладке 📁")
    else:
        if not st.session_state.clean_done:
            st.warning("💡 Очистка не применена — работаем с оригинальными данными. Перейдите на 🧹 если нужна обработка.")

        with st.expander("📋 Доступные колонки датасета"):
            sc = pd.DataFrame({
                'Колонка': df_work.columns,
                'Тип': df_work.dtypes.astype(str).values,
                'Уникальных': df_work.nunique().values,
                'Пример': [
                    str(df_work[c].dropna().iloc[0]) if df_work[c].notna().any() else '—'
                    for c in df_work.columns
                ],
            })
            st.dataframe(sc, use_container_width=True, height=200)

        st.markdown("**⚡ Быстрые шаблоны:**")
        TEMPLATES = {
            "📊 Топ 10 категорий":    "топ 10 категорий по сумме bar",
            "🥧 Доля (пирог)":        "пирог доля структура категорий",
            "📈 Динамика по времени":  "динамика линия тренд по времени",
            "🔵 Корреляция (scatter)": "корреляция scatter зависимость спирман",
            "📉 Распределение":        "распределение гистограмма",
            "📦 Box plot":             "box ящик разброс по категориям",
            "📋 Средние по группам":   "средние average по группам bar",
            "🌡️ Scatter + тренд":     "scatter корреляция зависимость тренд",
        }
        cols_r1 = st.columns(4)
        cols_r2 = st.columns(4)
        for i, (label, query_val) in enumerate(TEMPLATES.items()):
            row = cols_r1 if i < 4 else cols_r2
            if row[i % 4].button(label, key=f"tpl_{i}", use_container_width=True):
                st.session_state['uq_area'] = query_val
                st.rerun()

        user_query = st.text_area(
            "💬 Опишите график:",
            height=80,
            placeholder="Например: топ 10 стран по ВВП, горизонтальный бар, отсортировать по убыванию",
            key="uq_area"
        )
        chart_title = st.text_input("Заголовок графика (необязательно):", key="ct_input")

        col_g, col_a = st.columns([2, 1])
        btn_gen = col_g.button("🚀 Сгенерировать", type="primary", use_container_width=True)
        btn_auto = col_a.button("✨ Авто-EDA (5)", use_container_width=True)

        def _schema(df):
            rows = []
            for c in df.columns:
                rows.append(
                    f"  {c} ({df[c].dtype}), uniq={df[c].nunique()}, "
                    f"ex={str(df[c].dropna().iloc[0]) if df[c].notna().any() else 'N/A'}"
                )
            return "\n".join(rows)

        def call_groq(query, df, title=""):
            system = (
                "You are a Python Plotly expert. Output ONLY executable Python code.\n"
                "df is already defined. Use plotly.express or plotly.graph_objects.\n"
                "Save result to variable `fig`. Never call fig.show().\n"
                "Use colors: ['#5c7cfa','#4fc3f7','#81c784','#ffb74d','#f06292','#ba68c8']\n"
                "paper_bgcolor='#151820', plot_bgcolor='#151820', font_color='#c9d1d9'\n"
                "Return ONLY code. No markdown fences. No explanation."
            )
            user = (
                f"Schema:\n{_schema(df)}\n\n"
                f"Sample:\n{df.head(3).to_json(orient='records', default_handler=str)}\n\n"
                f"Request: {query}\nTitle: {title or 'auto'}\n\nCode:"
            )
            payload = pyjson.dumps({
                "model": llm_model,
                "messages": [
                    {"role":"system","content":system},
                    {"role":"user","content":user}
                ],
                "temperature": 0.15,
                "max_tokens": 1400
            }).encode()
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"
                }
            )
            with urllib.request.urlopen(req, timeout=35) as r:
                res = pyjson.loads(r.read())
            code = res['choices'][0]['message']['content']
            code = re.sub(r'```python\n?', '', code)
            code = re.sub(r'```\n?', '', code)
            return code.strip()

        def call_groq_text(prompt):
            payload = pyjson.dumps({
                "model": llm_model,
                "messages": [{"role":"user","content":prompt}],
                "temperature": 0.4,
                "max_tokens": 700
            }).encode()
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"
                }
            )
            with urllib.request.urlopen(req, timeout=35) as r:
                res = pyjson.loads(r.read())
            return res['choices'][0]['message']['content'].strip()

        def fallback_chart(query, df, title=""):
            q = query.lower()
            num = df.select_dtypes(include='number').columns.tolist()
            cat = df.select_dtypes(include='object').columns.tolist()
            dte = df.select_dtypes(include='datetime64').columns.tolist()
            ttl = title or query[:60]

            BAR_COLORS = ['#5c7cfa','#6a8ffb','#7a9ffc','#4fc3f7','#81c784',
                          '#ffb74d','#f06292','#ba68c8','#4dd0e1','#ff8a65']

            def _styled_bar(fig):
                fig.update_traces(
                    marker_line_color='rgba(0,0,0,0.35)',
                    marker_line_width=1.2,
                    opacity=0.92,
                )
                fig.update_layout(bargap=0.18, bargroupgap=0.06)
                return fig

            if any(w in q for w in ['топ','top','рейтинг','bar','бар','лучш']):
                if cat and num:
                    agg = df.groupby(cat[0])[num[0]].mean().nlargest(10).reset_index()
                    colors = [BAR_COLORS[i % len(BAR_COLORS)] for i in range(len(agg))]
                    fig = px.bar(agg, x=num[0], y=cat[0], orientation='h', title=ttl, text_auto='.0f')
                    fig.update_traces(
                        marker_color=colors,
                        marker_line_color='rgba(0,0,0,0.3)',
                        marker_line_width=1.2,
                        opacity=0.93,
                        textfont_size=11,
                        textposition='outside'
                    )
                    fig.update_layout(bargap=0.22, yaxis={'categoryorder':'total ascending'})
                    return fig

            if any(w in q for w in ['пирог','pie','доля','структур','круговой','circle']):
                if cat:
                    cnt = df[cat[0]].value_counts().nlargest(12).reset_index()
                    cnt.columns = [cat[0], 'count']
                    fig = px.pie(cnt, names=cat[0], values='count', title=ttl, hole=0.42)
                    fig.update_traces(
                        marker=dict(colors=BAR_COLORS[:len(cnt)], line=dict(color='#151820', width=2.5)),
                        textfont_size=12,
                        textposition='outside',
                        pull=[0.04 if i == 0 else 0.01 for i in range(len(cnt))]
                    )
                    return fig

            if any(w in q for w in ['динамик','линия','line','тренд','time','врем']):
                if dte and num:
                    fig = px.line(df.sort_values(dte[0]), x=dte[0], y=num[0], title=ttl, markers=True, line_shape='spline')
                    fig.update_traces(
                        line=dict(color='#5c7cfa', width=2.5),
                        marker=dict(color='#4fc3f7', size=5, line=dict(color='#151820', width=1)),
                        fill='tozeroy',
                        fillcolor='rgba(92,124,250,0.12)'
                    )
                    return fig
                elif cat and num:
                    agg = df.groupby(cat[0])[num[0]].mean().reset_index()
                    fig = px.line(agg, x=cat[0], y=num[0], title=ttl, markers=True, line_shape='spline')
                    fig.update_traces(
                        line=dict(color='#5c7cfa', width=2.5),
                        marker=dict(color='#4fc3f7', size=6, line=dict(color='#151820', width=1.5)),
                        fill='tozeroy',
                        fillcolor='rgba(92,124,250,0.12)'
                    )
                    return fig

            if any(w in q for w in ['scatter','корреляц','зависим','спирман','pearson','spearman','correlation']):
                if len(num) >= 2:
                    from scipy import stats as _stats
                    import numpy as _np
                    from scipy.stats import rankdata as _rankdata

                    # ── Умный выбор колонок по словам из запроса ──
                    def _find_col(words, candidates):
                        for w in words:
                            if len(w) < 2:
                                continue
                            for c in candidates:
                                if w.lower() in c.lower() or c.lower() in w.lower():
                                    return c
                        return None

                    q_words = q.replace(',', ' ').replace('и', ' ').replace('vs', ' ').split()
                    col_x = _find_col(q_words, num) or num[0]
                    remaining = [c for c in num if c != col_x]
                    col_y = _find_col(q_words, remaining) or (remaining[0] if remaining else num[1 if len(num) > 1 else 0])
                    if col_x == col_y:
                        col_y = remaining[0] if remaining else num[0]

                    fig = px.scatter(
                        df, x=col_x, y=col_y,
                        color=cat[0] if cat else None,
                        title=ttl or f'Корреляция: {col_x} vs {col_y}',
                        opacity=0.75,
                        color_discrete_sequence=BAR_COLORS,
                        trendline='ols',
                        trendline_color_override='#ff8a65'
                    )
                    fig.update_traces(
                        selector=dict(mode='markers'),
                        marker=dict(size=8, line=dict(color='rgba(0,0,0,0.3)', width=0.8))
                    )
                    x_s = df[col_x].dropna()
                    y_s = df[col_y].dropna()
                    idx = x_s.index.intersection(y_s.index)
                    x_s, y_s = x_s[idx], y_s[idx]
                    rho, pval = _stats.spearmanr(x_s, y_s)
                    rx = _rankdata(x_s)
                    sort_idx = _np.argsort(rx)
                    fig.add_scatter(
                        x=x_s.values[sort_idx],
                        y=y_s.values[sort_idx],
                        mode='lines',
                        line=dict(color='#4fc3f7', width=2, dash='dot'),
                        name=f'Спирман ρ={rho:.3f} (p={pval:.3f})',
                        opacity=0.8
                    )
                    fig.update_layout(
                        annotations=[dict(
                            text=f"ρ Спирмана = {rho:.3f} | p-value = {pval:.4f}",
                            xref='paper', yref='paper', x=0.01, y=0.99,
                            xanchor='left', yanchor='top',
                            bgcolor='rgba(92,124,250,0.15)',
                            bordercolor='#5c7cfa', borderwidth=1,
                            font=dict(color='#4fc3f7', size=12), showarrow=False
                        )]
                    )
                    return fig

            if any(w in q for w in ['распределен','гистограм','histog']):
                if num:
                    fig = px.histogram(
                        df, x=num[0],
                        color=cat[0] if cat else None,
                        title=ttl, nbins=35,
                        color_discrete_sequence=BAR_COLORS,
                        opacity=0.88
                    )
                    fig.update_traces(marker_line_color='rgba(0,0,0,0.35)', marker_line_width=1.0)
                    fig.update_layout(bargap=0.05)
                    return fig

            if any(w in q for w in ['box','ящик','разброс']):
                if cat and num:
                    top = df[cat[0]].value_counts().head(6).index
                    fig = px.box(
                        df[df[cat[0]].isin(top)],
                        x=cat[0], y=num[0], color=cat[0],
                        title=ttl,
                        color_discrete_sequence=BAR_COLORS
                    )
                    fig.update_traces(marker=dict(size=4, opacity=0.6), line=dict(width=1.5))
                    return fig

            if any(w in q for w in ['средн','average','группа']):
                if cat and num:
                    agg = df.groupby(cat[0])[num[0]].mean().reset_index()
                    fig = px.bar(agg, x=cat[0], y=num[0], title=ttl, color_discrete_sequence=BAR_COLORS)
                    return _styled_bar(fig)

            if cat and num:
                agg = df.groupby(cat[0])[num[0]].mean().reset_index()
                colors = [BAR_COLORS[i % len(BAR_COLORS)] for i in range(len(agg))]
                fig = px.bar(agg, x=cat[0], y=num[0], title=ttl, text_auto='.1f')
                fig.update_traces(
                    marker_color=colors,
                    marker_line_color='rgba(0,0,0,0.3)',
                    marker_line_width=1.2,
                    opacity=0.92
                )
                fig.update_layout(bargap=0.18)
                return fig

            if num:
                fig = px.histogram(df, x=num[0], title=ttl, nbins=30, color_discrete_sequence=['#5c7cfa'], opacity=0.88)
                fig.update_traces(marker_line_color='rgba(255,255,255,0.15)', marker_line_width=1.0)
                fig.update_layout(bargap=0.04)
                return fig

            return None

        def save_chart(fig, query, title):
            if fig is not None:
                fig = style_fig(fig)
                st.session_state.charts.append({
                    'id': uuid.uuid4().hex,
                    'title': title or query[:50],
                    'query': query,
                    'fig': fig,
                })

        def parse_intent(raw_query):
            """ИИ нормализует запрос в чёткое англ. описание графика. Без API — оригинал."""
            if not api_key:
                return raw_query
            try:
                prompt = (
                    "You are a data visualization intent parser.\n"
                    "User wants a chart. Their request may be in any language, "
                    "misspelled, or vague.\n"
                    "Translate and normalize it into a clear English chart description.\n"
                    "Output ONLY the normalized description, nothing else. Max 20 words.\n\n"
                    f"User input: {raw_query}\n"
                    "Normalized:"
                )
                payload = pyjson.dumps({
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 60
                }).encode()
                req = urllib.request.Request(
                    "https://api.groq.com/openai/v1/chat/completions",
                    data=payload,
                    headers={"Authorization": f"Bearer {api_key}",
                             "Content-Type": "application/json",
                             "User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=10) as r:
                    res = pyjson.loads(r.read())
                return res['choices'][0]['message']['content'].strip()
            except Exception:
                return raw_query

        if btn_gen:
            if not user_query.strip():
                st.warning("✏️ Введите описание графика или нажмите шаблон")
            else:
                with st.spinner("🤖 Генерирую..."):
                    normalized_query = parse_intent(user_query)
                    if normalized_query != user_query:
                        st.caption(f"🧠 ИИ понял запрос как: *{normalized_query}*")
                    fig = None
                    if api_key:
                        try:
                            code = call_groq(normalized_query, df_work, chart_title)
                            ns = {'df': df_work.copy(), 'pd': pd, 'np': np, 'px': px, 'go': go, 'fig': None}
                            exec(code, ns)
                            fig = ns.get('fig')
                        except Exception as e:
                            st.warning(f"⚠️ ИИ ошибка: {e} — использую встроенный генератор")
                    if fig is None:
                        fig = fallback_chart(normalized_query, df_work, chart_title)
                    save_chart(fig, user_query, chart_title)
                st.success("✅ График добавлен!")
                st.rerun()

        if btn_auto:
            with st.spinner("✨ Анализирую датасет..."):
                num = df_work.select_dtypes(include='number').columns.tolist()
                cat = df_work.select_dtypes(include='object').columns.tolist()
                dte = df_work.select_dtypes(include='datetime64').columns.tolist()
                added = 0

                if num:
                    col0 = num[0]
                    n_unique = df_work[col0].nunique()
                    if n_unique <= 50:
                        vc = df_work[col0].value_counts().sort_index().reset_index()
                        vc.columns = [col0, 'count']
                        colors = ['#5c7cfa','#4fc3f7','#81c784','#ffb74d','#f06292','#ba68c8','#4dd0e1','#ff8a65']
                        bar_colors = [colors[i % len(colors)] for i in range(len(vc))]
                        fig_eda = px.bar(vc, x=col0, y='count', title=f"Распределение: {col0}", text_auto=True)
                        fig_eda.update_traces(
                            marker_color=bar_colors,
                            marker_line_color='rgba(0,0,0,0.4)',
                            marker_line_width=1.2,
                            opacity=0.92
                        )
                        fig_eda.update_layout(bargap=0.15)
                    else:
                        fig_eda = px.histogram(
                            df_work, x=col0,
                            color=cat[0] if cat else None,
                            nbins=35,
                            title=f"Распределение: {col0}",
                            color_discrete_sequence=['#5c7cfa'],
                            opacity=0.88
                        )
                        fig_eda.update_traces(marker_line_color='rgba(255,255,255,0.15)', marker_line_width=1.0)
                        fig_eda.update_layout(bargap=0.04)
                    save_chart(fig_eda, f"Распределение {col0}", f"Распределение: {col0}")
                    added += 1

                if cat and num:
                    agg = df_work.groupby(cat[0])[num[0]].mean().nlargest(10).reset_index()
                    save_chart(
                        px.bar(agg, x=num[0], y=cat[0], orientation='h', title=f"Топ: {cat[0]} по {num[0]}",
                               color=num[0], color_continuous_scale='Blues', text_auto='.0f'),
                        f"Топ {cat[0]}", f"Топ: {cat[0]} по {num[0]}"
                    )
                    added += 1

                if cat:
                    cnt = df_work[cat[0]].value_counts().reset_index()
                    cnt.columns = [cat[0], 'count']
                    save_chart(
                        px.pie(cnt, names=cat[0], values='count', title=f"Структура: {cat[0]}", hole=0.42),
                        f"Структура {cat[0]}", f"Структура: {cat[0]}"
                    )
                    added += 1

                if len(num) >= 2:
                    save_chart(
                        px.scatter(df_work, x=num[0], y=num[1], color=cat[0] if cat else None, opacity=0.7,
                                   title=f"Корреляция: {num[0]} vs {num[1]}"),
                        "Корреляция", f"Корреляция: {num[0]} vs {num[1]}"
                    )
                    added += 1

                if dte and num:
                    save_chart(
                        px.line(df_work.sort_values(dte[0]), x=dte[0], y=num[0], title=f"Динамика: {num[0]}", line_shape='spline'),
                        f"Динамика {num[0]}", f"Динамика: {num[0]}"
                    )
                    added += 1
                elif cat and num and added < 5:
                    agg2 = df_work.groupby(cat[0])[num[0]].mean().reset_index()
                    save_chart(
                        px.bar(agg2, x=cat[0], y=num[0], color=cat[0], title=f"Средние: {cat[0]} → {num[0]}"),
                        f"Средние по {cat[0]}", f"Средние: {cat[0]} → {num[0]}"
                    )
                    added += 1

            st.success(f"✅ Добавлено {added} графиков")
            st.rerun()

        if st.session_state.charts:
            st.markdown("---")
            hdr, btn_clr = st.columns([5, 1])
            hdr.markdown(f"#### 📊 Графики ({len(st.session_state.charts)})")
            if btn_clr.button("🗑 Всё", key="clr_all"):
                st.session_state.charts = []
                st.rerun()

            for _ci, ch in enumerate(reversed(st.session_state.charts)):
                st.markdown('<div class="chart-card">', unsafe_allow_html=True)
                st.plotly_chart(ch['fig'], use_container_width=True, key=f"fig_r{_ci}_{ch['id'][:8]}")
                c_a, c_b = st.columns([6, 1])
                c_a.caption(f"🔍 {ch['query'][:100]}")
                if c_b.button("🗑", key=f"del_r{_ci}_{ch['id'][:8]}"):
                    st.session_state.charts = [c for c in st.session_state.charts if c['id'] != ch['id']]
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TAB 5 — ЭКСПОРТ
# ══════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="module-header module-header-teal">📦 Экспорт</div>', unsafe_allow_html=True)

    dfexp = get_df()

    if dfexp is None:
        st.info("👆 Сначала загрузите данные")
    else:
        st.markdown("#### 🧠 Executive Summary")
        ex1, ex2 = st.columns([3, 1])
        lang = ex1.selectbox("Язык:", ["Русский","English","Polski"], key="ex_lang")

        def call_groq_text(prompt):
            payload = pyjson.dumps({
                "model": llm_model,
                "messages": [{"role":"user","content":prompt}],
                "temperature": 0.4,
                "max_tokens": 700
            }).encode()
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"
                }
            )
            with urllib.request.urlopen(req, timeout=35) as r:
                res = pyjson.loads(r.read())
            return res['choices'][0]['message']['content'].strip()

        if ex2.button("✨ Сгенерировать", type="primary", use_container_width=True, key="gen_exec"):
            if not api_key:
                st.warning("Нужен API ключ Groq")
            else:
                with st.spinner("🧠 Анализирую..."):
                    try:
                        num2 = dfexp.select_dtypes(include='number')
                        lines = [
                            f"  {c}: mean={num2[c].mean():.2f}, min={num2[c].min():.2f}, max={num2[c].max():.2f}"
                            for c in num2.columns[:8]
                        ]
                        titles = [c['title'] for c in st.session_state.charts[:6]]
                        lmap = {"Русский":"Russian","English":"English","Polski":"Polish"}
                        prompt = (
                            f"You are a senior BI analyst. Write Executive Summary in {lmap[lang]}.\n"
                            f"Dataset: {len(dfexp):,} rows × {len(dfexp.columns)} columns.\n"
                            f"Columns: {', '.join(dfexp.columns[:15])}\n"
                            f"Stats:\n" + "\n".join(lines) + "\n"
                            f"Charts built: {', '.join(titles) or 'none'}\n\n"
                            f"Write 5-7 sentences. Start with key finding. Use real numbers. Identify trends and anomalies."
                        )
                        st.session_state.exec_summary = call_groq_text(prompt)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка: {e}")

        if st.session_state.exec_summary:
            st.markdown(f"""<div class="exec-summary">
                <h4>📋 Executive Summary</h4>
                <p>{st.session_state.exec_summary.replace(chr(10), '<br>')}</p>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        ec1, ec2 = st.columns(2)

        with ec1:
            st.markdown("#### 📄 Данные → CSV")
            buf = io.StringIO()
            dfexp.to_csv(buf, index=False)
            st.download_button(
                "⬇️ Скачать CSV",
                data=buf.getvalue().encode('utf-8-sig'),
                file_name=f"export_{datetime.now():%Y%m%d_%H%M}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.markdown(
                f"""<div style="font-size:0.8rem;color:#8892a4;margin-top:8px">
                {len(dfexp):,} строк × {len(dfexp.columns)} колонок</div>""",
                unsafe_allow_html=True
            )

        with ec2:
            st.markdown("#### 🌐 HTML отчёт")
            theme = st.selectbox("Тема:", ["Dark Pro","Light Clean","Navy Blue"], key="html_theme")

            if st.button("🔨 Собрать отчёт", type="primary", use_container_width=True):
                dark = "Dark" in theme
                light = "Light" in theme
                bg = '#0f1117' if dark else ('#ffffff' if light else '#0a1628')
                surf = '#151820' if dark else ('#f8f9fa' if light else '#0d1f3c')
                tc = '#e0e0e0' if dark else ('#212529' if light else '#e0e0e0')
                acc = '#5c7cfa' if dark else ('#0d6efd' if light else '#4fc3f7')
                mut = '#8892a4' if dark else ('#6c757d' if light else '#8892a4')
                brd = 'rgba(255,255,255,0.07)' if dark else ('rgba(0,0,0,0.1)' if light else 'rgba(255,255,255,0.07)')

                kpi_html = ""
                for col in dfexp.select_dtypes(include='number').columns[:6]:
                    h = len(dfexp) // 2
                    v1 = dfexp[col].iloc[:h].mean() if h else dfexp[col].mean()
                    v2 = dfexp[col].iloc[h:].mean() if h else dfexp[col].mean()
                    d = (v2 - v1) / v1 * 100 if v1 != 0 else 0
                    arrow, dc = ("▲", "#81c784") if d >= 0 else ("▼", "#f06292")
                    kpi_html += f"""
                    <div class="kpi"><div class="kv">{v2:,.1f}</div>
                    <div class="kl">{col}</div>
                    <div style="color:{dc};font-size:.8rem;margin-top:3px">
                        {arrow} {abs(d):.1f}%</div></div>"""

                import plotly.io as pio
                charts_html = ""
                for ch in st.session_state.charts:
                    try:
                        c_html = pio.to_html(
                            ch['fig'],
                            include_plotlyjs='cdn',
                            full_html=False,
                            div_id=f"c{ch['id']}",
                            config={'responsive': True, 'displayModeBar': False}
                        )
                        charts_html += (
                            f'<div class="cblock">'
                            f'<h3>{ch["title"]}</h3>'
                            f'{c_html}'
                            f'</div>'
                        )
                    except Exception as e:
                        charts_html += f'<div class="cblock"><p style="color:#f06292">Ошибка: {e}</p></div>'

                summ_html = ""
                if st.session_state.exec_summary:
                    summ_html = f"""
                    <div class="ebox"><h3>📋 Executive Summary</h3>
                    <p>{st.session_state.exec_summary.replace(chr(10), '<br>')}</p></div>"""

                html_out = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BI Report {datetime.now():%d.%m.%Y}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{bg};color:{tc};font-family:'Segoe UI',Inter,sans-serif;padding:32px}}
h1{{color:{acc};font-size:1.7rem;margin-bottom:4px}}
h3{{color:{tc};font-size:1rem;margin-bottom:10px;font-weight:600}}
.sub{{color:{mut};font-size:.84rem;margin-bottom:28px}}
.kpi-row{{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:28px}}
.kpi{{background:{surf};border:1px solid {brd};border-radius:12px;
      padding:18px 16px;min-width:130px;text-align:center;
      box-shadow:0 4px 14px rgba(0,0,0,.2)}}
.kv{{font-size:1.8rem;font-weight:700;color:{acc}}}
.kl{{font-size:.68rem;color:{mut};margin-top:5px;text-transform:uppercase;letter-spacing:.06em}}
.ebox{{background:rgba(92,124,250,.07);border:1px solid rgba(92,124,250,.22);
       border-radius:12px;padding:18px 22px;margin-bottom:24px}}
.ebox h3{{color:{acc}}}
.ebox p{{line-height:1.7;margin-top:8px;font-size:.93rem}}
.cblock{{background:{surf};border:1px solid {brd};border-radius:12px;
         padding:14px;margin-bottom:20px;box-shadow:0 4px 14px rgba(0,0,0,.15)}}
footer{{margin-top:36px;text-align:center;color:{mut};font-size:.76rem}}
</style>
</head>
<body>
<h1>📊 BI Report</h1>
<div class="sub">
  {datetime.now():%d.%m.%Y %H:%M} &nbsp;|&nbsp;
  {st.session_state.file_name} &nbsp;|&nbsp;
  {len(dfexp):,} строк × {len(dfexp.columns)} колонок
</div>
{summ_html}
<div class="kpi-row">{kpi_html}</div>
{charts_html}
<footer>Создано с BI Dashboard Builder</footer>
</body>
</html>"""

                st.download_button(
                    "📥 Скачать HTML отчёт",
                    data=html_out.encode('utf-8'),
                    file_name=f"report_{datetime.now():%Y%m%d_%H%M}.html",
                    mime="text/html",
                    use_container_width=True
                )