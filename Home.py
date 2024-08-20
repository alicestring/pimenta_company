import streamlit as st
from PIL import Image

st.set_page_config(page_title = 'Home', page_icon = '🤗', layout = 'wide')

image = Image.open('logo.png')
st.sidebar.image(image, width = 120)

st.sidebar.markdown('Pimenta Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")
st.write('Pimenta Company Growth Dashboard')
