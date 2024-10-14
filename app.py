import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import os  # Adicionado para acessar variáveis de ambiente

def buscar_dados_da_api(codigo_usuario):
    # URL da primeira API
    url_primeira_api = f"http://177.85.161.176:6017/api/millenium/codigo_barras/busca_barra?barra={codigo_usuario}&$format=json"
    
    # Nome de usuário e senha vindos das variáveis de ambiente (secrets do Streamlit)
    usuario = os.getenv("API_USER")
    senha = os.getenv("API_PASSWORD")
    
    try:
        resposta_primeira_api = requests.get(url_primeira_api, auth=HTTPBasicAuth(usuario, senha))
        
        # Verifique o status da resposta
        if resposta_primeira_api.status_code == 200:
            try:
                dados = resposta_primeira_api.json()
                return dados
            except ValueError:
                st.error("Erro ao processar a resposta da primeira API como JSON.")
                return None
        else:
            st.error(f"Erro ao acessar a primeira API: {resposta_primeira_api.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão com a primeira API: {e}")
        return None

def reset_input():
    # Função para limpar o campo de entrada e os dados do produto
    st.session_state['codigo_usuario'] = ''
    st.session_state['dados_produto'] = None

def main():
    st.title("Consulta de Preços")

    # Inicializar o estado da sessão se ainda não existir
    if 'codigo_usuario' not in st.session_state:
        st.session_state['codigo_usuario'] = ''
    if 'dados_produto' not in st.session_state:
        st.session_state['dados_produto'] = None

    # Solicitando o código do usuário
    # Use o argumento 'key' para associar o widget com 'codigo_usuario'
    codigo_usuario = st.text_input("Insira o código de barras:", key='codigo_usuario')

    # Botão "Buscar"
    if st.button("Buscar"):
        if st.session_state['codigo_usuario']:
            codigo_usuario = st.session_state['codigo_usuario']
            # Buscando dados da API
            dados = buscar_dados_da_api(codigo_usuario)
            if dados:
                # Verificar se "value" não está vazio
                value_list = dados.get("value", [])
                if value_list:
                    # Extraindo o valor da tag "produto"
                    produto = value_list[0].get("produto")
                    
                    if produto:
                        # URL da segunda API
                        url_segunda_api = f"http://177.85.161.176:6017/api/millenium_eco/produtos/precodetabela?produto={produto}&vitrine=201&$format=json"
                        
                        # Nome de usuário e senha vindos das variáveis de ambiente
                        usuario = os.getenv("API_USER")
                        senha = os.getenv("API_PASSWORD")

                        try:
                            # Fazendo a requisição GET para a segunda API
                            resposta_segunda_api = requests.get(url_segunda_api, auth=HTTPBasicAuth(usuario, senha))
                            
                            if resposta_segunda_api.status_code == 200:
                                dados_produto = resposta_segunda_api.json()
                                
                                # Armazenar os dados do produto no estado da sessão
                                st.session_state['dados_produto'] = dados_produto
                            else:
                                st.error(f"Erro ao acessar a segunda API: {resposta_segunda_api.status_code}")
                        except requests.exceptions.RequestException as e:
                            st.error(f"Erro de conexão com a segunda API: {e}")
                    else:
                        st.warning("Produto não encontrado na resposta da API.")
                else:
                    st.warning("Código de barras não encontrado.")
            else:
                st.error("Não foi possível obter os dados.")
        else:
            st.error("Por favor, insira o código de barras.")

    # Exibir os dados do produto se disponíveis
    if st.session_state.get('dados_produto'):
        dados_produto = st.session_state['dados_produto']
        codigo_usuario = st.session_state['codigo_usuario']

        # Verificar se a lista de produtos está vazia
        if not dados_produto.get("value", []):
            st.warning("Produto não cadastrado na vitrine.")
        else:
            st.success(f"Os valores do produto {codigo_usuario} são:")
            
            # Iterando sobre cada item na lista de produtos
            for item in dados_produto.get("value", []):
                tamanho = item.get("tamanho", "Tamanho não disponível")
                preco1 = item.get("preco1", "Preço não disponível")
                # Formatar o preço com "R$"
                preco_formatado = f"R$ {preco1}" if preco1 != "Preço não disponível" else preco1
                st.write(f"Tamanho: {tamanho}, Preço: {preco_formatado}")

        # Botão "Limpar" com callback, exibido apenas após a busca
        st.button("Limpar", on_click=reset_input)

if __name__ == "__main__":
    main()
