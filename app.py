import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# -------------------------
# CONFIG
# -------------------------

st.set_page_config(
    page_title="Smart Governance CRM",
    page_icon="🏛️",
    layout="wide"
)

DATA_FILE = "complaints.csv"

# -------------------------
# INIT DATA
# -------------------------

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=[
        "ID",
        "Name",
        "Location",
        "Category",
        "Issue",
        "Status",
        "Date"
    ])
    df.to_csv(DATA_FILE, index=False)

df = pd.read_csv(DATA_FILE)

# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.title("🏛️ Smart Governance CRM")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Submit Complaint",
        "Analytics",
        "AI Insights",
        "Admin Panel"
    ]
)

# -------------------------
# DASHBOARD
# -------------------------

if page == "Dashboard":

    st.title("📊 Governance Dashboard")

    total = len(df)
    resolved = len(df[df["Status"] == "Resolved"])
    pending = len(df[df["Status"] == "Pending"])

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Complaints", total)
    col2.metric("Resolved", resolved)
    col3.metric("Pending", pending)

    if total > 0:

        st.subheader("Complaints by Category")

        fig = px.histogram(
            df,
            x="Category",
            color="Category"
        )

        st.plotly_chart(fig, use_container_width=True)

# -------------------------
# SUBMIT COMPLAINT
# -------------------------

elif page == "Submit Complaint":

    st.title("📝 Submit Complaint")

    name = st.text_input("Name")
    location = st.text_input("Location")

    category = st.selectbox(
        "Category",
        [
            "Road",
            "Electricity",
            "Water",
            "Sanitation",
            "Other"
        ]
    )

    issue = st.text_area("Describe Issue")

    if st.button("Submit"):

        if name and location and issue:

            new_id = len(df) + 1

            new_row = {
                "ID": new_id,
                "Name": name,
                "Location": location,
                "Category": category,
                "Issue": issue,
                "Status": "Pending",
                "Date": datetime.now()
            }

            df = pd.concat(
                [df, pd.DataFrame([new_row])],
                ignore_index=True
            )

            df.to_csv(DATA_FILE, index=False)

            st.success("Complaint submitted successfully!")

        else:
            st.error("Please fill all fields")

# -------------------------
# ANALYTICS
# -------------------------

elif page == "Analytics":

    st.title("📈 Analytics")

    if len(df) > 0:

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Complaints by Location")

            fig = px.histogram(
                df,
                x="Location",
                color="Location"
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:

            st.subheader("Status Distribution")

            fig = px.pie(
                df,
                names="Status"
            )

            st.plotly_chart(fig, use_container_width=True)

# -------------------------
# AI INSIGHTS
# -------------------------

elif page == "AI Insights":

    st.title("🤖 AI Insights")

    if len(df) > 0:

        location_counts = df["Location"].value_counts()

        top_location = location_counts.idxmax()
        top_count = location_counts.max()

        st.success(
            f"⚠️ Priority Area: {top_location} ({top_count} complaints)"
        )

        category_counts = df["Category"].value_counts()

        top_category = category_counts.idxmax()

        st.info(
            f"Most common issue category: {top_category}"
        )

# -------------------------
# ADMIN PANEL
# -------------------------

elif page == "Admin Panel":

    st.title("🛠️ Admin Panel")

    st.dataframe(df)

    complaint_id = st.number_input(
        "Enter Complaint ID to Resolve",
        min_value=1,
        step=1
    )

    if st.button("Mark as Resolved"):

        df.loc[df["ID"] == complaint_id, "Status"] = "Resolved"

        df.to_csv(DATA_FILE, index=False)

        st.success("Complaint marked as resolved!")
