import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime
import plotly.express as px
import random

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Smart Governance CRM",
    layout="wide",
    page_icon="🏛️"
)

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "projects" not in st.session_state:
    st.session_state.projects = pd.DataFrame([
        {
            "ID": "P001",
            "Project": "Main Road Repair",
            "Location": "Ward 1",
            "Status": "Active",
            "Completion": 65,
            "Budget": 500000
        },
        {
            "ID": "P002",
            "Project": "Water Pipeline Fix",
            "Location": "Ward 3",
            "Status": "Delayed",
            "Completion": 40,
            "Budget": 300000
        },
        {
            "ID": "P003",
            "Project": "Street Light Installation",
            "Location": "Ward 5",
            "Status": "Completed",
            "Completion": 100,
            "Budget": 200000
        }
    ])

if "grievances" not in st.session_state:
    st.session_state.grievances = pd.DataFrame(columns=[
        "Name", "Category", "Description", "Time", "Priority"
    ])

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
st.sidebar.title("🏛️ Governance Portal")

menu = st.sidebar.radio(
    "Navigate",
    [
        "Leader Dashboard",
        "Field Officer Upload",
        "Citizen Grievances",
        "Analytics"
    ]
)

# -----------------------------
# LEADER DASHBOARD
# -----------------------------
if menu == "Leader Dashboard":

    st.title("🏛️ MLA Governance Dashboard")

    col1, col2, col3 = st.columns(3)

    active_projects = len(st.session_state.projects)
    delayed_projects = len(
        st.session_state.projects[
            st.session_state.projects["Status"] == "Delayed"
        ]
    )

    sentiment = random.randint(60, 95)

    col1.metric("Active Projects", active_projects)
    col2.metric("Delayed Projects", delayed_projects)
    col3.metric("Citizen Sentiment", f"{sentiment}%")

    st.divider()

    st.subheader("📊 Project Status")

    st.dataframe(st.session_state.projects, use_container_width=True)

    fig = px.bar(
        st.session_state.projects,
        x="Project",
        y="Completion",
        color="Status",
        title="Project Completion"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# FIELD OFFICER UPLOAD
# -----------------------------
elif menu == "Field Officer Upload":

    st.title("📸 Field Verification System")

    project = st.selectbox(
        "Select Project",
        st.session_state.projects["Project"]
    )

    file = st.file_uploader("Upload Site Image", type=["jpg", "png"])

    if file:
        image = Image.open(file)

        st.image(image, width=400)

        if st.button("Submit for AI Verification"):

            with st.spinner("AI verifying image and GPS metadata..."):

                import time
                time.sleep(2)

                st.success("Verification Successful!")

                st.info("Payment Released: 20%")

                idx = st.session_state.projects[
                    st.session_state.projects["Project"] == project
                ].index[0]

                st.session_state.projects.at[idx, "Completion"] += 10

# -----------------------------
# CITIZEN GRIEVANCES
# -----------------------------
elif menu == "Citizen Grievances":

    st.title("📝 Citizen Complaint Portal")

    name = st.text_input("Name")

    category = st.selectbox(
        "Category",
        ["Road", "Water", "Electricity", "Sanitation"]
    )

    description = st.text_area("Describe Issue")

    if st.button("Submit Complaint"):

        new = {
            "Name": name,
            "Category": category,
            "Description": description,
            "Time": datetime.now(),
            "Priority": random.choice(["High", "Medium", "Low"])
        }

        st.session_state.grievances = pd.concat(
            [st.session_state.grievances, pd.DataFrame([new])],
            ignore_index=True
        )

        st.success("Complaint Registered Successfully")

    st.divider()

    st.subheader("Recent Complaints")

    st.dataframe(st.session_state.grievances)

# -----------------------------
# ANALYTICS
# -----------------------------
elif menu == "Analytics":

    st.title("📈 Governance Analytics")

    if len(st.session_state.grievances) > 0:

        fig = px.histogram(
            st.session_state.grievances,
            x="Category",
            title="Complaints by Category"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:

        st.info("No complaints yet")

# -----------------------------
# FOOTER
# -----------------------------
st.sidebar.divider()

st.sidebar.write("Smart Governance CRM Prototype")
