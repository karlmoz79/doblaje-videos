import customtkinter as ctk
from gui.app import DoblajeApp

# Import modules (to be implemented)
# from modules.downloader import download_video
# from modules.extractor import extract_audio
# from modules.transcriber import transcribe_audio
# from modules.translator import translate_text
# from modules.tts import generate_speech
# from modules.assembler import assemble_video

def main():
    print("Iniciando aplicación de Doblaje Automático...")
    
    # Setup de interfaz (Fase 2)
    app = DoblajeApp()
    app.mainloop()

if __name__ == "__main__":
    main()
