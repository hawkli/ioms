if [ -d update.tmp ]; then
    echo "Given permission..."
    chmod +x ./update.tmp/*
    chown root:root ./update.tmp/*

    echo "Killing CMDServer4Linux process..."
    ps -ef | grep 'CMDServer4Linux' |grep -v grep | awk '{print "kill -9 "$2,$3}' | sh
    
    echo "Rename CMDServer4Linux..."
    mv -f CMDServer4Linux CMDServer4Linux.old

    echo "Copy new file..."
    \cp -f -p ./update.tmp/*.so .
    \cp -f -p ./update.tmp/CMDServer4Linux .

#    echo "restart CMDServer4Linux..."
#    nohup ./runCMD.sh 2>&1 &
#    sleep 2 
#    echo "CMDServer start over."
else
    echo "update.tmp not found, update failed."
fi
