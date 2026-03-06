import os
import json
import asyncio
import edge_tts
from pydub import AudioSegment

async def _generate_audio(text: str, voice: str, path: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(path)

def generate_speech(translated_json_path: str, output_folder: str, voice: str = 'es-ES-AlvaroNeural') -> str:
    """
    Toma el archivo JSON traducido, genera el audio de cada segmento 
    y los empalma en una pista de audio unificada respetando los timestamps originales.
    """
    if not os.path.exists(translated_json_path):
        raise FileNotFoundError(f"❌ No se encontró el JSON traducido en: {translated_json_path}")
        
    with open(translated_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    segments = data.get("segments", [])
    if not segments:
        raise ValueError("❌ El JSON traducido no contiene segmentos para sintetizar.")

    temp_audio_dir = os.path.join(output_folder, "temp_tts")
    os.makedirs(temp_audio_dir, exist_ok=True)
    
    # Encontramos la duración final del video usando el fin del último segmento transcrito
    last_end = max([float(seg.get("end", 0.0)) for seg in segments])
    
    # Silencio base con un pequeño margen final
    base_audio = AudioSegment.silent(duration=int((last_end + 2) * 1000))

    for idx, seg in enumerate(segments):
        text = seg.get("text", "")
        start_ms = int(float(seg.get("start", 0.0)) * 1000)
        
        if not text.strip():
            continue
            
        segment_path = os.path.join(temp_audio_dir, f"seg_{idx}.mp3")
        
        try:
            # Sintetizamos la voz
            asyncio.run(_generate_audio(text, voice, segment_path))
            
            # Cargamos el archivo usando pydub y lo superponemos
            if os.path.exists(segment_path):
                seg_audio = AudioSegment.from_file(segment_path)
                base_audio = base_audio.overlay(seg_audio, position=start_ms)
        except Exception as e:
            print(f"Advertencia: No se pudo generar/superponer audio para segmento {idx}: {e}")

    final_audio_path = os.path.join(output_folder, "doblaje_sintetizado.wav")
    base_audio.export(final_audio_path, format="wav")
    
    return final_audio_path
