cd python

set flask=flask_env

if not exist "%flask%" (
    .\python.exe -m virtualenv %flask% --system-site-packages
    call %flask%\Scripts\activate.bat
    pip install Flask flask-cors pymongo --no-warn-script-location
    pip install bcrypt pyjwt python-dotenv --no-warn-script-location
    deactivate
)

echo Todos os servidores foram iniciados.
pause