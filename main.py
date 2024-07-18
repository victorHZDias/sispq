import streamlit as st
import pandas as pd
from utils import inserir_venda, buscar_cliente,buscar_vendas_hoje,buscar_passaporte
import json
import time
import datetime as dt

st.set_page_config(
    page_title="Parque Havan",
    layout="wide",
    initial_sidebar_state="expanded"
)

def limpar_campos():
    st.session_state['telefone'] = ""
    st.session_state['responsavel'] = ""
    st.session_state['num_criancas'] = 1
    st.session_state['criancas'] = []

# Inicializa o Session State para os campos do formulário
if 'telefone' not in st.session_state:
    st.session_state['telefone'] = ""
if 'responsavel' not in st.session_state:
    st.session_state['responsavel'] = ""
if 'num_criancas' not in st.session_state:
    st.session_state['num_criancas'] = 1
if 'criancas' not in st.session_state:
    st.session_state['criancas'] = []
    
with st.sidebar:
    st.image("./static/logoParque-transformed.png",width=200)
    inputbot=st.text_input("Pesquisa Passaporte")
    # buscar=st.button("Buscar", type="primary")
    
    today = dt.datetime.now()
    next_year = today.year + 1
    jan_1 = dt.date(today.year, 1, 1)
    dec_31 = dt.date(next_year, 12, 31)
    dia_atual=dt.date(today.year, today.month, today.day)
    
    d = st.date_input(
        "Selecione o Período para Filtrar",
        (dia_atual, dia_atual),
        jan_1,
        dec_31,
        format="DD.MM.YYYY",
    )
    options = st.multiselect(
    "Selecione o Tipo",
    ["REGULAR", "AUTISTA", "ANIVERSARIO", "LOJA"],
    ["ANIVERSARIO"])
    filtrar=st.button("Filtrar", type="primary")
    
# Exibe o DataFrame com as vendas do dia

def tabela_vendas(options):
    vendas_hoje, nomes_tipos, passaportes,tipo = buscar_vendas_hoje()  # Desempacota as listas
    if vendas_hoje:
        # Adiciona as colunas "Crianças" e "Passaportes" ao DataFrame
        df_vendas = pd.DataFrame(vendas_hoje, columns=["ID","Telefone", "Data/Hora","Responsavel","Valor Total"])
        df_vendas["Crianças"] = nomes_tipos
        df_vendas["Passaportes"] = passaportes  
        df_vendas["Tipo"] = tipo
        df_vendas['Responsavel'] = df_vendas['Responsavel'].astype(str)
        
        # df_vendas['valor'] = df_vendas['Responsavel'].astype(str)
        try:  
            df_vendas=df_vendas[(df_vendas["Data/Hora"].dt.date>=d[0]) & (df_vendas["Data/Hora"].dt.date<=d[1])]
            df_vendas['Data/Hora'] = df_vendas['Data/Hora'].dt.strftime('%d/%m/%Y - %H:%M:%S')
        except:
            pass    
        if inputbot:
            return df_vendas.query("Passaportes.str.contains(@inputbot)")
        elif filtrar:
            regex_pattern = '|'.join(options)  # Cria um padrão regex que combina todas as opções selecionadas
            return df_vendas[df_vendas["Tipo"].str.contains(regex_pattern)]
        else:
            return df_vendas
    else:   
        return st.write("Nenhuma venda registrada hoje.")

tab1, tab2 = st.tabs([":family: Cadastro", ":memo: Lista"])

