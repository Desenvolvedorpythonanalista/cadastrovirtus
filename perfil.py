import os
import json
import streamlit as st
import sqlite3
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Função para autenticar no Google Drive
def authenticate_google_drive():
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    creds = None
    token_path = os.getenv('GOOGLE_TOKEN_PATH', 'token.json')
    client_secrets_path = os.getenv('GOOGLE_CLIENT_SECRETS_PATH', 'client_secret.json')
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

# Função para fazer o upload do arquivo para o Google Drive
def upload_file_to_drive(service, file, folder_id=None):
    # Salvar o arquivo temporariamente
    file_path = f"temp_{file.name}"
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())

    file_metadata = {'name': file.name}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    
    # Remover o arquivo temporário após o upload
    os.remove(file_path)
    
    return file.get('id')

# Função para carregar variáveis de ambiente
load_dotenv()

# Função para criar conexão com o banco de dados
def create_connection():
    try:
        conn = sqlite3.connect('client_profiles.db')
        return conn
    except sqlite3.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para criar a tabela no banco de dados
def create_table():
    conn = create_connection()
    if conn is not None:
        try:
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
        except sqlite3.Error as e:
            st.error(f"Erro ao criar tabela: {e}")
        finally:
            conn.close()

# Função para inserir dados no banco de dados
def insert_data(data, logo_path=None, pdf_path=None, video_path=None):
    conn = create_connection()
    if conn is not None:
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

            values = [json.dumps(item) if isinstance(item, list) else item for item in data.values()]
            values.extend([logo_path, pdf_path, video_path])
            cursor.execute(query, values)
            conn.commit()
        except sqlite3.Error as e:
            st.error(f"Erro ao inserir dados: {e}")
        finally:
            conn.close()

# Função para limpar o formulário
def clear_form():
    st.session_state['company_name'] = ''
    st.session_state['website'] = ''
    st.session_state['website_no_site'] = False
    st.session_state['client_type'] = []
    st.session_state['contact_name'] = ''
    st.session_state['city'] = ''
    st.session_state['email'] = ''
    st.session_state['phone_dd'] = ''
    st.session_state['phone_number'] = ''
    st.session_state['market_segment'] = []
    st.session_state['address'] = ''
    st.session_state['no_physical_address'] = False
    st.session_state['capital'] = ''
    st.session_state['desired_revenue'] = ''
    st.session_state['services'] = []
    st.session_state['payment_methods'] = []
    st.session_state['source'] = ''
    st.session_state['business_field'] = ''
    st.session_state['business_type'] = ''
    st.session_state['context'] = ''
    st.session_state['return_time'] = ''
    st.session_state['market_analysis'] = False
    st.session_state['difficulties'] = ''
    st.session_state['cnpj_or_cpf'] = ''
    st.session_state['employees'] = ''

# Streamlit app
st.title("Levantamento de Perfil do Cliente")

# Criação da tabela no banco de dados
create_table()

# Adiciona CSS para melhorar o layout do formulário
st.markdown("""
    <style>
        .reportview-container { background: url('assets/bg.png') no-repeat center center fixed; background-size: cover; }
        .sidebar .sidebar-content { background: rgba(255, 255, 255, 0.8); }
        .block-container { max-width: 1200px; padding: 2rem; margin: auto; }
        .stTextInput, .stTextArea, .stCheckbox, .stSelectbox, .stMultiselect { margin-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

# Variável para controlar se o formulário foi enviado
submitted = False

# Formulário de entrada
with st.form(key='profile_form'):
    # Ajuste das colunas
    col1, col2, col3 = st.columns([4, 4, 4])

    with col1:
        company_name = st.text_input("Nome da Empresa/Cliente")
        website = st.text_input("Site")
        website_no_site = st.checkbox("Não possuo um site")
        client_type = st.multiselect("Tipo de Cliente", 
                                     ["Empresário", "MEI", "Gestor de Projetos", "Stakeholder", 
                                      "Startup", "Holding", "Diretor", "Sócio", "CEO", 
                                      "Gerente", "Assessor", "Investidor", "Outro"])
        contact_name = st.text_input("Nome do Contato")
        city = st.text_input("Cidade")
        email = st.text_input("E-mail")
        phone_dd = st.text_input("DDD (2 dígitos)", max_chars=2)
        phone_number = st.text_input("Número de Telefone")
        phone = f"({phone_dd}) {phone_number}"

    with col2:
        market_segment = st.multiselect("Segmento de Mercado", 
                                        ["Tecnologia", "Educação", "Saúde", "Financeira", "Comércio", 
                                         "Serviços", "Outro"])
        address = st.text_area("Endereço")
        no_physical_address = st.checkbox("Não possuo endereço físico")
        capital = st.text_input("Capital")
        desired_revenue = st.text_input("Receita Desejada")
        services = st.multiselect("Serviços")
        payment_methods = st.multiselect("Métodos de Pagamento")
        source = st.text_input("Fonte")
        business_field = st.text_input("Área de Negócio")
        business_type = st.text_input("Tipo de Negócio")

    with col3:
        context = st.text_area("Contexto do Negócio")
        return_time = st.text_input("Tempo de Retorno")
        market_analysis = st.checkbox("Análise de Mercado")
        difficulties = st.text_area("Dificuldades")
        cnpj_or_cpf = st.text_input("CNPJ/CPF")
        employees = st.text_input("Número de Funcionários")

    submit_button = st.form_submit_button("Enviar")

    if submit_button:
        submitted = True
        data = {
            'company_name': company_name,
            'website': website,
            'client_type': client_type,
            'contact_name': contact_name,
            'city': city,
            'email': email,
            'phone': phone,
            'market_segment': market_segment,
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

        # Upload dos arquivos
        st.file_uploader("Faça o upload do logo", type=["png", "jpg", "jpeg"], key="logo")
        st.file_uploader("Faça o upload do PDF", type=["pdf"], key="pdf")
        st.file_uploader("Faça o upload do vídeo", type=["mp4"], key="video")

        # Conecte-se ao Google Drive
        drive_service = authenticate_google_drive()
        folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')

        # Enviar arquivos para o Google Drive
        logo_file = st.session_state.get('logo')
        pdf_file = st.session_state.get('pdf')
        video_file = st.session_state.get('video')

        logo_file_id = upload_file_to_drive(drive_service, logo_file, folder_id) if logo_file else None
        pdf_file_id = upload_file_to_drive(drive_service, pdf_file, folder_id) if pdf_file else None
        video_file_id = upload_file_to_drive(drive_service, video_file, folder_id) if video_file else None

        # Inserir dados no banco de dados
        insert_data(data, logo_file_id, pdf_file_id, video_file_id)

        st.success("Formulário enviado com sucesso!")

        # Limpar o formulário
        clear_form()
