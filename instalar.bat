@echo off
rem Instalador do app do Slime Display (Windows). Duplo clique e pronto.
rem Faz: acha/instala o Python, cria a pasta pc\.venv, instala as bibliotecas e cria um atalho na Area de Trabalho.
setlocal
cd /d "%~dp0"

rem 1) Python: usa o que ja existe; se nao houver, instala pelo winget (vem no Windows 10/11).
set PY=
where py >nul 2>&1 && set PY=py -3
if not defined PY where python >nul 2>&1 && set PY=python
if not defined PY (
  echo Python nao encontrado. Instalando...
  winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
  echo.
  echo Python instalado. FECHE esta janela e de duplo clique em instalar.bat de novo.
  pause
  exit /b
)

rem 2) Ambiente isolado + bibliotecas (so na primeira vez)
if not exist pc\.venv\Scripts\pythonw.exe %PY% -m venv pc\.venv
pc\.venv\Scripts\python -m pip install -q -r pc\requirements.txt
if errorlevel 1 ( echo Falhou ao instalar as bibliotecas. Veja se ha internet. & pause & exit /b 1 )

rem 3) Atalho na Area de Trabalho (abre sem janela preta)
powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\Slime Display.lnk'); $s.TargetPath='%~dp0pc\.venv\Scripts\pythonw.exe'; $s.Arguments='\"%~dp0pc\slime_display.py\"'; $s.WorkingDirectory='%~dp0pc'; $s.Save()"

echo.
echo Pronto! Ligue a placa na USB e abra o atalho "Slime Display" na Area de Trabalho.
pause
