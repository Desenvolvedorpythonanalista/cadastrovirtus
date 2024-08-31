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
        except sqlite3.Error as e:
            st.error(f"Erro ao criar tabela: {e}")
        finally:
            conn.close()

# Função para inserir dados no banco de dados
def insert_data(data, logo_path=None):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            columns = [
                'company_name', 'website', 'client_type', 'contact_name', 'contact_position',
                'email', 'phone', 'address', 'no_physical_address', 'capital', 'desired_revenue',
                'services', 'payment_methods', 'budget', 'business_field', 'business_type', 'context',
                'return_time', 'market_analysis', 'difficulties', 'cnpj_or_cpf', 'logo_path', 'logo_provided'
            ]

            # Remove colunas que não estão no formulário
            columns_to_insert = [col for col in columns if col not in ['contact_position']]
            placeholders = ', '.join('?' for _ in columns_to_insert)
            query = f'INSERT INTO profiles ({", ".join(columns_to_insert)}) VALUES ({placeholders})'

            # Convert lists to JSON strings
            values = [json.dumps(item) if isinstance(item, list) else item for item in data]
            values.append(logo_path if logo_path else None)
            values.append(1 if logo_path else 0)

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
        "Endereço", "Não Possuo Endereço Físico", "Nível de Capital Disponível", "Faturamento Desejado",
        "Serviços Requeridos", "Forma de Pagamento Preferida", "Orçamento Disponível", "Ramo de Negócio",
        "Tipo de Negócio", "Contexto e Objetivos", "Tempo para Retorno Desejado", "Análise de Mercado", "Dificuldades Enfrentadas",
        "CNPJ/CPF"
    ]

    pdf.set_fill_color(255, 255, 255)
    pdf.set_text_color(0, 0, 0)

    for heading, value in zip(headings, data):
        if isinstance(value, list):
            value = ', '.join(value)
        elif value is None:
            value = 'Não disponível'
        
        pdf.cell(200, 10, txt=f"{heading}: {value}", ln=True, align='L')

    if logo_path:
        try:
            pdf.image(logo_path, x=10, y=pdf.get_y() + 10, w=50)
        except Exception as e:
            st.error(f"Erro ao adicionar logo ao PDF: {e}")

    # Salvar o PDF na pasta 'logos'
    pdf_output_path = os.path.join(LOGOS_DIR, 'client_profile.pdf')
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
        business_field_options = ["Tecnologia", "Educação", "Saúde", "Finanças", "Indústria", "Varejo", "Serviços"]
        business_field = st.selectbox("Ramo de Negócio", business_field_options)
        
        business_type_options = ["Startup", "Pequena Empresa", "Média Empresa", "Grande Empresa", "Holding"]
        business_type = st.selectbox("Tipo de Negócio", business_type_options)
        
        context = st.text_area("Contexto e Objetivos")
        return_time = st.text_input("Tempo para Retorno Desejado")
        market_analysis = st.checkbox("Fez análise de mercado?")
        difficulties = st.text_area("Dificuldades Enfrentadas")
        logo_provided = st.checkbox("Logo fornecida")
        logo_file = st.file_uploader("Carregar Logo", type=["jpg", "jpeg", "png"])

    # Botão de envio
    submit_button = st.form_submit_button(label='Enviar')

    if submit_button:
        # Verificação dos campos obrigatórios
        if not company_name or not email or not phone or not (services or budget):
            st.error("Por favor, preencha todos os campos obrigatórios.")
        else:
            # Salvar logo no diretório
            logo_path = None
            if logo_provided and logo_file:
                try:
                    logo_path = os.path.join(LOGOS_DIR, logo_file.name)
                    with open(logo_path, "wb") as f:
                        f.write(logo_file.getvalue())
                except Exception as e:
                    st.error(f"Erro ao salvar o logo: {e}")
            
            # Preparar os dados para inserção
            data = [
                company_name, website if not website_no_site else 'Não disponível', 
                json.dumps(client_type), contact_name, city, email, phone, 
                address if not no_physical_address else 'Não disponível', 
                capital, desired_revenue, json.dumps(services), json.dumps(payment_methods), 
                budget, business_field, business_type, context, return_time, market_analysis, 
                difficulties, cnpj_or_cpf
            ]
            
            # Inserir dados no banco de dados
            insert_data(data, logo_path)
            
            # Gerar PDF
            pdf_path = generate_pdf(data, logo_path)
            submitted = True

# Exibir dados salvos e o PDF
if submitted:
    st.success("Dados enviados com sucesso!")
    
    # Exibir dados
    st.write("**Dados Enviados:**")
    st.json({
        "Nome da Empresa/Cliente": company_name,
        "Site": website if not website_no_site else 'Não disponível',
        "Tipo de Cliente": client_type,
        "Nome do Contato": contact_name,
        "Cidade": city,
        "E-mail": email,
        "Telefone": phone,
        "Endereço": address if not no_physical_address else 'Não disponível',
        "Valor de Capital Disponível": capital,
        "Faturamento Desejado": desired_revenue,
        "Serviços Requeridos": services,
        "Forma de Pagamento Preferida": payment_methods,
        "Orçamento Disponível": budget,
        "Ramo de Negócio": business_field,
        "Tipo de Negócio": business_type,
        "Contexto e Objetivos": context,
        "Tempo para Retorno Desejado": return_time,
        "Análise de Mercado": market_analysis,
        "Dificuldades Enfrentadas": difficulties,
        "CNPJ/CPF": cnpj_or_cpf
    })
    
    if pdf_path:
        st.write(f"**PDF Gerado:** [client_profile.pdf]({pdf_path})")
