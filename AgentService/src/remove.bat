taskkill /IM AgentService.exe /F
taskkill /IM CMDServer.exe /F
sc delete AgentService
pause
