# 安装开机自启动：创建 pythonw.exe 快捷方式（Unicode路径支持，无编码问题）
$Pythonw = "C:\Users\server\AppData\Local\Programs\Python\Python312\pythonw.exe"
$ScriptDir = "C:\Users\server\Desktop\钢城智慧铃声系统"
$WshShell = New-Object -ComObject WScript.Shell
$StartupFolder = [Environment]::GetFolderPath("Startup")
$ShortcutPath = Join-Path $StartupFolder "SchoolBell.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $Pythonw
$Shortcut.Arguments = "$ScriptDir\run.py"
$Shortcut.WorkingDirectory = $ScriptDir
$Shortcut.Description = "School Bell System"
$Shortcut.WindowStyle = 7
$Shortcut.Save()

Write-Host "✓ 开机自启动已安装到: $ShortcutPath"
Write-Host "  下次开机将自动启动系统"
