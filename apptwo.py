"""
Nassau Candy Distributor — Profit Intelligence Dashboard
Run: streamlit run nassau_candy_dashboard.py
Requirements: pip install streamlit pandas plotly
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Nassau Candy | Profit Intelligence",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    .stApp { background: #0f1117; color: #e8eaf0; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #161b27 !important;
        border-right: 1px solid #2a2f3e;
    }
    section[data-testid="stSidebar"] * { color: #c8ccd8 !important; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #161b27;
        border: 1px solid #2a2f3e;
        border-radius: 12px;
        padding: 16px 20px;
    }
    [data-testid="metric-container"] label { color: #8892a4 !important; font-size: 12px !important; letter-spacing: 0.08em; text-transform: uppercase; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #f0f4ff !important; font-size: 28px !important; font-weight: 700 !important; }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 13px !important; }

    /* Section headers */
    .section-header {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #4e9af1;
        margin: 24px 0 8px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid #2a2f3e;
    }

    /* Tab bar */
    .stTabs [data-baseweb="tab-list"] {
        background: #161b27;
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
        border: 1px solid #2a2f3e;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #8892a4;
        font-weight: 500;
        font-size: 14px;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: #4e9af1 !important;
        color: #fff !important;
    }

    /* Plotly chart containers */
    .js-plotly-plot { border-radius: 12px; }

    /* Risk flag badges */
    .badge-high { background: #1a3a1a; color: #4ade80; border: 1px solid #4ade80; border-radius: 6px; padding: 2px 10px; font-size: 12px; font-weight: 600; }
    .badge-low  { background: #3a1a1a; color: #f87171; border: 1px solid #f87171; border-radius: 6px; padding: 2px 10px; font-size: 12px; font-weight: 600; }

    /* Title */
    .dashboard-title {
        font-size: 28px; font-weight: 700; color: #f0f4ff;
        display: flex; align-items: center; gap: 12px;
    }
    .dashboard-subtitle { font-size: 14px; color: #8892a4; margin-top: 4px; }

    /* Divider */
    hr { border-color: #2a2f3e !important; }

    /* Scrollbars */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #161b27; }
    ::-webkit-scrollbar-thumb { background: #2a2f3e; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PLOTLY DARK TEMPLATE
# ─────────────────────────────────────────────
CHART_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor="#161b27",
        plot_bgcolor="#161b27",
        font=dict(family="DM Sans", color="#c8ccd8", size=12),
        colorway=["#4e9af1", "#a78bfa", "#34d399", "#fb923c", "#f472b6", "#facc15", "#60a5fa"],
        xaxis=dict(gridcolor="#2a2f3e", linecolor="#2a2f3e", zerolinecolor="#2a2f3e"),
        yaxis=dict(gridcolor="#2a2f3e", linecolor="#2a2f3e", zerolinecolor="#2a2f3e"),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#2a2f3e"),
        margin=dict(t=40, l=10, r=10, b=10),
    )
)

COLORS = {
    "Chocolate": "#fb923c",
    "Sugar":     "#a78bfa",
    "Other":     "#34d399",
    "Atlantic":  "#4e9af1",
    "Pacific":   "#f472b6",
    "Interior":  "#facc15",
    "Gulf":      "#60a5fa",
}

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    df["Ship_Date"]  = pd.to_datetime(df["Ship_Date"],  errors="coerce")
    for col in ["Sales", "Units", "Gross_Profit", "Cost", "profit",
                "Profit_margin", "Profit_per_unit", "Total_profit", "Contribution"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

RAW = load_data("data/Nassau Candy Distributor3.csv")

# ─────────────────────────────────────────────
# SIDEBAR — FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🍬 Nassau Candy")
    st.markdown("<div class='section-header'>Date Range</div>", unsafe_allow_html=True)

    min_d, max_d = RAW["Order_Date"].min().date(), RAW["Order_Date"].max().date()
    date_range = st.date_input("Order Date", value=(min_d, max_d), min_value=min_d, max_value=max_d)

    st.markdown("<div class='section-header'>Division</div>", unsafe_allow_html=True)
    divisions_all = sorted(RAW["Division"].dropna().unique())
    sel_divs = st.multiselect("Select Divisions", divisions_all, default=divisions_all)

    st.markdown("<div class='section-header'>Region</div>", unsafe_allow_html=True)
    regions_all = sorted(RAW["Region"].dropna().unique())
    sel_regions = st.multiselect("Select Regions", regions_all, default=regions_all)

    st.markdown("<div class='section-header'>Margin Threshold (%)</div>", unsafe_allow_html=True)
    margin_thresh = st.slider("Flag products below this margin", 0, 100, 30, step=5)

    st.markdown("<div class='section-header'>Product Search</div>", unsafe_allow_html=True)
    product_search = st.text_input("Search by product name", placeholder="e.g. Wonka Bar…")

    st.markdown("<div class='section-header'>Ship Mode</div>", unsafe_allow_html=True)
    ship_modes = sorted(RAW["Ship_Mode"].dropna().unique())
    sel_ship = st.multiselect("Ship Mode", ship_modes, default=ship_modes)

# ─────────────────────────────────────────────
# FILTER DATA
# ─────────────────────────────────────────────
df = RAW.copy()

if len(date_range) == 2:
    df = df[(df["Order_Date"].dt.date >= date_range[0]) & (df["Order_Date"].dt.date <= date_range[1])]

if sel_divs:
    df = df[df["Division"].isin(sel_divs)]
if sel_regions:
    df = df[df["Region"].isin(sel_regions)]
if sel_ship:
    df = df[df["Ship_Mode"].isin(sel_ship)]
if product_search.strip():
    df = df[df["Product_Name"].str.contains(product_search.strip(), case=False, na=False)]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class='dashboard-title'>🍬 Nassau Candy — Profit Intelligence Dashboard</div>
<div class='dashboard-subtitle'>Distribution analytics · Margin diagnostics · Concentration risk</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ─────────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────────
total_sales    = df["Sales"].sum()
total_profit   = df["profit"].sum()
avg_margin     = df["Profit_margin"].mean()
total_units    = df["Units"].sum()
num_products   = df["Product_ID"].nunique()
high_contrib   = (df["contribution_flag"] == "High Contributor").sum()
pct_high       = high_contrib / len(df) * 100 if len(df) else 0
at_risk        = (df["Profit_margin"] < margin_thresh).sum()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("💰 Total Sales",      f"${total_sales:,.0f}")
k2.metric("📈 Total Profit",     f"${total_profit:,.0f}")
k3.metric("🎯 Avg Margin",       f"{avg_margin:.1f}%")
k4.metric("📦 Units Sold",       f"{total_units:,.0f}")
k5.metric("🏷️ Unique Products",  f"{num_products}")
k6.metric("⚠️ Below Threshold",  f"{at_risk} SKUs", delta=f"{margin_thresh}% threshold", delta_color="inverse")

st.markdown("---")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Product Profitability",
    "🏢 Division Performance",
    "🔬 Cost & Margin Diagnostics",
    "🎯 Profit Concentration"
])

# ═══════════════════════════════════════════════
# TAB 1 — PRODUCT PROFITABILITY
# ═══════════════════════════════════════════════
with tab1:
    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("#### 🥇 Profit Margin Leaderboard — Top 20 Products")
        prod_margin = (
            df.groupby("Product_Name")
            .agg(Avg_Margin=("Profit_margin","mean"), Total_Profit=("profit","sum"), Sales=("Sales","sum"))
            .reset_index()
            .sort_values("Avg_Margin", ascending=False)
            .head(20)
        )
        prod_margin["Color"] = prod_margin["Avg_Margin"].apply(
            lambda x: "#4ade80" if x >= 70 else ("#facc15" if x >= margin_thresh else "#f87171")
        )
        fig_lead = go.Figure(go.Bar(
            x=prod_margin["Avg_Margin"],
            y=prod_margin["Product_Name"],
            orientation="h",
            marker_color=prod_margin["Color"],
            text=prod_margin["Avg_Margin"].apply(lambda x: f"{x:.1f}%"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Margin: %{x:.1f}%<extra></extra>",
        ))
        
        fig_lead.add_vline(x=margin_thresh, line_dash="dash", line_color="#f87171",
                           annotation_text=f"Threshold {margin_thresh}%", annotation_font_color="#f87171")
        st.plotly_chart(fig_lead, use_container_width=True)

    with c2:
        st.markdown("#### 💸 Profit Contribution — Top 20 Products")
        prod_profit = (
            df.groupby("Product_Name")
            .agg(Total_Profit=("profit","sum"), Division=("Division","first"))
            .reset_index()
            .sort_values("Total_Profit", ascending=False)
            .head(20)
        )
        prod_profit["Color"] = prod_profit["Division"].map(COLORS)
        fig_contrib = go.Figure(go.Bar(
            x=prod_profit["Total_Profit"],
            y=prod_profit["Product_Name"],
            orientation="h",
            marker_color=prod_profit["Color"],
            text=prod_profit["Total_Profit"].apply(lambda x: f"${x:,.0f}"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Profit: $%{x:,.0f}<extra></extra>",
        ))
           
        st.plotly_chart(fig_contrib, use_container_width=True)

    # Product detail table
    st.markdown("#### 📋 Product-Level Detail")
    prod_table = (
        df.groupby(["Product_ID", "Product_Name", "Division"])
        .agg(
            Avg_Margin   =("Profit_margin","mean"),
            Total_Profit =("profit","sum"),
            Total_Sales  =("Sales","sum"),
            Avg_PPU      =("Profit_per_unit","mean"),
            Orders       =("Order_ID","nunique"),
        )
        .reset_index()
        .sort_values("Total_Profit", ascending=False)
    )
    prod_table["Risk"] = prod_table["Avg_Margin"].apply(
        lambda x: "🟢 Healthy" if x >= 70 else ("🟡 Watch" if x >= margin_thresh else "🔴 At Risk")
    )
    prod_table_disp = prod_table.rename(columns={
        "Product_ID":"ID","Product_Name":"Product","Division":"Div",
        "Avg_Margin":"Margin %","Total_Profit":"Profit $","Total_Sales":"Sales $",
        "Avg_PPU":"Profit/Unit","Orders":"# Orders","Risk":"Status"
    })
    prod_table_disp["Margin %"] = prod_table_disp["Margin %"].round(1)
    prod_table_disp["Profit $"] = prod_table_disp["Profit $"].round(0)
    prod_table_disp["Sales $"]  = prod_table_disp["Sales $"].round(0)
    prod_table_disp["Profit/Unit"] = prod_table_disp["Profit/Unit"].round(2)
    st.dataframe(prod_table_disp, use_container_width=True, height=300)

# ═══════════════════════════════════════════════
# TAB 2 — DIVISION PERFORMANCE
# ═══════════════════════════════════════════════
with tab2:
    div_agg = (
        df.groupby("Division")
        .agg(
            Revenue=("Sales","sum"),
            Profit =("profit","sum"),
            Units  =("Units","sum"),
            Orders =("Order_ID","nunique"),
            Avg_Margin=("Profit_margin","mean"),
        )
        .reset_index()
    )
    div_agg["Margin_pct"] = (div_agg["Profit"] / div_agg["Revenue"] * 100).round(1)
    div_agg["Color"] = div_agg["Division"].map(COLORS)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 📊 Revenue vs Profit by Division")
        fig_rv = go.Figure()
        fig_rv.add_trace(go.Bar(
            name="Revenue", x=div_agg["Division"], y=div_agg["Revenue"],
            marker_color=[COLORS.get(d,"#4e9af1") for d in div_agg["Division"]],
            opacity=0.6, text=div_agg["Revenue"].apply(lambda x: f"${x/1e6:.2f}M"),
            textposition="outside",
        ))
        fig_rv.add_trace(go.Bar(
            name="Profit", x=div_agg["Division"], y=div_agg["Profit"],
            marker_color=[COLORS.get(d,"#4e9af1") for d in div_agg["Division"]],
            opacity=1.0, text=div_agg["Profit"].apply(lambda x: f"${x/1e6:.2f}M"),
            textposition="outside",
        ))
        fig_rv.update_layout(**CHART_TEMPLATE["layout"].to_plotly_json(),
                             barmode="group", height=380, yaxis_title="Value ($)")
        st.plotly_chart(fig_rv, use_container_width=True)

    with c2:
        st.markdown("#### 🎯 Margin Distribution by Division")
        fig_box = go.Figure()
        for div in df["Division"].dropna().unique():
            sub = df[df["Division"] == div]["Profit_margin"].dropna()
            fig_box.add_trace(go.Violin(
                y=sub, name=div,
                box_visible=True, meanline_visible=True,
                fillcolor=COLORS.get(div, "#4e9af1"),
                line_color=COLORS.get(div, "#4e9af1"),
                opacity=0.7,
            ))
        fig_box.update_layout(**CHART_TEMPLATE["layout"].to_plotly_json(),
                              height=380, showlegend=False, yaxis_title="Profit Margin (%)")
        fig_box.add_hline(y=margin_thresh, line_dash="dash", line_color="#f87171",
                          annotation_text=f"Threshold {margin_thresh}%", annotation_font_color="#f87171")
        st.plotly_chart(fig_box, use_container_width=True)

    # Division summary cards
    st.markdown("#### 📌 Division Scorecards")
    cols = st.columns(len(div_agg))
    for i, (_, row) in enumerate(div_agg.iterrows()):
        with cols[i]:
            color = COLORS.get(row["Division"], "#4e9af1")
            st.markdown(f"""
            <div style="background:#161b27;border:1px solid {color};border-top:3px solid {color};
                        border-radius:12px;padding:16px;text-align:center;">
              <div style="font-size:18px;font-weight:700;color:{color}">{row['Division']}</div>
              <div style="font-size:12px;color:#8892a4;margin:8px 0 4px">Revenue</div>
              <div style="font-size:20px;font-weight:600;color:#f0f4ff">${row['Revenue']/1e6:.2f}M</div>
              <div style="font-size:12px;color:#8892a4;margin:8px 0 4px">Profit</div>
              <div style="font-size:20px;font-weight:600;color:#4ade80">${row['Profit']/1e6:.2f}M</div>
              <div style="font-size:12px;color:#8892a4;margin:8px 0 4px">Avg Margin</div>
              <div style="font-size:20px;font-weight:600;color:#facc15">{row['Avg_Margin']:.1f}%</div>
              <div style="font-size:12px;color:#8892a4;margin:8px 0 4px">Orders</div>
              <div style="font-size:16px;font-weight:500;color:#c8ccd8">{row['Orders']:,}</div>
            </div>""", unsafe_allow_html=True)

    # Monthly trend by division
    st.markdown("#### 📅 Monthly Revenue Trend by Division")
    df["YearMonth"] = df["Order_Date"].dt.to_period("M").astype(str)
    monthly = df.groupby(["YearMonth","Division"])["Sales"].sum().reset_index()
    fig_trend = px.line(
        monthly, x="YearMonth", y="Sales", color="Division",
        color_discrete_map=COLORS, markers=True,
        labels={"Sales":"Revenue ($)","YearMonth":"Month","Division":"Division"},
    )
    fig_trend.update_layout(**CHART_TEMPLATE["layout"].to_plotly_json(), height=350)
    fig_trend.update_traces(line_width=2, marker_size=5)
    st.plotly_chart(fig_trend, use_container_width=True)

# ═══════════════════════════════════════════════
# TAB 3 — COST & MARGIN DIAGNOSTICS
# ═══════════════════════════════════════════════
with tab3:
    c1, c2 = st.columns([3, 2])

    with c1:
        st.markdown("#### 🔵 Cost vs Sales Scatter — Margin Zones")
        scatter_df = df[["Product_Name","Sales","Cost","Profit_margin","Division","profit"]].dropna()
        scatter_df["Risk"] = scatter_df["Profit_margin"].apply(
            lambda x: "🟢 Healthy" if x >= 70 else ("🟡 Watch" if x >= margin_thresh else "🔴 At Risk")
        )
        fig_sc = px.scatter(
            scatter_df, x="Cost", y="Sales",
            color="Division", color_discrete_map=COLORS,
            size="profit", size_max=18,
            hover_name="Product_Name",
            hover_data={"Profit_margin":":.1f","profit":":.2f","Risk":True},
            labels={"Cost":"Unit Cost ($)","Sales":"Unit Sales ($)"},
            opacity=0.75,
        )
        # Margin zone bands
        max_cost = scatter_df["Cost"].max()
        for thresh_pct, clr, lbl in [(100, "#4ade8020",""), (margin_thresh, "#f8717120", f"Below {margin_thresh}% margin")]:
            x_line = np.linspace(0, max_cost, 100)
            y_line = x_line / (1 - thresh_pct/100) if thresh_pct < 100 else x_line
            fig_sc.add_trace(go.Scatter(
                x=x_line, y=y_line, mode="lines",
                line=dict(color="#f87171" if thresh_pct == margin_thresh else "#4ade80",
                          dash="dash", width=1.5),
                name=lbl, showlegend=(lbl != ""),
            ))
        fig_sc.update_layout(**CHART_TEMPLATE["layout"].to_plotly_json(), height=440)
        st.plotly_chart(fig_sc, use_container_width=True)

    with c2:
        st.markdown("#### ⚠️ Margin Risk Flags")
        risk_df = (
            df[df["Profit_margin"] < margin_thresh]
            .groupby("Product_Name")
            .agg(Avg_Margin=("Profit_margin","mean"), Total_Sales=("Sales","sum"), Division=("Division","first"))
            .reset_index()
            .sort_values("Avg_Margin")
            .head(15)
        )
        if risk_df.empty:
            st.success(f"✅ No products below {margin_thresh}% margin threshold.")
        else:
            for _, row in risk_df.iterrows():
                margin_color = "#f87171" if row["Avg_Margin"] < margin_thresh * 0.7 else "#facc15"
                st.markdown(f"""
                <div style="background:#161b27;border:1px solid #2a2f3e;border-left:3px solid {margin_color};
                            border-radius:8px;padding:10px 14px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center">
                  <div>
                    <div style="font-size:13px;font-weight:600;color:#f0f4ff">{row['Product_Name'][:38]}</div>
                    <div style="font-size:11px;color:#8892a4">{row['Division']} · ${row['Total_Sales']:,.0f} sales</div>
                  </div>
                  <div style="font-size:18px;font-weight:700;color:{margin_color}">{row['Avg_Margin']:.1f}%</div>
                </div>""", unsafe_allow_html=True)

    # Cost efficiency heatmap
    st.markdown("#### 🗺️ Margin Heatmap — Division × Region")
    heat_df = df.groupby(["Division","Region"])["Profit_margin"].mean().reset_index()
    heat_pivot = heat_df.pivot(index="Division", columns="Region", values="Profit_margin").fillna(0)
    fig_heat = go.Figure(go.Heatmap(
        z=heat_pivot.values,
        x=heat_pivot.columns.tolist(),
        y=heat_pivot.index.tolist(),
        colorscale=[[0,"#f87171"],[0.5,"#facc15"],[1,"#4ade80"]],
        text=np.round(heat_pivot.values, 1),
        texttemplate="%{text}%",
        showscale=True,
        hovertemplate="Division: %{y}<br>Region: %{x}<br>Avg Margin: %{z:.1f}%<extra></extra>",
    ))
    fig_heat.update_layout(**CHART_TEMPLATE["layout"].to_plotly_json(), height=280,
                           xaxis_title="Region", yaxis_title="Division")
    st.plotly_chart(fig_heat, use_container_width=True)

# ═══════════════════════════════════════════════
# TAB 4 — PROFIT CONCENTRATION
# ═══════════════════════════════════════════════
with tab4:
    c1, c2 = st.columns([3, 2])

    with c1:
        st.markdown("#### 📈 Pareto Chart — Profit Concentration")
        pareto_df = (
            df.groupby("Product_Name")["profit"]
            .sum().sort_values(ascending=False)
            .reset_index()
        )
        pareto_df["Cum_Profit"] = pareto_df["profit"].cumsum()
        pareto_df["Cum_Pct"]    = pareto_df["Cum_Profit"] / pareto_df["profit"].sum() * 100
        pareto_df["Rank"]       = range(1, len(pareto_df) + 1)
        pareto_df["Rank_Pct"]   = pareto_df["Rank"] / len(pareto_df) * 100

        fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
        fig_pareto.add_trace(
            go.Bar(x=pareto_df["Rank"], y=pareto_df["profit"],
                   name="Product Profit", marker_color="#4e9af1", opacity=0.8,
                   hovertemplate="%{customdata}<br>Profit: $%{y:,.0f}<extra></extra>",
                   customdata=pareto_df["Product_Name"]),
            secondary_y=False,
        )
        fig_pareto.add_trace(
            go.Scatter(x=pareto_df["Rank"], y=pareto_df["Cum_Pct"],
                       name="Cumulative %", line=dict(color="#f472b6", width=2.5),
                       hovertemplate="Rank %{x}: %{y:.1f}% cumulative<extra></extra>"),
            secondary_y=True,
        )
        fig_pareto.add_hline(y=80, secondary_y=True, line_dash="dash", line_color="#facc15",
                             annotation_text="80% threshold", annotation_font_color="#facc15",
                             annotation_position="top right")
        fig_pareto.update_layout(**CHART_TEMPLATE["layout"].to_plotly_json(), height=420)
        fig_pareto.update_yaxes(title_text="Profit ($)", secondary_y=False,
                                gridcolor="#2a2f3e", color="#c8ccd8")
        fig_pareto.update_yaxes(title_text="Cumulative Profit %", secondary_y=True,
                                range=[0, 105], gridcolor="rgba(0,0,0,0)", color="#c8ccd8")
        fig_pareto.update_xaxes(title_text="Product Rank", gridcolor="#2a2f3e")
        st.plotly_chart(fig_pareto, use_container_width=True)

    with c2:
        st.markdown("#### 🎯 80/20 Dependency Indicators")
        total_p = pareto_df["profit"].sum()
        top10   = pareto_df.head(int(len(pareto_df) * 0.1))
        top20   = pareto_df.head(int(len(pareto_df) * 0.2))
        idx_80  = (pareto_df["Cum_Pct"] >= 80).idxmax()
        n_80    = idx_80 + 1
        pct_80  = n_80 / len(pareto_df) * 100

        indicators = [
            ("Top 10% of SKUs contribute", f"{top10['profit'].sum()/total_p*100:.1f}% of profit", "#4e9af1"),
            ("Top 20% of SKUs contribute", f"{top20['profit'].sum()/total_p*100:.1f}% of profit", "#a78bfa"),
            ("SKUs needed for 80% profit",  f"{n_80} SKUs ({pct_80:.0f}% of catalog)", "#facc15"),
            ("High Contributor SKUs",        f"{(df['contribution_flag']=='High Contributor').sum():,} orders ({pct_high:.1f}%)", "#4ade80"),
        ]
        for label, value, color in indicators:
            st.markdown(f"""
            <div style="background:#161b27;border:1px solid {color};border-radius:10px;
                        padding:14px 18px;margin-bottom:12px;">
              <div style="font-size:12px;color:#8892a4;margin-bottom:4px">{label}</div>
              <div style="font-size:22px;font-weight:700;color:{color}">{value}</div>
            </div>""", unsafe_allow_html=True)

        # Pie by division contribution
        st.markdown("#### 🥧 Profit Share by Division")
        div_pie = df.groupby("Division")["profit"].sum().reset_index()
        fig_pie = go.Figure(go.Pie(
            labels=div_pie["Division"], values=div_pie["profit"],
            hole=0.55,
            marker_colors=[COLORS.get(d,"#4e9af1") for d in div_pie["Division"]],
            textinfo="percent+label",
            hovertemplate="%{label}<br>$%{value:,.0f}<br>%{percent}<extra></extra>",
        ))
        fig_pie.update_layout(**CHART_TEMPLATE["layout"].to_plotly_json(), height=280, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    

    # Top profit concentration table
    st.markdown("#### 🏅 Top 30 Profit-Generating Products")
    top30 = pareto_df.head(30).copy()
    top30["Cum_Pct"] = top30["Cum_Pct"].round(1)
    top30["profit"]  = top30["profit"].round(0)
    top30["Pct_of_Total"] = (top30["profit"] / total_p * 100).round(2)
    top30_disp = top30[["Rank","Product_Name","profit","Pct_of_Total","Cum_Pct"]].rename(columns={
        "Rank":"#","Product_Name":"Product","profit":"Total Profit ($)",
        "Pct_of_Total":"% of Total","Cum_Pct":"Cumulative %"
    })
    st.dataframe(top30_disp, use_container_width=True, height=300)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;color:#4a5166;font-size:12px;padding:8px'>"
    f"Nassau Candy Distributor · Profit Intelligence Dashboard · "
    f"{len(df):,} records loaded · {df['Product_ID'].nunique()} products · "
    f"{df['Division'].nunique()} divisions · {df['Region'].nunique()} regions</div>",
    unsafe_allow_html=True,
)

