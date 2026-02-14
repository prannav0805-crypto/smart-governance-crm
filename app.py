import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime, timedelta
import os
import random
from PIL import Image

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


# -------------------------
# CONFIG
# -------------------------

st.set_page_config(
    page_title="CivicAI Smart Governance",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ CivicAI — AI Smart Governance System (WINNER++)")


DB_FILE = "complaints.db"
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


# -------------------------
# DATABASE
# -------------------------

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    complaint TEXT,
    category TEXT,
    priority TEXT,
    status TEXT,
    date TEXT,
    lat REAL,
    lon REAL,
    image_path TEXT
)
""")

conn.commit()


# -------------------------
# SAMPLE DATA
# -------------------------

def insert_sample_data():

    sample = [

        ("Rahul Sharma", "Garbage not collected for 5 days", "Sanitation", "High", "Pending", 19.07, 72.87, None),
        ("Priya Verma", "Street light not working", "Electricity", "Medium", "Pending", 19.08, 72.88, None),
        ("Amit Singh", "Huge pothole causing accidents", "Infrastructure", "High", "Pending", 19.06, 72.86, None),
        ("Neha Gupta", "Water leakage from main pipe", "Water", "Medium", "Resolved", 19.05, 72.89, None),

    ]

    for row in sample:

        c.execute("""
        INSERT INTO complaints
        (name, complaint, category, priority, status, date, lat, lon, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            row[5],
            row[6],
            row[7]
        ))

    conn.commit()


if c.execute("SELECT COUNT(*) FROM complaints").fetchone()[0] == 0:
    insert_sample_data()


# -------------------------
# AI CATEGORY
# -------------------------

def detect_category(text):

    text = text.lower()

    if "road" in text or "pothole" in text:
        return "Infrastructure"

    if "garbage" in text:
        return "Sanitation"

    if "water" in text:
        return "Water"

    if "electric" in text or "light" in text:
        return "Electricity"

    return "General"


# -------------------------
# ML PRIORITY MODEL
# -------------------------

def train_model():

    df = pd.read_sql("SELECT complaint, priority FROM complaints", conn)

    if len(df) < 2:
        return None, None

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df["complaint"])
    y = df["priority"]

    model = LogisticRegression()
    model.fit(X, y)

    return vectorizer, model


vectorizer, model = train_model()


def predict_priority(text):

    if model is None:
        return "Medium"

    X = vectorizer.transform([text])
    return model.predict(X)[0]


# -------------------------
# SLA SYSTEM
# -------------------------

SLA_HOURS = {

    "High": 24,
    "Medium": 48,
    "Low": 72

}


def get_sla_status(row):

    created = datetime.strptime(row["date"], "%Y-%m-%d %H:%M")

    deadline = created + timedelta(hours=SLA_HOURS.get(row["priority"], 48))

    remaining = deadline - datetime.now()

    if row["status"] == "Resolved":
        return "Resolved", "green"

    if remaining.total_seconds() < 0:
        return "BREACHED", "red"

    hours_left = int(remaining.total_seconds() / 3600)

    return f"{hours_left}h left", "orange"


# -------------------------
# NAVIGATION
# -------------------------

page = st.sidebar.radio(

    "Navigation",

    [
        "Citizen Portal",
        "Admin Dashboard",
        "Analytics",
        "AI Insights",
        "Chatbot Assistant"
    ]

)


df = pd.read_sql("SELECT * FROM complaints ORDER BY date DESC", conn)


# -------------------------
# CITIZEN PORTAL
# -------------------------

if page == "Citizen Portal":

    st.header("Submit Complaint")

    name = st.text_input("Name")

    complaint = st.text_area("Complaint")

    lat = st.number_input("Latitude", value=0.0)
    lon = st.number_input("Longitude", value=0.0)

    image = st.file_uploader("Upload Image", type=["jpg", "png"])


    if st.button("Submit"):

        category = detect_category(complaint)

        priority = predict_priority(complaint)

        image_path = None

        if image:
            path = f"{UPLOAD_DIR}/{image.name}"
            with open(path, "wb") as f:
                f.write(image.read())
            image_path = path


        c.execute("""
        INSERT INTO complaints
        (name, complaint, category, priority, status, date, lat, lon, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            complaint,
            category,
            priority,
            "Pending",
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            lat,
            lon,
            image_path
        ))

        conn.commit()

        st.success("Complaint submitted")


# -------------------------
# ADMIN DASHBOARD
# -------------------------

elif page == "Admin Dashboard":

    st.header("Admin Dashboard")

    st.metric("Total", len(df))

    for _, row in df.iterrows():

        sla, color = get_sla_status(row)

        st.markdown(f"""
        **ID {row['id']}**
        Complaint: {row['complaint']}
        Priority: {row['priority']}
        SLA: :{color}[{sla}]
        Status: {row['status']}
        """)

        if row["image_path"]:
            st.image(row["image_path"], width=200)

        if st.button(f"Resolve {row['id']}"):
            c.execute("UPDATE complaints SET status='Resolved' WHERE id=?", (row["id"],))
            conn.commit()
            st.rerun()


# -------------------------
# ANALYTICS
# -------------------------

elif page == "Analytics":

    st.header("Analytics")

    fig = px.pie(df, names="category")
    st.plotly_chart(fig)

    sla_status = [get_sla_status(row)[0] for _, row in df.iterrows()]

    sla_df = pd.DataFrame({"SLA": sla_status})

    fig2 = px.histogram(sla_df, x="SLA")

    st.plotly_chart(fig2)


# -------------------------
# AI INSIGHTS
# -------------------------

elif page == "AI Insights":

    st.header("AI Insights")

    st.write("Most common issue:", df["category"].value_counts().idxmax())

    breach = sum(1 for _, r in df.iterrows() if get_sla_status(r)[0]=="BREACHED")

    st.write("SLA breaches:", breach)


# -------------------------
# CHATBOT
# -------------------------

elif page == "Chatbot Assistant":

    st.header("AI Assistant")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    user = st.text_input("Ask")

    if st.button("Send"):

        if "status" in user.lower():

            response = f"{len(df[df.status=='Pending'])} pending complaints"

        elif "sla" in user.lower():

            response = "Monitoring SLA actively"

        else:

            response = "I assist with governance analytics"

        st.session_state.chat.append(("You", user))
        st.session_state.chat.append(("AI", response))


    for speaker, msg in st.session_state.chat:

        st.write(f"{speaker}: {msg}")
