Set WshShell = CreateObject("WScript.Shell")
' 获取脚本所在目录
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
' 后台运行 Python（pythonw 无控制台窗口）
WshShell.Run "pythonw.exe """ & scriptDir & "\run.py""", 0, False
