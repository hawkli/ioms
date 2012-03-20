echo "Killing Agent4Linux process..."
ps -ef | grep 'Agent4Linux' |grep -v grep
ps -ef | grep 'Agent4Linux' |grep -v grep | awk '{print "kill -9 "$2,$3}' | sh
echo "Killing CMDServer4Linux process..."
ps -ef | grep 'CMDServer4Linux' |grep -v grep
ps -ef | grep 'CMDServer4Linux' |grep -v grep | awk '{print "kill -9 "$2,$3}'| sh
echo "Kill over."

