import customtkinter as ctk
from tkinter import filedialog
import threading

# Configuración básica de CustomTkinter (modo y color)
ctk.set_appearance_mode("System")  # Soporta modo oscuro/claro del sistema
ctk.set_default_color_theme("blue")

class DoblajeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Ocultar carpetas y archivos ocultos en el filedialog nativo de Tkinter en Linux
        try:
            # 1. Forzar la carga silenciosa del módulo de Tcl 'tkfbox.tcl' enviando un argumento inválido
            self.tk.eval('catch {tk_getOpenFile -bogus}')
            # 2. Sobrescribir las variables por defecto del diálogo en memoria (que de otra forma lo muestran)
            self.tk.call('set', '::tk::dialog::file::showHiddenBtn', '1')
            self.tk.call('set', '::tk::dialog::file::showHiddenVar', '0')
        except Exception:
            pass

        # Configuración de la ventana principal
        self.title("Doblaje Automático de Videos")
        self.geometry("800x700")
        self.resizable(True, True)

        # Optimización para Linux: Evitar escalado fraccionario (1.1, 1.25)
        # Esto suele causar textos y bordes pixelados en monitores X11/Wayland.
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)
        ctk.set_appearance_mode("light")
        
        # Paleta de colores Premium Light
        ACCENT_COLOR = "#0ea5e9" # Azul cielo moderno
        HOVER_COLOR = "#0284c7"
        BG_COLOR = "#f4f4f5"     # Fondo principal claro
        FRAME_COLOR = "#ffffff"  # Fondo de la tarjeta central
        
        self.configure(fg_color=BG_COLOR)

        # Configuración de la grilla (para centrar elementos)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---------------------------------------------
        # 1. Marco Principal (Caja central estilo Web)
        # ---------------------------------------------
        self.main_frame = ctk.CTkFrame(self, fg_color=FRAME_COLOR, corner_radius=24, border_width=1, border_color="#27272a")
        self.main_frame.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(5, weight=1) # Para que el log ocupe el resto

        # Título y subtítulo
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Studio de Doblaje AI", 
            font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
            text_color="#18181b"
        )
        self.title_label.grid(row=0, column=0, padx=30, pady=(40, 5))
        
        self.subtitle_label = ctk.CTkLabel(
            self.main_frame, 
            text="Sube un video o pega un enlace de YouTube para comenzar el doblaje", 
            font=ctk.CTkFont(family="Inter", size=14),
            text_color="#52525b"
        )
        self.subtitle_label.grid(row=1, column=0, padx=30, pady=(0, 30))

        # ---------------------------------------------
        # 2. Área de Entradas (Inputs)
        # ---------------------------------------------
        self.input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, padx=50, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        self.file_button = ctk.CTkButton(
            self.input_frame, 
            text="📁 Explorar archivos multimedia...", 
            font=ctk.CTkFont(family="Inter", size=14, weight="normal"),
            fg_color="#e4e4e7",
            hover_color="#d4d4d8",
            text_color="#18181b",
            height=48,
            corner_radius=12,
            command=self.select_file
        )
        self.file_button.grid(row=0, column=0, pady=(0, 5), sticky="ew")

        self.file_path_label = ctk.CTkLabel(
            self.input_frame, 
            text="Ningún archivo seleccionado", 
            font=ctk.CTkFont(family="Inter", size=12),
            text_color="#71717a"
        )
        self.file_path_label.grid(row=1, column=0, pady=(0, 15))

        self.youtube_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="🔗 Pega el enlace de YouTube aquí...",
            font=ctk.CTkFont(family="Inter", size=14),
            height=48,
            corner_radius=12,
            border_width=1,
            border_color="#d4d4d8",
            fg_color="#ffffff",
            text_color="#18181b"
        )
        self.youtube_entry.grid(row=2, column=0, pady=10, sticky="ew")

        # ---------------------------------------------
        # 3. Acción Principal
        # ---------------------------------------------
        self.process_button = ctk.CTkButton(
            self.main_frame, 
            text="✨ Generar Doblaje", 
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"), 
            fg_color=ACCENT_COLOR, 
            hover_color=HOVER_COLOR,
            height=54,
            corner_radius=14,
            command=self.start_processing
        )
        self.process_button.grid(row=3, column=0, padx=50, pady=(20, 25), sticky="ew")

        # ---------------------------------------------
        # 4. Progreso y Logs
        # ---------------------------------------------
        self.progress_bar = ctk.CTkProgressBar(
            self.main_frame, 
            height=6,
            corner_radius=3,
            progress_color=ACCENT_COLOR,
            fg_color="#e4e4e7"
        )
        self.progress_bar.grid(row=4, column=0, padx=50, pady=(0, 15), sticky="ew")
        self.progress_bar.set(0)

        self.log_textbox = ctk.CTkTextbox(
            self.main_frame, 
            state="disabled",
            font=ctk.CTkFont(family="Fira Code", size=12), # Fuente monoespaciada para logs
            fg_color="#f8fafc",
            text_color="#3f3f46",
            border_width=1,
            border_color="#e4e4e7",
            corner_radius=12
        )
        self.log_textbox.grid(row=5, column=0, padx=50, pady=(0, 40), sticky="nsew")
        
        self.log_message("🚀 Sistema inicializado. Esperando video...")

        # Variables internas
        self.selected_file_path = ""
    def select_file(self):
        """Abre un diálogo del sistema nativo para seleccionar un archivo .mp4 o .srt"""
        file_path = filedialog.askopenfilename(
            initialdir="/home/karlmoz",
            title="Seleccionar multimedia",
            filetypes=[("Archivos de video y SRT", "*.mp4 *.mkv *.avi *.srt"), ("Video", "*.mp4 *.mkv *.avi"), ("Subtítulos SRT", "*.srt"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            self.selected_file_path = file_path
            self.file_path_label.configure(text=file_path, text_color="#18181b")
            # Limpiamos el campo de YouTube si elije algo local
            self.youtube_entry.delete(0, 'end') 
            self.log_message(f"Archivo seleccionado: {file_path}")

    def log_message(self, message: str):
        """Agrega un texto al final del log para dar retroalimentación del progreso al usuario"""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end") # Hace auto-scroll hacia abajo

    def start_processing(self):
        """Inicia el proceso general validando la entrada"""
        yt_link = self.youtube_entry.get().strip()

        # Regla de Negocio: Validar que existe o un archivo o un link antes de avanzar
        if not self.selected_file_path and not yt_link:
            self.log_message("❌ Error: Seleccione un archivo o ingrese un link de YouTube.")
            return

        # Deshabilitar los botones para evitar doble clic durante el trabajo
        self.process_button.configure(state="disabled")
        self.file_button.configure(state="disabled")
        self.youtube_entry.configure(state="disabled")
        self.progress_bar.set(0.1)
        
        self.log_message("⏳ Iniciando el proceso...")

        # Ejecutamos el pipeline principal en un hilo separado
        threading.Thread(target=self.run_pipeline, args=(yt_link,), daemon=True).start()

    def run_pipeline(self, yt_link: str):
        """Pipeline central que orquesta todos los módulos (ejecutado en hilo secundario)"""
        # Importación local para evitar la dependencia circular rígida en este archivo UI
        import os
        import shutil
        from modules.downloader import download_video
        from modules.extractor import extract_audio
        from modules.transcriber import transcribe_audio
        from modules.translator import translate_transcription
        from modules.tts import generate_speech
        from modules.srt_parser import parse_srt_to_json

        try:
            working_video_path = self.selected_file_path
            
            # Directorios de salida
            videos_dir = os.path.expanduser("~/Vídeos")
            docs_dir = os.path.expanduser("~/Documentos")
            os.makedirs(videos_dir, exist_ok=True)
            os.makedirs(docs_dir, exist_ok=True)
            
            # Directorio universal de trabajo temporal para todas las fases
            temp_dir = os.path.join(os.getcwd(), "temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            # FASE 3: Descarga de YouTube (si aplica)
            if not working_video_path and yt_link:
                self.log_message("⬇️ Iniciando descarga desde YouTube...")
                working_video_path = download_video(yt_link, videos_dir)
                nombre_archivo = os.path.basename(working_video_path)
                self.log_message(f"✅ Video descargado con éxito: {nombre_archivo}")
                self.progress_bar.set(0.15)
                
            is_srt = working_video_path and working_video_path.lower().endswith('.srt')
            base_name = os.path.splitext(os.path.basename(working_video_path))[0]
            
            if is_srt:
                self.log_message("📄 Archivo de subtítulos detectado. Omitiendo extracción de audio y transcripción...")
                transcription_path = parse_srt_to_json(working_video_path, temp_dir)
                self.log_message("✅ Subtítulos procesados para traducción.")
                self.progress_bar.set(0.5)
            else:
                # FASE 4: Extracción de Audio
                self.log_message("🎵 Extrayendo pista de audio del video...")
                audio_path = extract_audio(working_video_path, temp_dir)
                nombre_audio = os.path.basename(audio_path)
                self.log_message(f"✅ Audio preparado con éxito: {nombre_audio}")
                self.progress_bar.set(0.3)

                # FASE 5: Transcripción de Audio
                self.log_message("✍️ Transcribiendo audio (esto puede tomar varios minutos). Por favor espera...")
                transcription_path = transcribe_audio(audio_path, temp_dir, model_size="base")
                self.log_message("✅ Transcripción generada: transcription.json")
                self.progress_bar.set(0.5)

            # FASE 6: Traducción de Texto con Gemini
            self.log_message("🌐 Traduciendo transcripción al español usando Gemini...")
            translation_path = translate_transcription(transcription_path, temp_dir, target_language="español")
            self.log_message("✅ Traducción completada: translated.json")
            self.progress_bar.set(0.65)

            # FASE 7: Síntesis de voz (TTS)
            self.log_message("🗣️ Sintetizando doblaje de voz y respetando tiempos originales...")
            tts_audio_path = generate_speech(translation_path, temp_dir, voice='es-MX-DaliaNeural')
            
            final_audio_output = os.path.join(videos_dir, f"{base_name}_doblado.wav")
            shutil.copy2(tts_audio_path, final_audio_output)
            self.log_message(f"✅ Audio de doblaje sintetizado con éxito y guardado en: {final_audio_output}")
            self.progress_bar.set(0.85)

            # FASE 8: Copiar metadatos y finalizar sin mp4
            self.log_message("📂 Exportando archivos JSON de transcripción y traducción...")
            transcription_dest = os.path.join(docs_dir, f"{base_name}_transcription.json")
            translation_dest = os.path.join(docs_dir, f"{base_name}_translated.json")
            
            if 'transcription_path' in locals() and transcription_path and os.path.exists(transcription_path):
                shutil.copy2(transcription_path, transcription_dest)
            if 'translation_path' in locals() and translation_path and os.path.exists(translation_path):
                shutil.copy2(translation_path, translation_dest)

            self.log_message(f"🎉 ¡PROCESO FINALIZADO CON ÉXITO! Archivos de resultados guardados en {videos_dir} y {docs_dir}.")
            self.progress_bar.set(1.0)
        
        except ValueError as e:
            self.log_message(f"🚫 Entrada inválida: {str(e)}")
        except Exception as e:
            # Captura errores generales y controlados por nosotros (como FileNotFoundError)
            self.log_message(str(e))
        finally:
            # Restaurar controles de UI siempre, ocurra error o no
            self.reset_ui()

    def reset_ui(self):
        """Restaura los controles a su estado original después del procesamiento"""
        self.process_button.configure(state="normal")
        self.file_button.configure(state="normal")
        self.youtube_entry.configure(state="normal")
        self.progress_bar.set(0)
