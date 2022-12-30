from fastapi import FastAPI, Response, status, UploadFile, File
from fastapi.responses import HTMLResponse
import soundfile as sf
from soundfile import SoundFile

app = FastAPI()

AUDIO_FORMAT = sf.available_formats()['WAV']
TYPE = 'int16'
DURATION = 10


@app.get('/')
async def root():
    return HTMLResponse('AudioVerifyAPI')


@app.post('/audio/verify', status_code = 200)
async def audio_verify(response:Response, file: UploadFile = File(...)):
    try:
        audio = SoundFile(file.file)
        format = audio.format_info
        type = audio.read().dtype
        duration = float(audio.frames) / audio.samplerate
        
        if format == AUDIO_FORMAT and type == TYPE and duration <= DURATION:
            success = True
            message = "Формат аудио файла корректный."
        else:
            success = False
            message = "Формат аудио файла неверный:"
            if format != AUDIO_FORMAT:
                message += " Формат аудио не 'WAV (Microsoft)';"
            if type != TYPE:
                message += " Запись отсчётов не 'int16';"
            if duration > DURATION:
                message += " Длительность более 10 секунд;"
            response.status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        audio.close()
    except Exception:
        response.status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        return {"success": False, "message": "Этот файл не является аудиозаписью."}
    finally:
        file.file.close()

    reply = {
        'success': success,
        'message': message
        }

    return reply
