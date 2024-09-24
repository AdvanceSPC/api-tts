import os
import uuid
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings

# Cargar la clave API de ElevenLabs desde el archivo .env
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable not set")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Inicializar la app Flask
app = Flask(__name__)

# Función para convertir texto a archivo de audio
def text_to_speech_file(text: str) -> str:
    response = client.text_to_speech.convert(
        voice_id="Xb7hH8MSUJpSbSDYk0k2",  # Voz Alice
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

    # Generar un nombre de archivo único
    save_file_path = f"{uuid.uuid4()}.mp3"

    # Guardar el archivo de audio
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    return save_file_path

# Ruta para manejar las solicitudes POST
@app.route('/generate-audio', methods=['POST'])
def generate_audio():
    try:
        data = request.get_json()
        if not data or 'Text' not in data:
            return jsonify({'error': 'Invalid input'}), 400

        # Convertir el texto a archivo de audio
        file_path = text_to_speech_file(data['Text'])

        # Devolver la URL del archivo
        return jsonify({'file_url': f"/static/{file_path}"})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
