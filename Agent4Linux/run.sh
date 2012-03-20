. k.sh
./setCfg
echo "Agent start..."
nohup ./runAgent.sh 2>&1 &
sleep 5 
echo "Agent start over."
ps -ef | grep Agent4Linux
ps -ef | grep CMDServer4Linux

