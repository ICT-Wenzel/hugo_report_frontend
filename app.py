import streamlit as st
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
img = Image.open(BASE_DIR / "assets" / "tph.png")
icon = Image.open(BASE_DIR / "assets" / "paw_icon.png")
st.logo(img, size="large")

st.set_page_config(page_title="Hugo Automation Service Report", layout="wide", page_icon=icon)


create_bug_page = st.Page("./views/create_bug.py", title="Create Bug")
list_bug_page = st.Page("./views/bug_list.py", title="List Bugs")
dashboard_home = st.Page("./views/dashboard.py", title="Dashboard")
bug_detail_page = st.Page("./views/bug_detail.py", title="Bug Detail")


pg = st.navigation(
    {
        "Menu": [dashboard_home, create_bug_page, list_bug_page, bug_detail_page]
    }
)

pg.run()