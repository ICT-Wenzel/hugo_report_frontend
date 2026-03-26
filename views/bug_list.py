# views/bug_list.py
import streamlit as st
from utils.api_client import get_all_bugs

SEVERITY_BADGE = {
    "low":      "🟢 low",
    "medium":   "🟡 medium",
    "high":     "🟠 high",
    "critical": "🔴 critical",
}

STATUS_BADGE = {
    "open":        "⬜ open",
    "in_progress": "🔵 in progress",
    "closed":      "✅ closed",
}


def show():
    st.header("📋 Bug List")

    with st.expander("Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            f_severity = st.selectbox("Severity", ["(all)", "low", "medium", "high", "critical"])
        with col2:
            f_status = st.selectbox("Status", ["(all)", "open", "in_progress", "closed"])
        with col3:
            f_category = st.selectbox(
                "Category",
                ["(all)", "client_management", "inventory", "xmc", "toolbox", "engineering"],
            )

    try:
        bugs = get_all_bugs(
            status=None if f_status == "(all)" else f_status,
            severity=None if f_severity == "(all)" else f_severity,
            category=None if f_category == "(all)" else f_category,
        )
    except Exception as exc:
        st.error(f"Could not load bugs: {exc}")
        return

    if not bugs:
        st.info("No bugs match the current filters.")
        return

    st.caption(f"{len(bugs)} result(s)")

    hcols = st.columns([3, 2, 2, 2, 2])
    for col, label in zip(hcols, ["Title", "Severity", "Type", "Category", "Status"]):
        col.markdown(f"**{label}**")
    st.divider()

    for bug in bugs:
        cols = st.columns([3, 2, 2, 2, 2])
        cols[0].write(bug["title"])
        cols[1].write(SEVERITY_BADGE.get(bug["severity"], bug["severity"]))
        cols[2].write(bug["type"])
        cols[3].write(bug["category"])
        cols[4].write(STATUS_BADGE.get(bug["status"], bug["status"]))

        if cols[0].button("Open →", key=f"open_{bug['id']}"):
            st.session_state["selected_bug_id"] = bug["id"]
            st.session_state["page"] = "bug_detail"
            st.switch_page("./views/bug_detail.py")
            st.rerun()


show()