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

# Variável para controlar se o formulário foi enviado
submitted = False
pdf_path = None
video_path = None

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
                                         ["Boleto", "Cartão de Crédito", "Transferência Bancária", "Pix", "Outro"])
        
        source_options = ["Indicação", "YouTube", "Google", "Evento/Treinamento", "Redes sociais"]
        source = st.selectbox("Meio pelo qual veio", source_options)

    with col3:
        business_field_options = ["Tecnologia", "Saúde", "Educação", "Financeiro", "Indústria", "Varejo", "Serviços", "Agronegócio", "Outra", "Ainda não decidi"]
        business_field = st.multiselect("Ramo de Negócio (Escolha todos que se aplicam)", business_field_options)
        
        business_type = st.selectbox("Tipo de Negócio", ["Novo", "Em crescimento", "Estável", "Em dificuldade", "Ainda não decidi"])
        
        context = st.text_area("Contexto e Objetivos")
        
        return_time_options = ["Até 3 meses", "Até 6 meses", "Até 1 ano", "Entre 1 a 5 anos", "Acima de 5 anos"]
        return_time = st.selectbox("Tempo para Retorno Desejado", return_time_options)
        
        market_analysis = st.checkbox("Já realizou análise de mercado?")
        difficulties = st.text_area("Dificuldades Enfrentadas")
        cnpj_or_cpf = st.text_input("CNPJ/CPF")
        
        employees_options = ["Não", "1-5", "6-10", "11-20", "21-50", "51-100", "101-200", "201-500", "501-1000", "Acima de 1000"]
        employees = st.selectbox("Possui Funcionários?", employees_options)

    # Adicionar upload de logo e vídeo
    logo = st.file_uploader("Logo da Empresa (opcional)", type=['png', 'jpg', 'jpeg'])
    video = st.file_uploader("Vídeo de Apresentação (opcional)", type=['mp4', 'mov'])

    # Botão de envio do formulário
    submit_button = st.form_submit_button(label='Enviar')

    if submit_button:
        submitted = True
        logo_path = None
        if logo is not None:
            logo_path = f"uploads/{company_name}_logo.{logo.type.split('/')[1]}"
            with open(logo_path, 'wb') as f:
                f.write(logo.read())
        
        video_path = None
        if video is not None:
            video_path = f"uploads/{company_name}_video.{video.type.split('/')[1]}"
            with open(video_path, 'wb') as f:
                f.write(video.read())
        
        data = [company_name, website if not website_no_site else "Não disponível", client_type, contact_name, 
                email, phone, address if not no_physical_address else "Não disponível", no_physical_address,
                capital, desired_revenue, services, payment_methods, source, business_field, business_type, 
                context, return_time, market_analysis, difficulties, cnpj_or_cpf, employees]
        
        pdf_path = generate_pdf(data, logo_path)
        insert_data(data, logo_path=logo_path, pdf_path=pdf_path, video_path=video_path)

        st.success("Dados enviados e PDF gerado com sucesso!")

# Mostrar o botão de download do PDF fora do formulário
if pdf_path:
    st.download_button(label="Baixar PDF", data=open(pdf_path, 'rb').read(), file_name="client_profile.pdf", mime="application/pdf")

# Mostrar os dados recuperados do banco de dados
data = get_data()
if data:
    st.subheader("Último Perfil do Cliente Enviado:")
    st.write({
        "Nome da Empresa/Cliente": data[1],
        "Site": data[2],
        "Tipo de Cliente": json.loads(data[3]),
        "Nome do Contato": data[4],
        "E-mail": data[5],
        "Telefone": data[6],
        "Endereço": data[7],
        "Não Possuo Endereço Físico": data[8],
        "Valor de Capital Disponível": data[9],
        "Faturamento Desejado": data[10],
        "Serviços Requeridos": json.loads(data[11]),
        "Forma de Pagamento Preferida": json.loads(data[12]),
        "Meio pelo qual veio": data[13],
        "Ramo de Negócio": json.loads(data[14]),
        "Tipo de Negócio": data[15],
        "Contexto e Objetivos": data[16],
        "Tempo para Retorno Desejado": data[17],
        "Análise de Mercado": data[18],
        "Dificuldades Enfrentadas": data[19],
        "CNPJ/CPF": data[20],
        "Número de Funcionários": data[21],
        "Logo Path": data[22],
        "PDF Path": data[23],
        "Video Path": data[24]
    })
