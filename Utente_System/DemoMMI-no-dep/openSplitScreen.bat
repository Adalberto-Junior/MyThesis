@REM @echo off
@REM set ip=%1

@REM echo ^<html^> > split.html
@REM echo ^<head^>^<title^>Split View^</title^>^</head^> >> split.html
@REM echo ^<style^>body{margin:0;display:flex;height:100vh;}iframe{flex:1;border:none;}^</style^> >> split.html
@REM echo ^<body^> >> split.html
@REM echo ^<iframe src="https://%ip%:8082"^>^</iframe^> >> split.html
@REM echo ^<iframe src="https://%ip%:8082/login.html"^>^</iframe^> >> split.html
@REM echo ^</body^>^</html^> >> split.html

@REM start "" "split.html"

@echo off
set ip=%1

echo ^<html^> > splitLauncher.html
echo ^<head^>^<title^>Split Launcher^</title^> >> splitLauncher.html
echo ^<script^> >> splitLauncher.html
echo function openWindows() { >> splitLauncher.html
echo   const screenWidth = window.screen.availWidth; >> splitLauncher.html
echo   const screenHeight = window.screen.availHeight; >> splitLauncher.html
echo   const width = Math.floor(screenWidth / 2); >> splitLauncher.html
echo   const height = screenHeight; >> splitLauncher.html
echo   const ip = "%ip%"; >> splitLauncher.html
echo   window.open(`https://${ip}:8082`, "LeftWindow", `width=${width},height=${height},left=0,top=0`); >> splitLauncher.html
echo   window.open(`https://${ip}:8082/login.html`, "RightWindow", `width=${width},height=${height},left=${width},top=0`); >> splitLauncher.html
echo } >> splitLauncher.html
echo ^</script^> >> splitLauncher.html
echo ^</head^> >> splitLauncher.html
echo ^<body onload="openWindows()"^> >> splitLauncher.html
echo ^<p^>Abrindo janelas lado a lado...^</p^> >> splitLauncher.html
echo ^</body^> >> splitLauncher.html
echo ^</html^> >> splitLauncher.html

start "" "splitLauncher.html"

