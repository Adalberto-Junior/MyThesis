cd python 

set mongodb=mongodb_env

if not exist "%mongodb%" (
    .\python.exe -m virtualenv %mongodb% --system-site-packages
    call %mongodb%\Scripts\activate.bat
    pip install pymongo --no-warn-script-location
    pip install websockets --no-warn-script-location
    pip install requests --no-warn-script-location
    pip install aioconsole --no-warn-script-location
    deactivate
)
