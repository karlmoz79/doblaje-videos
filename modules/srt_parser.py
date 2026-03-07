import codecs
import json
import os
from typing import Dict, Any, List

def parse_time(time_str: str) -> float:
    """Converts SRT time format (00:00:00,000) to seconds as a float."""
    time_str = time_str.replace(',', '.')
    parts = time_str.split(':')
    if len(parts) == 3:
        h, m, s = parts
        return float(h) * 3600 + float(m) * 60 + float(s)
    return 0.0

def parse_srt_to_json(srt_path: str, output_dir: str) -> str:
    """
    Parses an SRT file and converts it to a translation-ready JSON structure.
    Saves the JSON to output_dir/transcription.json and returns the path.
    """
    if not os.path.exists(srt_path):
        raise FileNotFoundError(f"❌ Archivo SRT no encontrado: {srt_path}")
        
    with codecs.open(srt_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    segments: List[Dict[str, Any]] = []
    current_segment: Dict[str, Any] = {}
    current_text: List[str] = []
    
    state = "index"  # states: index, time, text
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_segment and current_text:
                current_segment["text"] = " ".join(current_text)
                segments.append(current_segment)
            current_segment = {}
            current_text = []
            state = "index"
            continue
            
        if state == "index":
            if line.isdigit():
                state = "time"
            else:
                # Fallback if malformed
                if "-->" in line:
                    times = line.split("-->")
                    current_segment["start"] = parse_time(times[0].strip())
                    current_segment["end"] = parse_time(times[1].strip())
                    state = "text"
        elif state == "time":
            if "-->" in line:
                times = line.split("-->")
                current_segment["start"] = parse_time(times[0].strip())
                current_segment["end"] = parse_time(times[1].strip())
                state = "text"
        elif state == "text":
            current_text.append(line)
            
    # Add the last segment if the file doesn't end with an empty line
    if current_segment and current_text:
        current_segment["text"] = " ".join(current_text)
        segments.append(current_segment)
        
    # Create Whisper-like structure for the translator plugin
    data = {
        "text": " ".join([s.get("text", "") for s in segments]), 
        "segments": segments
    }
    
    output_path = os.path.join(output_dir, "transcription.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    return output_path
