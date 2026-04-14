# EXTRAER TEXTO DE UN VIDEO

Para este propósito, la mejor herramienta actual para ejecutar de forma local es Whisper, un modelo de reconocimiento de voz de código abierto desarrollado por OpenAI que funciona excepcionalmente bien.(la verdad es que existen mejores opciones pero son de paga y yo soy pobre :-) )

---

## 1. El Flujo de Trabajo (Workflow)

El proceso se divide en tres etapas lógicas:

1.  Extracción: Separar el flujo de audio del contenedor de vídeo (MP4, MKV, etc.) y convertirlo a un formato que el transcriptor entienda fácilmente (por lo que ví en documentación,generalmente WAV).

2.  Procesamiento: El script de Python carga el archivo de audio y lo pasa por un modelo de red neuronal (Whisper).

3.  Salida: El texto resultante se guarda en un archivo de texto plano (.txt) o incluso en formatos de subtítulos (.srt).

---

## 2. Fase 1: Extracción de Audio con FFmpeg

Para que el modelo de IA trabaje de forma eficiente, lo ideal es extraer el audio en un formato sin pérdida o con parámetros estándar (16kHz, mono).

Comando empleado:

- 1 ffmpeg -i video_entrada.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio_salida.wav

### Explicación de los flags:

- -i video_entrada.mp4: El archivo de vídeo original.
- -vn: (Video None) Deshabilita el procesamiento de vídeo; solo nos quedamos con el audio.
- -acodec pcm_s16le: Codifica el audio en PCM de 16 bits (estándar para muchos sistemas de voz).
- -ar 16000: Ajusta la frecuencia de muestreo a 16,000 Hz (ideal para transcripción).
- -ac 1: Convierte el audio a un solo canal (mono), lo que reduce el peso del archivo y facilita el análisis.

---

## 3. Fase 2: Transcripción con Python y Whisper

Whisper es muy potente (según aseguran los especialistas) porque puede detectar el idioma automáticamente y es muy robusto frente al ruido de fondo.

Instalación de dependencias:
Primero, instalar la librería :

- 1 pip install openai-whisper torch

Los script de Python son muy simples de entender... si sabes programar, pero si eres como yo hace falta detallar para aclarar sus capacidades.

---

## 4. Análisis de los Modelos de Whisper

Whisper ofrece diferentes "tamaños" de modelo. A mayor tamaño, mayor precisión pero requiere más potencia de cómputo (RAM/GPU). Y si, como es mi caso, no tienes una máquina con buenos recursos (tarjeta de video NVIDIA y un procesador con más núcleos que neuronas en mi cerebro)preparate para 'oler' a tu cpu. 🔥🔥🔥🔥

---

### Comparativa de Modelos

---

- Modelo: tiny
  - Precisión: Baja (bueno para pruebas rápidas).
  - Velocidad: Muy alta.
  - Uso de memoria: ~1GB.

- Modelo: base
  - Precisión: Decente (equilibrio ideal).
  - Velocidad: Alta.
  - Uso de memoria: ~1GB.

- Modelo: small (el recomandado)
  - Precisión: Buena.
  - Velocidad: Media.
  - Uso de memoria: ~2GB.

- Modelo: medium / large
  - Precisión: Excelente (profesional).
  - Velocidad: Lenta (recomendado usar GPU).
  - Uso de memoria: 5GB a 10GB.

---

## 5. Consideraciones Finales

- Hardware: **REPITO** Si tienes una tarjeta gráfica NVIDIA, Whisper la usará automáticamente a través de CUDA, acelerando el proceso enormemente. **Si no, usará el procesador (CPU)** , lo cual es más lento pero funciona a costa de hacer sufrir a tu hardware.

- Idiomas: Whisper detecta el idioma automáticamente. Si el vídeo está en español y quieres forzarlo, puedes añadir language='es' en la función `model.transcribe()`.

- Automatización: Se integra el comando de FFmpeg dentro del propio script de Python usando la librería subprocess para hacer todo el proceso en un solo paso.

---

# 1. El Diseño Modular del Script

El script sigue un flujo lógico de "Entrada -> Proceso -> Salida", con una etapa intermedia de limpieza para no dejar archivos temporales de audio ocupando espacio.

---

## Arquitectura del Proceso Automatizado

---

- Fase 1: Extracción de Audio
  - Herramienta: subprocess.run(["ffmpeg", ...])
  - Acción: Extrae el flujo de audio del vídeo y lo guarda como un archivo .wav temporal.

