import os
import json
import streamlit as st
import sqlite3
from fpdf import FPDF

# Definir o diretório de logos
LOGOS_DIR = 'logos'  # Usando um caminho relativo

# Criar o diretório se não existir
if not os.path.exists(LOGOS_DIR):
    os.makedirs(LOGOS_DIR)

# Função para criar conexão com o banco de dados
def create_connection():
    conn = sqlite3.connect('client_profiles.db')
    return conn

# Função para criar a tabela no banco de dados
def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            website TEXT,
            client_type TEXT,
            contact_name TEXT,
            contact_position TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            no_physical_address BOOLEAN,
            capital TEXT,
            desired_revenue TEXT,
            services TEXT,
            payment_methods TEXT,
            budget TEXT,
            business_field TEXT,
            business_type TEXT,
            context TEXT,
            return_time TEXT,
            market_analysis BOOLEAN,
            difficulties TEXT,
            cnpj_or_cpf TEXT,
            logo_path TEXT,
            logo_provided BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

# Função para inserir dados no banco de dados
def insert_data(data, logo_path=None):
    conn = create_connection()
    cursor = conn.cursor()

    columns = [
        'company_name', 'website', 'client_type', 'contact_name', 'contact_position',
        'email', 'phone', 'address', 'no_physical_address', 'capital', 'desired_revenue',
        'services', 'payment_methods', 'budget', 'business_field', 'business_type', 'context',
        'return_time', 'market_analysis', 'difficulties', 'cnpj_or_cpf', 'logo_path', 'logo_provided'
    ]

    columns_to_insert = columns.copy()
    placeholders = ', '.join('?' for _ in columns_to_insert)
    query = f'INSERT INTO profiles ({", ".join(columns_to_insert)}) VALUES ({placeholders})'

    # Convert lists to JSON strings
    values = [json.dumps(item) if isinstance(item, list) else item for item in data]
    values.append(logo_path if logo_path else None)
    values.append(1 if logo_path else 0)

    cursor.execute(query, values)
    conn.commit()
    conn.close()

# Função para gerar o PDF
def generate_pdf(data, logo_path=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    headings = [
        "Nome da Empresa/Cliente", "Site", "Tipo de Cliente", "Nome do Contato", "Cidade", "E-mail", "Telefone",
        "Endereço", "Não Possuo Endereço Físico", "Nível de Capital Disponível", "Faturamento Desejado",
        "Serviços Requeridos", "Forma de Pagamento Preferida", "Orçamento Disponível", "CNPJ/CPF", 
        "Ramo de Negócio", "Tipo de Negócio", "Contexto e Objetivos", "Tempo para Retorno Desejado", 
        "Análise de Mercado", "Dificuldades Enfrentadas"
    ]
    
    for heading, value in zip(headings, data):
        pdf.cell(200, 10, txt=f"{heading}: {value}", ln=True)

    if logo_path:
        pdf.image(logo_path, x=10, y=pdf.get_y() + 10, w=50)

    # Salvar o PDF na pasta 'logos'
    pdf_output_path = os.path.join(LOGOS_DIR, 'client_profile.pdf')
    pdf.output(pdf_output_path)
    return pdf_output_path

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
        market_segment = st.selectbox("Segmento de Mercado", ["B2B", "B2C", "B2G", "Outro"])   
        address = st.text_input("Endereço Físico")
        no_physical_address = st.checkbox("Não possuo endereço físico")
        capital = st.text_input("Valor de Capital Disponível")
        desired_revenue = st.text_input("Faturamento Desejado")

        services_options = ["Jurídico", "Proteção de Marca", "Sistemas de Gestão Comercial", "Automatização", 
                            "Marketing", "Negócio Digital", "Social Media", "Site/Landing Page", "Tráfego", 
                            "Contabilidade", "Produto (MVP)"]
        services = st.multiselect("Serviços Requeridos (Escolha todas as opções que se aplicam)", services_options)

        payment_methods_options = ["Boleto Bancário", "Transferência Bancária", "Cartão de Crédito", "Débito em Conta", 
                                   "Pagamento Online (PayPal, etc.)", "Outros"]
        payment_methods = st.multiselect("Forma de Pagamento Preferida (Escolha todas as opções que se aplicam)", 
                                         payment_methods_options)
        
        # Novo campo de orçamento disponível
        budget = st.text_input("Orçamento Disponível")

    with col3:
        cnpj_or_cpf = st.text_input("CNPJ/CPF")
        business_field_options = ["Tecnologia", "Saúde", "Educação", "Financeiro", "Comércio", "Serviços", 
                                  "Imobiliário", "Indústria", "Agronegócio", "Outros"]
        business_field = st.selectbox("Ramo de Negócio", business_field_options)

        business_type = st.selectbox("Tipo de Negócio", ["Físico", "Digital", "Ambos", "Ainda não decidi"])
        
        return_time_options = ["Até 6 meses", "1 ano", "Entre 1 a 5 anos", "5 anos ou mais"]
        return_time = st.selectbox("Tempo para Retorno Desejado", return_time_options)

        context = st.text_area("Contexto e Objetivos")
        market_analysis = st.checkbox("Análise de Mercado Já Realizada?")
        difficulties = st.text_area("Qual tem sido sua maior dificuldade? Descreva com todos os detalhes")

        logo_provided = st.checkbox("Logo Fornecida")
        
        # Upload de logo
        uploaded_logo = st.file_uploader("Carregue o arquivo da Logo", type=['jpg', 'jpeg', 'png'])

    # Submissão do formulário
    submit_button = st.form_submit_button("Enviar")
    
    if submit_button:
        # Transformar dados em uma lista
        data = [
            company_name, website, client_type, contact_name, city, email, phone, address, no_physical_address,
            capital, desired_revenue, services, payment_methods, budget, business_field, business_type, context,
            return_time, market_analysis, difficulties, cnpj_or_cpf
        ]

        if uploaded_logo:
            # Salvar o logo no diretório
            logo_path = os.path.join(LOGOS_DIR, uploaded_logo.name)
            with open(logo_path, "wb") as f:
                f.write(uploaded_logo.read())
        else:
            logo_path = None

        # Inserir dados no banco de dados
        insert_data(data, logo_path)
        
        # Gerar PDF
        pdf_path = generate_pdf(data, logo_path)
        submitted = True

# Mostrar PDF gerado após a submissão
if submitted:
    st.success("Dados enviados e PDF gerado com sucesso!")

    # Exibir o botão para baixar o PDF na Streamlit
    with open(pdf_path, "rb") as pdf_file:
        st.download_button(
            label="Baixar PDF",
            data=pdf_file,
            file_name="client_profile.pdf",
            mime="application/pdf"
        )
