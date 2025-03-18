import streamlit as st

st.set_page_config(
    page_title="AI Assignment 1",
    page_icon="🏠",
    layout="wide"
)

st.title("Artificial Intelligence– A1(IITJ)")
st.markdown("**Prepared by:** Mahantesh Hiremath- G24AIT2178")

st.markdown("""
### Navigation Guide:
1. **📦 Warehouse Logistics Optimization**
   - Simulate a warehouse robot optimizing package delivery
   - Configure warehouse size, packages, and obstacles
   - Visualize paths and performance metrics

2. **🤝 City Meetup Search**
   - Find optimal meeting points between two cities
   - Compare different search algorithms and heuristics
   - Interactive map visualization

Use the sidebar to navigate between sections.
""")
# Adding a footer
footer="""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: white;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Developed with ❤️ by <a style='display: inline; text-align: center;' href="https://bit.ly/atozaboutdata" target="_blank">MAHANTESH HIREMATH</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)