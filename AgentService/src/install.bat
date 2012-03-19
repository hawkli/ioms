setCfg.exe
AgentService.exe -install
sc config AgentService start= auto
sc start AgentService
pause