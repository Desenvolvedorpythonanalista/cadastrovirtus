import os
import json
import streamlit as st
import sqlite3
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

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
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT,
                    website TEXT,
                    client_type TEXT,
                    contact_name TEXT,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    no_physical_address BOOLEAN,
                    capital TEXT,
                    desired_revenue TEXT,
                    services TEXT,
                    payment_methods TEXT,
                    source TEXT,
                    business_field TEXT,
                    business_type TEXT,
                    context TEXT,
                    return_time TEXT,
                    market_analysis BOOLEAN,
                    difficulties TEXT,
                    cnpj_or_cpf TEXT,
                    logo_path TEXT,
                    pdf_path TEXT,
                    video_path TEXT,
                    employees TEXT
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
            values.append(logo_path if logo_path else None)
            values.append(pdf_path if pdf_path else None)
            values.append(video_path if video_path else None)

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
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_297185839442-0m4p4sbfbodbqsk816ca3q0o14phbk5u.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

# Função para fazer o upload do arquivo para o Google Drive
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

# Streamlit app
st.title("Levantamento de Perfil do Cliente")

# Criação da tabela no banco de dados
create_table()

# Adiciona CSS para melhorar o layout do formulário
st.markdown("""
    <style>
        .reportview-container {
            background: url('assets/bg.png') no-repeat center center fixed; 
            background-size: cover;
        }
        .sidebar .sidebar-content {
            background: rgba(255, 255, 255, 0.8); /* White background with opacity for the sidebar */
        }
        .block-container {
            max-width: 1200px; /* Define the maximum width of the form */
            padding: 2rem; /* Add padding for better spacing */
            margin: auto; /* Center the form horizontally */
        }
        .stTextInput, .stTextArea, .stCheckbox, .stSelectbox, .stMultiselect {
            margin-bottom: 1rem; /* Add space between form fields */
        }
    </style>
""", unsafe_allow_html=True)

# Variável para controlar se o formulário foi enviado
submitted = False

# Formulário de entrada
with st.form(key='profile_form'):
    # Ajuste das colunas
    col1, col2, col3 = st.columns([4, 4, 4])  # Ajustando a largura das colunas para mais espaço horizontal

    with col1:
        company_name = st.text_input("Nome da Empresa/Cliente")
        website = st.text_input("Site")
        website_no_site = st.checkbox("Não possuo um site")
        client_type = st.multiselect("Tipo de Cliente (Escolha todas as opções que se aplicam)", 
                                    ["Empresário", "MEI", "Gestor de Projetos", "Stakeholder", "Startup", "Holding", 
                                     "Diretor", "Sócio", "CEO", "Gerente", "Assessor", "Investidor", "Outro"])
        contact_name = st.text_input("Nome do Contato")
        city = st.text_input("Cidade")
        email = st.text_input("E-mail")
        phone_dd = st.text_input("DDD (2 dígitos)", max_chars=2)
        phone_number = st.text_input("Número de Telefone")
        phone = f"({phone_dd}) {phone_number}"

    with col2:
        market_segment = st.multiselect("Segmento de Mercado (Escolha todas as opções que se aplicam)", 
                                        ["B2B", "B2C", "Ainda não decidi"])   
        address = st.text_input("Endereço Físico")
        no_physical_address = st.checkbox("Não possuo endereço físico")
        
        capital_options = ["20mil", "40mil", "60mil", "80mil", "100mil", "200mil", "400mil", "600mil", "800mil", "1mi"]
        capital = st.selectbox("Capital Disponível", capital_options)
        
        desired_revenue_options = ["10mil", "20mil", "30mil", "40mil", "50mil", "100mil", "200mil", "300mil", "400mil", "500mil"]
        desired_revenue = st.selectbox("Faturamento Desejado", desired_revenue_options)

        services = st.multiselect("Serviços Requeridos (Escolha todas as opções que se aplicam)", 
                                 ["Desenvolvimento Web", "Consultoria", "Design Gráfico", "Marketing Digital", 
                                  "Suporte Técnico", "Treinamento", "Outros"])

    with col3:
        payment_methods = st.multiselect("Formas de Pagamento Preferidas", 
                                         ["Boleto", "Cartão de Crédito", "Transferência Bancária", "PIX", "PayPal", "Outros"])
        source = st.text_input("Como conheceu nossa empresa?")
        business_field = st.text_input("Ramo de Negócio")
        business_type = st.text_input("Tipo de Negócio")
        context = st.text_area("Contexto e Objetivos")
        return_time = st.text_input("Tempo para Retorno Desejado")
        market_analysis = st.checkbox("Fez alguma análise de mercado?")
        difficulties = st.text_area("Dificuldades Enfrentadas")
        cnpj_or_cpf = st.text_input("CNPJ/CPF")
        employees = st.text_input("Número de Funcionários")

    logo_file = st.file_uploader("Upload do Logo", type=['png', 'jpg', 'jpeg'])
    pdf_file = st.file_uploader("Upload do PDF", type=['pdf'])
    video_file = st.file_uploader("Upload do Vídeo", type=['mp4', 'mov', 'avi'])
    
    submit_button = st.form_submit_button("Enviar")

    if submit_button:
        submitted = True
        # Salvar arquivos se forem enviados
        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)

        if logo_file:
            logo_path = os.path.join(upload_dir, logo_file.name)
            with open(logo_path, "wb") as f:
                f.write(logo_file.read())
        else:
            logo_path = None

        if pdf_file:
            pdf_path = os.path.join(upload_dir, pdf_file.name)
            with open(pdf_path, "wb") as f:
                f.write(pdf_file.read())
        else:
            pdf_path = None

        if video_file:
            video_path = os.path.join(upload_dir, video_file.name)
            with open(video_path, "wb") as f:
                f.write(video_file.read())
        else:
            video_path = None

        # Dados do formulário
        data = [
            company_name, website, client_type, contact_name, city, email, phone, address, no_physical_address, 
            capital, desired_revenue, services, payment_methods, source, business_field, business_type, context, 
            return_time, market_analysis, difficulties, cnpj_or_cpf, None, None, None, employees
        ]
        
        # Inserir dados no banco de dados
        insert_data(data, logo_path, pdf_path, video_path)

        # Autenticar no Google Drive e fazer upload dos arquivos
        service = authenticate_google_drive()
        folder_id = '13X_YJqvB3jGdOxCCIrNzt5vi8UwtWNlE'  # ID da pasta do Google Drive onde o arquivo será salvo

        if logo_path:
            upload_file_to_drive(service, logo_path, folder_id)
        if pdf_path:
            upload_file_to_drive(service, pdf_path, folder_id)
        if video_path:
            upload_file_to_drive(service, video_path, folder_id)

        st.success("Dados enviados com sucesso!")

        # Limpar o formulário
        clear_form()
        
        # Limpar arquivos temporários
        if logo_path and os.path.exists(logo_path):
            os.remove(logo_path)
        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
