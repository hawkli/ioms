
while true
    do
        vars=`ps -ef | grep 'Agent4Linux' |grep -v grep | awk '{print $2}'|wc -l`
        if [ $vars -eq 1 ];then
           echo "normal running"
           sleep 1
        elif [ $vars -eq 0 ]; then
           echo "Agent4Linux not running,restart it."
           nohup ./Agent4Linux 2>&1 &
           sleep 1
        elif [ $vars -gt 1 ]; then
           echo "warning, found multiple programs are running. pls kill someone!"
           killprocessid=`ps -ef | grep 'Agent4Linux' |grep -v grep | awk '{print $2}'`
           killer=`kill -9 $killprocessid`
           echo "kill process $killprocessid completed. restart Agent4Linux again."
           nohup ./Agent4Linux 2>&1 &
           sleep 1
        fi
        sleep 59
    done
