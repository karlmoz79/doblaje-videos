# Aplicación de Doblaje Automático de Video 🎬

Una poderosa herramienta con interfaz gráfica (GUI) que automatiza por completo el proceso de doblar videos del inglés (u otros idiomas) al español. Esta aplicación extrae el audio, lo transcribe, lo traduce conservando sus marcas de tiempo originales, sintetiza una nueva voz y mezcla todo junto en un video final.

## Características ✨

1. **Soporte Universal de Entrada**: Proporciona el enlace de un video de YouTube, un archivo de video local (.mp4, .mkv, .avi) o directamente proporciona un archivo de subtítulos `.srt`.
2. **Extracción Automática**: Usa `ffmpeg` para desvincular el audio del video de forma eficiente.
3. **Transcripción Precisa**: Implementa `faster-whisper` para detectar y transcribir el idioma original generando un mapa estructurado de texto y tiempos (este paso se omite si provees un `.srt`).
4. **Traducción Inteligente**: Emplea el SDK oficial moderno `google-genai` de Gemini (Google) usando "Structured Outputs" para asegurar que la traducción se mantenga perfectamente ensamblada al formato de tiempos JSON.
5. **Generador de Voces (TTS)**: Utiliza `edge-tts` con voces neuronales (como *es-ES-AlvaroNeural*) para sintetizar fragmentos de voz de alta calidad adaptados a cada marca de tiempo y `pydub` para alinearlos milimétricamente.
6. **Ensamblado Profesional**: Mezcla el audio original atenuado junto a la nueva voz resaltada sobre el video inicial (o genera un archivo de audio final si usas `.srt`).
7. **Interfaz Moderna**: Cuenta con un panel sumamente atractivo y fluido construido con `customtkinter` (Premium Light Theme).

## Requisitos de Sistema ⚙️

- Sistema operativo **Linux / macOS / Windows**
- **FFmpeg** instalado globalmente en el sistema y accesible desde el PATH (`sudo apt install ffmpeg` en Ubuntu/Debian).
- **Python 3.10+** (Recomendamos encarecidamente la gestión mediante **`uv`**).

## Instalación y Configuración 🚀

La gestión del proyecto está hecha a través de `uv`. Sigue estos pasos para configurarlo:

1. **Instalar dependencias**:
```bash
uv sync # O simplemente uv add si necesitas añadir un paquete extra
```

2. **Configuración de la API Key (Gemini)**:
El servicio de traducción funciona mediante la Inteligencia Artificial de Google (Gemini). Antes de ejecutar el proyecto debes tener disponible la variable de entorno correspondiente:
```bash
export GEMINI_API_KEY="tu_clave_de_api_aqui"
```
*(Si lo prefieres, puedes usar python-dotenv y crear un archivo `.env` en la raíz del proyecto para alojar esta clave permanentemente)*.

## Uso 💻

Para iniciar la aplicación, simplemente ejecuta el archivo principal a través del ecosistema de `uv`:

```bash
uv run python main.py
```

1. **Ingreso:** Pega la URL del video de YouTube o usa el botón "Seleccionar Archivo" para abrir tu video local (.mp4, .mkv, .avi) o archivo de subtítulos (.srt).
2. **Proceso:** Presiona el botón "Iniciar Doblaje".
3. **Magia:** Observa los registros y la barra de progreso mientras la aplicación procesa las Fases automatizadas. Si provees un `.srt`, el sistema inteligentemente omitirá el uso intensivo de extracción de audio y transcripción saltando rápido a la etapa de traducción.
4. **Resultado:** Al concluir, tu archivo doblado aparecerá en el mismo directorio de entrada con el sufijo `_doblado` (por ejemplo: `mi_video_doblado.mp4` o `mi_audio_doblado.wav`).

## Estructura del Proyecto 📁

```
video_doblaje/
├── main.py              # Punto de entrada de la aplicación
├── README.md            # Este archivo
├── gui/
│   └── app.py           # Configuración de CustomTkinter y orquestación del flujo
└── modules/
    ├── downloader.py    # Gestión de descargas y procesamiento de YouTube (yt-dlp)
    ├── extractor.py     # Separación de canales de audio (ffmpeg)
    ├── srt_parser.py    # Parseador de subtítulos SRT locales saltando fases exhaustivas
    ├── transcriber.py   # Motor Whisper de inteligencia artificial off-line
    ├── translator.py    # Puente a Gemini API (google-genai) con Structured Outputs
    ├── tts.py           # Text-to-Speech neuronal y alineación (edge-tts + pydub)
    └── assembler.py     # Ensamblado del video final (ffmpeg mix audio overlay)
```

## Aclaraciones y Notas 📝

- Recuerda que la sincronía del video depende directamente de la calidad del motor de transcripción `faster-whisper`. Por defecto, está configurado para ejecutarse en modelo `base` con CPU para agilizar pruebas. Puedes ajustarlo a `small` o `medium` dentro de la llamada en `app.py` para mayor precisión de marcas temporales.
