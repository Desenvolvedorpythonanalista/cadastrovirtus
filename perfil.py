import os
import json
import streamlit as st
import sqlite3
from fpdf import FPDF
from tempfile import NamedTemporaryFile

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

# Função para gerar o PDF
def generate_pdf(data, logo_path=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    headings = [
        "Nome da Empresa/Cliente", "Site", "Tipo de Cliente", "Nome do Contato", "Cidade", "E-mail", "Telefone",
        "Endereço", "Não Possuo Endereço Físico", "Valor de Capital Disponível", "Faturamento Desejado",
        "Serviços Requeridos", "Forma de Pagamento Preferida", "Meio pelo qual veio", "Ramo de Negócio",
        "Tipo de Negócio", "Contexto e Objetivos", "Tempo para Retorno Desejado", "Análise de Mercado", "Dificuldades Enfrentadas",
        "CNPJ/CPF", "Número de Funcionários"
    ]

    pdf.set_fill_color(255, 255, 255)
    pdf.set_text_color(0, 0, 0)

    for heading, value in zip(headings, data):
        if isinstance(value, list):
            value = ', '.join(value)
        elif value is None:
            value = 'Não disponível'
        
        pdf.cell(200, 10, txt=f"{heading}: {value}", ln=True, align='L')

    if logo_path and os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=10, y=pdf.get_y() + 10, w=50)
        except Exception as e:
            st.error(f"Erro ao adicionar logo ao PDF: {e}")

    # Salvar o PDF em um arquivo temporário
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf_output_path = tmp_file.name
        try:
            pdf.output(pdf_output_path)
        except Exception as e:
            st.error(f"Erro ao salvar PDF: {e}")
    return pdf_output_path

# Função para recuperar e exibir dados do banco de dados
def get_data():
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM profiles ORDER BY id DESC LIMIT 1")  # Recupera o último registro inserido
            data = cursor.fetchone()
        except sqlite3.Error as e:
            st.error(f"Erro ao recuperar dados: {e}")
            data = None
        finally:
            conn.close()
    else:
        data = None
    return data

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

# Verificar se o diretório de uploads existe
upload_dir = "uploads"
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

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
        
        capital_options = ["20mil", "40mil", "60mil", "80mil", "100mil", "200mil", "400mil", "600mil", "800mil", "1milhão", "Acima de 1 milhão"]
        capital = st.selectbox("Valor de Capital Disponível", capital_options)
        
        desired_revenue = st.text_input("Faturamento Desejado")
        services = st.multiselect("Serviços Requeridos (Escolha todos que se aplicam)", 
                                  ["Desenvolvimento Web", "Consultoria", "Marketing", "Design", "Análise de Dados", "Outros"])
        
        payment_methods = st.multiselect("Forma de Pagamento Preferida", 
                                          ["Pix", "Transferência Bancária", "Boleto", "Cartão de Crédito", "Débito em Conta", "Outros"])

    with col3:
        source = st.selectbox("Meio pelo qual veio", ["Indicação", "Redes Sociais", "Publicidade", "Evento", "Outros"])
        business_field = st.selectbox("Ramo de Negócio", 
                                      ["Tecnologia", "Educação", "Saúde", "Finanças", "Varejo", "Outros"])
        
        business_type = st.text_input("Tipo de Negócio")
        context = st.text_area("Contexto e Objetivos", height=200)
        
        return_time = st.selectbox("Tempo para Retorno Desejado", 
                                    ["Imediato", "6 meses", "1 ano", "2 anos", "Outro"])
        market_analysis = st.checkbox("Desejo uma análise de mercado para minha empresa")
        
        difficulties = st.text_area("Principais Dificuldades", height=200)
        cnpj_or_cpf = st.text_input("CNPJ ou CPF")
        
        employees = st.text_input("Número de Funcionários")

    # Uploads dos arquivos
    st.header("Uploads de Arquivos")
    logo_file = st.file_uploader("Faça o upload do logo da empresa", type=['jpg', 'jpeg', 'png'])
    pdf_file = st.file_uploader("Faça o upload de um PDF (opcional)", type=['pdf'])
    video_file = st.file_uploader("Faça o upload de um vídeo de apresentação (opcional)", type=['mp4', 'mov', 'avi'])

    # Submissão do formulário
    submitted = st.form_submit_button("Enviar Formulário")

