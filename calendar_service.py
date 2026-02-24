
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from auth import autenticar_cuenta

def obtener_agenda(cuentas):
    """
    Recorre tus cuentas y busca eventos para los próximos 10 DÍAS.
    """
    agenda_texto = []
    
    # Rango: Desde ahora hasta dentro de 10 días
    now = datetime.utcnow().isoformat() + 'Z'
    future = (datetime.utcnow() + timedelta(days=10)).isoformat() + 'Z'

    print("📅 Consultando agenda extendida...")

    for cuenta in cuentas:
        try:
            creds = autenticar_cuenta(cuenta["nombre"], cuenta["token"])
            if not creds: continue
            
            service = build('calendar', 'v3', credentials=creds)
            
            # Pedimos eventos
            events_result = service.events().list(
                calendarId='primary', 
                timeMin=now, 
                timeMax=future, # Rango ampliado
                maxResults=20,  # Más eventos
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])

            if events:
                agenda_texto.append(f"--- Calendario de {cuenta['nombre']} ---")
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    # Formato limpio de fecha y hora
                    # Ejemplo entrada: 2023-12-08T10:00:00 -> Salida: Viernes 08, 10:00
                    try:
                        dt_obj = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        dia_semana_nombres = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                        nombre_dia = dia_semana_nombres[dt_obj.weekday()]
                        fecha_str = f"{nombre_dia} {dt_obj.day}, {dt_obj.strftime('%H:%M')}"
                    except:
                        fecha_str = start # Fallback si falla el formato
                    
                    summary = event.get('summary', 'Sin título')
                    agenda_texto.append(f"[{fecha_str}] {summary}")
        
        except Exception as e:
            print(f"Error calendario {cuenta['nombre']}: {e}")
            
    return "\n".join(agenda_texto)