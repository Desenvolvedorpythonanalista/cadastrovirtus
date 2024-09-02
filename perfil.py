import os
import streamlit as st
import sqlite3
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Função para autenticar o usuário via OAuth 2.0
def authenticate_user():
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    # Caminho absoluto para o arquivo client_secret.json
    client_secrets_path = 'C:\\Users\\NIL\\Desktop\\PERFIL\\client_secret.json'
    flow = Flow.from_client_secrets_file(client_secrets_path, scopes=SCOPES, redirect_uri='http://localhost:8501')
    
    st.write("Verificando o estado da autenticação...")

    if 'credentials' not in st.session_state:
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.write(f'[Clique aqui para autenticar]({auth_url})')
        st.write("Por favor, complete a autenticação e cole o código aqui:")
        auth_code = st.text_input("Código de Autenticação")
        
        if auth_code:
            st.write("Código de autenticação recebido. Tentando trocar o código por um token...")
            try:
                flow.fetch_token(code=auth_code)
                credentials = flow.credentials
                st.session_state['credentials'] = credentials_to_dict(credentials)
                st.write("Autenticação bem-sucedida! Recarregando a página...")
                st.experimental_rerun()  # Recarrega a página para mostrar o formulário
            except Exception as e:
                st.write(f"Erro ao trocar o código por um token: {e}")
        return None
    
    credentials = Credentials(**st.session_state['credentials'])
    
    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            st.write("Credenciais expiradas. Tentando atualizar...")
            try:
                credentials.refresh(Request())
                st.session_state['credentials'] = credentials_to_dict(credentials)
                st.write("Credenciais atualizadas com sucesso!")
            except Exception as e:
                st.write(f"Erro ao atualizar as credenciais: {e}")
                return None
        else:
            st.write("Credenciais inválidas. Redirecionando para a autenticação...")
            auth_url, _ = flow.authorization_url(prompt='consent')
            st.write(f'[Clique aqui para autenticar novamente]({auth_url})')
            return None
    
    return credentials

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

# Função para fazer upload de arquivos para o Google Drive
def upload_file_to_drive(service, file, folder_id=None):
    if file is None:
        st.error("Nenhum arquivo selecionado para upload.")
        return None

    file_path = f"temp_{file.name}"
    
    # Escreve o arquivo
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())

    file_metadata = {'name': file.name}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    media = MediaFileUpload(file_path, resumable=True)
    
    try:
        uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = uploaded_file.get('id')
        st.write(f"Arquivo '{file.name}' enviado com sucesso! ID: {file_id}")
    except Exception as e:
        st.error(f"Erro ao fazer upload do arquivo '{file.name}': {e}")
        return None
    finally:
        # Remova a linha abaixo se não quiser remover o arquivo temporário
        # try:
        #     os.remove(file_path)
        # except Exception as e:
        #     st.error(f"Erro ao remover o arquivo temporário '{file_path}': {e}")
        pass
    
    return uploaded_file.get('id')

# Função para criar conexão com o banco de dados
def create_connection():
    conn = sqlite3.connect('client_profiles.db')
    return conn

