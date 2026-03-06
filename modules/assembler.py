import os
import subprocess

def assemble_video(video_path: str, tts_audio_path: str, output_path: str) -> str:
    """
    Mezcla el video original con el audio sintetizado usando FFmpeg.
    Reduce el volumen del audio original y sobrepone el nuevo audio.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"❌ Video original no encontrado: {video_path}")
    if not os.path.exists(tts_audio_path):
        raise FileNotFoundError(f"❌ Audio sintetizado no encontrado: {tts_audio_path}")

    # Comando ffmpeg:
    # -i video_path (input 0)
    # -i tts_audio_path (input 1)
    # filter_complex: 
    #   [0:a]volume=0.15[a0] (Baja volumen original al 15%)
    #   [1:a]volume=1.5[a1] (Sube volumen del doblaje)
    #   [a0][a1]amix=inputs=2:duration=first:dropout_transition=3[a] (Mezcla ambos)
    # -map 0:v -map [a] (Usa el video original y el audio mezclado)
    
    command = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", tts_audio_path,
        "-filter_complex", "[0:a]volume=0.15[a0];[1:a]volume=1.5[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=3[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        output_path
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
        raise RuntimeError(f"❌ Error al empalmar el video con FFmpeg: {error_msg}")

    return output_path
