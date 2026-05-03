cd python

set rasa_env=rasa_env

:: Criar os ambientes se não existirem
if not exist "%rasa_env%" (
    .\python.exe -m virtualenv %rasa_env% --system-site-packages
    call %rasa_env%\Scripts\activate.bat
    pip install rasa --no-warn-script-location
    deactivate

)