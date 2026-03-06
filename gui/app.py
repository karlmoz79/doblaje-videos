import customtkinter as ctk
from tkinter import filedialog
import threading

# Configuración básica de CustomTkinter (modo y color)
ctk.set_appearance_mode("System")  # Soporta modo oscuro/claro del sistema
ctk.set_default_color_theme("blue")

class DoblajeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Doblaje Automático de Videos")
        self.geometry("700x520")
        self.resizable(False, False)

        # Configuración de la grilla (para centrar elementos)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---------------------------------------------
        # 1. Marco Principal
        # ---------------------------------------------
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Título dentro de la interfaz
        self.title_label = ctk.CTkLabel(self.main_frame, text="🎙️ App de Doblaje Automático", 
                                        font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=20)

        # ---------------------------------------------
        # 2. Área de selección local (.mp4)
        # ---------------------------------------------
        self.file_button = ctk.CTkButton(self.main_frame, text="📁 Seleccionar archivo .mp4", command=self.select_file)
        self.file_button.grid(row=1, column=0, padx=20, pady=10)

        self.file_path_label = ctk.CTkLabel(self.main_frame, text="Ningún archivo seleccionado", text_color="gray")
        self.file_path_label.grid(row=2, column=0, padx=20, pady=(0, 10))

        # ---------------------------------------------
        # 3. Separador 
        # ---------------------------------------------
        self.or_label = ctk.CTkLabel(self.main_frame, text="— O —", font=ctk.CTkFont(size=14))
        self.or_label.grid(row=3, column=0, pady=5)

        # ---------------------------------------------
        # 4. Campo de texto para Link remoto (YouTube)
        # ---------------------------------------------
        self.youtube_entry = ctk.CTkEntry(self.main_frame, placeholder_text="🔗 Ingresar link de YouTube", width=400)
        self.youtube_entry.grid(row=4, column=0, padx=20, pady=10)

        # ---------------------------------------------
        # 5. Acción Principal
        # ---------------------------------------------
        self.process_button = ctk.CTkButton(self.main_frame, text="▶️ Procesar", 
                                            font=ctk.CTkFont(size=16, weight="bold"), 
                                            fg_color="green", hover_color="darkgreen", 
                                            command=self.start_processing)
        self.process_button.grid(row=5, column=0, padx=20, pady=20)

        # ---------------------------------------------
        # 6. Progreso del estado (Loading y Logs)
        # ---------------------------------------------
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=400)
        self.progress_bar.grid(row=6, column=0, padx=20, pady=10)
        self.progress_bar.set(0) # Inicializar en vacío

        # Cuadro de texto para Logs
        self.log_textbox = ctk.CTkTextbox(self.main_frame, height=100, width=550, state="disabled")
        self.log_textbox.grid(row=7, column=0, padx=20, pady=10)
        
        self.log_message("✅ Interfaz lista. Esperando instrucción...")

        # Variable interna para saber si el usuario seleccionó un archivo físico
        self.selected_file_path = ""

    def select_file(self):
        """Abre un diálogo del sistema nativo para seleccionar un archivo .mp4"""
        file_path = filedialog.askopenfilename(
            initialdir="/home/karlmoz",
            title="Seleccionar video",
            filetypes=[("Archivos MP4", "*.mp4")]
        )
        if file_path:
            self.selected_file_path = file_path
            self.file_path_label.configure(text=file_path, text_color="white")
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
        from modules.downloader import download_video
        from modules.extractor import extract_audio
        from modules.transcriber import transcribe_audio
        from modules.translator import translate_transcription
        from modules.tts import generate_speech
        from modules.assembler import assemble_video

        try:
            working_video_path = self.selected_file_path
            
            # Directorio universal de trabajo temporal para todas las fases
            temp_dir = os.path.join(os.getcwd(), "temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            # FASE 3: Descarga de YouTube (si aplica)
            if not working_video_path and yt_link:
                self.log_message("⬇️ Iniciando descarga desde YouTube...")
                working_video_path = download_video(yt_link, temp_dir)
                nombre_archivo = os.path.basename(working_video_path)
                self.log_message(f"✅ Video descargado con éxito: {nombre_archivo}")
                self.progress_bar.set(0.15)

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
            tts_audio_path = generate_speech(translation_path, temp_dir, voice='es-ES-AlvaroNeural')
            self.log_message("✅ Audio de doblaje sintetizado con éxito!")
            self.progress_bar.set(0.85)

            # FASE 8: Ensamblado del Video (con mezcla de audio ffmpeg)
            self.log_message("🎬 Mezclando doblaje con video original en volumen atenuado...")
            final_output = os.path.join(os.getcwd(), "video_doblado_final.mp4")
            assemble_video(working_video_path, tts_audio_path, final_output)
            self.log_message(f"🎉 ¡PROCESO FINALIZADO CON ÉXITO! Video exportado a: {final_output}")
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
