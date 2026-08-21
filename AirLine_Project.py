import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

st.set_page_config(page_title="Airline Analytics Dashboard", layout="wide", page_icon="✈️")

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background-color: #0d1117; }
    .stApp { background-color: #0d1117; color: #e6edf3; }

    .metric-card {
        background: linear-gradient(135deg, #161b22, #1c2333);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-label { font-size: 13px; color: #8b949e; font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase; }
    .metric-value { font-size: 32px; font-weight: 700; color: #58a6ff; margin-top: 6px; }

    .section-title {
        font-size: 18px;
        font-weight: 600;
        color: #e6edf3;
        border-left: 3px solid #58a6ff;
        padding-left: 12px;
        margin-bottom: 16px;
        margin-top: 8px;
    }

    .stSidebar { background-color: #161b22; border-right: 1px solid #30363d; }
    .stSidebar [data-testid="stSidebarNav"] { background-color: #161b22; }

    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #161b22, #1c2333);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ── Load Data ────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(r"D:\firefox downloads\air data\Airline Dataset Updated - v2.csv")
    df['Departure Date'] = pd.to_datetime(df['Departure Date'], errors='coerce')
    df['Month'] = df['Departure Date'].dt.month_name()
    df['Month_Num'] = df['Departure Date'].dt.month
    return df

df = load_data()

COLORS = {
    "On Time":  "#3fb950",
    "Delayed":  "#f0883e",
    "Cancelled":"#f85149"
}
ACCENT = "#58a6ff"
BG     = "#05295e"
PAPER  = "#0d1117"
FONT   = "#e6edf3"

plotly_theme = dict(
    paper_bgcolor=PAPER,
    plot_bgcolor=BG,
    font=dict(color=FONT, family="Inter"),
    xaxis=dict(gridcolor="#21262d", linecolor="#30363d"),
    yaxis=dict(gridcolor="#21262d", linecolor="#30363d"),
)

# ── Sidebar Filters ────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/airplane-mode-on.png", width=60)
st.sidebar.title("✈️ Airline Dashboard")
st.sidebar.markdown("---")

page = st.sidebar.radio("📂 Navigate", [
    "🏠 Overview",
    "🌍 Geography",
    "👥 Passenger Demographics",
    "📅 Time Trends",
    "✈️ Flight Status",
    "🛩️ Live Flight Tracker"
])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 Filters")

continents = ["All"] + sorted(df["Continents"].dropna().unique().tolist())
sel_continent = st.sidebar.selectbox("Continent", continents)

statuses = ["All"] + sorted(df["Flight Status"].dropna().unique().tolist())
sel_status = st.sidebar.selectbox("Flight Status", statuses)

age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
age_range = st.sidebar.slider("Age Range", age_min, age_max, (age_min, age_max))

gender_opts = ["All"] + sorted(df["Gender"].dropna().unique().tolist())
sel_gender = st.sidebar.selectbox("Gender", gender_opts)

# ── Apply Filters ──────────────────────────────────────────
fdf = df.copy()
if sel_continent != "All":
    fdf = fdf[fdf["Continents"] == sel_continent]
if sel_status != "All":
    fdf = fdf[fdf["Flight Status"] == sel_status]
if sel_gender != "All":
    fdf = fdf[fdf["Gender"] == sel_gender]
fdf = fdf[(fdf["Age"] >= age_range[0]) & (fdf["Age"] <= age_range[1])]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Showing:** {len(fdf):,} passengers")


# ══════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.title("✈️ Airline Analytics Dashboard")
    st.markdown("Real-time insights across **98,619 passenger records**.")
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Passengers", f"{len(fdf):,}")
    with c2:
        on_time = len(fdf[fdf["Flight Status"] == "On Time"])
        st.metric("On Time", f"{on_time:,}", delta=f"{on_time/max(len(fdf),1)*100:.1f}%")
    with c3:
        delayed = len(fdf[fdf["Flight Status"] == "Delayed"])
        st.metric("Delayed", f"{delayed:,}", delta=f"-{delayed/max(len(fdf),1)*100:.1f}%", delta_color="inverse")
    with c4:
        cancelled = len(fdf[fdf["Flight Status"] == "Cancelled"])
        st.metric("Cancelled", f"{cancelled:,}", delta=f"-{cancelled/max(len(fdf),1)*100:.1f}%", delta_color="inverse")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Flight Status Distribution</div>', unsafe_allow_html=True)
        status_counts = fdf["Flight Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig = px.pie(status_counts, names="Status", values="Count",
                     color="Status", color_discrete_map=COLORS, hole=0.5)
        fig.update_layout(**plotly_theme, showlegend=True, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Passengers by Continent</div>', unsafe_allow_html=True)
        cont_counts = fdf["Continents"].value_counts().reset_index()
        cont_counts.columns = ["Continent", "Count"]
        fig2 = px.bar(cont_counts, x="Continent", y="Count",
                      color="Count", color_continuous_scale="Blues",
                      text="Count")
        fig2.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig2.update_layout(**plotly_theme, coloraxis_showscale=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE: GEOGRAPHY
# ══════════════════════════════════════════════════════════
elif page == "🌍 Geography":
    st.title("🌍 Geographic Analysis")
    st.markdown("---")

    st.markdown('<div class="section-title">Passengers by Country</div>', unsafe_allow_html=True)
    country_counts = fdf["Country Name"].value_counts().reset_index()
    country_counts.columns = ["Country", "Count"]
    fig = px.choropleth(country_counts, locations="Country", locationmode="country names",
                        color="Count", color_continuous_scale="Blues",
                        title="Passenger Volume by Country")
    fig.update_layout(**plotly_theme, margin=dict(t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Top 15 Countries</div>', unsafe_allow_html=True)
        top_countries = country_counts.head(15)
        fig2 = px.bar(top_countries, x="Count", y="Country", orientation="h",
                      color="Count", color_continuous_scale="Blues")
        fig2.update_layout(**plotly_theme, coloraxis_showscale=False, margin=dict(t=10, b=10))
        fig2.update_yaxes(autorange="reversed", gridcolor="#21262d")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Flight Status by Continent</div>', unsafe_allow_html=True)
        cont_status = fdf.groupby(["Continents", "Flight Status"]).size().reset_index(name="Count")
        fig3 = px.bar(cont_status, x="Continents", y="Count", color="Flight Status",
                      color_discrete_map=COLORS, barmode="group")
        fig3.update_layout(**plotly_theme, margin=dict(t=10, b=10))
        st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE: DEMOGRAPHICS
# ══════════════════════════════════════════════════════════
elif page == "👥 Passenger Demographics":
    st.title("👥 Passenger Demographics")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Gender Distribution</div>', unsafe_allow_html=True)
        gender_counts = fdf["Gender"].value_counts().reset_index()
        gender_counts.columns = ["Gender", "Count"]
        fig = px.pie(gender_counts, names="Gender", values="Count",
                     color="Gender",
                     color_discrete_map={"Male": "#58a6ff", "Female": "#f778ba"}, hole=0.4)
        fig.update_layout(**plotly_theme, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Age Distribution</div>', unsafe_allow_html=True)
        fig2 = px.histogram(fdf, x="Age", nbins=30, color_discrete_sequence=[ACCENT])
        fig2.update_layout(**plotly_theme, bargap=0.05, margin=dict(t=10, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Age Distribution by Flight Status</div>', unsafe_allow_html=True)
    fig3 = px.box(fdf, x="Flight Status", y="Age", color="Flight Status",
                  color_discrete_map=COLORS)
    fig3.update_layout(**plotly_theme, margin=dict(t=10, b=10))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="section-title">Gender vs Flight Status</div>', unsafe_allow_html=True)
    gen_status = fdf.groupby(["Gender", "Flight Status"]).size().reset_index(name="Count")
    fig4 = px.bar(gen_status, x="Gender", y="Count", color="Flight Status",
                  color_discrete_map=COLORS, barmode="group", text="Count")
    fig4.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig4.update_layout(**plotly_theme, margin=dict(t=10, b=10))
    st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE: TIME TRENDS
# ══════════════════════════════════════════════════════════
elif page == "📅 Time Trends":
    st.title("📅 Time Trends")
    st.markdown("---")

    month_order = ["January","February","March","April","May","June",
                   "July","August","September","October","November","December"]

    st.markdown('<div class="section-title">Monthly Passenger Volume</div>', unsafe_allow_html=True)
    monthly = fdf.groupby(["Month", "Month_Num"]).size().reset_index(name="Count")
    monthly = monthly.sort_values("Month_Num")
    fig = px.line(monthly, x="Month", y="Count", markers=True,
                  color_discrete_sequence=[ACCENT])
    fig.update_traces(line=dict(width=2.5), marker=dict(size=8))
    fig.update_layout(**plotly_theme, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Monthly Flight Status Breakdown</div>', unsafe_allow_html=True)
        ms = fdf.groupby(["Month", "Month_Num", "Flight Status"]).size().reset_index(name="Count")
        ms = ms.sort_values("Month_Num")
        fig2 = px.bar(ms, x="Month", y="Count", color="Flight Status",
                      color_discrete_map=COLORS, barmode="stack")
        fig2.update_layout(**plotly_theme, margin=dict(t=10, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Avg Age of Passengers per Month</div>', unsafe_allow_html=True)
        avg_age = fdf.groupby(["Month", "Month_Num"])["Age"].mean().reset_index()
        avg_age = avg_age.sort_values("Month_Num")
        fig3 = px.bar(avg_age, x="Month", y="Age",
                      color="Age", color_continuous_scale="Blues",
                      text=avg_age["Age"].round(1))
        fig3.update_traces(textposition='outside')
        fig3.update_layout(**plotly_theme, coloraxis_showscale=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE: FLIGHT STATUS
# ══════════════════════════════════════════════════════════
elif page == "✈️ Flight Status":
    st.title("✈️ Flight Status Analysis")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Status by Continent</div>', unsafe_allow_html=True)
        cs = fdf.groupby(["Continents", "Flight Status"]).size().reset_index(name="Count")
        fig = px.bar(cs, x="Count", y="Continents", color="Flight Status",
                     color_discrete_map=COLORS, barmode="stack", orientation="h")
        fig.update_layout(**plotly_theme, margin=dict(t=10, b=10))
        fig.update_yaxes(autorange="reversed", gridcolor="#21262d")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Status by Gender</div>', unsafe_allow_html=True)
        gs = fdf.groupby(["Gender", "Flight Status"]).size().reset_index(name="Count")
        fig2 = px.bar(gs, x="Gender", y="Count", color="Flight Status",
                      color_discrete_map=COLORS, barmode="group", text="Count")
        fig2.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig2.update_layout(**plotly_theme, margin=dict(t=10, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Top 10 Nationalities by Flight Status</div>', unsafe_allow_html=True)
    top_nat = fdf["Nationality"].value_counts().head(10).index.tolist()
    nat_df = fdf[fdf["Nationality"].isin(top_nat)]
    nat_status = nat_df.groupby(["Nationality", "Flight Status"]).size().reset_index(name="Count")
    fig3 = px.bar(nat_status, x="Nationality", y="Count", color="Flight Status",
                  color_discrete_map=COLORS, barmode="group")
    fig3.update_layout(**plotly_theme, margin=dict(t=10, b=10))
    st.plotly_chart(fig3, use_container_width=True)

    

# ══════════════════════════════════════════════════════════
# PAGE: LIVE FLIGHT TRACKER
# ══════════════════════════════════════════════════════════
elif page == "🛩️ Live Flight Tracker":
    st.title("🛩️ Live Flight Tracker")
    st.markdown("Real-time flight data powered by **OpenSky Network API** — updates every 30 seconds.")
    st.markdown("---")

    # ── Fetch from OpenSky ─────────────────────────────────
    @st.cache_data(ttl=30)
    def fetch_flights():
        try:
            url = "https://opensky-network.org/api/states/all"
            resp = requests.get(url, timeout=15)
            if resp.status_code != 200:
                return None, f"API error: {resp.status_code}"
            data = resp.json()
            states = data.get("states", [])
            if not states:
                return None, "No flight data returned."
            cols = ["icao24","callsign","origin_country","time_position","last_contact",
                    "longitude","latitude","baro_altitude","on_ground","velocity",
                    "true_track","vertical_rate","sensors","geo_altitude",
                    "squawk","spi","position_source"]
            rows = []
            for s in states:
                if len(s) >= 17:
                    rows.append(s[:17])
            df_f = pd.DataFrame(rows, columns=cols)
            df_f = df_f[df_f["latitude"].notna() & df_f["longitude"].notna()]
            df_f = df_f[df_f["on_ground"] == False]
            df_f["callsign"]       = df_f["callsign"].astype(str).str.strip()
            df_f["velocity_kmh"]   = pd.to_numeric(df_f["velocity"], errors="coerce") * 3.6
            df_f["altitude_m"]     = pd.to_numeric(df_f["baro_altitude"], errors="coerce")
            df_f["latitude"]       = pd.to_numeric(df_f["latitude"], errors="coerce")
            df_f["longitude"]      = pd.to_numeric(df_f["longitude"], errors="coerce")
            df_f["vertical_rate"]  = pd.to_numeric(df_f["vertical_rate"], errors="coerce")
            df_f["true_track"]     = pd.to_numeric(df_f["true_track"], errors="coerce")
            return df_f, None
        except Exception as e:
            return None, str(e)

    # ── Controls ───────────────────────────────────────────
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 1])
    with col_ctrl1:
        country_filter = st.text_input("🔍 Filter by Country (e.g. India, United States)", "")
    with col_ctrl2:
        max_flights = st.slider("Max flights to display on map", 100, 5000, 1000, step=100)
    with col_ctrl3:
        st.markdown("<br>", unsafe_allow_html=True)
        refresh_btn = st.button("🔄 Refresh Now")

    if refresh_btn:
        st.cache_data.clear()

    # ── Load data ──────────────────────────────────────────
    with st.spinner("Fetching live flights from OpenSky Network..."):
        df_live, err = fetch_flights()

    if err:
        st.error(f"❌ Could not fetch live data: {err}")
        st.info("💡 OpenSky may be temporarily unavailable. Try clicking **Refresh Now** in a moment.")
        st.stop()

    # Apply country filter
    if country_filter.strip():
        df_live = df_live[df_live["origin_country"].str.contains(country_filter.strip(), case=False, na=False)]

    df_map = df_live.dropna(subset=["latitude","longitude"]).head(max_flights)

    # ── KPI Row ────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("✈️ Live Flights", f"{len(df_map):,}")
    with k2:
        avg_spd = df_map["velocity_kmh"].dropna().mean()
        st.metric("⚡ Avg Speed", f"{avg_spd:.0f} km/h" if pd.notna(avg_spd) else "N/A")
    with k3:
        avg_alt = df_map["altitude_m"].dropna().mean()
        st.metric("🏔️ Avg Altitude", f"{avg_alt:,.0f} m" if pd.notna(avg_alt) else "N/A")
    with k4:
        countries = df_map["origin_country"].nunique()
        st.metric("🌍 Countries", f"{countries}")

    st.markdown("---")

    # ── Live Map ───────────────────────────────────────────
    st.markdown('<div class="section-title">🗺️ Live Flight Map</div>', unsafe_allow_html=True)

    df_map["hover_text"] = (
        "✈️ " + df_map["callsign"].fillna("Unknown") +
        "<br>🌍 " + df_map["origin_country"].fillna("Unknown") +
        "<br>📍 Lat: " + df_map["latitude"].round(2).astype(str) +
        "  Lon: " + df_map["longitude"].round(2).astype(str) +
        "<br>⚡ Speed: " + df_map["velocity_kmh"].fillna(0).round(0).astype(int).astype(str) + " km/h" +
        "<br>🏔️ Alt: " + df_map["altitude_m"].fillna(0).round(0).astype(int).astype(str) + " m" +
        "<br>↕️ V.Rate: " + df_map["vertical_rate"].fillna(0).round(1).astype(str) + " m/s" +
        "<br>🧭 Track: " + df_map["true_track"].fillna(0).round(0).astype(int).astype(str) + "°"
    )

    fig_map = go.Figure(go.Scattergeo(
        lat=df_map["latitude"],
        lon=df_map["longitude"],
        mode="markers",
        marker=dict(
            size=5,
            color=df_map["velocity_kmh"].fillna(0),
            colorscale="Turbo",
            colorbar=dict(title="Speed (km/h)", thickness=12, len=0.5),
            opacity=0.85,
            cmin=0,
            cmax=1000,
        ),
        text=df_map["hover_text"],
        hoverinfo="text",
        name="Flights"
    ))

    fig_map.update_layout(
        paper_bgcolor="#0d1117",
        geo=dict(
            bgcolor="#0d1117",
            showland=True, landcolor="#161b22",
            showocean=True, oceancolor="#0d1b2e",
            showlakes=True, lakecolor="#0d1b2e",
            showcountries=True, countrycolor="#30363d",
            showcoastlines=True, coastlinecolor="#21262d",
            projection_type="natural earth",
        ),
        margin=dict(t=10, b=10, l=0, r=0),
        height=520,
        font=dict(color="#e6edf3", family="Inter"),
    )

    st.plotly_chart(fig_map, use_container_width=True)
    st.caption(f"🕐 Data fetched live · Showing {len(df_map):,} airborne flights · Hover over a dot for details")

    st.markdown("---")

    # ── Charts Row ─────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Top 15 Countries by Active Flights</div>', unsafe_allow_html=True)
        top_countries = df_map["origin_country"].value_counts().head(15).reset_index()
        top_countries.columns = ["Country", "Flights"]
        fig_c = px.bar(top_countries, x="Flights", y="Country", orientation="h",
                       color="Flights", color_continuous_scale="Blues", text="Flights")
        fig_c.update_traces(textposition="outside")
        fig_c.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
                            font=dict(color="#e6edf3", family="Inter"),
                            coloraxis_showscale=False, margin=dict(t=10, b=10))
        fig_c.update_yaxes(autorange="reversed", gridcolor="#21262d")
        fig_c.update_xaxes(gridcolor="#21262d")
        st.plotly_chart(fig_c, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Speed Distribution of Live Flights</div>', unsafe_allow_html=True)
        spd = df_map["velocity_kmh"].dropna()
        spd = spd[(spd > 0) & (spd < 1500)]
        fig_s = px.histogram(spd, nbins=40, color_discrete_sequence=["#58a6ff"])
        fig_s.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
                            font=dict(color="#e6edf3", family="Inter"),
                            xaxis=dict(gridcolor="#21262d", title="Speed (km/h)"),
                            yaxis=dict(gridcolor="#21262d", title="Flights"),
                            bargap=0.05, margin=dict(t=10, b=10))
        st.plotly_chart(fig_s, use_container_width=True)

    # ── Altitude vs Speed Scatter ──────────────────────────
    st.markdown('<div class="section-title">Altitude vs Speed (Live Flights)</div>', unsafe_allow_html=True)
    df_scatter = df_map.dropna(subset=["altitude_m","velocity_kmh"])
    df_scatter = df_scatter[(df_scatter["velocity_kmh"] > 0) & (df_scatter["altitude_m"] > 0)]
    fig_sc = px.scatter(df_scatter.sample(min(2000, len(df_scatter)), random_state=42),
                        x="velocity_kmh", y="altitude_m",
                        color="origin_country", opacity=0.6,
                        hover_data=["callsign","origin_country","latitude","longitude"],
                        labels={"velocity_kmh":"Speed (km/h)", "altitude_m":"Altitude (m)"},
                        color_discrete_sequence=px.colors.qualitative.Vivid)
    fig_sc.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
                         font=dict(color="#e6edf3", family="Inter"),
                         xaxis=dict(gridcolor="#21262d"),
                         yaxis=dict(gridcolor="#21262d"),
                         showlegend=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig_sc, use_container_width=True)

    # ── Data Table ─────────────────────────────────────────
    st.markdown('<div class="section-title">📋 Live Flight Data Table</div>', unsafe_allow_html=True)
    table_cols = ["callsign","origin_country","latitude","longitude",
                  "altitude_m","velocity_kmh","vertical_rate","true_track"]
    df_table = df_map[table_cols].copy()
    df_table.columns = ["Callsign","Country","Latitude","Longitude",
                        "Altitude (m)","Speed (km/h)","Vertical Rate (m/s)","Track (°)"]
    df_table = df_table.fillna("N/A")
    for col in ["Altitude (m)","Speed (km/h)","Vertical Rate (m/s)","Track (°)"]:
        df_table[col] = pd.to_numeric(df_table[col], errors="coerce").round(1)
    st.dataframe(df_table.reset_index(drop=True), use_container_width=True, height=350)
    st.caption(f"Showing top {len(df_table):,} flights · Auto-refreshes every 30 seconds")
