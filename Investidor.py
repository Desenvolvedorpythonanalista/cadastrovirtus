import streamlit as st
import matplotlib.pyplot as plt
import os

# Função para mostrar as informações de alocação e gerar o gráfico de pizza
def mostrar_alocacao_e_grafico(investidor, capital):
    alocacoes = {
        'Inicial': {
            '20mil': {
                'Valor em Patrimônio': 60000,
                '10% para o valor de investimento na Virtus': 2000,
                '30% para reserva de emergência': 6000,
                '10% para custos de abertura': 2000,
                '20% para custos de tráfego': 4000,
                '15% para Treinamento Empresarial': 3000,
                '15% para infraestrutura': 3000,
            },
            '40mil': {
                'Valor em Patrimônio': 120000,
                '10% para o valor de investimento na Virtus': 4000,
                '30% para reserva de emergência': 12000,
                '10% para custos de abertura': 4000,
                '20% para custos de tráfego': 8000,
                '15% para Treinamento Empresarial': 6000,
                '15% para infraestrutura': 6000,
            },
            '60mil': {
                'Valor em Patrimônio': 180000,
                '10% para o valor de investimento na Virtus': 6000,
                '30% para reserva de emergência': 18000,
                '10% para custos de abertura': 6000,
                '20% para custos de tráfego': 12000,
                '15% para Treinamento Empresarial': 9000,
                '15% para infraestrutura': 9000,
            },
            '80mil': {
                'Valor em Patrimônio': 240000,
                '10% para o valor de investimento na Virtus': 8000,
                '30% para reserva de emergência': 24000,
                '10% para custos de abertura': 8000,
                '20% para custos de tráfego': 16000,
                '15% para Treinamento Empresarial': 12000,
                '15% para infraestrutura': 12000,
            },
            '100mil': {
                'Valor em Patrimônio': 300000,
                '10% para o valor de investimento na Virtus': 10000,
                '30% para reserva de emergência': 30000,
                '10% para custos de abertura': 10000,
                '20% para custos de tráfego': 20000,
                '15% para Treinamento Empresarial': 15000,
                '15% para infraestrutura': 15000,
            }
        },
        'Intermediário': {
            '200mil': {
                'Valor em Patrimônio': 600000,
                '10% para o valor de investimento na Virtus': 20000,
                '30% para reserva de emergência': 60000,
                '10% para custos de abertura': 20000,
                '20% para custos de tráfego': 40000,
                '15% para Treinamento Empresarial': 30000,
                '15% para infraestrutura': 30000,
            },
            '400mil': {
                'Valor em Patrimônio': 1200000,
                '10% para o valor de investimento na Virtus': 40000,
                '30% para reserva de emergência': 120000,
                '10% para custos de abertura': 40000,
                '20% para custos de tráfego': 80000,
                '15% para Treinamento Empresarial': 60000,
                '15% para infraestrutura': 60000,
            },
            '600mil': {
                'Valor em Patrimônio': 1800000,
                '10% para o valor de investimento na Virtus': 60000,
                '30% para reserva de emergência': 180000,
                '10% para custos de abertura': 60000,
                '20% para custos de tráfego': 120000,
                '15% para Treinamento Empresarial': 90000,
                '15% para infraestrutura': 90000,
            },
            '800mil': {
                'Valor em Patrimônio': 2400000,
                '10% para o valor de investimento na Virtus': 80000,
                '30% para reserva de emergência': 240000,
                '10% para custos de abertura': 80000,
                '20% para custos de tráfego': 160000,
                '15% para Treinamento Empresarial': 120000,
                '15% para infraestrutura': 120000,
            },
            '1milhão': {
                'Valor em Patrimônio': 3000000,
                '10% para o valor de investimento na Virtus': 100000,
                '30% para reserva de emergência': 300000,
                '10% para custos de abertura': 100000,
                '20% para custos de tráfego': 200000,
                '15% para Treinamento Empresarial': 150000,
                '15% para infraestrutura': 150000,
            }
        },
        'Avançado': {
            '1milhão': {
                'Valor em Patrimônio': 3000000,
                '10% para o valor de investimento na Virtus': 100000,
                '30% para reserva de emergência': 300000,
                '10% para custos de abertura': 100000,
                '20% para custos de tráfego': 200000,
                '15% para Treinamento Empresarial': 150000,
                '15% para infraestrutura': 150000,
            }
        }
    }
    alocacao = alocacoes[investidor][capital]
    
    # Criar gráfico de pizza
    labels = list(alocacao.keys())[1:]  # Excluir 'Valor em Patrimônio'
    sizes = list(alocacao.values())[1:]  # Excluir 'Valor em Patrimônio'
    
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired(range(len(labels))))
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    return alocacao, fig

