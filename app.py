import sys
import subprocess
from io import BytesIO

try:
    import streamlit as st
    import pandas as pd
    import openpyxl
except ImportError:
    print("Dependencies not found. Installing now...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 'pandas', 'streamlit', 'openpyxl'
        ])
        print("Dependencies installed successfully. Please restart the script.")
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies. Please install manually.")
    sys.exit()

# --- Configuração da página ---
st.set_page_config(
    page_title="Calculadora de Divisão Ponderada",
    page_icon="⚖️",
    layout="wide"
)

# --- Estilos CSS ---
st.markdown("""
<style>
    /* Estilo para a fonte e cor de fundo */
    .main {
        background-color: #f0f2f6;
    }
    .stApp {
        font-family: 'Segoe UI', 'Arial', sans-serif;
    }
    /* Estilo para os cabeçalhos */
    h1, h2, h3 {
        color: #004d40;
    }
    h1 {
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 10px;
    }
    /* Estilo para os botões */
    .stButton>button {
        background-color: #00796b;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #004d40;
        color: #fff;
    }
    /* Estilo para as caixas de entrada de número */
    .stNumberInput, .stTextInput {
        background-color: #ffffff;
        border-radius: 8px;
    }
    /* Estilo para as caixas de informação e aviso */
    .stAlert {
        border-radius: 8px;
    }
    /* Estilo para a tabela */
    .stDataFrame {
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    /* Estilo para os subtítulos (marcados com **) */
    p strong {
        color: #333;
    }
    
</style>
""", unsafe_allow_html=True)


# Título principal da aplicação
st.title("Calculadora de Divisão Ponderada")
st.write("Faça o upload de uma planilha de contratos. A calculadora irá extrair os nomes dos vendedores e permitir que você insira o salário e auxílio de cada um para realizar a divisão ponderada.")

# --- Estrutura com abas ---
tab1, tab2 = st.tabs(["Upload e Dados", "Resultados e Análise"])

# --- Lógica de processamento e entrada de dados na aba 1 ---
with tab1:
    st.header("1. Upload da Planilha de Contratos")
    st.markdown("A planilha deve conter as colunas: `vendedor`, `contrato` e `valor`.")
    uploaded_file = st.file_uploader("Escolha um arquivo Excel (.xlsx) ou CSV (.csv)", type=["xlsx", "csv"])

    # Inicializa o dataframe na sessão
    if 'df_contratos' not in st.session_state:
        st.session_state.df_contratos = pd.DataFrame()

    if uploaded_file is not None:
        try:
            # Lendo o arquivo
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, sep=';', decimal=',')
            else:
                df = pd.read_excel(uploaded_file, engine='openpyxl')

            # Normaliza os nomes das colunas
            df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
            
            colunas_obrigatorias = ['vendedor', 'contrato', 'valor']
            if not all(col in df.columns for col in colunas_obrigatorias):
                st.error("A planilha não contém todas as colunas obrigatórias: 'vendedor', 'contrato' e 'valor'.")
            else:
                st.session_state.df_contratos = df.dropna(subset=colunas_obrigatorias)
                st.session_state.df_contratos['valor'] = pd.to_numeric(st.session_state.df_contratos['valor'], errors='coerce')
                
                # Exibe a planilha carregada
                st.subheader("Planilha Carregada")
                total_contratos = st.session_state.df_contratos.shape[0]
                vendedores_unicos = st.session_state.df_contratos['vendedor'].nunique()
                st.markdown(f"**Total de Contratos:** {total_contratos} | **Vendedores Únicos:** {vendedores_unicos}")
                st.dataframe(st.session_state.df_contratos)
                
        except Exception as e:
            st.error(f"Houve um erro ao ler o arquivo. Por favor, verifique se a planilha está no formato correto. Erro: {e}")
            st.session_state.df_contratos = pd.DataFrame()
    
    # Se o DataFrame foi carregado, mostra os campos para inserir os rendimentos fixos
    if not st.session_state.df_contratos.empty:
        st.header("2. Insira os Rendimentos Fixos por Vendedor")
        
        # Obtém a lista de vendedores únicos e calcula o total de contratos de cada um
        df_agrupado = st.session_state.df_contratos.groupby('vendedor')['valor'].sum().reset_index()
        df_agrupado['valor'] = df_agrupado['valor'].map("R$ {:,.2f}".format)
        
        # Inicializa o dicionário de rendimentos fixos na sessão
        if 'rendimentos_fixos' not in st.session_state:
            st.session_state.rendimentos_fixos = {vendedor: {'salario_fixo': 0.0, 'auxilio': 0.0} for vendedor in df_agrupado['vendedor']}
            
        # Cria as caixas de entrada para cada vendedor
        for index, row in df_agrupado.iterrows():
            vendedor = row['vendedor']
            total_contratos = row['valor']
            
            st.markdown(f"### {vendedor.title()}")
            st.markdown(f"**Contratos:** {total_contratos}")
            
            salario = st.number_input(f"Salário Fixo para {vendedor.title()} (R$)", min_value=0.0, value=st.session_state.rendimentos_fixos[vendedor]['salario_fixo'], step=100.0, key=f"{vendedor}_salario")
            auxilio = st.number_input(f"Auxílio para {vendedor.title()} (R$)", min_value=0.0, value=st.session_state.rendimentos_fixos[vendedor]['auxilio'], step=10.0, key=f"{vendedor}_auxilio")
            
            total_fixos = salario + auxilio
            total_geral_calculado = float(total_contratos.replace('R$ ', '').replace('.', '').replace(',', '.')) + total_fixos
            
            st.markdown(f"**Total de Rendimentos Fixos:** R$ {total_fixos:,.2f}")
            st.markdown(f"**Total Geral (Contratos + Fixos):** R$ {total_geral_calculado:,.2f}")
            
            st.session_state.rendimentos_fixos[vendedor]['salario_fixo'] = salario
            st.session_state.rendimentos_fixos[vendedor]['auxilio'] = auxilio
            st.markdown("---")


