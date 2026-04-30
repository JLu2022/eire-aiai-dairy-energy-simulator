import streamlit as st
from src.utils.ollama_client import query_ollama

st.set_page_config(page_title="EIRE AIAI Dairy Energy Simulator", layout="wide")
st.title("EIRE AIAI Dairy Energy Simulator")
st.markdown("""
Select a page on the left:
- **Farm Energy Estimator**: Farm load estimation  
- **PV Adoption**: Explore PV adoption scenarios
- **PV ROI**: ROI calculation
""")

st.divider()
st.header("Local LLM Assistant")

user_input = st.text_area("Ask about energy management or related topics:")

col1, col2 = st.columns(2)
with col1:
    model = st.selectbox("Select Model", ["llama3.2:3b"])

with col2:
    temp = st.slider("Temperature", 0.0, 1.5, 0.7, 0.1)

if st.button("Generate Answer"):
    with st.spinner("Querying local LLM"):
        result = query_ollama(user_input, model=model, temperature=temp)
    st.markdown("#### Model Answer:")
    st.write(result)
