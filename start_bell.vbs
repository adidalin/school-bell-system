Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\server\Desktop\钢城智慧铃声系统"
WshShell.Run "python run.py", 0, False
