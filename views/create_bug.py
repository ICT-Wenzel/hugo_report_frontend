# views/create_bug.py
import streamlit as st
from utils.api_client import create_bug, upload_images

SEVERITIES = ["low", "medium", "high", "critical"]
TYPES      = ["bug", "feature", "improvement"]
CATEGORIES = ["client_management", "inventory", "xmc", "toolbox", "engineering"]


def show():
    st.header("Report a Bug")

    with st.form("create_bug_form", clear_on_submit=True):
        title = st.text_input("Title", max_chars=200, placeholder="Short, descriptive title")
        description = st.text_area(
            "Description",
            height=150,
            placeholder="Steps to reproduce, expected vs actual behaviour …",
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            severity = st.selectbox("Severity", SEVERITIES, index=1)
        with col2:
            bug_type = st.selectbox("Type", TYPES)
        with col3:
            category = st.selectbox("Category", CATEGORIES)

        uploaded_files = st.file_uploader(
            "Attachments (optional)",
            type=["png", "jpg", "jpeg", "gif", "webp"],
            accept_multiple_files=True,
        )

        submitted = st.form_submit_button("Submit", use_container_width=True)

    if submitted:
        if not title.strip():
            st.error("Title is required.")
            return
        if not description.strip():
            st.error("Description is required.")
            return

        n_images = len(uploaded_files) if uploaded_files else 0
        total_steps = 2 if n_images else 1  # upload step + save step

        progress = st.progress(0, text="Starting…")

        try:
            # Step 1 — Upload images (if any)
            urls = []
            if n_images:
                progress.progress(10, text=f"Uploading {n_images} image(s)…")
                files = [
                    {"name": f.name, "bytes": f.read(), "mime": f.type}
                    for f in uploaded_files
                ]
                urls = upload_images(files)
                progress.progress(60, text="Images uploaded. Saving bug…")
            else:
                progress.progress(50, text="Saving bug…")

            # Step 2 — Save bug with URLs in one INSERT
            create_bug(
                title=title.strip(),
                description=description.strip(),
                severity=severity,
                bug_type=bug_type,
                category=category,
                attachment_urls=urls,
            )

            progress.progress(100, text="Done!")

            if n_images:
                st.success(f"Bug reported with {n_images} image(s) attached!")
            else:
                st.success("Bug reported successfully!")

        except Exception as exc:
            progress.empty()
            st.error(f"Something went wrong: {exc}")

show()