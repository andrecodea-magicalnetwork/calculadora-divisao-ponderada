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
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, sep=';', decimal=',')
            else:
                df = pd.read_excel(uploaded_file, engine='openpyxl')

            df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
            
            colunas_obrigatorias = ['vendedor', 'contrato', 'valor']
            if not all(col in df.columns for col in colunas_obrigatorias):
                st.error("A planilha não contém todas as colunas obrigatórias: 'vendedor', 'contrato' e 'valor'.")
            else:
                st.session_state.df_contratos = df.dropna(subset=colunas_obrigatorias)
                st.session_state.df_contratos['valor'] = pd.to_numeric(st.session_state.df_contratos['valor'], errors='coerce')
                
                st.subheader("Planilha Carregada")
                total_contratos = st.session_state.df_contratos.shape[0]
                vendedores_unicos_list = st.session_state.df_contratos['vendedor'].unique().tolist()
                st.session_state.vendedores_unicos = vendedores_unicos_list
                st.markdown(f"**Total de Contratos:** {total_contratos} | **Vendedores Únicos:** {len(vendedores_unicos_list)}")
                st.dataframe(st.session_state.df_contratos)

                if 'rendimentos_fixos' not in st.session_state:
                    st.session_state.rendimentos_fixos = {v: {'salario_fixo': 0.0, 'auxilio': 0.0} for v in vendedores_unicos_list}

        except Exception as e:
            st.error(f"Houve um erro ao ler o arquivo. Por favor, verifique se a planilha está no formato correto. Erro: {e}")
            st.session_state.df_contratos = pd.DataFrame()
            st.session_state.vendedores_unicos = []
            st.session_state.rendimentos_fixos = {}

    if 'df_contratos' in st.session_state and not st.session_state.df_contratos.empty:
        st.header("2. Insira os Rendimentos Fixos por Vendedor")
        
        df_agrupado = st.session_state.df_contratos.groupby('vendedor')['valor'].sum().reset_index()
        
        for index, row in df_agrupado.iterrows():
            vendedor = row['vendedor']
            total_vendas = row['valor']
            
            st.markdown(f"### {vendedor.title()}")
            st.markdown(f"**Total em Vendas:** R$ {total_vendas:,.2f}")
            
            # Aqui está a correção: usando 'value' com o valor do session_state
            salario = st.number_input(
                f"Salário Fixo para {vendedor.title()} (R$)",
                value=st.session_state.rendimentos_fixos[vendedor]['salario_fixo'],
                format="%.2f",
                key=f"{vendedor}_salario",
            )
            
            auxilio = st.number_input(
                f"Auxílio para {vendedor.title()} (R$)",
                value=st.session_state.rendimentos_fixos[vendedor]['auxilio'],
                format="%.2f",
                key=f"{vendedor}_auxilio",
            )

            # Atualiza o session_state com os valores digitados
            st.session_state.rendimentos_fixos[vendedor]['salario_fixo'] = salario
            st.session_state.rendimentos_fixos[vendedor]['auxilio'] = auxilio
            
            total_fixos = salario + auxilio
            total_geral_calculado = total_vendas + total_fixos
            
            st.markdown(f"**Total de Rendimentos Fixos:** R$ {total_fixos:,.2f}")
            st.markdown(f"**Total Geral (Vendas + Fixos):** R$ {total_geral_calculado:,.2f}")
            st.markdown("---")


# --- Exibição dos resultados na segunda aba ---
with tab2:
    if 'df_contratos' in st.session_state and not st.session_state.df_contratos.empty:
        st.header("Análise e Resultados")
        st.markdown("Selecione um vendedor para ver a divisão ponderada dos rendimentos fixos.")

        lista_vendedores = st.session_state.vendedores_unicos
        vendedor_selecionado = st.selectbox("Selecione o Vendedor para Análise", lista_vendedores)
        
        if vendedor_selecionado:
            df_vendedor = st.session_state.df_contratos[st.session_state.df_contratos['vendedor'] == vendedor_selecionado].copy()
            
            rendimentos = st.session_state.rendimentos_fixos.get(vendedor_selecionado, {'salario_fixo': 0.0, 'auxilio': 0.0})
            salario_fixo = rendimentos['salario_fixo']
            auxilio = rendimentos['auxilio']
            total_rendimentos_fixos = salario_fixo + auxilio
            
            if not df_vendedor.empty:
                st.header(f"Resultados para {vendedor_selecionado.title()}")
                st.markdown(f"**Salário Fixo:** R$ {salario_fixo:,.2f} | **Auxílio:** R$ {auxilio:,.2f} | **Total:** R$ {total_rendimentos_fixos:,.2f}")
                
                total_contratos_valor = df_vendedor['valor'].sum()
                
                if total_contratos_valor > 0:
                    df_resultados = df_vendedor.copy()
                    
                    df_resultados['proporcao_contrato'] = df_resultados['valor'] / total_contratos_valor
                    df_resultados['valor_ponderado'] = df_resultados['proporcao_contrato'] * total_rendimentos_fixos
                    
                    st.subheader("Resumo Financeiro")
                    st.markdown(f"**Total dos Contratos:** R$ {total_contratos_valor:,.2f}")
                    st.markdown(f"**Total dos Rendimentos Fixos (a ser dividido):** R$ {total_rendimentos_fixos:,.2f}")
                    st.markdown("---")
                    
                    st.subheader("Divisão Ponderada dos Rendimentos Fixos por Contrato")
                    
                    df_resultados['Valor Ponderado (R$)'] = df_resultados['valor_ponderado'].map("R$ {:,.2f}".format)
                    df_resultados['Proporção do Contrato (%)'] = (df_resultados['proporcao_contrato'] * 100).map("{:.2f}%".format)
                    df_resultados['Valor do Contrato (R$)'] = df_resultados['valor'].map("R$ {:,.2f}".format)
                    df_resultados_final = df_resultados.rename(columns={'contrato': 'Contrato'})[
                        ['Contrato', 'Valor do Contrato (R$)', 'Proporção do Contrato (%)', 'Valor Ponderado (R$)']
                    ]

                    st.dataframe(df_resultados_final, use_container_width=True)

                    soma_ponderada = df_resultados['valor_ponderado'].sum()
                    st.markdown(f"**Verificação:** A soma dos valores ponderados é de **R$ {soma_ponderada:,.2f}**")
                    st.markdown("Esse valor deve ser igual ao total dos rendimentos fixos.")
                    
                    csv_data = df_resultados_final.to_csv(index=False, sep=';', decimal=',').encode('utf-8')
                    st.download_button(
                        label=f"Baixar Planilha de {vendedor_selecionado.title()} (CSV)",
                        data=csv_data,
                        file_name=f'{vendedor_selecionado}_contratos_ponderados.csv',
                        mime='text/csv',
                    )
                else:
                    st.warning(f"O vendedor '{vendedor_selecionado}' não tem valor total de contratos para fazer a ponderação.")
            else:
                st.info(f"O vendedor '{vendedor_selecionado}' não possui contratos válidos na planilha.")
    else:
        st.info("Aguardando o upload de uma planilha com os contratos na aba 'Upload e Dados'.")