# Processamento dos dados após submissão do formulário
if submitted:
    # Definir os caminhos para salvar os arquivos
    logo_path = None
    pdf_path = None
    video_path = None

    if logo_file is not None:
        logo_path = os.path.join(upload_dir, f"{company_name}_logo.{logo_file.name.split('.')[-1]}")
        with open(logo_path, "wb") as f:
            f.write(logo_file.getbuffer())

    if pdf_file is not None:
        pdf_path = os.path.join(upload_dir, f"{company_name}_document.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_file.getbuffer())

    if video_file is not None:
        video_path = os.path.join(upload_dir, f"{company_name}_video.{video_file.name.split('.')[-1]}")
        with open(video_path, "wb") as f:
            f.write(video_file.getbuffer())

    # Dados do formulário
    form_data = [
        company_name,
        website if not website_no_site else "Não possuo site",
        client_type,
        contact_name,
        email,
        phone,
        address,
        no_physical_address,
        capital,
        desired_revenue,
        services,
        payment_methods,
        source,
        business_field,
        business_type,
        context,
        return_time,
        market_analysis,
        difficulties,
        cnpj_or_cpf,
        employees
    ]

    # Inserir os dados no banco de dados
    insert_data(form_data, logo_path=logo_path, pdf_path=pdf_path, video_path=video_path)

    # Gerar o PDF
    pdf_output_path = generate_pdf(form_data, logo_path=logo_path)

    # Exibir mensagem de sucesso e fornecer link para o PDF
    st.success("Formulário enviado com sucesso!")
    st.write(f"O PDF gerado foi salvo em: {pdf_output_path}")

    # Exibir link para download do PDF gerado
    with open(pdf_output_path, "rb") as pdf_file:
        st.download_button(
            label="Baixar PDF",
            data=pdf_file,
            file_name=f"{company_name}_perfil.pdf",
            mime="application/pdf"
        )

    # Recuperar e exibir os dados do banco de dados
    profile_data = get_data()
    if profile_data:
        st.header("Último Perfil Cadastrado")
        st.write(f"Nome da Empresa: {profile_data[1]}")
        st.write(f"Site: {profile_data[2]}")
        st.write(f"Tipo de Cliente: {profile_data[3]}")
        st.write(f"Nome do Contato: {profile_data[4]}")
        st.write(f"E-mail: {profile_data[5]}")
        st.write(f"Telefone: {profile_data[6]}")
        st.write(f"Endereço: {profile_data[7]}")
        st.write(f"Capital Disponível: {profile_data[9]}")
        st.write(f"Faturamento Desejado: {profile_data[10]}")
        st.write(f"Serviços Requeridos: {profile_data[11]}")
        st.write(f"Forma de Pagamento: {profile_data[12]}")
        st.write(f"Meio pelo qual veio: {profile_data[13]}")
        st.write(f"Ramo de Negócio: {profile_data[14]}")
        st.write(f"Tipo de Negócio: {profile_data[15]}")
        st.write(f"Contexto e Objetivos: {profile_data[16]}")
        st.write(f"Tempo para Retorno Desejado: {profile_data[17]}")
        st.write(f"Análise de Mercado: {profile_data[18]}")
        st.write(f"Dificuldades Enfrentadas: {profile_data[19]}")
        st.write(f"CNPJ/CPF: {profile_data[20]}")
        st.write(f"Número de Funcionários: {profile_data[23]}")

# Adicionar uma função para limpar o formulário após submissão bem-sucedida
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

if submitted:
    clear_form()
