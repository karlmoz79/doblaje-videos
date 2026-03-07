# 🤖 Guía para Agentes de IA (AGENTS.md)

¡Hola, colega IA! Este documento contiene el contexto, las reglas arquitectónicas y las directrices principales de este repositorio. Si eres un asistente de programación (como Claude, GitHub Copilot, Cursor, etc.) leyendo este archivo, **debes seguir estrictamente estas reglas** antes de proponer cambios o crear nuevas funcionalidades.

## 🎯 Contexto del Proyecto

Esta es una aplicación de escritorio de **Doblaje Automático de Video** (Video Dubbing) escrita en Python. Su principal propósito es tomar un video (o un archivo local de subtítulos SRT) en un idioma origen (por ejemplo, Inglés), transcribir su audio si es necesario, traducirlo estructuradamente a otro idioma (Español) conservando milimétricamente las marcas de tiempo (timestamps), sintetizar nueva voz y mezclarla encima del video original.

## 🛠️ Stack Tecnológico y Reglas Generales

1. **Gestor de Paquetes y Entorno Virtual**: **Exclusivamente `uv`**.
   - No uses `pip`, `poetry` ni `conda`.
   - Para añadir dependencias usa: `uv add <paquete>`.
   - Para ejecutar scripts usa: `uv run python <script.py>`.
2. **Interfaz Gráfica (GUI)**: Se utiliza `customtkinter`. Todo código visual debe ser moderno, responsivo y orientado a un "Premium Light Theme" combinando grises claros y blancos neutros.
3. **Versión de Python**: `3.13+`. Ten en cuenta que en Python 3.13 algunos módulos antiguos (como `audioop`) fueron removidos del núcleo estándar; por esta razón inyectamos `audioop-lts` para dar compatibilidad a dependencias del ecosistema del audio (como `pydub`).

## 🧠 Modelos de IA Internos (Agentes Embebidos)

El proyecto funciona usando un patrón de agentes en cadena o *pipeline* de IAs. Ténlo presente al modificar los módulos:

1. **Whisper (Agent Transcriptor)** -> `modules/transcriber.py`
   - **Librería**: `faster-whisper`.
   - **Misión**: Extraer texto y marcas de tiempo precisas (`start`, `end`, `text`).
   - El entorno por defecto corre en CPU (`model="base"`) para compatibilidad universal, con la posibilidad de escalar a modelos pesados si el entorno tiene VRAM.

2. **Gemini (Agent Traductor)** -> `modules/translator.py`
   - **Librería**: `google-genai` (Maneja variables de entorno `GEMINI_API_KEY`).
   - **Misión**: Traducir transcripciones manteniendo la estructura de datos intacta. Usa _Structured Outputs_ y `Pydantic` de manera obligatoria para retornar siempre una lista perfecta de JSON que el subsiguiente agente pueda leer sin parseos extraños.

3. **Edge-TTS (Agent Locutor)** -> `modules/tts.py`
   - **Librería**: `edge-tts`.
   - **Misión**: Generar audios segmentados (`.mp3`) para cada oración traducida. Luego, ensamblarlos sobre un "silencio" del largo original del video usando `pydub`, calzando perfectamente cada _start timestamp_.

## 📂 Arquitectura (El Pipeline)

Las fases completas del pipeline se orquestan centralmente en la GUI principal `gui/app.py`. Si el usuario provee un `.srt`, los pasos 1, 2 y 3 se omiten por completo, entrando en el `srt_parser.py`:
1. `downloader.py`: Descarga el video desde YouTube (si es URL vía `yt-dlp`).
2. `extractor.py`: Separador del flujo video/audio (`ffmpeg`).
3. `transcriber.py`: Transcripción de IA (`faster-whisper`).
4. `srt_parser.py`: Parseo y estructuración de archivos `.srt` nativamente a formato JSON del _Pipeline_.
5. `translator.py`: Traducción LLM (`google-genai`).
6. `tts.py`: Audio neuronal emparejado (`edge-tts` + `pydub`).
7. `assembler.py`: Mezclador del video final atenuando los sonidos originales (`ffmpeg`).

## 🛑 Directrices Clave para Modificaciones de Código

- **No bloquees el MainThread**: La interfaz visual se congela irremediablemente si el trabajo de cómputo denso (IA, Descargas, Parseos) reside en el hilo principal. Usa `threading.Thread(target=tun_pipeline)` como está implementado hoy, para mantener el `mainloop()` de CustomTkinter fluido.
- **Rutas Relativas al Workspace**: Siempre usa la carpeta temporal universal (`os.path.join(os.getcwd(), "temp")`) para todas las fases, y deja el resultado final en el directorio de entrada. Recuerda que todos los outputs de éxito deben llevar el sufijo `{base_name}_doblado` de forma dinámica conservando su extensión.
- **Registro Centralizado**: Usa `self.log_message(msg)` (definido en la clase principal App) para reportar estados e interactuar con el usuario. Las invocaciones `print()` de sistema en crudo se pierden en la GUI.
- **Resiliencia Modular**: Si alteras las salidas de un módulo, recuerda que el siguiente paso del pipeline espera exactamente el contrato de entrada previo. Por ejemplo, el `translator.py` expulsa un JSON y el `tts.py` depende 100% de la key `start` en él.
