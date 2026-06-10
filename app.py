"""
Dynamic Dashboard Generator
Production-ready Streamlit app that auto-analyzes any tabular dataset.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dynamic Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Root palette ── */
:root {
    --bg:        #0d0f14;
    --surface:   #13161e;
    --card:      #181c27;
    --border:    rgba(255,255,255,0.07);
    --accent1:   #4f8ef7;
    --accent2:   #a78bfa;
    --accent3:   #34d399;
    --accent4:   #f59e0b;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --danger:    #f87171;
    --radius:    14px;
    --shadow:    0 8px 32px rgba(0,0,0,0.45);
}

/* ── Base ── */
html, body, .stApp {
    background: var(--bg) !important;
    font-family: 'Inter', sans-serif;
    color: var(--text);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Hide default header ── */
header[data-testid="stHeader"] { display: none; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: #2a2f3d; border-radius: 3px; }

/* ── Glass card ── */
.glass-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow);
    backdrop-filter: blur(12px);
    transition: border-color .25s;
}
.glass-card:hover { border-color: rgba(79,142,247,0.28); }

/* ── KPI cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
    gap: 14px;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.25rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent-color, var(--accent1));
    border-radius: var(--radius) var(--radius) 0 0;
}
.kpi-label {
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: .45rem;
}
.kpi-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1.1;
    font-family: 'DM Mono', monospace;
}
.kpi-sub {
    font-size: .72rem;
    color: var(--muted);
    margin-top: .3rem;
}

/* ── Section header ── */
.section-head {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 1.6rem 0 1rem;
}
.section-head h2 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text);
    margin: 0;
}
.section-pill {
    font-size: .7rem;
    font-weight: 600;
    letter-spacing: .06em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 99px;
    background: rgba(79,142,247,0.15);
    color: var(--accent1);
    border: 1px solid rgba(79,142,247,0.25);
}

/* ── Dashboard title ── */
.dash-title {
    font-size: 1.8rem;
    font-weight: 700;
    letter-spacing: -.02em;
    background: linear-gradient(120deg, var(--accent1), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.dash-sub {
    color: var(--muted);
    font-size: .85rem;
    margin-top: .2rem;
}

/* ── Meta badges ── */
.meta-row {
    display: flex;
    gap: 10px;
    margin-top: .75rem;
    flex-wrap: wrap;
}
.meta-badge {
    font-size: .75rem;
    font-weight: 500;
    padding: 4px 12px;
    border-radius: 99px;
    background: var(--card);
    border: 1px solid var(--border);
    color: var(--muted);
}
.meta-badge span { color: var(--text); font-weight: 600; }

/* ── Insight cards ── */
.insight-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 12px;
}
.insight-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    display: flex;
    gap: 12px;
    align-items: flex-start;
}
.insight-icon {
    font-size: 1.4rem;
    line-height: 1;
    flex-shrink: 0;
    margin-top: 2px;
}
.insight-title {
    font-size: .78rem;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: .07em;
    margin-bottom: .25rem;
}
.insight-body {
    font-size: .88rem;
    color: var(--text);
    line-height: 1.45;
}

/* ── Upload area ── */
.upload-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem 2rem;
    border: 2px dashed rgba(79,142,247,0.3);
    border-radius: var(--radius);
    background: var(--card);
    text-align: center;
    margin: 2rem auto;
    max-width: 560px;
}
.upload-icon { font-size: 3rem; margin-bottom: 1rem; }
.upload-title { font-size: 1.15rem; font-weight: 600; color: var(--text); }
.upload-sub { font-size: .85rem; color: var(--muted); margin-top: .4rem; }

/* ── Plotly charts dark theme ── */
.js-plotly-plot { border-radius: var(--radius); overflow: hidden; }

/* ── Divider ── */
.divider { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }

/* ── Streamlit element tweaks ── */
div[data-testid="stFileUploader"] { color: var(--text); }
div[data-testid="stFileUploader"] label { color: var(--text) !important; }
.stSelectbox label, .stMultiSelect label, .stDateInput label,
.stSlider label, .stCheckbox label { color: var(--muted) !important; font-size: .8rem !important; }
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: var(--card) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PLOTLY DARK TEMPLATE
# ─────────────────────────────────────────────
CHART_PALETTE = ["#4f8ef7","#a78bfa","#34d399","#f59e0b","#f87171",
                 "#38bdf8","#fb923c","#e879f9","#a3e635","#2dd4bf"]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#94a3b8", size=12),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
    colorway=CHART_PALETTE,
)

def apply_template(fig, title=""):
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=title, font=dict(color="#e2e8f0", size=14)))
    return fig

# ─────────────────────────────────────────────
# SCHEMA DETECTION
# ─────────────────────────────────────────────
def detect_schema(df: pd.DataFrame) -> dict:
    """Auto-detect column types from dataframe."""
    schema = {"date": [], "numeric": [], "categorical": [], "id": [], "boolean": []}

    DATE_HINTS = {"date","time","year","month","day","created","updated","period","week","quarter"}
    ID_HINTS   = {"id","uuid","code","key","index","no","num","#","serial","ref"}
    CAT_LIMIT  = 50  # max unique values to be considered categorical

    for col in df.columns:
        col_lower = col.lower()
        series = df[col].dropna()
        if series.empty:
            continue

        # ── Try date parse ──
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            schema["date"].append(col)
            continue
        if any(h in col_lower for h in DATE_HINTS):
            try:
                pd.to_datetime(series.head(50), infer_datetime_format=True)
                schema["date"].append(col)
                continue
            except Exception:
                pass

        # ── Numeric ──
        if pd.api.types.is_numeric_dtype(df[col]):
            nuniq = series.nunique()
            if nuniq <= 2:
                schema["boolean"].append(col)
            elif any(h in col_lower for h in ID_HINTS) and nuniq > 0.8 * len(series):
                schema["id"].append(col)
            else:
                schema["numeric"].append(col)
            continue

        # ── Try coerce numeric (e.g. "$1,234") ──
        cleaned = series.astype(str).str.replace(r"[,$€£¥%\s]","",regex=True)
        try:
            coerced = pd.to_numeric(cleaned, errors="raise")
            df[col] = coerced
            schema["numeric"].append(col)
            continue
        except Exception:
            pass

        # ── Categorical vs ID string ──
        nuniq = series.nunique()
        if any(h in col_lower for h in ID_HINTS) and nuniq > 0.5 * len(series):
            schema["id"].append(col)
        elif nuniq <= CAT_LIMIT or nuniq / len(series) < 0.15:
            schema["categorical"].append(col)
        else:
            schema["id"].append(col)

    return schema


def pick_primary_measure(df: pd.DataFrame, numeric_cols: list) -> str | None:
    """Pick the most 'interesting' numeric column for primary KPIs."""
    if not numeric_cols:
        return None
    PRIORITY = ["revenue","sales","amount","value","total","profit","cost","price",
                "salary","income","spend","budget","score","qty","quantity"]
    for kw in PRIORITY:
        for col in numeric_cols:
            if kw in col.lower():
                return col
    # fallback: highest sum (likely most "important")
    return max(numeric_cols, key=lambda c: df[c].sum())


def fmt_number(n) -> str:
    """Smart number formatting."""
    if pd.isna(n):
        return "—"
    n = float(n)
    if abs(n) >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    if abs(n) >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if abs(n) >= 1_000:
        return f"{n/1_000:.1f}K"
    if n == int(n):
        return f"{int(n):,}"
    return f"{n:,.2f}"


# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    if file_name.endswith(".csv"):
        for enc in ["utf-8","latin1","cp1252"]:
            try:
                return pd.read_csv(io.BytesIO(file_bytes), encoding=enc)
            except Exception:
                pass
    else:
        return pd.read_excel(io.BytesIO(file_bytes))
    raise ValueError("Could not parse file.")


def coerce_dates(df: pd.DataFrame, date_cols: list) -> pd.DataFrame:
    for col in date_cols:
        try:
            df[col] = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")
        except Exception:
            pass
    return df


# ─────────────────────────────────────────────
# KPI GENERATION
# ─────────────────────────────────────────────
def build_kpis(df: pd.DataFrame, schema: dict, primary: str | None) -> list[dict]:
    """Return list of {label, value, sub, color} dicts."""
    kpis = []
    colors = CHART_PALETTE

    # 1. Total records
    kpis.append({"label":"Total Records","value":fmt_number(len(df)),"sub":"rows in dataset","color":colors[0]})

    # 2. Primary measure
    if primary:
        total = df[primary].sum()
        avg   = df[primary].mean()
        kpis.append({"label":f"Total {primary}","value":fmt_number(total),"sub":f"avg {fmt_number(avg)}","color":colors[1]})

    # 3. Secondary numeric measures
    for col in schema["numeric"]:
        if col == primary or len(kpis) >= 7:
            break
        kpis.append({"label":f"Avg {col}","value":fmt_number(df[col].mean()),"sub":f"max {fmt_number(df[col].max())}","color":colors[len(kpis)%len(colors)]})

    # 4. Categorical distincts
    for col in schema["categorical"][:3]:
        if len(kpis) >= 8:
            break
        kpis.append({"label":f"Unique {col}","value":fmt_number(df[col].nunique()),"sub":f"distinct values","color":colors[len(kpis)%len(colors)]})

    # 5. Date range
    if schema["date"]:
        dcol = schema["date"][0]
        mn, mx = df[dcol].min(), df[dcol].max()
        if pd.notna(mn) and pd.notna(mx):
            kpis.append({"label":"Date Range","value":str((mx-mn).days)+" d","sub":f"{mn.strftime('%b %Y')} – {mx.strftime('%b %Y')}","color":colors[len(kpis)%len(colors)]})

    return kpis[:8]


# ─────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────
def chart_time_series(df: pd.DataFrame, date_col: str, num_col: str) -> go.Figure:
    tmp = df[[date_col, num_col]].dropna()
    tmp[date_col] = pd.to_datetime(tmp[date_col])
    # resample monthly
    tmp = tmp.set_index(date_col).resample("ME")[num_col].sum().reset_index()
    fig = px.area(tmp, x=date_col, y=num_col, color_discrete_sequence=[CHART_PALETTE[0]])
    fig.update_traces(fill="tozeroy", line_width=2, fillcolor="rgba(79,142,247,0.15)")
    return apply_template(fig, f"{num_col} Over Time")


def chart_category_bar(df: pd.DataFrame, cat_col: str, num_col: str, top_n: int = 15) -> go.Figure:
    grp = df.groupby(cat_col, observed=True)[num_col].sum().nlargest(top_n).reset_index()
    grp = grp.sort_values(num_col, ascending=True)
    fig = px.bar(grp, x=num_col, y=cat_col, orientation="h",
                 color=num_col, color_continuous_scale=["#1e3a5f","#4f8ef7"])
    fig.update_layout(coloraxis_showscale=False, yaxis_title="", xaxis_title=num_col)
    return apply_template(fig, f"Top {top_n} {cat_col} by {num_col}")


def chart_distribution(df: pd.DataFrame, num_col: str) -> go.Figure:
    series = df[num_col].dropna()
    fig = px.histogram(series, nbins=30, color_discrete_sequence=[CHART_PALETTE[2]])
    fig.update_traces(marker_line_width=0)
    return apply_template(fig, f"Distribution of {num_col}")


def chart_category_pie(df: pd.DataFrame, cat_col: str, num_col: str | None) -> go.Figure:
    if num_col:
        grp = df.groupby(cat_col, observed=True)[num_col].sum().reset_index()
        vals, names = num_col, cat_col
    else:
        grp = df[cat_col].value_counts().reset_index()
        grp.columns = [cat_col, "count"]
        vals, names = "count", cat_col
    grp = grp.nlargest(10, vals)
    fig = px.pie(grp, values=vals, names=names, hole=.45,
                 color_discrete_sequence=CHART_PALETTE)
    fig.update_traces(textposition="outside", textinfo="percent+label")
    return apply_template(fig, f"{cat_col} Breakdown")


def chart_monthly_heatmap(df: pd.DataFrame, date_col: str, num_col: str) -> go.Figure:
    tmp = df[[date_col, num_col]].dropna()
    tmp[date_col] = pd.to_datetime(tmp[date_col])
    tmp["Month"] = tmp[date_col].dt.month_name().str[:3]
    tmp["Year"]  = tmp[date_col].dt.year
    pivot = tmp.pivot_table(index="Month", columns="Year", values=num_col, aggfunc="sum")
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    pivot = pivot.reindex([m for m in month_order if m in pivot.index])
    fig = px.imshow(pivot, color_continuous_scale=["#0d1117","#1e3a5f","#4f8ef7"],
                    aspect="auto", text_auto=True)
    return apply_template(fig, f"{num_col} Heatmap (Month × Year)")


def chart_scatter(df: pd.DataFrame, x_col: str, y_col: str, color_col: str | None) -> go.Figure:
    kw = dict(color=color_col) if color_col else {}
    fig = px.scatter(df.sample(min(2000, len(df))), x=x_col, y=y_col,
                     opacity=.7, color_discrete_sequence=CHART_PALETTE, **kw)
    return apply_template(fig, f"{y_col} vs {x_col}")


def chart_cat_count(df: pd.DataFrame, cat_col: str) -> go.Figure:
    grp = df[cat_col].value_counts().nlargest(15).reset_index()
    grp.columns = [cat_col, "count"]
    fig = px.bar(grp, x=cat_col, y="count", color="count",
                 color_continuous_scale=["#1e3a5f","#a78bfa"])
    fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-30)
    return apply_template(fig, f"{cat_col} Frequency")


def chart_box(df: pd.DataFrame, cat_col: str, num_col: str) -> go.Figure:
    top = df[cat_col].value_counts().nlargest(10).index
    tmp = df[df[cat_col].isin(top)]
    fig = px.box(tmp, x=cat_col, y=num_col, color=cat_col,
                 color_discrete_sequence=CHART_PALETTE)
    fig.update_layout(showlegend=False, xaxis_tickangle=-30)
    return apply_template(fig, f"{num_col} Distribution by {cat_col}")


# ─────────────────────────────────────────────
# INSIGHTS
# ─────────────────────────────────────────────
def generate_insights(df: pd.DataFrame, schema: dict, primary: str | None) -> list[dict]:
    insights = []
    cat_cols = schema["categorical"]
    num_cols = schema["numeric"]

    if primary and cat_cols:
        # Top performer
        grp = df.groupby(cat_cols[0], observed=True)[primary].sum()
        top_val, top_name = grp.max(), grp.idxmax()
        pct = grp.max() / grp.sum() * 100
        insights.append({"icon":"🏆","title":"Top Performer",
                          "body":f"<b>{top_name}</b> leads {cat_cols[0]} with {fmt_number(top_val)} ({pct:.1f}% of total)."})

        # Bottom performer
        bot_name = grp.idxmin()
        bot_val  = grp.min()
        insights.append({"icon":"⚠️","title":"Needs Attention",
                          "body":f"<b>{bot_name}</b> has the lowest {primary} at {fmt_number(bot_val)}."})

    if primary and schema["date"]:
        dcol = schema["date"][0]
        tmp = df[[dcol, primary]].dropna()
        tmp[dcol] = pd.to_datetime(tmp[dcol])
        monthly = tmp.set_index(dcol).resample("ME")[primary].sum()
        if len(monthly) >= 2:
            peak_m = monthly.idxmax()
            insights.append({"icon":"📈","title":"Peak Month",
                              "body":f"Highest {primary} in <b>{peak_m.strftime('%B %Y')}</b> at {fmt_number(monthly.max())}."})
            # recent trend
            last2 = monthly.iloc[-2:]
            if len(last2) == 2:
                chg = (last2.iloc[-1] - last2.iloc[-2]) / (abs(last2.iloc[-2]) + 1e-9) * 100
                arrow = "↑" if chg >= 0 else "↓"
                insights.append({"icon":"📊","title":"Recent Trend",
                                  "body":f"Last month changed by <b>{arrow} {abs(chg):.1f}%</b> vs previous month."})

    if primary:
        z = (df[primary] - df[primary].mean()) / (df[primary].std() + 1e-9)
        outlier_count = (z.abs() > 3).sum()
        if outlier_count > 0:
            insights.append({"icon":"🔍","title":"Outliers Detected",
                              "body":f"<b>{outlier_count}</b> records in {primary} fall outside 3 standard deviations."})

    if len(num_cols) >= 2:
        corr = df[num_cols].corr()
        np.fill_diagonal(corr.values, 0)
        max_corr = corr.abs().unstack().idxmax()
        c1, c2 = max_corr
        if c1 != c2:
            r = corr.loc[c1, c2]
            direction = "positive" if r > 0 else "negative"
            insights.append({"icon":"🔗","title":"Correlation Found",
                              "body":f"Strong {direction} correlation ({r:.2f}) between <b>{c1}</b> and <b>{c2}</b>."})

    if not insights:
        insights.append({"icon":"📋","title":"Dataset Loaded",
                          "body":f"Dataset has <b>{len(df):,}</b> rows and <b>{len(df.columns)}</b> columns."})

    return insights


# ─────────────────────────────────────────────
# SIDEBAR FILTERS  →  returns filtered df
# ─────────────────────────────────────────────
def render_sidebar_filters(df: pd.DataFrame, schema: dict) -> pd.DataFrame:
    st.sidebar.markdown("## ⚙ Filters")
    filtered = df.copy()

    # Date range
    if schema["date"]:
        dcol = schema["date"][0]
        dates = pd.to_datetime(filtered[dcol].dropna())
        if not dates.empty:
            mn, mx = dates.min().date(), dates.max().date()
            sel = st.sidebar.date_input("Date Range", value=(mn, mx),
                                         min_value=mn, max_value=mx, key="date_range")
            if isinstance(sel, (list, tuple)) and len(sel) == 2:
                start, end = pd.Timestamp(sel[0]), pd.Timestamp(sel[1])
                mask = (pd.to_datetime(filtered[dcol]) >= start) & (pd.to_datetime(filtered[dcol]) <= end)
                filtered = filtered[mask]

    # Categorical filters
    shown = 0
    for col in schema["categorical"]:
        if shown >= 5:
            break
        vals = sorted(df[col].dropna().unique().tolist())
        if 1 < len(vals) <= 100:
            sel = st.sidebar.multiselect(col, vals, default=[], key=f"filter_{col}")
            if sel:
                filtered = filtered[filtered[col].isin(sel)]
            shown += 1

    # Numeric range for primary
    if schema["numeric"]:
        num_col = schema["numeric"][0]
        col_data = df[num_col].dropna()
        if not col_data.empty:
            mn, mx = float(col_data.min()), float(col_data.max())
            if mn < mx:
                sel = st.sidebar.slider(f"{num_col} Range", mn, mx, (mn, mx), key=f"slider_{num_col}")
                filtered = filtered[(filtered[num_col] >= sel[0]) & (filtered[num_col] <= sel[1])]

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"<div style='color:#64748b;font-size:.8rem;'>Showing <b style='color:#e2e8f0'>{len(filtered):,}</b> of {len(df):,} rows</div>", unsafe_allow_html=True)
    return filtered


# ─────────────────────────────────────────────
# SECTION HEADER HELPER
# ─────────────────────────────────────────────
def section_header(title: str, badge: str = ""):
    badge_html = f'<span class="section-pill">{badge}</span>' if badge else ""
    st.markdown(f"""
    <div class="section-head">
        <h2>{title}</h2>
        {badge_html}
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
def main():
    # ── Sidebar upload ──
    with st.sidebar:
        st.markdown("""
        <div style='margin-bottom:1.5rem'>
            <div style='font-size:1.15rem;font-weight:700;color:#e2e8f0'>📊 Dashboard</div>
            <div style='font-size:.75rem;color:#64748b;margin-top:2px'>Universal Data Explorer</div>
        </div>
        """, unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload Dataset", type=["csv","xlsx","xls"],
                                     label_visibility="collapsed")

    if uploaded is None:
        # ── Welcome screen ──
        st.markdown("""
        <div style='padding:2rem 0;'>
            <div class='dash-title'>Universal Dashboard</div>
            <div class='dash-sub'>Drop any CSV or Excel file — instant analytics.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='upload-wrapper'>
            <div class='upload-icon'>⬆️</div>
            <div class='upload-title'>Upload your dataset</div>
            <div class='upload-sub'>Supports CSV, XLSX, XLS<br>The dashboard adapts to any tabular data</div>
        </div>
        """, unsafe_allow_html=True)

        # Feature preview
        cols = st.columns(3)
        features = [
            ("🧠","Smart Detection","Auto-identifies dates, numbers, and categories."),
            ("📈","Dynamic Charts","Selects the best visualizations for your data."),
            ("💡","Auto Insights","Surfaces top performers, trends, and outliers."),
        ]
        for col, (icon, title, desc) in zip(cols, features):
            col.markdown(f"""
            <div class='glass-card' style='text-align:center'>
                <div style='font-size:2rem;margin-bottom:.5rem'>{icon}</div>
                <div style='font-weight:600;margin-bottom:.3rem'>{title}</div>
                <div style='color:#64748b;font-size:.82rem'>{desc}</div>
            </div>""", unsafe_allow_html=True)
        return

    # ── Load & parse ──
    with st.spinner("Analyzing dataset…"):
        try:
            df_raw = load_data(uploaded.read(), uploaded.name)
        except Exception as e:
            st.error(f"Could not load file: {e}")
            return

    schema  = detect_schema(df_raw)
    df_raw  = coerce_dates(df_raw, schema["date"])
    primary = pick_primary_measure(df_raw, schema["numeric"])

    # ── Sidebar filters ──
    df = render_sidebar_filters(df_raw, schema)

    # ── Header ──
    file_label = uploaded.name.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
    st.markdown(f"""
    <div style='padding:.5rem 0 1rem'>
        <div class='dash-title'>{file_label}</div>
        <div class='dash-sub'>Automatically generated interactive dashboard</div>
        <div class='meta-row'>
            <div class='meta-badge'><span>{len(df):,}</span> rows</div>
            <div class='meta-badge'><span>{len(df.columns)}</span> columns</div>
            <div class='meta-badge'><span>{len(schema["numeric"])}</span> numeric</div>
            <div class='meta-badge'><span>{len(schema["categorical"])}</span> categorical</div>
            {'<div class="meta-badge">📅 <span>' + schema["date"][0] + '</span></div>' if schema["date"] else ""}
        </div>
    </div>
    <hr class='divider'>
    """, unsafe_allow_html=True)

    # ─── KPIs ───
    kpis = build_kpis(df, schema, primary)
    section_header("Key Metrics", "KPIs")
    kpi_html = '<div class="kpi-grid">'
    for kpi in kpis:
        kpi_html += f"""
        <div class='kpi-card' style='--accent-color:{kpi["color"]}'>
            <div class='kpi-label'>{kpi["label"]}</div>
            <div class='kpi-value'>{kpi["value"]}</div>
            <div class='kpi-sub'>{kpi["sub"]}</div>
        </div>"""
    kpi_html += "</div>"
    st.markdown(kpi_html, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ─── CHARTS ───
    section_header("Visualizations", "Auto-selected")

    has_date  = bool(schema["date"])
    has_num   = bool(schema["numeric"])
    has_cat   = bool(schema["categorical"])

    rendered = 0

    # Row 1: time series + category breakdown
    if has_date and primary:
        c1, c2 = st.columns([3, 2])
        with c1:
            with st.container():
                st.plotly_chart(chart_time_series(df, schema["date"][0], primary),
                                use_container_width=True)
        with c2:
            if has_cat:
                st.plotly_chart(chart_category_pie(df, schema["categorical"][0], primary),
                                use_container_width=True)
            else:
                st.plotly_chart(chart_distribution(df, primary), use_container_width=True)
        rendered += 1

    # Row 2: top-N bar + distribution
    if has_cat and primary:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(chart_category_bar(df, schema["categorical"][0], primary),
                            use_container_width=True)
        with c2:
            st.plotly_chart(chart_distribution(df, primary), use_container_width=True)
        rendered += 1

    # Row 3: heatmap + secondary category
    if has_date and primary:
        c1, c2 = st.columns([3, 2])
        with c1:
            st.plotly_chart(chart_monthly_heatmap(df, schema["date"][0], primary),
                            use_container_width=True)
        with c2:
            if len(schema["categorical"]) > 1:
                st.plotly_chart(chart_cat_count(df, schema["categorical"][1]),
                                use_container_width=True)
            elif has_cat:
                st.plotly_chart(chart_cat_count(df, schema["categorical"][0]),
                                use_container_width=True)
        rendered += 1

    # Row 4: scatter + box (if enough columns)
    if len(schema["numeric"]) >= 2:
        c1, c2 = st.columns(2)
        with c1:
            color_col = schema["categorical"][0] if has_cat else None
            st.plotly_chart(chart_scatter(df, schema["numeric"][0],
                                          schema["numeric"][1], color_col),
                            use_container_width=True)
        with c2:
            if has_cat and primary:
                st.plotly_chart(chart_box(df, schema["categorical"][0], primary),
                                use_container_width=True)
            else:
                st.plotly_chart(chart_distribution(df, schema["numeric"][1]),
                                use_container_width=True)
        rendered += 1

    # Fallback if nothing rendered
    if rendered == 0:
        if has_num:
            st.plotly_chart(chart_distribution(df, schema["numeric"][0]),
                            use_container_width=True)
        elif has_cat:
            st.plotly_chart(chart_cat_count(df, schema["categorical"][0]),
                            use_container_width=True)
        else:
            st.info("No plottable columns found. Check your dataset.")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ─── INSIGHTS ───
    section_header("Automated Insights", "AI-style")
    insights = generate_insights(df, schema, primary)

    ins_html = '<div class="insight-grid">'
    for ins in insights:
        ins_html += f"""
        <div class='insight-card'>
            <div class='insight-icon'>{ins["icon"]}</div>
            <div>
                <div class='insight-title'>{ins["title"]}</div>
                <div class='insight-body'>{ins["body"]}</div>
            </div>
        </div>"""
    ins_html += "</div>"
    st.markdown(ins_html, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ─── DATA PREVIEW ───
    with st.expander("📋 Data Preview", expanded=False):
        st.dataframe(df.head(200), use_container_width=True, height=300)

    # ─── SCHEMA ───
    with st.expander("🔬 Detected Schema", expanded=False):
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown("**📅 Date columns**")
            for c in schema["date"] or ["—"]:
                st.markdown(f"`{c}`")
        with sc2:
            st.markdown("**🔢 Numeric columns**")
            for c in schema["numeric"] or ["—"]:
                st.markdown(f"`{c}`")
        with sc3:
            st.markdown("**🏷 Categorical columns**")
            for c in schema["categorical"] or ["—"]:
                st.markdown(f"`{c}`")


if __name__ == "__main__":
    main()
