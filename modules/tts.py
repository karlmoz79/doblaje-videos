import os
import json
import asyncio
import edge_tts
import subprocess
from pydub import AudioSegment

async def _generate_audio(text: str, voice: str, path: str, rate: str = "+12%"):
    # Genera el habla con un ligero extra de velocidad asumiendo la mayor extensión del español
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(path)

def adjust_audio_tempo(input_path: str, output_path: str, tempo_ratio: float):
    """
    Ajusta la velocidad usando el filtro 'atempo' de FFmpeg 
    para NO DISTORSIONAR EL TONO DE LA VOZ y mantener profesionalidad.
    'atempo' permite valores nativos entre 0.5 y 100.0.
    """
    tempo_ratio = max(0.5, min(tempo_ratio, 2.0))
    command = [
        "ffmpeg", "-y", "-i", input_path,
        "-filter:a", f"atempo={tempo_ratio}",
        output_path
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def generate_speech(translated_json_path: str, output_folder: str, voice: str = 'es-MX-DaliaNeural') -> str:
    """
    Toma el archivo JSON traducido, genera el audio de cada segmento 
    y los empalma en una pista de audio unificada respetando los timestamps originales.
    Evita traslapes ajustando el tiempo de inicio de manera 'Profesional' sin mutar el pitch.
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
    
    # Encontramos la duración final usando el fin del último segmento transcrito
    last_end = max([float(seg.get("end", 0.0)) for seg in segments])
    
    base_audio = AudioSegment.silent(duration=int((last_end + 2) * 1000))

    for idx, seg in enumerate(segments):
        text = seg.get("text", "")
        start_ms = int(float(seg.get("start", 0.0)) * 1000)
        
        if idx + 1 < len(segments):
            next_start_ms = int(float(segments[idx+1].get("start", last_end)) * 1000)
        else:
            next_start_ms = int((last_end + 2) * 1000)
            
        available_time_ms = next_start_ms - start_ms
        
        if not text.strip():
            continue
            
        segment_path = os.path.join(temp_audio_dir, f"seg_{idx}.mp3")
        
        try:
            # 1. Base rate incrementado en el API para mayor naturalidad nativa
            asyncio.run(_generate_audio(text, voice, segment_path, rate="+10%"))
            
            if os.path.exists(segment_path):
                seg_audio = AudioSegment.from_file(segment_path)
                dur_audio_ms = len(seg_audio)
                
                # 2. Si todavía sobrepasa el espacio, Time-Stretching con FFmpeg (atempo)
                if dur_audio_ms > available_time_ms and available_time_ms > 0:
                    ratio = dur_audio_ms / float(available_time_ms)
                    
                    if ratio <= 1.40:
                        # Compresión preservando el tono ("pitch") del hablante
                        stretched_path = os.path.join(temp_audio_dir, f"stretched_{idx}.mp3")
                        adjust_audio_tempo(segment_path, stretched_path, ratio)
                        seg_audio = AudioSegment.from_file(stretched_path)
                    else:
                        # Si es demasiado largo reducimos a lo más rápido soportable sin sonar ridículo (1.40x)
                        # y usamos fade_out para recortar el resto sin clics bruscos.
                        stretched_path = os.path.join(temp_audio_dir, f"stretched_{idx}.mp3")
                        adjust_audio_tempo(segment_path, stretched_path, 1.40)
                        
                        seg_audio = AudioSegment.from_file(stretched_path)
                        if len(seg_audio) > available_time_ms:
                            fade_duration = min(150, available_time_ms)
                            seg_audio = seg_audio[:available_time_ms].fade_out(fade_duration)

                # 3. Superposición en la pista base de forma inmaculada
                base_audio = base_audio.overlay(seg_audio, position=start_ms)
                
        except Exception as e:
            print(f"Advertencia: No se pudo generar/superponer audio para segmento {idx}: {e}")

    final_audio_path = os.path.join(output_folder, "doblaje_sintetizado.wav")
    base_audio.export(final_audio_path, format="wav")
    
    return final_audio_path
