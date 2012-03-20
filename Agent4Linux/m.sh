cxfreeze CMDServer4Linux.py --target-dir agent
cxfreeze Agent4Linux.py --target-dir agent
cxfreeze setCfg.py --target-dir agent
cp *.ini agent
cp *.sh agent
chmod +x agent/*.sh
