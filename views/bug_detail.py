# views/bug_detail.py
import streamlit as st
from utils.api_client import (
    get_bug_by_id,
    get_comments_for_bug,
    update_bug_status,
    close_bug_with_resolution,
    add_comment,
)
from utils.config import get_config



def _format_dt(iso: str | None) -> str:
    if not iso:
        return "—"
    return iso[:19].replace("T", " ")


def show():
    bug_id = st.session_state.get("selected_bug_id")

    if not bug_id:
        st.warning("No bug selected. Go to the Bug List and open one.")
        return

    if st.button("← Back to list"):
        st.session_state["page"] = "bug_list"
        st.switch_page("./views/bug_list.py")
        st.rerun()

    try:
        bug = get_bug_by_id(bug_id)
    except Exception as exc:
        st.error(f"Failed to load bug: {exc}")
        return

    if not bug:
        st.error("Bug not found.")
        return

    # --- Header ---
    st.header(f"{bug['title']}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Status",   bug["status"])
    col2.metric("Severity", bug["severity"])
    col3.metric("Type",     bug["type"])
    col4.metric("Category", bug["category"])

    st.divider()

    # --- Description ---
    st.subheader("Description")
    st.write(bug["description"])

    with st.expander("Timestamps"):
        st.write(f"Created:  {_format_dt(bug.get('created_at'))}")
        st.write(f"Updated:  {_format_dt(bug.get('updated_at'))}")
        st.write(f"Closed:   {_format_dt(bug.get('closed_at'))}")

    if bug.get("resolution"):
        st.subheader("Resolution")
        st.info(bug["resolution"])

    st.divider()

    # --- Attachments ---
    import os
    from dotenv import load_dotenv

    load_dotenv()
    urls = bug.get("attachment_urls") or []
    if urls:
        st.subheader(f"Attachments ({len(urls)})")

        # interne Docker URL → Browser-zugängliche URL ersetzen
        public_url = get_config("PUBLIC_SUPABASE_URL").rstrip("/")
        internal_url = get_config("SUPABASE_URL").rstrip("/")

        cols = st.columns(min(len(urls), 3))
        for i, url in enumerate(urls):
            display_url = url.replace(internal_url, public_url) if public_url else url
            with cols[i % 3]:
                st.image(display_url, use_container_width=True)

        st.divider()

    # --- Actions ---
    if bug["status"] != "closed":
        st.subheader("Actions")
        col_a, col_b = st.columns(2)

        with col_a:
            if bug["status"] == "open":
                if st.button("▶ Mark as In Progress", use_container_width=True):
                    try:
                        update_bug_status(bug_id, "in_progress")
                        st.success("Status updated to In Progress.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

        with col_b:
            with st.expander("Close Bug"):
                resolution = st.text_area("Resolution notes", key="resolution_input")
                if st.button("Confirm Close", use_container_width=True):
                    if not resolution.strip():
                        st.error("Resolution is required to close a bug.")
                    else:
                        try:
                            close_bug_with_resolution(bug_id, resolution.strip())
                            st.success("Bug closed.")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))

        st.divider()

    # --- Comments ---
    st.subheader("Comments")

    try:
        comments = get_comments_for_bug(bug_id)
    except Exception as exc:
        st.error(f"Could not load comments: {exc}")
        comments = []

    if comments:
        for c in comments:
            with st.container(border=True):
                st.caption(_format_dt(c.get("created_at")))
                st.write(c["comment"])
    else:
        st.caption("No comments yet.")

    with st.form("add_comment_form", clear_on_submit=True):
        new_comment = st.text_area("Add a comment", height=80)
        if st.form_submit_button("Post Comment", use_container_width=True):
            if not new_comment.strip():
                st.error("Comment cannot be empty.")
            else:
                try:
                    add_comment(bug_id, new_comment.strip())
                    st.success("Comment added.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

show()