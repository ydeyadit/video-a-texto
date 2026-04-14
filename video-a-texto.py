#!/usr/bin/env python3
import subprocess
import os
import sys
import argparse

# Comprobamos dependencias
try:
    import whisper
    import torch
except ImportError as e:
    print(f"Error: falta dependencia '{e.name}'. Instálala con pip.")
    sys.exit(1)


def extraer_audio_ffmpeg(video_input, audio_output):
    """Extrae el audio del video usando FFmpeg en formato compatible con Whisper."""
    print(f"--- [1/3] Extrayendo audio de: {video_input} ---")

    comando = [
        "ffmpeg",
        "-i",
        video_input,
        "-vn",  # Desactivar video
        "-acodec",
        "pcm_s16le",  # Codec PCM 16-bit
        "-ar",
        "16000",  # Frecuencia de muestreo 16kHz
        "-ac",
        "1",  # Canal mono
        "-y",  # Sobrescribir si existe
        audio_output,
    ]

    try:
        subprocess.run(
            comando, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
        )
        print("--- Audio extraído correctamente ---")
    except subprocess.CalledProcessError as e:
        print(
            f"Error: Falló la extracción con FFmpeg.\n{e.stderr.decode(errors='ignore').splitlines()[0]}"
        )
        sys.exit(1)
    except FileNotFoundError:
        print("Error: FFmpeg no está instalado en el sistema.")
        sys.exit(1)


def transcribir_audio(audio_path, modelo_nombre, idioma=None):
    """Carga el modelo de Whisper y realiza la transcripción."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    fp16 = torch.cuda.is_available()

    lang_info = f"en idioma '{idioma}'" if idioma else "con detección automática"
    print(
        f"--- [2/3] Transcribiendo {lang_info} con modelo '{modelo_nombre}' en {device} ---"
    )

    try:
        model = whisper.load_model(modelo_nombre, device=device)
        result = model.transcribe(audio_path, fp16=fp16, language=idioma, verbose=False)
        return result["text"]
    except Exception as e:
        print(f"Error durante la transcripción: {e}")
        sys.exit(1)


def procesar_todo(video_archivo, modelo, idioma, salida=None):
    """Flujo completo: Extraer -> Transcribir -> Guardar -> Limpiar."""
    audio_temp = "temp_audio_ext_whisper.wav"
    nombre_base = os.path.splitext(video_archivo)[0]
    txt_salida = salida if salida else f"{nombre_base}_transcripcion.txt"

    try:
        # Paso 1: Extraer Audio
        extraer_audio_ffmpeg(video_archivo, audio_temp)

        # Paso 2: Transcribir
        texto = transcribir_audio(audio_temp, modelo, idioma)

        # Paso 3: Guardar Resultado
        print(f"--- [3/3] Guardando transcripción en: {txt_salida} ---")
        with open(txt_salida, "w", encoding="utf-8") as f:
            f.write(texto.strip())

        print(f"\n¡Listo! El proceso ha finalizado con éxito.")

    finally:
        # Limpieza de archivos temporales
        if os.path.exists(audio_temp):
            os.remove(audio_temp)
            print(f"--- Limpieza: Archivo temporal eliminado ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Herramienta para extraer diálogos de video a texto plano."
    )

    parser.add_argument("video", help="Ruta al archivo de video (mp4, mkv, avi, etc.)")
    parser.add_argument(
        "-l", "--lang", help="Idioma del audio (ej: es, en). Opcional.", default=None
    )
    parser.add_argument(
        "-m",
        "--model",
        help="Modelo de Whisper (tiny, base, small, medium, large).",
        default="base",
    )
    parser.add_argument(
        "-o", "--output", help="Archivo de salida para la transcripción.", default=None
    )

    args = parser.parse_args()

    if os.path.exists(args.video):
        procesar_todo(args.video, args.model, args.lang, args.output)
    else:
        print(f"Error: El archivo '{args.video}' no existe.")
