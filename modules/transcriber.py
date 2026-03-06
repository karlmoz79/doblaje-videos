import os
import json
from faster_whisper import WhisperModel

def transcribe_audio(audio_path: str, output_folder: str, model_size: str = "base") -> str:
    """
    Transcribe el audio utilizando Faster-Whisper.
    Guarda los segmentos en un archivo JSON en la carpeta indicada.
    Retorna la ruta absoluta del archivo JSON de salida.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"❌ No se encontró el audio en la ruta: {audio_path}")
        
    os.makedirs(output_folder, exist_ok=True)
    json_output_path = os.path.join(output_folder, "transcription.json")
    
    try:
        # Cargamos el modelo (descargará automáticamente la primera vez).
        # compute_type="int8" reduce el uso de RAM/VRAM para entornos sin GPU (corre en CPU).
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
        # Inicia la transcripción. 
        # language=None hará que el modelo autodetecte el idioma del audio original.
        segments, info = model.transcribe(audio_path, beam_size=5)
        
        # Preparamos la estructura del archivo JSON final
        transcription_data = {
            "source_language": info.language,
            "language_probability": info.language_probability,
            "segments": []
        }
        
        # 'segments' es un generador: al iterar sobre él se va transcribiendo el audio pedazo a pedazo
        for segment in segments:
            segment_dict = {
                "id": segment.id,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            }
            transcription_data["segments"].append(segment_dict)
            
        # Volcamos todo en el fichero 'transcription.json'
        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump(transcription_data, f, indent=4, ensure_ascii=False)
            
        return json_output_path
        
    except Exception as e:
        raise RuntimeError(f"❌ Error durante la transcripción: {str(e)}")
