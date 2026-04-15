import os
import json
import time
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

class TranslatedSegment(BaseModel):
    id: int
    start: float
    end: float
    text: str

class TranslationResponse(BaseModel):
    segments: list[TranslatedSegment]


PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
]
MAX_RETRIES_PER_MODEL = 3
BASE_RETRY_DELAY_SECONDS = 3


def _is_retryable_gemini_error(error: Exception) -> bool:
    error_text = str(error).lower()
    retryable_markers = (
        "503",
        "unavailable",
        "high demand",
        "temporarily unavailable",
        "resource exhausted",
        "deadline exceeded",
        "timeout",
    )
    return any(marker in error_text for marker in retryable_markers)

def translate_transcription(json_path: str, output_folder: str, target_language: str = "español") -> str:
    """
    Toma el archivo JSON de la transcripción y traduce sus segmentos al idioma objetivo 
    usando la nueva API de Google Gemini (gemini-2.5-flash).
    """
    # Cargamos el archivo .env si existe en el entorno
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("❌ No se encontró GEMINI_API_KEY. Configúrala en un archivo .env en la raíz del proyecto.")
        
    client = genai.Client(api_key=api_key)
    
    # 1. Leemos el archivo JSON original
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"❌ No se encontró la transcripción en: {json_path}")
        
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    segments = data.get("segments", [])
    if not segments:
        raise ValueError("❌ El archivo de transcripción no contiene segmentos analizables.")
    
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "translated.json")
    
    # 2. Preparamos el Prompt
    prompt = f"""
    Eres un traductor profesional experto en doblaje audiovisual. 
    Traduce los 'text' de los siguientes segmentos JSON del idioma original a {target_language}.
    Intenta que la longitud de la traducción no difiera drásticamente de la original, manteniendo el sentido.
    
    DEBES devolver EXACTAMENTE la misma estructura de array de objetos original, pero con la traducción en su lugar.
    Mantén intactos los campos 'id', 'start', 'end'. Responde SOLAMENTE con el JSON plano de los segmentos.
    
    TEXTO ORIGINAL:
    {json.dumps(segments, ensure_ascii=False, indent=2)}
    """
    
    # 3. Llamada al modelo con reintentos y fallback para errores temporales del servicio.
    translated_segments = None
    attempted_models = []
    last_error = None

    for model_name in [PRIMARY_MODEL, *FALLBACK_MODELS]:
        attempted_models.append(model_name)

        for attempt in range(1, MAX_RETRIES_PER_MODEL + 1):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={
                        'response_mime_type': 'application/json',
                        'response_schema': TranslationResponse,
                    },
                )
                # Gemini responderá con un string JSON que cumple el esquema.
                response_json = json.loads(response.text)
                translated_segments = response_json.get("segments", [])
                break
            except Exception as e:
                last_error = e

                if not _is_retryable_gemini_error(e):
                    raise RuntimeError(
                        f"❌ Error al comunicarse con Gemini o leyendo el JSON resultante: {str(e)}"
                    ) from e

                if attempt < MAX_RETRIES_PER_MODEL:
                    delay_seconds = BASE_RETRY_DELAY_SECONDS * attempt
                    time.sleep(delay_seconds)
                    continue

        if translated_segments is not None:
            break

    if translated_segments is None:
        attempted_models_text = ", ".join(attempted_models)
        raise RuntimeError(
            "❌ Gemini no estuvo disponible tras varios reintentos. "
            f"Modelos probados: {attempted_models_text}. Último error: {last_error}"
        )
        
    translated_data = {
        "source_language": data.get("source_language", "auto"),
        "target_language": target_language,
        "segments": translated_segments
    }
    
    # 4. Volcamos la información en el fichero traducido
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(translated_data, f, indent=4, ensure_ascii=False)
        
    return output_path
