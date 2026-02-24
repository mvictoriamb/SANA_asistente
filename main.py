import speech_recognition as sr
import os
import edge_tts  
import asyncio   
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import base64
import time
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from auth import autenticar_cuenta
from ia_brain import (analizar_correos_con_gemini, seleccionar_correo_por_voz, 
                      limpiar_cuerpo_para_voz, generar_resumen_dia)
from calendar_service import obtener_agenda

# --- CONFIGURACIÓN DE AUDIO (EDGE TTS) ---
# Opciones de voz: "es-ES-AlvaroNeural" (Hombre), "es-ES-ElviraNeural" (Mujer)
VOZ = "es-ES-ElviraNeural"
VELOCIDAD = "+25%" 

async def generar_audio_edge(texto, archivo_salida):
    """Genera el archivo de audio usando el motor de Microsoft Edge"""
    communicate = edge_tts.Communicate(texto, VOZ, rate=VELOCIDAD)
    await communicate.save(archivo_salida)

def hablar(texto):
    """
    Función síncrona que llama al motor asíncrono de Edge,
    reproduce el audio con Pygame y borra el archivo.
    """
    if not texto or not texto.strip(): return

    print(f"🤖 SANA: {texto}")
    
    # Limpieza básica
    texto_limpio = texto.replace("*", "").replace("#", "").replace("_", "")
    archivo_temporal = "temp_voz.mp3"

    try:
        # 1. Generar audio (Ejecutamos la función async dentro de este código normal)
        asyncio.run(generar_audio_edge(texto_limpio, archivo_temporal))
        
        # 2. Reproducir con Pygame
        pygame.mixer.init()
        try:
            pygame.mixer.music.load(archivo_temporal)
            pygame.mixer.music.play()
            
            # Esperar a que termine (con un pequeño sleep para no saturar CPU)
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
        except pygame.error as e:
            print(f"Error reproduciendo audio: {e}")
        finally:
            pygame.mixer.quit() # Importante: liberar el archivo para poder borrarlo
        
        # 3. Borrar archivo
        if os.path.exists(archivo_temporal):
            try:
                os.remove(archivo_temporal)
            except PermissionError:
                pass # A veces Windows tarda en soltar el archivo, no pasa nada
            
    except Exception as e:
        print(f"Error en el sistema de voz: {e}")

# --- TUS CUENTAS ---
CUENTAS = [
    {"nombre": "Personal", "token": "token_personal.json"},
    {"nombre": "UMA", "token": "token_uma.json"},
    {"nombre": "Secundaria", "token": "token_tercero.json"}
]

# --- FUNCIONES TÉCNICAS (GMAIL) ---
def limpiar_html(html_content):
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text(separator='. ')
        return ' '.join(text.split())
    except: return html_content

def decodificar_cuerpo(payload):
    texto_plano, texto_html = "", ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if part['body'].get('data'):
                    texto_plano += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif part['mimeType'] == 'text/html':
                if part['body'].get('data'):
                    texto_html += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    else:
        data = payload['body'].get('data')
        if data:
            decoded = base64.urlsafe_b64decode(data).decode('utf-8')
            if payload.get('mimeType') == 'text/html': texto_html = decoded
            else: texto_plano = decoded
    
    if texto_html: return limpiar_html(texto_html)
    return texto_plano

def obtener_cuerpo_mensaje(service, msg_id):
    try:
        mensaje = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        return decodificar_cuerpo(mensaje.get('payload', {}))
    except Exception: return ""

def obtener_lista_correos():
    buzon = [] 
    for cuenta in CUENTAS:
        try:
            creds = autenticar_cuenta(cuenta["nombre"], cuenta["token"])
            if not creds: continue
            service = build('gmail', 'v1', credentials=creds)
            results = service.users().messages().list(userId='me', q='is:inbox is:unread', maxResults=5).execute()
            mensajes = results.get('messages', [])
            for msg in mensajes:
                det = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
                headers = det['payload']['headers']
                buzon.append({
                    "id": msg['id'], 
                    "cuenta": cuenta["nombre"], 
                    "service": service,
                    "remitente": next((h['value'] for h in headers if h['name'] == 'From'), "Desconocido"),
                    "asunto": next((h['value'] for h in headers if h['name'] == 'Subject'), "Sin asunto"),
                    "snippet": det.get('snippet', '')
                })
        except: pass
    return buzon

