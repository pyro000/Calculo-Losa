from cx_Freeze import setup, Executable

build_exe_options = {"packages": ['PySimpleGUI', 'PIL', 'io'], "excludes": [], 'include_files': ['data/']}

base_gui = "Win32GUI"

setup(
    name = "Calculo Losa",
    version = "0.1",
    description = "Calculo Losa",
    options = {"build_exe": build_exe_options},
    executables = [Executable("main.py", target_name='Calculo Losa.exe', base=base_gui)]
)