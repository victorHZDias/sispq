import streamlit as st
import psycopg2
import bcrypt  # Para hash de senhas
from psycopg2 import OperationalError
from dotenv import load_dotenv
import os
import datetime as dt
import json

load_dotenv()

# Conexão com o PostgreSQL
def conectar_db():
    try:
        conn = psycopg2.connect(
            database="db_pq_postgres",
            user="postgres",
            password=os.getenv('POSTGRES_PASSWORD'),
            host="77.37.40.212",  # Ou o endereço do seu servidor
            port='5432'  # Porta padrão do PostgreSQL
        )
        print("Conectado ao banco de dados PostgreSQL!")
        return conn
    except OperationalError as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        
def autenticar(login, senha):
    with conectar_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT senha, classe_usuario FROM acessos WHERE login = %s", (login,))
            resultado = cur.fetchone()
            if resultado:
                senha_hash, classe_usuario = resultado
                senha_hash = senha_hash.encode('utf-8')  # Converter senha_hash para bytes
                if bcrypt.checkpw(senha.encode(), senha_hash):
                    st.session_state.classe_usuario = classe_usuario
                    dataHora=dt.datetime.now()
                    # Atualizar último acesso
                    cur.execute("UPDATE acessos SET ultimo_acesso = %s WHERE login = %s", (dataHora, login))
                    conn.commit()  # Confirmar a atualização

                    return True
    return False

def cadastrar_colaborador(nome, endereco, telefone, data_nascimento, cargo, data_contratacao, data_saida=None):
    """Insere um novo colaborador no banco de dados."""

    with conectar_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO funcionarios (nome, endereco, telefone, data_nascimento, cargo, data_contratacao, data_saida)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (nome, endereco, telefone, data_nascimento, cargo, data_contratacao, data_saida)
            )
            conn.commit()
            print("Colaborador cadastrado com sucesso!")

def criar_usuario(login, senha, classe_usuario):
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
    with conectar_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO acessos (login, senha, classe_usuario) VALUES (%s, %s, %s)",
                (login, senha_hash.decode('utf-8'), classe_usuario),  # Armazenar o hash como string
            )
            
def ler_usuarios():
    """Lê todos os usuários do banco de dados."""

    with conectar_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, login, classe_usuario, ultimo_acesso FROM acessos")  # Não seleciona a senha!
            usuarios = cur.fetchall()
    return usuarios

def atualizar_usuario(id, novo_login, nova_senha, nova_classe):
    with conectar_db() as conn:
        with conn.cursor() as cur:
            query = "UPDATE acessos SET login = %s, classe_usuario = %s"
            params = [novo_login, nova_classe]

            if nova_senha:
                nova_senha_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()
                query += ", senha = %s"
                params.append(nova_senha_hash)

            query += " WHERE id = %s"
            params.append(id)

            cur.execute(query, params)
            conn.commit()
            
def deletar_usuario(id):
    """Deleta um usuário do banco de dados."""
    with conectar_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM acessos WHERE id = %s", (id,))

def inserir_venda(telefone, responsavel, criancas):
    with conectar_db() as conn:
        with conn.cursor() as cur:
        # Verifica se o cliente já existe
            cur.execute("SELECT telefone FROM clientes WHERE telefone = %s", (telefone,))
            cliente_existe = cur.fetchone()

            # Se o cliente não existe, insere na tabela clientes
            if not cliente_existe:
                cur.execute(
                    "INSERT INTO clientes (telefone, responsavel, crianca) VALUES (%s, %s, %s)",
                    (telefone, responsavel, criancas),
                )

            criancas = json.loads(criancas)

 
            # Calcular o valor total da venda
            valor_total = sum(
                float(crianca.get("valor", 0))  # Extrai o valor e trata como float
                for crianca in criancas
            )

            # Converter a lista de dicionários de volta para JSON
            criancas_json = json.dumps(criancas)

            # Inserir a venda na tabela vendas (com o valor total e criancas em JSON)
            cur.execute(
                "INSERT INTO vendas (telefone, data_venda, crianca, responsavel, valor) VALUES (%s, %s, %s, %s, %s)",
                (telefone, dt.datetime.now().strftime(r"%Y-%m-%d %H:%M:%S"), criancas_json, responsavel, valor_total),
            )
            cur.execute(
                "UPDATE clientes SET crianca = %s WHERE telefone = %s",
                (criancas_json, telefone),
            )
        conn.commit()
    
def buscar_cliente(telefone):
    with conectar_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT telefone, responsavel, crianca FROM clientes WHERE telefone = %s", (telefone,))  # Seleciona telefone em vez de id
            cliente = cur.fetchone()
            return cliente
    
def buscar_passaporte(tipo):
    with conectar_db() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {tipo} FROM passaportes")
            passaporte = cur.fetchone()
            if passaporte:  # Verifica se a consulta retornou um resultado
                return passaporte[0]
            else:
                # Retorna um valor padrão (0, por exemplo) ou lança uma exceção
                return 0 
        
# Consulta para obter as vendas do dia atual

def buscar_vendas_hoje():
    with conectar_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM vendas")
            vendas = cur.fetchall()

            vendas_lista = []
            nomes_tipos_criancas = []
            passaportes_criancas = []
            tipos_criancas = []
            
            for venda in vendas:
                criancas_data = []
                passaporte_data = []  # Lista para passaportes
                tipos_cri= []
                for crianca in venda[3]:
                    criancas_data.append(crianca['nome'])
                    passaporte_data.append(crianca['passaporte'])
                    tipos_cri.append(crianca['tipo'])
                    
                vendas_lista.append(venda[:3] + (venda[4],)+ (venda[5],)) # Copia os 3 primeiros elementos da tupla
                
                nomes_tipos_criancas.append(", ".join(criancas_data))
                passaportes_criancas.append(", ".join(passaporte_data))  # Adiciona os passaportes à lista separada
                tipos_criancas.append(", ".join(tipos_cri))  # Adiciona os tipos à lista separada

            return vendas_lista, nomes_tipos_criancas, passaportes_criancas,tipos_criancas
        
def deletar_venda(id_venda):
    with conectar_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM vendas WHERE id = %s", (int(id_venda),))  # Converter para int
            conn.commit()
            if cur.rowcount > 0:
                return st.success(f"Item {id_venda} Deletado")  # Deletado com sucesso
            else:
                return st.error('This is an error', icon="🚨") # ID não encontrado

def atualizar_venda(selected_row,valorPass):
    with conectar_db() as conn:
        with conn.cursor() as cur:

            # Extrai os dados da linha selecionada
            id_venda = int(selected_row[0])
            telefone = selected_row[1]
            responsavel = selected_row[3]
            valor_total = int(valorPass)
            criancas = selected_row[5]
            passaportes = selected_row[6]
            tipo = selected_row[7]

            # Converte a lista de tipos para string
            tipo = tipo[0] if isinstance(tipo, list) else tipo

            # Cria a lista de dicionários para o JSON
            criancas_json = json.dumps([
                {
                    "nome": criancas,
                    "tipo": tipo,
                    "valor": valor_total,
                    "passaporte": passaportes,
                }
            ])

            # Atualiza a venda na tabela vendas
            cur.execute(
                """
                UPDATE vendas 
                SET telefone = %s, responsavel = %s, crianca = %s, valor = %s
                WHERE id = %s
                """,
                (telefone, responsavel, criancas_json, valor_total, id_venda),
            )
            cur.execute(
                "UPDATE clientes SET crianca = %s WHERE telefone = %s",
                (criancas_json, telefone),
            )

            conn.commit()
