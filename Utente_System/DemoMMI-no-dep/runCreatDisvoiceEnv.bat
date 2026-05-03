cd python

set disvoice=disvoice_env

if not exist "%disvoice%" (
    .\python.exe -m virtualenv %disvoice% --system-site-packages
    call %disvoice%\Scripts\activate.bat
    pip install pyaudio webrtcvad --no-warn-script-location
    pip install websockets --no-warn-script-location
    pip install pygame --no-warn-script-location
    pip install SpeechRecognition --no-warn-script-location
    pip install librosa --no-warn-script-location
    pip install matplotlib --no-warn-script-location
    pip install praat-parselmouth --no-warn-script-location
    pip install disvoice --no-warn-script-location
    pip install scipy==1.10.0
    pip install aioconsole --no-warn-script-location
    pip install soundfile
    pip install pyworld
    deactivate
)

echo Todos os servidores foram iniciados.
pause