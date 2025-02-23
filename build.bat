@echo off
rmdir /s /q build dist
del main.spec
pyinstaller --onefile --windowed --icon=icon.ico main.py
pause