- Fase 2: Transcripción de IA
  - Herramienta: whisper.load_model()
  - Acción: Carga el modelo seleccionado y procesa el audio temporal para extraer el texto.

- Fase 3: Gestión de Archivos
  - Herramienta: os.remove()
  - Acción: Elimina el archivo .wav temporal una vez que el texto ha sido extraído con éxito.

---

## 2. Requisitos Previos

Antes de ejecutar el script, asegúrate de tener instalados los componentes necesarios en tu sistema:

1.  FFmpeg instalado: Debe estar disponible en tu PATH de Linux.
2.  Librerías de Python:
    1 pip install openai-whisper torch

3.  Cómo usar el Script

- Para transcribir un vídeo, simplemente ejecuta el script desde tu terminal pasando la ruta del vídeo como argumento:
  - python video_a_texto.py mi_video_interesante.mkv

El script generará un archivo llamado mi_video_interesante_transcripcion.txt en el mismo directorio.

---

4. Puntos Clave para Recordar

- Uso de subprocess.run: Hemos configurado check=True para que el script se detenga si FFmpeg falla, y stdout=subprocess.DEVNULL para que no ensucie la pantalla con logs técnicos de FFmpeg.
- Bloque finally: Esto es crucial en programación robusta. Garantiza que, incluso si el proceso de transcripción falla o lo detienes manualmente (Ctrl+C), el archivo .wav temporal sea eliminado, manteniendo tu sistema limpio.
- Modularidad: Hemos separado las tareas en funciones independientes (extraer_audio_ffmpeg, transcribir_audio). Esto permite, en el futuro, mejorar una parte sin romper la otra (por ejemplo, cambiar Whisper por otra IA o añadir más flags a FFmpeg como se hizo en video-o-audio-a-texto.py).

- Ventajas de Especificar el Idioma
  Cuando no le pasas el idioma a Whisper, la IA realiza un paso previo llamado "Language Detection" (otra vez,segun la documentación que encontré) analizando los primeros 30 segundos del audio. Al proporcionarlo tú mismo mediante flags, obtenemos:
  - Mayor Precisión: Evitas que la IA se confunda en vídeos con mucho ruido de fondo o música, donde podría malinterpretar el idioma inicial.
  - Ahorro de Tiempo: Saltamos la fase de detección automática, yendo directamente al grano.
  - Consistencia: Si el vídeo tiene fragmentos en otros idiomas pero el principal es el español, forzamos a que la transcripción mantenga la estructura del idioma que nos interesa.

---

## Mapeo de Idiomas para Whisper

---

- Español: El código estándar es 'es'.
- Inglés Americano: El código estándar es 'en'.
- Detección Automática: (Si no se especifica) Whisper intenta adivinarlo.

---

### Implementación de idioma y vídeo: Uso de argparse.

Para manejar múltiples argumentos de forma elegante (el vídeo y el idioma), lo ideal en Python es usar la librería argparse. Esto nos permite crear una interfaz de línea de comandos real con ayuda integrada.

## 3. Cómo Ejecutar el Nuevo Script

    - python video_a_texto.py mi_video.mp4 --lang es

Caso 2: Vídeo en Inglés Americano - python video_a_texto.py tutorial_usa.mkv -l en

Caso 3: Si no estás seguro del idioma (Detección automática) - python video_a_texto.py misterio.mp4

---

- Parámetro language: En la función model.transcribe(), el argumento language acepta el código ISO del idioma. Si le pasas None, Whisper activa su motor de detección.
- Uso de Flags Cortos: Hemos configurado -l como abreviatura de --lang, lo cual es muy cómodo para perezosos.
- Ayuda integrada: Si ejecutas python video_a_texto.py --help, el script te explicará automáticamente cómo usarlo.

### Resumen de Compensaciones (Trade-offs)

Para facilitar tu elección, aquí tienes una comparación directa de modelos:

    - Si buscas Velocidad Extrema: Usa tiny o base.
    - Si buscas un Equilibrio (Recomendación General): Usa small.
    - Si el Audio es Difícil o Técnico: Usa medium o large (pero prepárate para esperar).

### Modelos **English-only** (Solo para Inglés):

    Si estás 100% seguro de que el vídeo es en inglés, puedes usar las variantes .en (ejemplo: base.en, small.en). Estos modelos son ligeramente más precisos y rápidos que sus equivalentes multilingües, pero no entenderán ni una palabra en español.

\*NOTA:
**Los que me sorŕende de este script es que funciona**
