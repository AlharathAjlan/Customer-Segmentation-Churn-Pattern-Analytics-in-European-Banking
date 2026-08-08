import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------------------
# Page config — must be the first Streamlit command
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Bank Churn Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------
# Data loading + cleaning (cached so it only runs once, not on every click)
# ---------------------------------------------------------------------
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    drop_cols = [c for c in ["Surname", "Year"] if c in df.columns]
    df = df.drop(columns=drop_cols)

    def age_band(age):
        if age < 30:
            return "<30"
        elif age <= 45:
            return "30-45"
        elif age <= 60:
            return "46-60"
        return "60+"

    def tenure_group(t):
        if t <= 2:
            return "New"
        elif t <= 6:
            return "Mid-term"
        return "Long-term"

    def balance_segment(b):
        if b == 0:
            return "Zero-balance"
        elif b < 100_000:
            return "Low-balance"
        return "High-balance"

    def credit_band(score):
        if score < 580:
            return "Low"
        elif score < 670:
            return "Medium"
        return "High"

    df["AgeGroup"] = df["Age"].apply(age_band)
    df["TenureGroup"] = df["Tenure"].apply(tenure_group)
    df["BalanceSegment"] = df["Balance"].apply(balance_segment)
    df["CreditBand"] = df["CreditScore"].apply(credit_band)

    return df


DATA_PATH = "European_Bank.csv"  # <-- point this at your actual CSV filename
df = load_data(DATA_PATH)

# ---------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------
st.sidebar.title("Bank Churn Analytics")
page = st.sidebar.radio(
    "Navigate",
    ["Overall Summary", "Geography", "Age & Tenure", "High-Value Customers"],
)

# ---------------------------------------------------------------------
# Global segment filters (must come BEFORE the modules, so filtered_df
# exists before any module tries to use it)
# ---------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Segment Filters")

geo_options = st.sidebar.multiselect(
    "Geography",
    options=sorted(df["Geography"].unique()),
    default=list(df["Geography"].unique()),
)
gender_options = st.sidebar.multiselect(
    "Gender",
    options=sorted(df["Gender"].unique()),
    default=list(df["Gender"].unique()),
)
age_options = st.sidebar.multiselect(
    "Age Group",
    options=["<30", "30-45", "46-60", "60+"],
    default=["<30", "30-45", "46-60", "60+"],
)
active_options = st.sidebar.multiselect(
    "Active Member",
    options=[0, 1],
    default=[0, 1],
    format_func=lambda x: "Active" if x == 1 else "Inactive",
)

filtered_df = df[
    df["Geography"].isin(geo_options)
    & df["Gender"].isin(gender_options)
    & df["AgeGroup"].isin(age_options)
    & df["IsActiveMember"].isin(active_options)
]

st.sidebar.markdown(f"**{len(filtered_df):,}** of {len(df):,} customers match filters")

if len(filtered_df) == 0:
    st.warning("No customers match the selected filters. Adjust filters in the sidebar.")
    st.stop()

# ---------------------------------------------------------------------
# MODULE 1: Overall Churn Summary
# ---------------------------------------------------------------------
if page == "Overall Summary":
    st.title("Overall Churn Summary")

    total_customers = len(filtered_df)
    churned = int(filtered_df["Exited"].sum())
    retained = total_customers - churned
    churn_rate = churned / total_customers * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", f"{total_customers:,}")
    col2.metric("Churned Customers", f"{churned:,}")
    col3.metric("Overall Churn Rate", f"{churn_rate:.2f}%")

    st.subheader("Churn Split")
    pie_data = pd.DataFrame(
        {"Status": ["Retained", "Churned"], "Count": [retained, churned]}
    )
    fig = px.pie(
        pie_data,
        names="Status",
        values="Count",
        color="Status",
        color_discrete_map={"Retained": "#2E86AB", "Churned": "#E63946"},
        hole=0.4,
    )
    st.plotly_chart(fig, width="stretch")

    # -----------------------------------------------------------------
    # Key Performance Indicators
    # -----------------------------------------------------------------
    st.markdown("---")
    st.subheader("Key Performance Indicators")

    baseline_churn_rate = filtered_df["Exited"].mean() * 100

    seg_rows = []
    for col in ["Geography", "AgeGroup", "BalanceSegment"]:
        seg = filtered_df.groupby(col)["Exited"].mean().mul(100).round(2)
        for k, v in seg.items():
            seg_rows.append({"Segment Type": col, "Segment": k, "Churn Rate %": v})
    st.markdown("**Segment Churn Rate**")
    st.dataframe(pd.DataFrame(seg_rows), width="stretch")

    st.markdown("**Geographic Risk Index** (Regional Churn Rate ÷ Overall Baseline)")
    geo_risk = filtered_df.groupby("Geography")["Exited"].mean().mul(100).round(2)
    geo_risk_df = geo_risk.reset_index()
    geo_risk_df.columns = ["Geography", "Churn Rate %"]
    geo_risk_df["Risk Index"] = (geo_risk_df["Churn Rate %"] / baseline_churn_rate).round(2)
    st.dataframe(geo_risk_df.sort_values("Risk Index", ascending=False), width="stretch")

    hv_rate = filtered_df[filtered_df["BalanceSegment"] == "High-balance"]["Exited"].mean() * 100
    st.markdown(f"**High-Value Churn Ratio:** {hv_rate:.2f}% (vs {baseline_churn_rate:.2f}% baseline)")

    active_rate = filtered_df[filtered_df["IsActiveMember"] == 1]["Exited"].mean() * 100
    inactive_rate = filtered_df[filtered_df["IsActiveMember"] == 0]

