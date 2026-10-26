Set WshShell = CreateObject("WScript.Shell")
Dim scriptPath
scriptPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptPath
WshShell.Run "cmd.exe /k python universal_save_bot.py", 1
Set WshShell = Nothing