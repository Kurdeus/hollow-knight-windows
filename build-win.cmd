@echo off
chcp 65001 > nul

:: Clean previous builds
if exist setup.spec del setup.spec
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

:: Set virtual environment command prefix
set VENV_CMD=.venv\Scripts\
if not exist .venv set VENV_CMD=

:: Install required packages
%VENV_CMD%pip install -r requirements.txt

:: Build optimized executable
%VENV_CMD%pyi-makespec ^
  --onefile ^
  --icon=app.ico ^
  --name="Hollow Knight Editor" ^
  --strip ^
  --noconsole ^
  --optimize 2 ^
  --hidden-import=win32gui,win32process,win32con ^
  --hidden-import=tkinter,tkinter.filedialog,tkinter.scrolledtext,tkinter.messagebox,tkinter.ttk ^
  --hidden-import=Crypto.Cipher.AES ^
  --hidden-import=base64,json,os,webbrowser ^
  --hidden-import=requests ^
  --hidden-import=typing ^
  --exclude-module=wx ^
  setup.py && ^
ren "Hollow Knight Editor.spec" setup.spec && ^
%VENV_CMD%pyinstaller --noconfirm --upx-dir=./upx --clean setup.spec