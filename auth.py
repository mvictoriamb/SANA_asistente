import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar.readonly'
]

def autenticar_cuenta(nombre_cuenta, archivo_token):
    creds = None
    
    if os.path.exists(archivo_token):
        # print(f"[{nombre_cuenta}] Cargando token...") # SILENCIADO
        try:
            creds = Credentials.from_authorized_user_file(archivo_token, SCOPES)
        except Exception:
            # print(f"[{nombre_cuenta}] Token corrupto.") # SILENCIADO
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # print(f"[{nombre_cuenta}] Refrescando token...") # SILENCIADO
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        
        if not creds:
            print(f"\n>>> ⚠️ SE REQUIERE LOGIN PARA: {nombre_cuenta} <<<")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(archivo_token, 'w') as token:
            token.write(creds.to_json())

    return creds