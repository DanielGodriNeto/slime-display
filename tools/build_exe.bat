@echo off
rem Gera dist\SlimeDisplay.exe (arquivo unico, sem precisar de Python). Rode da raiz do projeto.
cd /d "%~dp0.."
pc\.venv\Scripts\pip install -q pyinstaller
pc\.venv\Scripts\pyinstaller --noconfirm --onefile --noconsole --name SlimeDisplay ^
  --paths pc --add-data "pc\icons;icons" --add-data "pc\slimes.json;." ^
  --collect-all tkinterdnd2 --collect-all soundcard --collect-all pycaw ^
  --collect-submodules winrt --hidden-import pystray._win32 ^
  pc\slime_display.py