# --- MICROFONO ---
def escuchar_microfono(tiempo_espera=5):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"\n🎤 ...") 
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=tiempo_espera, phrase_time_limit=tiempo_espera)
            return r.recognize_google(audio, language="es-ES").lower()
        except sr.WaitTimeoutError: return ""
        except Exception: return "RUIDO" 

# --- MODOS ---
def modo_resumen_dia():
    hablar("Dame un segundo, estoy recopilando tu información.")
    agenda = obtener_agenda(CUENTAS)
    lista = obtener_lista_correos()
    datos_ia = [{"de": m["remitente"], "asunto": m["asunto"]} for m in lista]
    informe = generar_resumen_dia(agenda, str(datos_ia))
    hablar(informe)

def modo_solo_correo():
    hablar("Revisando tus bandejas.")
    lista_correos = obtener_lista_correos()
    
    if not lista_correos:
        hablar("Todo limpio. No tienes correos nuevos.")
        return

    hablar("Analizando contenido...")
    resumen = analizar_correos_con_gemini(lista_correos)
    
    if "Error" in resumen:
        hablar("Problema técnico con la IA.")
        return

    hablar(resumen)

    hablar("¿Quieres que te lea alguno o prefieres un resumen de todos?")
    respuesta = escuchar_microfono(6)

    if respuesta and respuesta != "RUIDO" and "no" not in respuesta:
        decision = seleccionar_correo_por_voz(lista_correos, respuesta)
        
        if decision == "ALL":
            hablar(f"Resumen rápido de {len(lista_correos)} correos.")
            for i, correo in enumerate(lista_correos, 1):
                nombre = correo['remitente'].split('<')[0].replace('"', '')
                # Leemos todo junto
                hablar(f"Correo {i} de {nombre}. {correo['asunto']}. {correo['snippet']}")
            hablar("Eso es todo.")

        elif decision != "NONE":
            obj = next((m for m in lista_correos if m["id"] == decision), None)
            if obj:
                hablar(f"Abriendo mensaje de {obj['remitente']}...")
                cuerpo = obtener_cuerpo_mensaje(obj['service'], decision)
                cuerpo_limpio = limpiar_cuerpo_para_voz(cuerpo)
                hablar("Dice lo siguiente:")
                hablar(cuerpo_limpio)
                hablar("Fin del mensaje.")
            else:
                hablar("No encuentro ese correo.")
        else:
            hablar("No te he entendido bien.")
    else:
        hablar("De acuerdo.")

# --- CONTROLADOR ---
def procesar_orden(comando):
    if any(x in comando for x in ["calendario", "agenda", "actividad", "resumen"]):
        modo_resumen_dia()
        return True
    elif any(x in comando for x in ["correo", "buzón", "bandeja", "email"]):
        modo_solo_correo()
        return True
    elif any(x in comando for x in ["apaga", "salir", "adiós", "nada"]):
        return "EXIT"
    return False

def main():
    primera_vez = True
    while True:
        if primera_vez:
            hablar("¡Buenos días! Soy SANA, tu asistente virtual. ¿Qué necesitas hoy?")
            primera_vez = False
        else:
            hablar("¿Necesitas algo más?")
        
        comando = escuchar_microfono(8)
        
        if not comando:
            hablar("Hasta luego.")
            break 

        resultado = procesar_orden(comando)

        if resultado == "EXIT":
            hablar("¡Adiós!")
            break
        
        elif resultado == True:
            continue 
        
        else:
            hablar("No entendí. ¿Puedes repetir?")
            comando_retry = escuchar_microfono(6)
            
            if not comando_retry:
                hablar("Hasta luego.")
                break
                
            resultado_retry = procesar_orden(comando_retry)
            if resultado_retry == "EXIT" or not resultado_retry:
                hablar("¡Adiós!")
                break

if __name__ == '__main__':
    main()