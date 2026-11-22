
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="ATM Analytics Dashboard",
    page_icon="🏧",
    layout="wide"
)

# ---------------- CUSTOM DESIGN ----------------

st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
h1 {
    color: #17365D;
}
.metric-card {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATASET ----------------

@st.cache_data
def load_data():
    df = pd.read_csv("atm_transactions.csv")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)

    df["Hour"] = pd.to_datetime(
        df["Time"].astype(str),
        format="mixed",
        errors="coerce"
    ).dt.hour

    return df

df = load_data()

# ---------------- SIDEBAR ----------------

st.sidebar.title("🏧 ATM Analytics")
st.sidebar.write("Transaction Monitoring System")

locations = st.sidebar.multiselect(
    "Select Location",
    options=sorted(df["Location"].dropna().unique()),
    default=sorted(df["Location"].dropna().unique())
)

statuses = st.sidebar.multiselect(
    "Select Status",
    options=sorted(df["Status"].dropna().unique()),
    default=sorted(df["Status"].dropna().unique())
)

filtered_df = df[
    (df["Location"].isin(locations)) &
    (df["Status"].isin(statuses))
]

# ---------------- PAGE TITLE ----------------

st.title("🏧 ATM Usage & Transaction Analysis")
st.write("Interactive ATM Transaction Monitoring Dashboard")

st.markdown("---")

# ---------------- KPI CALCULATIONS ----------------

total_transactions = len(filtered_df)
total_amount = filtered_df["Amount"].sum()

average_amount = (
    filtered_df["Amount"].mean()
    if total_transactions > 0 else 0
)

successful = (
    filtered_df["Status"].str.lower() == "success"
).sum()

failed = (
    filtered_df["Status"].str.lower() == "failed"
).sum()

success_rate = (
    successful / total_transactions * 100
    if total_transactions > 0 else 0
)

# ---------------- KPI CARDS ----------------

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Transactions", total_transactions)
col2.metric("Total Amount", f"₹{total_amount:,.0f}")
col3.metric("Average Amount", f"₹{average_amount:,.0f}")
col4.metric("Success Rate", f"{success_rate:.1f}%")

col5, col6, col7 = st.columns(3)

col5.metric("Successful Transactions", successful)
col6.metric("Failed Transactions", failed)

most_used_atm = (
    filtered_df["ATM_ID"].mode().iloc[0]
    if not filtered_df.empty else "N/A"
)

col7.metric("Most Used ATM", most_used_atm)

st.markdown("---")

# ---------------- CHART 1: TRANSACTION TYPE ----------------

st.subheader("📊 Transaction Type Analysis")

if not filtered_df.empty:
    transaction_counts = filtered_df["Transaction_Type"].value_counts()

    fig1 = px.bar(
        x=transaction_counts.index,
        y=transaction_counts.values,
        labels={"x": "Transaction Type", "y": "Number of Transactions"},
        color=transaction_counts.index,
        title="Transactions by Type"
    )

    st.plotly_chart(fig1, use_container_width=True)

# ---------------- CHART 2: STATUS ----------------

st.subheader("✅ Transaction Status Analysis")

if not filtered_df.empty:
    status_counts = filtered_df["Status"].value_counts()

    fig2 = px.pie(
        names=status_counts.index,
        values=status_counts.values,
        title="Successful vs Failed Transactions",
        hole=0.4
    )

    st.plotly_chart(fig2, use_container_width=True)

# ---------------- CHART 3: LOCATION ----------------

st.subheader("📍 Location-wise ATM Usage")

if not filtered_df.empty:
    location_counts = filtered_df["Location"].value_counts()

    fig3 = px.bar(
        x=location_counts.index,
        y=location_counts.values,
        labels={"x": "Location", "y": "Transactions"},
        title="ATM Usage by Location"
    )

    st.plotly_chart(fig3, use_container_width=True)

# ---------------- CHART 4: HOURLY ANALYSIS ----------------

st.subheader("🕒 Hourly Transaction Analysis")

hourly_usage = (
    filtered_df.dropna(subset=["Hour"])
    .groupby("Hour")
    .size()
    .reset_index(name="Transactions")
)

if not hourly_usage.empty:
    fig4 = px.line(
        hourly_usage,
        x="Hour",
        y="Transactions",
        markers=True,
        title="Transactions by Hour"
    )

    st.plotly_chart(fig4, use_container_width=True)

# ---------------- CHART 5: DAILY ANALYSIS ----------------

st.subheader("📅 Daily Transaction Analysis")

daily_usage = (
    filtered_df.groupby("Date")
    .size()
    .reset_index(name="Transactions")
)

if not daily_usage.empty:
    fig5 = px.bar(
        daily_usage,
        x="Date",
        y="Transactions",
        title="Daily ATM Transactions"
    )

    st.plotly_chart(fig5, use_container_width=True)

# ---------------- CHART 6: ATM USAGE ----------------

st.subheader("🏧 ATM Machine Usage")

if not filtered_df.empty:
    atm_counts = filtered_df["ATM_ID"].value_counts()

    fig6 = px.bar(
        x=atm_counts.index,
        y=atm_counts.values,
        labels={"x": "ATM ID", "y": "Number of Transactions"},
        title="Transactions by ATM Machine"
    )

    st.plotly_chart(fig6, use_container_width=True)

# ---------------- TRANSACTION TABLE ----------------

st.markdown("---")
st.subheader("📋 Transaction Details")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# ---------------- FINAL SUMMARY ----------------

st.markdown("---")
st.subheader("📌 Project Summary")

if not filtered_df.empty:
    st.write(f"**Total Transactions:** {total_transactions}")
    st.write(f"**Total Transaction Amount:** ₹{total_amount:,.0f}")
    st.write(f"**Successful Transactions:** {successful}")
    st.write(f"**Failed Transactions:** {failed}")
    st.write(f"**Success Rate:** {success_rate:.1f}%")
    st.write(f"**Most Used ATM:** {most_used_atm}")

st.success("ATM Transaction Analysis Completed Successfully!")