# Função para criar a tabela no banco de dados
def create_table():
    conn = create_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT, website TEXT, client_type TEXT,
                contact_name TEXT, email TEXT, phone TEXT, address TEXT,
                no_physical_address BOOLEAN, capital TEXT, desired_revenue TEXT,
                services TEXT, payment_methods TEXT, source TEXT, business_field TEXT,
                business_type TEXT, context TEXT, return_time TEXT, market_analysis BOOLEAN,
                difficulties TEXT, cnpj_or_cpf TEXT, logo_path TEXT, pdf_path TEXT,
                video_path TEXT, employees TEXT
            )
        ''')
        conn.commit()

# Função para inserir dados no banco de dados
def insert_data(data, logo_path=None, pdf_path=None, video_path=None):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        columns = [
            'company_name', 'website', 'client_type', 'contact_name', 
            'email', 'phone', 'address', 'no_physical_address', 
            'capital', 'desired_revenue', 'services', 'payment_methods', 
            'source', 'business_field', 'business_type', 'context', 
            'return_time', 'market_analysis', 'difficulties', 
            'cnpj_or_cpf', 'logo_path', 'pdf_path', 'video_path', 'employees'
        ]
        placeholders = ', '.join('?' for _ in columns)
        query = f'INSERT INTO profiles ({", ".join(columns)}) VALUES ({placeholders})'
        values = [data.get(column) for column in columns[:-3]]  # Ajustado para não incluir logo_path, pdf_path e video_path no values
        values.extend([logo_path, pdf_path, video_path])
        cursor.execute(query, values)
        conn.commit()
        st.write("Dados inseridos no banco de dados com sucesso!")
    except Exception as e:
        st.error(f"Erro ao inserir dados no banco de dados: {e}")
    finally:
        conn.close()

# Streamlit app
st.title("Levantamento de Perfil do Cliente")
create_table()

# ID da pasta no Google Drive onde os arquivos serão enviados
FOLDER_ID = '13X_YJqvB3jGdOxCCIrNzt5vi8UwtWNlE'

# Autenticação do usuário via OAuth
credentials = authenticate_user()

if credentials:
    drive_service = build('drive', 'v3', credentials=credentials)

    # Formulário de entrada
    with st.form(key='profile_form'):
        company_name = st.text_input("Nome da Empresa/Cliente")
        website = st.text_input("Website")
        client_type = st.text_input("Tipo de Cliente")
        contact_name = st.text_input("Nome do Contato")
        email = st.text_input("Email")
        phone = st.text_input("Telefone")
        address = st.text_input("Endereço")
        no_physical_address = st.checkbox("Sem endereço físico")
        capital = st.text_input("Capital")
        desired_revenue = st.text_input("Receita Desejada")
        services = st.text_area("Serviços")
        payment_methods = st.text_input("Métodos de Pagamento")
        source = st.text_input("Fonte")
        business_field = st.text_input("Campo de Negócio")
        business_type = st.text_input("Tipo de Negócio")
        context = st.text_area("Contexto")
        return_time = st.text_input("Tempo de Retorno")
        market_analysis = st.checkbox("Análise de Mercado")
        difficulties = st.text_area("Dificuldades")
        cnpj_or_cpf = st.text_input("CNPJ ou CPF")
        employees = st.text_input("Número de Funcionários")
        
        # Botão de envio
        submit_button = st.form_submit_button(label="Enviar")

        if submit_button:
            st.write("Formulário enviado. Iniciando o upload dos arquivos...")

            data = {
                'company_name': company_name,
                'website': website,
                'client_type': client_type,
                'contact_name': contact_name,
                'email': email,
                'phone': phone,
                'address': address,
                'no_physical_address': no_physical_address,
                'capital': capital,
                'desired_revenue': desired_revenue,
                'services': services,
                'payment_methods': payment_methods,
                'source': source,
                'business_field': business_field,
                'business_type': business_type,
                'context': context,
                'return_time': return_time,
                'market_analysis': market_analysis,
                'difficulties': difficulties,
                'cnpj_or_cpf': cnpj_or_cpf,
                'employees': employees
            }

            # Verificar se arquivos foram carregados
            logo_file = st.file_uploader("Carregar Logotipo", type=['jpg', 'jpeg', 'png'])
            pdf_file = st.file_uploader("Carregar PDF", type=['pdf'])
            video_file = st.file_uploader("Carregar Vídeo", type=['mp4', 'mpeg4'])

            logo_id = None
            pdf_id = None
            video_id = None
            
            if logo_file:
                st.write(f"Logotipo carregado: {logo_file.name}")
                logo_id = upload_file_to_drive(drive_service, logo_file, folder_id=FOLDER_ID)
            
            if pdf_file:
                st.write(f"PDF carregado: {pdf_file.name}")
                pdf_id = upload_file_to_drive(drive_service, pdf_file, folder_id=FOLDER_ID)
            
            if video_file:
                st.write(f"Vídeo carregado: {video_file.name}")
                video_id = upload_file_to_drive(drive_service, video_file, folder_id=FOLDER_ID)
            
            insert_data(data, logo_path=logo_id, pdf_path=pdf_id, video_path=video_id)
