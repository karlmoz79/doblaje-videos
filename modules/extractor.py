import os
from moviepy import VideoFileClip

def extract_audio(video_path: str, output_folder: str) -> str:
    """
    Extrae el audio de un archivo de video y lo guarda como .wav.
    Retorna la ruta del archivo de audio exportado.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"❌ No se encontró el video en la ruta: {video_path}")

    # Aseguramos la existencia de la carpeta destino
    os.makedirs(output_folder, exist_ok=True)
    
    # Construimos la ruta de salida, reemplazando la extensión original por .wav
    base_name = os.path.basename(video_path)
    name_without_ext = os.path.splitext(base_name)[0]
    audio_output_path = os.path.join(output_folder, f"{name_without_ext}.wav")
    
    try:
        # Cargamos el archivo a memoria
        video_clip = VideoFileClip(video_path)
        
        # Validación de seguridad: el video podría ser mudo
        if video_clip.audio is None:
            video_clip.close()
            raise ValueError("❌ El video no tiene ninguna pista de audio.")
            
        # Exportamos su componente de audio. 
        # Forzamos los parámetros 'pcm_s16le' a 16kHz (WAV lineal de 16-bits).
        # Esto es vital porque 'faster-whisper' requiere exactamente estos parámetros 
        # para escuchar el vocabulario correctamente en la Fase 5.
        video_clip.audio.write_audiofile(
            audio_output_path,
            fps=16000, 
            codec="pcm_s16le",
            logger=None # Evitar llenar la terminal de métricas de proceso
        )
        
        # Debemos cerrar el stream para liberar el archivo y prevenir que quede 'bloqueado' 
        # (.locked) por el sistema operativo posteriormente si queremos borrarlo o moverlo.
        video_clip.close()
        
        return audio_output_path
        
    except Exception as e:
        raise RuntimeError(f"❌ Error al intentar separar el audio: {str(e)}")
