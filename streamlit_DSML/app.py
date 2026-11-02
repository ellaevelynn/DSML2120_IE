import streamlit as st

st.set_page_config(
    page_title="My Streamlit Site",
    page_icon="📊",
    layout="wide"
)

st.title(" Welcome to My Streamlit Site")
st.markdown(
    """
    This is a two-page Streamlit app:
    - **Bio**: who I am
    - **Visualization**: a tiny interactive chart

    Use the left sidebar to switch pages.
    """
)

with st.expander("How this app is organized (for students)"):
    st.write(
        """
        - `app.py` is the entry point.
        - Pages live in the `/pages` folder and auto-appear in the sidebar.
        - Edit `pages/1_Bio.py` and `pages/2_Visualization.py` to complete the assignment.
        """
    )

st.caption("Built with Streamlit • Class template")
# Requirement 5: Link to the sales dashboard page
st.page_link("pages/1_Sales_Dashboard.py", label="See my dashboard", icon="☕")

