# Aplicación de Doblaje Automático de Video

Aplicación de escritorio en Python para procesar videos o subtítulos `.srt` y generar un doblaje en español usando un pipeline de IA. La interfaz está construida con `customtkinter` y el proyecto se gestiona exclusivamente con `uv`.

## Estado actual

El pipeline implementado hoy hace esto:

1. Acepta una URL de YouTube, un video local (`.mp4`, `.mkv`, `.avi`) o un archivo `.srt`.
2. Si la entrada es YouTube, descarga el video con `yt-dlp`.
3. Si la entrada es un video, extrae su audio con `moviepy`.
4. Si la entrada es un `.srt`, omite extracción y transcripción.
5. Transcribe con `faster-whisper` cuando aplica.
6. Traduce con Gemini usando `google-genai` y `Pydantic`.
7. Genera el doblaje con `edge-tts` y lo ensambla en una pista `.wav`.

Importante: en el estado actual de la app, la GUI exporta un audio doblado `.wav` y archivos JSON intermedios. El módulo `modules/assembler.py` existe, pero todavía no está conectado al flujo principal de la interfaz para producir un video final `.mp4`.

## Características actuales

- Entrada por URL de YouTube, video local o subtítulos `.srt`.
- Interfaz gráfica con `customtkinter`.
- Transcripción local con `faster-whisper`.
- Traducción estructurada con Gemini.
- Síntesis de voz con `edge-tts`.
- Alineación de segmentos con `pydub`.
- Manejo más robusto de errores temporales de Gemini:
  - Reintentos automáticos ante errores como `503 UNAVAILABLE`.
  - Espera progresiva entre intentos.
  - Fallback automático a otros modelos si `gemini-2.5-flash` sigue saturado.

## Requisitos

- Python `3.13+`
- `uv`
- `ffmpeg` disponible en el `PATH`
- Variable de entorno `GEMINI_API_KEY`

Ejemplo en Ubuntu/Debian:

```bash
sudo apt install ffmpeg
```

## Instalación

```bash
uv sync
```

Configura tu API key de Gemini:

```bash
export GEMINI_API_KEY="tu_clave_de_api_aqui"
```

También puedes usar un archivo `.env` en la raíz del proyecto.

## Ejecución

```bash
uv run python main.py
```

## Flujo de uso

1. Abre la aplicación.
2. Selecciona un archivo local o pega un enlace de YouTube.
3. Pulsa `Generar Doblaje`.
4. Revisa el progreso en el panel de logs.

## Salidas actuales

Cuando el proceso termina correctamente, la app genera:

- Un archivo de audio doblado `.wav` en `~/Vídeos`
- Un JSON de transcripción en `~/Documentos`
- Un JSON de traducción en `~/Documentos`

Los nombres se construyen con el nombre base del archivo de entrada:

- `mi_video_doblado.wav`
- `mi_video_transcription.json`
- `mi_video_translated.json`

## Estructura

```text
.
├── main.py
├── gui/
│   └── app.py
├── modules/
│   ├── assembler.py
│   ├── downloader.py
│   ├── extractor.py
│   ├── srt_parser.py
│   ├── transcriber.py
│   ├── translator.py
│   └── tts.py
├── pyproject.toml
└── README.md
```

## Módulos

- `gui/app.py`: interfaz y orquestación principal del pipeline.
- `modules/downloader.py`: descarga de videos desde YouTube.
- `modules/extractor.py`: extracción de audio desde video.
- `modules/transcriber.py`: transcripción con Whisper.
- `modules/srt_parser.py`: convierte `.srt` a JSON compatible con el pipeline.
- `modules/translator.py`: traducción con Gemini, schema validation, reintentos y fallback de modelo.
- `modules/tts.py`: generación de voz y ensamblado del audio doblado final.
- `modules/assembler.py`: mezcla de video + audio doblado, disponible pero no integrado todavía en la GUI.

## Notas

- La primera ejecución de `faster-whisper` puede tardar más porque descarga el modelo.
- La traducción depende de un servicio externo y puede fallar temporalmente por saturación.
- El proyecto usa `uv`; no se recomienda `pip`, `poetry` ni `conda` para este repositorio.
