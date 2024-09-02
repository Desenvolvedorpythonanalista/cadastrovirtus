import streamlit as st
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os

def authenticate_google_drive():
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    creds = None
    # Verifique se o arquivo token.json existe
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Se não houver credenciais ou se forem inválidas, faça a autenticação novamente
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use o caminho correto para seu arquivo client_secret
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_297185839442-0m4p4sbfbodbqsk816ca3q0o14phbk5u.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Salve as credenciais para futuras execuções
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def upload_file_to_drive(service, file_path, folder_id=None):
    file_metadata = {'name': os.path.basename(file_path)}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

st.title("Upload de Arquivo para o Google Drive")

# Faça o upload do arquivo
uploaded_file = st.file_uploader("Escolha um arquivo", type=["jpg", "png", "pdf", "txt"])

if uploaded_file is not None:
    # Crie um arquivo temporário para o upload
    temp_file_path = "temp_file_" + uploaded_file.name
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    st.write("Arquivo selecionado: ", uploaded_file.name)
    
    if st.button("Fazer Upload para o Google Drive"):
        service = authenticate_google_drive()
        folder_id = '13X_YJqvB3jGdOxCCIrNzt5vi8UwtWNlE'  # ID da pasta do Google Drive onde o arquivo será salvo
        file_id = upload_file_to_drive(service, temp_file_path, folder_id)
        st.success(f"Arquivo carregado com sucesso! ID do arquivo no Drive: {file_id}")
        
        # Limpe o arquivo temporário após o upload
        os.remove(temp_file_path)
