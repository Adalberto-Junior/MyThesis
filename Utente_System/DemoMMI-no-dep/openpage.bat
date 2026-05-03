@echo off
setlocal enabledelayedexpansion

for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set ip=%%A
    set ip=!ip:~1!
)

@REM echo Seu IP é: %ip%
@REM start "" "https://%ip%:8082"
@REM @REM start "" "https://%ip%:8082/appGui.htm"
@REM @REM start "" "https://%ip%:8082/registro.html"
@REM start "" "https://%ip%:8082/login.html"
@REM @REM start "" "https://%ip%:8082/addExercise2.html"

echo Seu IP é: !ip!
call openSplitScreen.bat !ip!

@REM $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -match "Wi-Fi|Ethernet"}).IPAddress

@REM Start-Process "msedge.exe" "--new-window https://$ip:8082 --window-position=0,0 --window-size=960,1040"
@REM Start-Process "msedge.exe" "--new-window https://$ip:8082/login.html --window-position=960,0 --window-size=960,1040"


wt --window 0 --title Broker --suppressApplicationTitle -d . -p "Windows Powershell" cmd /k "cd .\WebAppAssistantV2\Aplicaction\ && ..\..\Python\python.exe broker.py"
timeout /t 5 /nobreak

wt --window 0 --title Assistente --suppressApplicationTitle -d . -p "Windows Powershell" cmd /k "cd .\WebAppAssistantV2\Aplicaction\ && ..\..\Python\python.exe assistente.py"
::wt --window 0 --title DataManager --suppressApplicationTitle -d . -p "Windows Powershell" cmd /k "cd .\WebAppAssistantV2\Aplicaction\ && ..\..\Python\python.exe dataManager.py"
REM wt --window 0 --title Diagnostico --suppressApplicationTitle -d . -p "Windows Powershell" cmd /k "cd .\WebAppAssistantV2\Aplicaction\ && ..\..\Python\python.exe diagnosticModule.py"
wt --window 0 --title DataManager --suppressApplicationTitle -d . -p "Windows Powershell" cmd /k "cd .\WebAppAssistantV2\Aplicaction\ && ..\..\Python\mongodb_env\Scripts\activate.bat && python dataManager.py"
wt --window 0 --title Diagnostico --suppressApplicationTitle -d . -p "Windows Powershell" cmd /k "cd .\WebAppAssistantV2\Aplicaction\ && ..\..\Python\disvoice_env\Scripts\activate.bat && python diagnosticModule.py"
@REM wt --window 0 --title UserManager --suppressApplicationTitle -d . -p "Windows Powershell" cmd /k "cd .\WebAppAssistantV2\Aplicaction\ && ..\..\Python\python.exe userManager.py"
wt --window 0 --title ExerciseModule --suppressApplicationTitle -d . -p "Windows Powershell" cmd /k "cd .\WebAppAssistantV2\Aplicaction\ && ..\..\Python\python.exe exerciseModule.py"
