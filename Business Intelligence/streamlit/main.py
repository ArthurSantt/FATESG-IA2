import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(page_title="Agro BI", layout="wide")

st.title('📊 Painel de Investimentos - Pecuária Goiás')
st.markdown("---")


# O arquivo deve estar na mesma pasta que este script
df_base = pd.read_csv("financiamentoPecuaria.csv", encoding='utf-8-sig', sep=';')

# Limpeza das colunas
if 'Variável' in df_base.columns:
    df_base = df_base.drop(columns=['Variável'])

lista_anos = [col for col in df_base.columns if col != 'Localidade']



for ano in lista_anos:
    texto_limpo = df_base[ano].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip()
    
    texto_limpo = texto_limpo.replace('-', '0')
    
    df_base[ano] = pd.to_numeric(texto_limpo, errors='coerce').fillna(0)

st.sidebar.header("Configurações")
modo = st.sidebar.radio("Modo de Visualização:", ["Estado Completo", "Por Cidade"])

if modo == "Por Cidade":
    selecao = st.sidebar.selectbox("Selecione a Localidade:", df_base["Localidade"].unique())
    df_filtrado = df_base[df_base["Localidade"] == selecao]
    dados_grafico = df_filtrado[lista_anos].iloc[0]
    titulo = f"Resultados de {selecao}"
else:
    df_filtrado = df_base.copy()
    dados_grafico = df_base[lista_anos].mean()
    titulo = "Média Geral do Estado de Goiás"

aba1, aba2 = st.tabs(["📈 Gráficos e Métricas", "📋 Tabela de Dados"])

with aba1:
    st.subheader(titulo)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Média do Período", f"R$ {dados_grafico.mean():,.2f}")
    c2.metric("Maior Valor Registrado", f"R$ {dados_grafico.max():,.2f}")
    c3.metric("Ano de Pico", dados_grafico.idxmax())
    
    st.write("### Evolução Temporal")
    st.area_chart(dados_grafico)

with aba2:
    st.write("### Dados Brutos")
    st.dataframe(df_filtrado, use_container_width=True)

st.divider()
st.caption("Dashboard desenvolvido para a aula de Business Intelligence.")