import os
import shutil
import subprocess

try:
    import PyInstaller.__main__
except ImportError:
    print("Installing PyInstaller...")
    subprocess.check_call(["pip", "install", "pyinstaller", "--break-system-packages"])
    import PyInstaller.__main__

try:
    import customtkinter
except ImportError:
    print("Installing requirements...")
    subprocess.check_call(["pip", "install", "-r", "requirements.txt", "--break-system-packages"])
    import customtkinter

# Find where CustomTkinter is installed to bundle its internal heavy assets securely
customtkinter_path = os.path.dirname(customtkinter.__file__)

print("Starting SimSlayer build process...")

PyInstaller.__main__.run([
    '--noconfirm',
    '--onedir',
    '--windowed',
    '--name=SimSlayer',
    f'--add-data={customtkinter_path}:customtkinter/',
    '--add-data=payloads/default_payloads.json:payloads/',
    'main.py'
])

print("\n--- Build Complete! ---")
print("You can find your bundled application in the newly generated `dist/SimSlayer` folder.")
print("To share it, just ZIP the `dist/SimSlayer` folder and send it over!")
