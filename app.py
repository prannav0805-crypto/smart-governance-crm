import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime
import random

# -------------------------
# PAGE CONFIG
# -------------------------

st.set_page_config(
    page_title="CivicAI Smart Governance",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ CivicAI — AI Powered Smart Governance System")

# -------------------------
# DATABASE
# -------------------------

conn = sqlite3.connect("complaints.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    complaint TEXT,
    category TEXT,
    priority TEXT,
    status TEXT,
    date TEXT
)
""")

conn.commit()

# -------------------------
# SAMPLE DATA (FOR JUDGES)
# -------------------------

def insert_sample_data():

    sample = [

        ("Rahul Sharma", "Garbage not collected for 5 days", "Sanitation", "High", "Pending"),
        ("Priya Verma", "Street light not working", "Electricity", "Medium", "Pending"),
        ("Amit Singh", "Huge pothole causing accidents", "Infrastructure", "High", "Pending"),
        ("Neha Gupta", "Water leakage from main pipe", "Water", "Medium", "Resolved"),
        ("Arjun Patel", "Road completely broken", "Infrastructure", "High", "Pending"),
        ("Sneha Kapoor", "Overflowing garbage bin", "Sanitation", "High", "Pending"),
        ("Vikas Yadav", "No electricity since morning", "Electricity", "High", "Resolved"),
        ("Anjali Mehta", "Water supply very dirty", "Water", "Medium", "Pending"),
    ]

    for row in sample:

        c.execute("""
        INSERT INTO complaints
        (name, complaint, category, priority, status, date)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))

    conn.commit()

# Insert sample only if empty
count = c.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]

if count == 0:
    insert_sample_data()

# -------------------------
# AI CATEGORY DETECTION
# -------------------------

def detect_category(text):

    text = text.lower()

    if "road" in text or "pothole" in text:
        return "Infrastructure"

    elif "garbage" in text or "waste":
        return "Sanitation"

    elif "water" in text:
        return "Water"

    elif "electric" in text or "light":
        return "Electricity"

    else:
        return "General"


# -------------------------
# AI PRIORITY
# -------------------------

def detect_priority(text):

    text = text.lower()

    if "accident" in text or "emergency" in text:
        return "High"

    elif "not working" in text or "broken":
        return "Medium"

    else:
        return "Low"


# -------------------------
# SIDEBAR NAVIGATION
# -------------------------

page = st.sidebar.radio(
    "Navigation",
    ["Citizen Portal", "Admin Dashboard", "Analytics", "AI Insights"]
)

# -------------------------
# LOAD DATA
# -------------------------

df = pd.read_sql("SELECT * FROM complaints", conn)

# -------------------------
# CITIZEN PORTAL
# -------------------------

if page == "Citizen Portal":

    st.header("Submit Complaint")

    name = st.text_input("Your Name")

    complaint = st.text_area("Enter complaint")

    if st.button("Submit"):

        if complaint:

            category = detect_category(complaint)
            priority = detect_priority(complaint)

            c.execute("""
            INSERT INTO complaints
            (name, complaint, category, priority, status, date)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name,
                complaint,
                category,
                priority,
                "Pending",
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ))

            conn.commit()

            st.success("Complaint submitted successfully")

            st.info(f"AI Category: {category}")
            st.info(f"AI Priority: {priority}")

# -------------------------
# ADMIN DASHBOARD
# -------------------------

elif page == "Admin Dashboard":

    st.header("Admin Dashboard")

    st.metric("Total Complaints", len(df))

    pending = len(df[df.status == "Pending"])
    resolved = len(df[df.status == "Resolved"])

    col1, col2 = st.columns(2)

    col1.metric("Pending", pending)
    col2.metric("Resolved", resolved)

    st.dataframe(df, use_container_width=True)

    complaint_id = st.number_input("Enter complaint ID")

    if st.button("Mark Resolved"):

        c.execute("""
        UPDATE complaints
        SET status = 'Resolved'
        WHERE id = ?
        """, (complaint_id,))

        conn.commit()

        st.success("Complaint resolved")


# -------------------------
# ANALYTICS
# -------------------------

elif page == "Analytics":

    st.header("Analytics Dashboard")

    col1, col2 = st.columns(2)

    with col1:

        fig = px.pie(
            df,
            names="category",
            title="Complaint Categories"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        fig2 = px.bar(
            df,
            x="priority",
            color="priority",
            title="Priority Distribution"
        )

        st.plotly_chart(fig2, use_container_width=True)


# -------------------------
# AI INSIGHTS (Hackathon killer feature)
# -------------------------

elif page == "AI Insights":

    st.header("AI Insights")

    most_common = df.category.value_counts().idxmax()

    st.success(f"Most common issue: {most_common}")

    resolution_rate = (len(df[df.status=="Resolved"]) / len(df)) * 100

    st.success(f"Resolution rate: {resolution_rate:.1f}%")

    st.info("AI recommends increasing resources in high complaint areas")
