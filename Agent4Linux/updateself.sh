if [ -d update.tmp ]; then
    echo "Given permission..."
    chmod +x ./update.tmp/*
    chown root:root ./update.tmp/*

    echo "Killing Agent4Linux process..."
    ps -ef | grep 'Agent4Linux' |grep -v grep | awk '{print "kill -9 "$2,$3}' | sh
    
    echo "Rename Agent4Linux..."
    mv -f Agent4Linux Agent4Linux.old

    echo "Copy new file..."
    \cp -f -p ./update.tmp/*.so .
    \cp -f -p ./update.tmp/*.sh .
    \cp -f -p ./update.tmp/Agent4Linux .

    echo "restart Agent4Linux..."
    nohup ./runAgent.sh 2>&1 & > updateself.log
    sleep 2 
    echo "Agent start over."
else
    echo "update.tmp not found, update failed."
fi
