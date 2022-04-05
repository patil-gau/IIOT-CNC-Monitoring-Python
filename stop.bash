#!/bin/bash
#while true;
#do
	echo "........killing  application............"
	pid=`ps -ef | awk '/main.py/{print $2}'`
	echo $pid
	sleep 2
	sudo kill -9 $pid
	echo "done"