# Título da aplicação
st.title('Olá')

# Mensagem acolhedora e informativa
st.markdown(
    """
    **Bem-vindo à Virtus!**

    Aqui na Virtus, valorizamos profundamente a confiança que você deposita em nossa marca. Entendemos que ao investir conosco, você está em busca de uma oportunidade valiosa para criar ou alavancar um negócio. Queremos que você se sinta completamente confortável e bem-vindo, sabendo que está diante de uma grande chance de crescer.

    A Virtus se dedica a criar e otimizar negócios para empreendedores como você. Se você está começando um novo projeto ou buscando alavancar uma empresa existente, estamos aqui para oferecer suporte e expertise. Nosso objetivo é proporcionar o melhor para nossos clientes, criando negócios sólidos e marcas de sucesso.
    
    Para personalizar ainda mais sua jornada conosco, escolha as opções abaixo para adaptar a experiência conforme suas preferências e necessidades. 

    Após fazer suas seleções, você pode explorar mais sobre nossos serviços e iniciar seu empreendimento por meio dos links fornecidos. Abaixo, você encontrará botões para acessar o site oficial da Virtus e para iniciar seu processo de empreendedorismo.
    """
)

# Formulário para coleta de dados do cliente
st.subheader('Informações do Cliente')
nome = st.text_input('Nome:')
telefone = st.text_input('Telefone:')
email = st.text_input('Email:')

# Seleção do tipo de investidor
investidor = st.selectbox(
    'Selecione o tipo de investidor:',
    ['Inicial', 'Intermediário', 'Avançado']
)

# Níveis de capital para cada tipo de investidor
nivels_capital = {
    'Inicial': ['20mil', '40mil', '60mil', '80mil', '100mil'],
    'Intermediário': ['200mil', '400mil', '600mil', '800mil', '1milhão'],
    'Avançado': ['1milhão']
}

# Seleção do valor de investimento
capital = st.selectbox(
    'Selecione o valor de investimento:',
    nivels_capital[investidor]
)

# Mostrar alocação e gráfico baseado na seleção
if st.button('Gerar Relatório'):
    if nome and telefone and email:
        alocacao, fig = mostrar_alocacao_e_grafico(investidor, capital)
        
        st.subheader(f'Investimento com Capital de {capital}')
        st.write(f'**Valor em Patrimônio:** R$ {alocacao["Valor em Patrimônio"]:,.2f}')
        for chave, valor in alocacao.items():
            if chave != 'Valor em Patrimônio':
                st.write(f'**{chave}:** R$ {valor:,.2f}')

        st.subheader('Distribuição do Capital')
        st.pyplot(fig)
        
        # Salvar dados em arquivo
        caminho_pasta = 'Simulacoes'
        if not os.path.exists(caminho_pasta):
            os.makedirs(caminho_pasta)
        
        nome_arquivo = f"{nome.replace(' ', '_')}_{telefone.replace(' ', '_')}_{email.replace('@', '_').replace('.', '_')}.txt"
        caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
        
        with open(caminho_arquivo, 'w') as f:
            f.write(f"Nome: {nome}\n")
            f.write(f"Telefone: {telefone}\n")
            f.write(f"Email: {email}\n")
            f.write(f"Tipo de Investidor: {investidor}\n")
            f.write(f"Valor de Investimento: {capital}\n")
            for chave, valor in alocacao.items():
                f.write(f"{chave}: R$ {valor:,.2f}\n")
                
        st.success(
            "Teste realizado com sucesso! Vou dar uma olhada no seu perfil e te contatar em breve. Enquanto isso, conheça mais sobre nossos serviços e oportunidades em nosso site oficial: [Visite nosso site](https://perfildecliente-bx5se8ftwibx9xprerpcrd.streamlit.app)."
        )
    else:
        st.error("Por favor, preencha todos os campos obrigatórios (Nome, Telefone e Email) antes de gerar o relatório.")
