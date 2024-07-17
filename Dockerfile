# Usar uma imagem base com Python e Streamlit
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc
    
# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar o arquivo requirements.txt para o container
COPY requirements.txt .

# Instalar as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto do código do aplicativo para o container
COPY . .

# Expor a porta que o Streamlit usa
EXPOSE 8501

# Comando para iniciar o aplicativo quando o container for executado
CMD ["streamlit", "run", "main.py"]