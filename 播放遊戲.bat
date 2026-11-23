@echo off
chcp 65001 >nul
cd /d "%~dp0"
title tanime - 猜動漫歌

set "PY="
where py      >nul 2>nul && set "PY=py"      && goto run
where python  >nul 2>nul && set "PY=python"  && goto run
where python3 >nul 2>nul && set "PY=python3" && goto run
goto fallback

:run
echo.
echo   使用 %PY% 啟動本地伺服器...
echo   遊玩期間請「保持這個視窗開著」，關閉視窗即可結束遊戲。
echo   瀏覽器會自動跳出，若沒有，請手動開啟視窗中顯示的網址。
echo.
%PY% server.py
goto end

:fallback
echo.
echo   找不到 Python，改為直接開啟 index.html。
echo.
start "" "index.html"

:end
