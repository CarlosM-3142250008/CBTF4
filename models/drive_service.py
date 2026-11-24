import os
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# se usa drive completo para poder entrar a carpetas compartidas
SCOPES = ['https://www.googleapis.com/auth/drive']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')

# id de la carpeta raiz CBTF en google drive
CARPETA_RAIZ_ID = '18o8xOYT658ZUJJVI9KpkIoSLJgCKBYjm'


class DriveService:
    def __init__(self):
        self.service = self.authenticar()

    def authenticar(self):
        # revisa si ya existe el token guardado o abre el navegador para iniciar sesion
        creds = None
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())

        return build('drive', 'v3', credentials=creds)

    def obtener_o_crear_subcarpeta(self, nombre_carpeta):
        print(f"--> Buscando en carpeta raiz ID: [{CARPETA_RAIZ_ID}]")
        if not nombre_carpeta:
            return CARPETA_RAIZ_ID

        nombre_limpio = nombre_carpeta.replace("'", "\\'").strip()
        query = (
            f"name = '{nombre_limpio}' and "
            f"'{CARPETA_RAIZ_ID}' in parents and "
            f"mimeType = 'application/vnd.google-apps.folder' and "
            f"trashed = false"
        )
        resultados = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        archivos = resultados.get('files', [])

        if archivos:
            return archivos[0]['id']

        metadata_carpeta = {
            'name': nombre_carpeta.strip(),
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [CARPETA_RAIZ_ID]
        }
        carpeta = self.service.files().create(
            body=metadata_carpeta,
            fields='id',
            supportsAllDrives=True
        ).execute()
        return carpeta.get('id')

    def subir_archivo(self, ruta_local, nombre_academia=None):
        # sube el archivo a la carpeta de su academia y lo pone publico para lectura
        if not os.path.exists(ruta_local):
            return None

        try:
            carpeta_destino_id = self.obtener_o_crear_subcarpeta(nombre_academia)
            nombre_archivo = os.path.basename(ruta_local)

            metadata = {
                'name': nombre_archivo,
                'parents': [carpeta_destino_id]
            }
            media = MediaFileUpload(ruta_local, resumable=True)

            archivo = self.service.files().create(
                body=metadata,
                media_body=media,
                fields='id, webViewLink',
                supportsAllDrives=True
            ).execute()

            # permiso para que cualquier docente con el enlace lo pueda ver
            self.service.permissions().create(
                fileId=archivo.get('id'),
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()

            return archivo.get('webViewLink')

        except Exception as e:
            print(f"--> Error al subir archivo a Google Drive: {e}")
            return None

    def eliminar_archivo(self, enlace_drive):
        # saca el id del link de drive y borra el archivo de la nube
        if not enlace_drive or 'drive.google.com' not in enlace_drive:
            return

        match = re.search(r'/d/([a-zA-Z0-9_-]+)', enlace_drive)
        if not match:
            return

        file_id = match.group(1)
        try:
            self.service.files().delete(fileId=file_id).execute()
        except Exception as e:
            print(f"--> No se pudo eliminar el archivo en Google Drive ({file_id}): {e}")