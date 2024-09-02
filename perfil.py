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

# Carregar variáveis de ambiente
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

            values = [json.dumps(item) if isinstance(item, list) else item for item in data]
            cursor.execute(query, values)
            conn.commit()
        except sqlite3.Error as e:
            st.error(f"Erro ao inserir dados: {e}")
        finally:
            conn.close()

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
<<<<<<< HEAD
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
=======
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_path, SCOPES)
>>>>>>> 1f33cc5dded2753576eac642f6dd13434c6082a0
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

# Função para fazer o upload do arquivo para o Google Drive
<<<<<<< HEAD
def upload_file_to_drive(service, file, folder_id=None):
    file_metadata = {'name': file.name}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    media = MediaFileUpload(file, resumable=True)
    file_drive = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file_drive.get('id')

# Função para limpar o formulário
def clear_form():
    fields = [
        'company_name', 'website', 'website_no_site', 'client_type', 'contact_name',
        'city', 'email', 'phone_dd', 'phone_number', 'market_segment', 'address',
        'no_physical_address', 'capital', 'desired_revenue', 'services', 'payment_methods',
        'source', 'business_field', 'business_type', 'context', 'return_time',
        'market_analysis', 'difficulties', 'cnpj_or_cpf', 'employees'
    ]
    for field in fields:
        st.session_state[field] = ''
=======
def upload_file_to_drive(service, file_path, folder_id=None):
    file_metadata = {'name': os.path.basename(file_path)}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

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
>>>>>>> 1f33cc5dded2753576eac642f6dd13434c6082a0

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
        market_segment = st.multiselect("Segmento de Mercado", ["B2B", "B2C", "Ainda não decidi"])
        address = st.text_input("Endereço Físico")
        no_physical_address = st.checkbox("Não possuo endereço físico")
<<<<<<< HEAD
        capital = st.selectbox("Capital Disponível", ["20mil", "40mil", "60mil", "80mil", 
                                                     "100mil", "200mil", "400mil", "600mil", 
                                                     "800mil", "1 milhão", "Mais de 1 milhão"])
        desired_revenue = st.text_input("Receita Desejada")
        services = st.multiselect("Serviços Desejados", ["Consultoria", "Desenvolvimento Web", 
                                                         "Marketing Digital", "Gestão de Projetos", "Outros"])
        payment_methods = st.multiselect("Formas de Pagamento", ["Pix", "Boleto", "Cartão de Crédito", 
                                                                 "Transferência", "PayPal", "Outros"])
        source = st.text_input("Fonte de Aquisição")

=======
        
        capital_options = ["20mil", "40mil", "60mil", "80mil", "100mil", "200mil", "400mil", "600mil", "800mil", "1 milhão", "Mais de 1 milhão"]
        capital = st.selectbox("Capital Disponível", capital_options)
        
        desired_revenue = st.text_input("Receita Desejada")
        
        services = st.multiselect("Serviços que deseja contratar (Escolha todos que se aplicam)", 
                                  ["Consultoria", "Desenvolvimento Web", "Marketing Digital", "Gestão de Projetos", "Outros"])
        
        payment_methods = st.multiselect("Formas de Pagamento Preferidas (Escolha todas que se aplicam)", 
                                         ["Pix", "Boleto", "Cartão de Crédito", "Transferência", "PayPal", "Outros"])
        
        source = st.text_input("Fonte de Aquisição")
        
>>>>>>> 1f33cc5dded2753576eac642f6dd13434c6082a0
    with col3:
        business_field = st.text_input("Área de Atuação")
        business_type = st.text_input("Tipo de Negócio")
        context = st.text_area("Contexto do Projeto")
        return_time = st.text_input("Prazo de Retorno")
        market_analysis = st.checkbox("Análise de Mercado Concluída")
        difficulties = st.text_area("Dificuldades Encontradas")
        cnpj_or_cpf = st.text_input("CNPJ ou CPF")
        employees = st.text_input("Número de Funcionários")

    st.markdown("<hr>", unsafe_allow_html=True)
<<<<<<< HEAD

    # Upload de arquivos
=======
    
    # Arquivos
>>>>>>> 1f33cc5dded2753576eac642f6dd13434c6082a0
    st.subheader("Envio de Arquivos")
    uploaded_logo = st.file_uploader("Envie o Logo da Empresa", type=['jpg', 'jpeg', 'png'])
    uploaded_pdf = st.file_uploader("Envie o PDF", type=['pdf'])
    uploaded_video = st.file_uploader("Envie o Vídeo", type=['mp4'])

    # Submissão do formulário
    submit_button = st.form_submit_button(label="Enviar")
    
    if submit_button:
        # Prepara os dados
<<<<<<< HEAD
        form_data = [
            company_name, website, client_type, contact_name, email, phone, address, no_physical_address,
            capital, desired_revenue, services, payment_methods, source, business_field, business_type,
            context, return_time, market_analysis, difficulties, cnpj_or_cpf, employees
        ]

        # Salva os dados no banco de dados
        insert_data(form_data, uploaded_logo.name if uploaded_logo else None, 
                    uploaded_pdf.name if uploaded_pdf else None, 
                    uploaded_video.name if uploaded_video else None)

        # Autentica no Google Drive
        drive_service = authenticate_google_drive()

        # Faz upload dos arquivos, se fornecidos
        if uploaded_logo:
            upload_file_to_drive(drive_service, uploaded_logo)
        if uploaded_pdf:
            upload_file_to_drive(drive_service, uploaded_pdf)
        if uploaded_video:
            upload_file_to_drive(drive_service, uploaded_video)

        st.success("Formulário enviado com sucesso!")
        submitted = True

# Limpar formulário após submissão bem-sucedida
if submitted:
    clear_form()
=======
        form_data = [company_name, website, client_type, contact_name, email, phone, address, no_physical_address, 
                     capital, desired_revenue, services, payment_methods, source, business_field, business_type, 
                     context, return_time, market_analysis, difficulties, cnpj_or_cpf, employees]
        
        # Adiciona os caminhos dos arquivos se disponíveis
        logo_path = uploaded_logo.name if uploaded_logo else None
        pdf_path = uploaded_pdf.name if uploaded_pdf else None
        video_path = uploaded_video.name if uploaded_video else None

        # Salva os dados no banco de dados
        insert_data(form_data, logo_path, pdf_path, video_path)
        
        # Upload dos arquivos para o Google Drive
        drive_service = authenticate_google_drive()
        
        if uploaded_logo:
            logo_drive_id = upload_file_to_drive(drive_service, uploaded_logo)
            st.success(f"Logo enviado com sucesso! ID do arquivo no Drive: {logo_drive_id}")

        if uploaded_pdf:
            pdf_drive_id = upload_file_to_drive(drive_service, uploaded_pdf)
            st.success(f"PDF enviado com sucesso! ID do arquivo no Drive: {pdf_drive_id}")

        if uploaded_video:
            video_drive_id = upload_file_to_drive(drive_service, uploaded_video)
            st.success(f"Vídeo enviado com sucesso! ID do arquivo no Drive: {video_drive_id}")

        # Limpar o formulário após o envio
        clear_form()
        submitted = True
        st.success("Formulário enviado com sucesso!")
>>>>>>> 1f33cc5dded2753576eac642f6dd13434c6082a0
