import os
import yt_dlp

def is_valid_youtube_url(url: str) -> bool:
    """
    Función auxiliar simple para verificar que la URL parece ser de YouTube.
    """
    return "youtube.com" in url or "youtu.be" in url

def download_video(url: str, output_folder: str) -> str:
    """
    Descarga el video desde YouTube a la carpeta indicada.
    Retorna la ruta completa del archivo descargado.
    Lanza excepciones específicas si ocurre algún error.
    """
    if not is_valid_youtube_url(url):
        raise ValueError("El enlace no parece ser de YouTube válido.")

    # Asegurarnos de que existe la carpeta
    os.makedirs(output_folder, exist_ok=True)

    # Configuración de youtube-dl (yt-dlp)
    # outtmpl define el patrón de nombre: 'output_folder/TituloVideo.mp4'
    outtmpl_pattern = os.path.join(output_folder, '%(title)s.%(ext)s')

    ydl_opts = {
        # Solicitamos video de max 720p con audio (incluso juntos o separados si hace falta merge)
        'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best', 
        'outtmpl': outtmpl_pattern,
        'quiet': True,           # Para que no sature la consola con texto
        'no_warnings': True      # Omitir warnings molestos
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extract_info=True baja el video y nos retorna la metadata
            info_dict = ydl.extract_info(url, download=True)
            
            # Recuperamos el nombre final del archivo generado por yt-dlp
            downloaded_file_path = ydl.prepare_filename(info_dict)
            
            return downloaded_file_path

    # === Manejo de Excepciones Comunes en Descargas === #
    except yt_dlp.utils.DownloadError as e:
        error_message = str(e).lower()
        
        # Filtramos por texto común en los errores de red/yt-dlp
        if "private video" in error_message or "sign in" in error_message:
            raise PermissionError("❌ El video es privado o requiere inicio de sesión.")
        elif "unavailable" in error_message or "404" in error_message:
            raise FileNotFoundError("❌ El video no está disponible o ha sido eliminado.")
        elif "name or service not known" in error_message or "network is unreachable" in error_message:
            raise ConnectionError("❌ Error de red: Verifica tu conexión a internet.")
        else:
            # Excepción general si es otro problema no contemplado
            raise RuntimeError(f"❌ Error al descargar: {str(e)}")
