import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')


class DriveService:
    def __init__(self):
        self.service = self.authenticar()
        
    def authenticar(self):
        creds = None
        if os.path.exists(TOKEN_PATH):
            creds= Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow= InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds= flow.run_local_server(port=0)
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
                
        return build('drive', 'v3', credentials=creds)
    
    def subir_archivo(self, ruta_local):
        if os.path.exists(ruta_local):
            try:
                nombre_archivo = os.path.basename(ruta_local)
                metadata = {'name': nombre_archivo}
                media = MediaFileUpload(ruta_local, resumable=True)
                
                archivo = self.service.files().create(body=metadata, media_body=media, fields='id,webViewLink').execute()
                self.service.permissions().create(fileId=archivo.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
                return archivo.get('webViewLink')
            
            except Exception as e:
                print(f"--> Error al subir archivo a Google Drive: {e}")
                return None