cd python
.\python.exe .\get-pip.py --no-warn-script-location
.\python.exe -m  pip install --target .\Lib\site-packages pywin32 docopt-0.6.2-py2.py3-none-any.whl
.\python.exe -m  pip install virtualenv --no-warn-script-location
.\python.exe -m  pip install websocket-client --no-warn-script-location
.\python.exe -m  pip install pyaudio --no-warn-script-location
.\python.exe -m  pip install websockets --no-warn-script-location
.\python.exe -m  pip install requests --no-warn-script-location
.\python.exe -m  pip install lxml --no-warn-script-location
.\python.exe -m  pip install pygame --no-warn-script-location
.\python.exe -m  pip install SpeechRecognition --no-warn-script-location
.\python.exe -m  pip freeze --no-warn-script-location
.\python.exe -m  pip install bcrypt --no-warn-script-location
.\python.exe -m  pip install aioconsole --no-warn-script-location


:: Definir os ambientes virtuais
set rasa_env=rasa_env
set disvoice=disvoice_env
set mongodb=mongodb_env

:: Criar os ambientes se não existirem
if not exist "%rasa_env%" (
    .\python.exe -m virtualenv %rasa_env% --system-site-packages
    call %rasa_env%\Scripts\activate.bat
    pip install rasa --no-warn-script-location
    deactivate

)
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
if not exist "%mongodb%" (
    .\python.exe -m virtualenv %mongodb% --system-site-packages
    call %mongodb%\Scripts\activate.bat
    pip install pymongo --no-warn-script-location
    pip install websockets --no-warn-script-location
    pip install requests --no-warn-script-location
    pip install aioconsole --no-warn-script-location
    deactivate
)


:: Abrir cada script em um terminal separado para rodar continuamente
::start "Servidor 1" cmd /k "%rasa_env%\Scripts\activate && python script1.py"
::start "Servidor 2" cmd /k "%disvoice%\Scripts\activate && python script2.py"
::start "Servidor 3" cmd /k "%mongodb%\Scripts\activate && python script3.py"

echo Todos os servidores foram iniciados.
pause

:: OBS:
:: VER A ABA CONTROLE DE GRAVAÇÃO DO AUDIO NO CHATGPT::::::::::::::