# ---------------------------------------------------------------------
# MODULE 2: Geography-wise Churn Visualization
# ---------------------------------------------------------------------
elif page == "Geography":
    st.title("Churn by Geography")

    geo_stats = filtered_df.groupby("Geography")["Exited"].agg(
        total_customers="count", churned_customers="sum"
    ).reset_index()
    geo_stats["churn_rate_%"] = (
        geo_stats["churned_customers"] / geo_stats["total_customers"] * 100
    ).round(2)
    geo_stats = geo_stats.sort_values("churn_rate_%", ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Churn Rate by Country")
        fig1 = px.bar(
            geo_stats,
            x="Geography",
            y="churn_rate_%",
            color="Geography",
            text="churn_rate_%",
        )
        fig1.update_traces(texttemplate="%{text}%", textposition="outside")
        fig1.add_hline(
            y=filtered_df["Exited"].mean() * 100,
            line_dash="dash",
            line_color="gray",
            annotation_text="Filtered baseline",
        )
        st.plotly_chart(fig1, width="stretch")

    with col2:
        st.subheader("Share of Total Churn")
        fig2 = px.pie(
            geo_stats,
            names="Geography",
            values="churned_customers",
        )
        st.plotly_chart(fig2, width="stretch")

    st.subheader("Geography × Age Group Churn Rate")
    pivot = filtered_df.pivot_table(
        index="Geography", columns="AgeGroup", values="Exited", aggfunc="mean"
    ) * 100
    fig3 = px.imshow(
        pivot.round(2),
        text_auto=True,
        color_continuous_scale="Reds",
        labels=dict(color="Churn Rate %"),
    )
    st.plotly_chart(fig3, width="stretch")

    st.subheader("Drill down: click a country to see its customers")
    selected_geo = st.selectbox("Select Geography", geo_stats["Geography"])
    st.dataframe(
        filtered_df[filtered_df["Geography"] == selected_geo][
            ["Gender", "Age", "Balance", "NumOfProducts", "IsActiveMember", "Exited"]
        ],
        width="stretch",
    )

    st.dataframe(geo_stats, width="stretch")

## ---------------------------------------------------------------------
# MODULE 3: Age & Tenure Churn Comparison
# ---------------------------------------------------------------------
elif page == "Age & Tenure":
    st.title("Age & Tenure Churn Comparison")

    age_order = ["<30", "30-45", "46-60", "60+"]
    tenure_order = ["New", "Mid-term", "Long-term"]

    total_churned_filtered = filtered_df["Exited"].sum()

    age_stats = filtered_df.groupby("AgeGroup")["Exited"].agg(
        total_customers="count", churned_customers="sum"
    ).reindex(age_order).reset_index()
    age_stats["churn_rate_%"] = (
        age_stats["churned_customers"] / age_stats["total_customers"] * 100
    ).round(2)
    age_stats["%_of_total_churn"] = (
        age_stats["churned_customers"] / total_churned_filtered * 100
    ).round(2)

    tenure_stats = filtered_df.groupby("TenureGroup")["Exited"].agg(
        total_customers="count", churned_customers="sum"
    ).reindex(tenure_order).reset_index()
    tenure_stats["churn_rate_%"] = (
        tenure_stats["churned_customers"] / tenure_stats["total_customers"] * 100
    ).round(2)
    tenure_stats["%_of_total_churn"] = (
        tenure_stats["churned_customers"] / total_churned_filtered * 100
    ).round(2)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Churn Rate by Age Group")
        fig1 = px.bar(
            age_stats, x="AgeGroup", y="churn_rate_%",
            text="churn_rate_%", color="churn_rate_%",
            color_continuous_scale="Reds",
        )
        fig1.update_traces(texttemplate="%{text}%", textposition="outside")
        fig1.add_hline(y=filtered_df["Exited"].mean() * 100, line_dash="dash", line_color="gray")
        st.plotly_chart(fig1, width="stretch")

    with col2:
        st.subheader("Churn Rate by Tenure Group")
        fig2 = px.bar(
            tenure_stats, x="TenureGroup", y="churn_rate_%",
            text="churn_rate_%", color="churn_rate_%",
            color_continuous_scale="Blues",
        )
        fig2.update_traces(texttemplate="%{text}%", textposition="outside")
        fig2.add_hline(y=filtered_df["Exited"].mean() * 100, line_dash="dash", line_color="gray")
        st.plotly_chart(fig2, width="stretch")

    st.subheader("Age Group × Tenure Group Churn Rate")
    pivot = filtered_df.pivot_table(
        index="AgeGroup", columns="TenureGroup",
        values="Exited", aggfunc="mean"
    ).reindex(index=age_order, columns=tenure_order) * 100
    fig3 = px.imshow(
        pivot.round(2), text_auto=True,
        color_continuous_scale="Reds",
        labels=dict(color="Churn Rate %"),
    )
    st.plotly_chart(fig3, width="stretch")

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**Age Group Breakdown**")
        st.dataframe(age_stats, width="stretch")
    with col4:
        st.markdown("**Tenure Group Breakdown**")
        st.dataframe(tenure_stats, width="stretch")

# ---------------------------------------------------------------------
# MODULE 4: High-Value Customer Churn Explorer
# ---------------------------------------------------------------------
elif page == "High-Value Customers":
    st.title("High-Value Customer Churn Explorer")

    st.markdown("Define what counts as 'high-value' using the slider below.")
    balance_cutoff = st.slider(
        "High-value balance threshold",
        min_value=0,
        max_value=int(df["Balance"].max()),
        value=100_000,
        step=5_000,
    )

    high_value = filtered_df[filtered_df["Balance"] >= balance_cutoff]
    hv_churn_rate = high_value["Exited"].mean() * 100 if len(high_value) else 0
    baseline_rate = filtered_df["Exited"].mean() * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("High-Value Customers", f"{len(high_value):,}")
    col2.metric(
        "High-Value Churn Rate",
        f"{hv_churn_rate:.2f}%",
        delta=f"{hv_churn_rate - baseline_rate:+.2f} pts vs baseline",
        delta_color="inverse",
    )

    total_balance_all = filtered_df["Balance"].sum()
    total_balance_churned = filtered_df[filtered_df["Exited"] == 1]["Balance"].sum()
    pct_balance_at_risk = (
        (total_balance_churned / total_balance_all) * 100 if total_balance_all > 0 else 0
    )
    col3.metric("Total Balance Lost to Churn", f"{pct_balance_at_risk:.2f}%")

    st.subheader("Churn Rate by Balance Quartile")
    df_q = filtered_df.copy()
    df_q["BalanceQuartile"] = pd.qcut(
        df_q["Balance"].rank(method="first"), 4,
        labels=["Q1 (low)", "Q2", "Q3", "Q4 (high)"],
    )
    quartile_stats = df_q.groupby("BalanceQuartile")["Exited"].mean().mul(100).round(2).reset_index()
    quartile_stats.columns = ["Balance Quartile", "Churn Rate %"]

    fig = px.bar(
        quartile_stats, x="Balance Quartile", y="Churn Rate %",
        text="Churn Rate %", color="Churn Rate %",
        color_continuous_scale="Reds",
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    st.plotly_chart(fig, width="stretch")

    st.subheader("Revenue at Risk")
    churned_subset = filtered_df[filtered_df["Exited"] == 1]
    avg_lost = churned_subset["Balance"].mean() if len(churned_subset) > 0 else 0
    st.markdown(
        f"""
        - **Total balance across filtered customers:** ${total_balance_all:,.0f}
        - **Total balance held by churned customers:** ${total_balance_churned:,.0f}
        - **Average balance per churned customer:** ${avg_lost:,.0f}
        """
    )

    st.subheader(f"High-Value Customer Records (Balance ≥ ${balance_cutoff:,})")
    st.dataframe(
        high_value[["Geography", "Age", "Balance", "NumOfProducts", "IsActiveMember", "Exited"]],
        width="stretch",
    )

