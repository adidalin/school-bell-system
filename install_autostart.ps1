# 安装开机自启动：将 start_bell.vbs 添加到 Windows 启动项
$WshShell = New-Object -ComObject WScript.Shell
$StartupFolder = [Environment]::GetFolderPath("Startup")
$ShortcutPath = Join-Path $StartupFolder "钢城智慧铃声系统.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "$env:windir\System32\wscript.exe"
$Shortcut.Arguments = """C:\Users\server\Desktop\钢城智慧铃声系统\start_bell.vbs"""
$Shortcut.WorkingDirectory = "C:\Users\server\Desktop\钢城智慧铃声系统"
$Shortcut.Description = "钢城智慧铃声系统 - 校园智能广播"
$Shortcut.Save()
Write-Host "✓ 开机自启动已安装到: $ShortcutPath"
Write-Host "  下次开机将自动启动系统"
Write-Host ""
Write-Host "如需移除，请删除以下文件:"
Write-Host "  $ShortcutPath"
