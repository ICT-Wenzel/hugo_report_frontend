# views/dashboard.py
from collections import Counter

import streamlit as st
from utils.api_client import get_all_bugs


def show():
    st.header("Dashboard")

    try:
        bugs = get_all_bugs()
    except Exception as exc:
        st.error(f"Could not load data: {exc}")
        return

    if not bugs:
        st.info("No bugs recorded yet.")
        return

    total    = len(bugs)
    open_    = sum(1 for b in bugs if b["status"] == "open")
    in_prog  = sum(1 for b in bugs if b["status"] == "in_progress")
    closed   = sum(1 for b in bugs if b["status"] == "closed")
    critical = sum(1 for b in bugs if b["severity"] == "critical")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total",       total)
    c2.metric("Open",        open_)
    c3.metric("In Progress", in_prog)
    c4.metric("Closed",      closed)
    c5.metric("Critical 🔴", critical)

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("By Severity")
        severity_counts = Counter(b["severity"] for b in bugs)
        ordered = ["low", "medium", "high", "critical"]
        st.bar_chart({s: severity_counts.get(s, 0) for s in ordered})

    with col_b:
        st.subheader("By Category")
        st.bar_chart(dict(Counter(b["category"] for b in bugs)))

    st.subheader("By Status")
    st.bar_chart(dict(Counter(b["status"] for b in bugs)))

show()