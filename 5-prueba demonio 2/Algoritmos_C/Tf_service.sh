#!/bin/bash

# /etc/init.d/test

case "$1" in
   start)
      echo "Starting server"
      sudo python3 /home/ubuntu/rasberry/Algoritmos_C/demonio.py start 
      ;;

   stop)
      echo "Stopping server"
      sudo python3 /home/ubuntu/rasberry/Algoritmos_C/demonio.py stop
      ;;

   restart)
      echo "Restarting server"
      sudo python3 /home/ubuntu/rasberry/Algoritmos_C/demonio.py restart
      ;;

   *)
      echo "Usage: /etc/init.d/Tf_service.sh {start|stop|restart}"
      exit 1
      ;;
esac
exit 0