# --- Exibição dos resultados na segunda aba ---
with tab2:
    if not st.session_state.df_contratos.empty and 'rendimentos_fixos' in st.session_state:
        st.header("Análise e Resultados")
        st.markdown("Selecione um vendedor para ver a divisão ponderada dos rendimentos fixos.")

        # Seletor para escolher o vendedor para a análise
        lista_vendedores = st.session_state.df_contratos['vendedor'].unique().tolist()
        vendedor_selecionado = st.selectbox("Selecione o Vendedor para Análise", lista_vendedores)
        
        # Pega os dados do vendedor selecionado
        df_vendedor = st.session_state.df_contratos[st.session_state.df_contratos['vendedor'] == vendedor_selecionado].copy()
        
        # Pega os rendimentos fixos do vendedor
        salario_fixo = st.session_state.rendimentos_fixos[vendedor_selecionado]['salario_fixo']
        auxilio = st.session_state.rendimentos_fixos[vendedor_selecionado]['auxilio']
        total_rendimentos_fixos = salario_fixo + auxilio
        
        if not df_vendedor.empty:
            st.header(f"Resultados para {vendedor_selecionado.title()}")
            st.markdown(f"**Salário Fixo:** R$ {salario_fixo:,.2f} | **Auxílio:** R$ {auxilio:,.2f} | **Total:** R$ {total_rendimentos_fixos:,.2f}")
            
            total_contratos = df_vendedor['valor'].sum()
            total_geral = total_contratos + total_rendimentos_fixos

            st.subheader("Resumo Financeiro")
            st.markdown(f"**Total dos Contratos:** R$ {total_contratos:,.2f}")
            st.markdown(f"**Total dos Rendimentos Fixos:** R$ {total_rendimentos_fixos:,.2f}")
            st.markdown(f"**Valor Total Geral:** R$ {total_geral:,.2f}")
            st.markdown("---")
            
            st.subheader("Divisão Ponderada")
            
            df_resultados = df_vendedor.copy()
            
            if total_geral > 0:
                df_resultados['proporcao_no_total'] = (df_resultados['valor'] / total_geral)
                df_resultados['valor_ponderado'] = df_resultados['proporcao_no_total'] * total_rendimentos_fixos
            else:
                df_resultados['proporcao_no_total'] = 0
                df_resultados['valor_ponderado'] = 0
            
            # Formata as colunas para melhor visualização
            df_resultados['Valor Ponderado (R$)'] = df_resultados['valor_ponderado'].map("R$ {:,.2f}".format)
            df_resultados['Proporção no Total (%)'] = (df_resultados['proporcao_no_total'] * 100).map("{:.2f}%".format)
            df_resultados['Valor do Contrato (R$)'] = df_resultados['valor'].map("R$ {:,.2f}".format)
            df_resultados = df_resultados.rename(columns={'contrato': 'Contrato'})
            df_resultados = df_resultados.drop(columns=['valor', 'vendedor', 'proporcao_no_total', 'valor_ponderado'])

            st.dataframe(df_resultados, use_container_width=True)

            soma_ponderada = sum(
                [float(v.replace('R$ ', '').replace('.', '').replace(',', '.')) 
                for v in df_resultados['Valor Ponderado (R$)']]
            )
            st.markdown(f"**Verificação:** A soma dos valores ponderados é de **R$ {soma_ponderada:,.2f}**")
            st.markdown("Esse valor deve ser igual ao total dos rendimentos fixos.")

            # Botão de download
            csv_data = df_resultados.to_csv(index=False, sep=';', decimal=',')
            st.download_button(
                label=f"Baixar Planilha de {vendedor_selecionado.title()} (CSV)",
                data=csv_data,
                file_name=f'{vendedor_selecionado}_contratos_ponderados.csv',
                mime='text/csv',
            )
        else:
            st.info(f"O vendedor '{vendedor_selecionado}' não possui contratos válidos na planilha.")

    else:
        st.info("Aguardando o upload de uma planilha com os contratos na aba 'Upload e Dados'.")