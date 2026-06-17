Set WshShell = CreateObject("WScript.Shell")
' Use script's directory as working dir so relative paths work
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir
' Run pythonw in hidden window
WshShell.Run "pythonw.exe run.py", 0, False
