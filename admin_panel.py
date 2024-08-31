import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO

# Função para conectar ao banco de dados e buscar os dados
def view_data(db_name, table_name):
    conn = sqlite3.connect(db_name)
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Função para criar um botão de download para o banco de dados
def download_database(db_name):
    conn = sqlite3.connect(db_name)
    with BytesIO() as buffer:
        for line in conn.iterdump():
            buffer.write(f"{line}\n".encode())
        buffer.seek(0)
        return buffer.read()

# Função para exibir os dados em uma tabela
def display_data(df):
    if df.empty:
        st.write("Nenhum dado encontrado.")
        return
    st.write("**Dados Enviados:**")
    st.dataframe(df)

# Função para autenticação
def authenticate():
    password = st.text_input("Senha:", type="password")
    if password == '00000100000':
        return True
    elif password:
        st.error("Senha incorreta.")
    return False

# Função para apagar dados
def delete_data(db_name, table_name, id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE id=?", (id,))
    conn.commit()
    conn.close()

# Função para adicionar novos dados
def add_data(db_name, table_name, data):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    placeholders = ', '.join(['?' for _ in data])
    columns = ', '.join(data.keys())
    cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", tuple(data.values()))
    conn.commit()
    conn.close()

# Aplicativo Streamlit
def main():
    st.title("Painel Administrativo")

    if authenticate():
        st.sidebar.title("Opções")
        db_options = st.sidebar.radio("Escolha o banco de dados", ("client_profiles.db", "clientes.db"))

        if db_options == "client_profiles.db":
            table_name = "profiles"
        else:
            table_name = "clientes"

        if st.sidebar.button("Baixar Banco de Dados"):
            db_content = download_database(db_options)
            st.download_button(
                label=f"Baixar {db_options}",
                data=db_content,
                file_name=db_options,
                mime="application/x-sqlite3"
            )

        # Exibir os dados
        data_df = view_data(db_options, table_name)
        display_data(data_df)

        # Opção para apagar dados
        st.subheader("Excluir Dados")
        id_to_delete = st.number_input("ID do Registro para Excluir:", min_value=1)
        if st.button("Excluir Registro"):
            delete_data(db_options, table_name, id_to_delete)
            st.success(f"Registro com ID {id_to_delete} excluído com sucesso.")
            # Atualizar a visualização dos dados
            data_df = view_data(db_options, table_name)
            display_data(data_df)

        # Opção para adicionar novos dados
        st.subheader("Cadastrar Novo Registro")
        with st.form("add_form"):
            if db_options == "client_profiles.db":
                name = st.text_input("Nome da Empresa/Cliente")
                site = st.text_input("Site")
                client_type = st.text_input("Tipo de Cliente (separado por vírgulas)")
                contact_name = st.text_input("Nome do Contato")
                city = st.text_input("Cidade")
                email = st.text_input("E-mail")
                phone = st.text_input("Telefone")
                address = st.text_input("Endereço")
                no_physical_address = st.checkbox("Não Possuo Endereço Físico")
                capital_available = st.text_input("Valor de Capital Disponível")
                desired_revenue = st.text_input("Faturamento Desejado")
                required_services = st.text_input("Serviços Requeridos (separado por vírgulas)")
                preferred_payment_method = st.text_input("Forma de Pagamento Preferida (separado por vírgulas)")
                available_budget = st.text_input("Orçamento Disponível")
                business_field = st.text_input("Ramo de Negócio")
                business_type = st.text_input("Tipo de Negócio")
                context_and_goals = st.text_input("Contexto e Objetivos")
                desired_return_time = st.text_input("Tempo para Retorno Desejado")
                market_analysis = st.checkbox("Análise de Mercado")
                difficulties_faced = st.text_input("Dificuldades Enfrentadas")
                cnpj_cpf = st.text_input("CNPJ/CPF")
                logo_path = st.text_input("Caminho do Logo")
                logo_provided = st.checkbox("Logo Fornecida")

                submitted = st.form_submit_button("Cadastrar")
                if submitted:
                    new_data = {
                        'name': name, 'site': site, 'client_type': ','.join(client_type.split(',')), 'contact_name': contact_name,
                        'city': city, 'email': email, 'phone': phone, 'address': address, 'no_physical_address': no_physical_address,
                        'capital_available': capital_available, 'desired_revenue': desired_revenue, 'required_services': ','.join(required_services.split(',')),
                        'preferred_payment_method': ','.join(preferred_payment_method.split(',')), 'available_budget': available_budget,
                        'business_field': business_field, 'business_type': business_type, 'context_and_goals': context_and_goals,
                        'desired_return_time': desired_return_time, 'market_analysis': market_analysis, 'difficulties_faced': difficulties_faced,
                        'cnpj_cpf': cnpj_cpf, 'logo_path': logo_path, 'logo_provided': logo_provided
                    }
                    add_data(db_options, table_name, new_data)
                    st.success("Novo registro adicionado com sucesso.")
                    # Atualizar a visualização dos dados
                    data_df = view_data(db_options, table_name)
                    display_data(data_df)
            else:
                nome = st.text_input("Nome")
                telefone = st.text_input("Telefone")
                email = st.text_input("Email")
                investidor = st.selectbox("Tipo de Investidor", ["Inicial", "Intermediário", "Avançado"])
                capital = st.selectbox("Capital Disponível", ["20mil", "40mil", "60mil", "80mil", "100mil", "200mil", "400mil", "600mil", "800mil", "1milhão"])

                submitted = st.form_submit_button("Cadastrar")
                if submitted:
                    # Defina um dicionário de alocação padrão para exemplo
                    alocacao = {
                        'Valor em Patrimônio': 60000, '10% para o valor de investimento na Virtus': 2000,
                        '30% para reserva de emergência': 6000, '10% para custos de abertura': 2000,
                        '20% para custos de tráfego': 4000, '15% para Treinamento Empresarial': 3000,
                        '15% para infraestrutura': 3000
                    }
                    new_data = {
                        'nome': nome, 'telefone': telefone, 'email': email, 'investidor': investidor,
                        'capital': capital, 'patrimonio': alocacao['Valor em Patrimônio'], 'valor_virtus': alocacao['10% para o valor de investimento na Virtus'],
                        'reserva_emergencia': alocacao['30% para reserva de emergência'], 'custos_abertura': alocacao['10% para custos de abertura'],
                        'custos_trafego': alocacao['20% para custos de tráfego'], 'treinamento_empresarial': alocacao['15% para Treinamento Empresarial'],
                        'infraestrutura': alocacao['15% para infraestrutura']
                    }
                    add_data(db_options, table_name, new_data)
                    st.success("Novo registro adicionado com sucesso.")
                    # Atualizar a visualização dos dados
                    data_df = view_data(db_options, table_name)
                    display_data(data_df)

if __name__ == "__main__":
    main()