with tab1:
    col1,col2,col3=st.columns([2,5,2])

    with col2:
        st.markdown(
            """
            <h1 style='text-align: center;'>
                <span class="material-icons" style="font-size: 50px;">person_add</span> 
                Cadastro de Clientes
            </h1>
            """,
            unsafe_allow_html=True,
        )        
        st.markdown(
            '<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">',
            unsafe_allow_html=True,
        )
        # Adiciona um botão para limpar o formulário
        if st.button("Limpar Formulário"):
            limpar_campos()
        with st.container(border=True):
            # Busca os dados do cliente ao digitar o telefone
            placeholder_telefone = st.empty()  # Placeholder para o campo de telefone
            # telefone = placeholder_telefone.text_input("Telefone do Cliente")
            telefone = placeholder_telefone.text_input("Telefone do Cliente", key="telefone", 
                                    value=st.session_state['telefone'],
                                    help="Digite o telefone com DDD",
                                    placeholder="(XX) XXXXX-XXXX")

            if telefone:  # Acessa a variável 'telefone' diretamente
                cliente = buscar_cliente(telefone)
                if cliente:
                    responsavel = cliente[1]
                    criancas_existentes = cliente[2] if cliente[2] else []
                    num_criancas = len(criancas_existentes)
                else:
                    responsavel = ""
                    criancas_existentes = []
                    num_criancas = 1
            else:
                responsavel = ""
                criancas_existentes = []
                num_criancas = 1
                
            # Input para quantidade de crianças (valor inicial 1)
            num_criancas = st.number_input("Número de Crianças", min_value=1, step=1, value=num_criancas)

            with st.form("venda_form",border=False):

                # Preenche o campo de responsável
                responsavel = st.text_input("Nome do Responsável", value=responsavel)

                if criancas_existentes:
                    num_criancas = len(criancas_existentes)
                    # st.number_input("Número de Crianças", min_value=1, step=1, value=num_criancas, key="num_criancas")
                    
                # Campos para dados das crianças
                criancas = []
                for i in range(num_criancas):
                    with st.expander(f"Criança {i+1}"):
                        nome_value = criancas_existentes[i].get("nome", "") if i < len(criancas_existentes) else ""
                        data_nascimento_value = pd.to_datetime(criancas_existentes[i].get("data_nascimento", "2000-01-01")) if i < len(criancas_existentes) else pd.to_datetime("2000-01-01")
                        passaporte_value = criancas_existentes[i].get("passaporte", "") if i < len(criancas_existentes) else ""
                        tipo_value = criancas_existentes[i].get("tipo", "REGULAR") if i < len(criancas_existentes) else "REGULAR"

                        nome = st.text_input("Nome da Criança", value=nome_value, key=f"nome_{i}")  # Chave única para cada nome
                        data_nascimento = st.date_input("Data de Nascimento",format="DD/MM/YYYY", value=data_nascimento_value, key=f"data_nascimento_{i}")  # Chave única para cada data
                        passaporte = st.text_input("Número do Passaporte", value=passaporte_value, key=f"passaporte_{i}")  # Chave única para cada passaporte
                        tipo = st.selectbox("Selecione o Tipo", ["REGULAR", "AUTISTA", "ANIVERSARIO", "LOJA"], index=["REGULAR", "AUTISTA", "ANIVERSARIO", "LOJA"].index(tipo_value), key=f"tipo_{i}")  # Chave única para cada tipo

                        criancas.append({
                            "nome": nome,
                            "data_nascimento": data_nascimento.strftime("%Y-%m-%d"),
                            "passaporte": passaporte,
                            "tipo": tipo,
                            "valor":buscar_passaporte(tipo.lower())
                            })
                        
                        
                # Botão de submit dentro do formulário
                if st.form_submit_button("Cadastrar"):  # Movido para dentro do formulário
                    try:
                        criancas_input = json.dumps(criancas)
                        
                        inserir_venda(telefone, responsavel, criancas_input)
                        st.success("Venda registrada com sucesso!")
                        # Limpa o formulário após o registro
                        placeholder_telefone.empty()
        
                        # Limpa o placeholder para recriar o widget na próxima execução

            
                    except json.JSONDecodeError:
                        st.error("Dados das crianças inválidos. Certifique-se de que o JSON está correto.")
  
            
with tab2:
    col1,col2,col3=st.columns([1,7,1])
    
    with col2:
        tabela =tabela_vendas(options)
        df=tabela
        df['Tipo'] = tabela['Tipo'].astype(str).str.split(',')

        # Explodir as listas
        df_exploded = df.explode('Tipo')

        # Contar valores
        contagem = len(df_exploded['Tipo'])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Passaportes", f"{contagem}")
        col2.metric("Valor Total", f"R${tabela['Valor Total'].sum():,.2f}")
       
                
        st.markdown(
            """
            <h1 style='text-align: center;'>
                <span class="material-symbols-outlined">
                list_alt
                </span>
                Lista de Clientes
            </h1>
            """,
            unsafe_allow_html=True,
        )        
        st.markdown(
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />',
            unsafe_allow_html=True,
        )
        st.dataframe(tabela,hide_index=True,width=1300,height=500)
        
 