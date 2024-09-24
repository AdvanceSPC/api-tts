import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# Cargar variables de entorno
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable not set")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

app = Flask(__name__)

# confirmo o creo una carpeta static para almacenar local
if not os.path.exists('static'):
    os.makedirs('static')

def text_to_speech_file(text: str) -> str:
    """
    Convierte texto a voz y guarda el resultado como un archivo MP3 en la carpeta 'static'.
    """
    response = client.text_to_speech.convert(
        voice_id="Xb7hH8MSUJpSbSDYk0k2",  # Alice
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    # Genero un nombre único y almaceno en la carpeta static
    save_file_path = f"static/{uuid.uuid4()}.mp3"
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"Archivo de audio guardado en: {save_file_path}")
    return save_file_path

@app.route("/convert", methods=["POST"])
def convert_text_to_speech():
    """
    Recibe una solicitud POST con un JSON que contiene un campo 'Text' y devuelve el enlace del archivo de audio.
    """
    data = request.get_json()
    if not data or "Text" not in data:
        return jsonify({"error": "Falta el campo 'Text' en la solicitud"}), 400

    text = data["Text"]

    try:
        # Conversión de texto a un archivo de audio
        audio_file_path = text_to_speech_file(text)
        # Extraer solo el nombre del archivo
        file_name = os.path.basename(audio_file_path)
        # Devolver la URL del archivo generado
        return jsonify({"audio_file_url": f"/files/{file_name}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/files/<path:filename>")
def download_file(filename):
    """
    Sirve los archivos de audio generados desde la carpeta 'static'.
    """
    return send_from_directory('static', filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
