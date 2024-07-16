import streamlit as st
import pandas as pd
from utils import conectar_db, autenticar, criar_usuario, ler_usuarios, atualizar_usuario, deletar_usuario,cadastrar_colaborador

# Tela de Login
if "logged_in" not in st.session_state:
    st.title("Login")
    login = st.text_input("Login")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar") and autenticar(login, senha):  # Passar o login também
        st.session_state.logged_in = True
        st.experimental_rerun()
    else:
        st.error("Login ou senha incorretos")

# Tela de Administração (após login)
else:
    st.title("Administração de Usuários")

    # Opções do menu lateral
    opcao = st.sidebar.selectbox("Selecione uma ação:", ["Listar Usuários", "Cadastrar Colaborador","Criar Usuário", "Editar Usuário", "Excluir Usuário"])

    if opcao == "Listar Usuários":
        usuarios = ler_usuarios()
        st.subheader("Lista de Usuários")
        if usuarios:
            df_usuarios = pd.DataFrame(usuarios, columns=["ID", "Login", "Classe","Ultimo Acesso"])
            st.dataframe(df_usuarios,hide_index=True)
        else:
            st.write("Nenhum usuário encontrado.")

    elif opcao == "Cadastrar Colaborador":
        st.subheader("Cadastrar Colaborador")
        with st.form("criar_colaborador"):

            nome = st.text_input("Nome")
            endereco = st.text_input("Endereço")
            telefone = st.text_input("Telefone")
            data_nascimento = st.date_input("Data de Nascimento", format="DD/MM/YYYY")
            cargo = st.selectbox("Cargo", ["monitor","folguista","faxineira","gerente"])
            data_contratacao = st.date_input("Data de Contratação", format="DD/MM/YYYY")
            data_saida = st.date_input("Data de Saída", format="DD/MM/YYYY", value=None)  # Adicionado campo Data de Saída (opcional)

            if st.form_submit_button("Criar"):
                cadastrar_colaborador(nome, endereco, telefone, data_nascimento, cargo, data_contratacao, data_saida)
                st.success("Funcionário cadastrado com sucesso!")
                
    elif opcao == "Criar Usuário":
        st.subheader("Criar Novo Usuário")
        with st.form("criar_usuario"):
            login = st.text_input("Login")
            senha = st.text_input("Senha", type="password")
            classe_usuario = st.selectbox("Classe de Usuário", ["gerente", "funcionario"])
            if st.form_submit_button("Criar"):
                criar_usuario(login, senha, classe_usuario)
                st.success("Usuário criado com sucesso!")

    elif opcao == "Editar Usuário":
        st.subheader("Editar Usuário")
        usuarios = ler_usuarios()
        dictUsu={u[0]:u[1] for u in usuarios}
        id_usuario = st.selectbox("Selecione o usuário:", [u[0] for u in usuarios if u[2] != "admin"])
        usuario = next((u for u in usuarios if u[0] == id_usuario), None)
        
        if usuario:
            with st.form("editar_usuario"):
                novo_login = st.text_input("Novo Login", value=usuario[1])
                nova_senha = st.text_input("Nova Senha (opcional)", type="password")
                nova_classe = st.selectbox("Nova Classe de Usuário", ["admin", "gerente", "funcionario"], index=["admin", "gerente", "funcionario"].index(usuario[2]))
                if st.form_submit_button("Atualizar"):
                    atualizar_usuario(id_usuario, novo_login, nova_senha, nova_classe)
                    st.success("Usuário atualizado com sucesso!")

    elif opcao == "Excluir Usuário":
        st.subheader("Excluir Usuário")
        usuarios = ler_usuarios()
        dictUsu={u[0]:u[1] for u in usuarios}
        id_usuario = st.selectbox("Selecione o usuário:", [u[0] for u in usuarios if u[2] != "admin"])
        st.write(f"Você tem certeza que deseja excluir o usuário {dictUsu[id_usuario]}?")

        if st.button("Confirmar Exclusão"):
            deletar_usuario(id_usuario)
            st.success("Usuário excluído com sucesso!")
