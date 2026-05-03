cd .\rasaDemo
set rasa_env=..\Python\rasa_env

call %rasa_env%\Scripts\activate.bat
python -m rasa train
deactivate
::..\Python\python.exe -m rasa train