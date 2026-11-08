# **SANA: Smart Assistant & Notification Agent**

**Voz Natural** | **Gestión Unificada de Gmail** | **Agenda 10 Días** | **IA Gemini 2.5 Flash**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4?style=for-the-badge&logo=google-gemini&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](https://opensource.org/licenses/MIT)

## **Características Principales**

| **Módulo** | **Funcionalidad** |
|------------|-------------------|
| **Voz Realista** | Interacción auditiva fluida mediante Microsoft **Edge TTS**. |
| **IA Brain** | Resúmenes inteligentes de hilos de correo largos usando **Gemini**. |
| **Agenda 10D** | Consulta de eventos para los próximos 10 días de forma unificada. |
| **OAuth 2.0** | Autenticación segura y persistente por cuenta mediante tokens locales. |

## **Stack Técnico**

* **IA Generativa:** `google-generativeai` (Gemini 2.5 Flash) para análisis de texto.
* **Google APIs:** Integración con `google-api-python-client` para Gmail y Calendar.
* **Audio & Voz:** `edge-tts` para síntesis de voz y `SpeechRecognition` para captura de comandos.
* **Motor de Audio:** `pygame` para la reproducción fluida de respuestas.

## **Instalación y Configuración**

### 1. Requisitos Previos
* Tener instalado **Python 3.9** o superior.
* Crear un proyecto en **Google Cloud Console** con las APIs de Gmail y Calendar activadas.

### 2. Configuración del entorno
```bash
# 1. Clonar el repositorio
git clone https://github.com/mvictoriamb/SANA_asistente.git
cd SANA_asistente

# 2. Instalar dependencias
pip install -r requirements.txt
```

### 3. Credenciales y Seguridad
Crea un archivo *.env* basado en *.env.example* con tu GEMINI_API_KEY.
Descarga tu archivo *credentials.json* de **Google Cloud** y colócalo en la raíz.

### Ejemplos de comandos de voz
Una vez iniciado el script con python main.py, puedes interactuar con SANA:
"¿Qué tengo en la agenda?" 
"Dime si tengo correos nuevos de la UMA" 
"Léeme el último correo sobre ciberseguridad" 

## Seguridad y Privacidad
Este proyecto está diseñado siguiendo las mejores prácticas de seguridad:

### Gestión de Sesiones:
SANA utiliza OAuth 2.0 para acceso autorizado sin almacenar contraseñas.

### Tokens Temporales: 
Los tokens de acceso se generan localmente al primer inicio de sesión.

## Estructura del Proyecto
```plaintext
SANA-Assistant/
├── main.py             # Controlador principal y gestión de audio
├── ia_brain.py         # Lógica de IA y procesamiento de texto
├── calendar_service.py # Conector con Google Calendar API
├── auth.py             # Gestión de OAuth2 y tokens
├── requirements.txt    # Librerías necesarias
└── .gitignore          # Archivos excluidos del repositorio
```
