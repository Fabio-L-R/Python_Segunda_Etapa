import streamlit as st
import pandas as pd

st.write("Olá mundo")

nome = "Fábio"
idade = 17

st.write(nome, idade)

df = pd.DataFrame({
    'first column': ['Português', 'Matemática', 'Python', 'Frame'],
    'second column': [5, 9, 7, 10]
})

st.title('Meu primeiro dash')
st.subheader(nome)

st.dataframe(df)