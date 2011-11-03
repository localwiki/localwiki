while [ 1 ];
do
    ping -W 1 -q -c1 $1 
    if [ $? -eq 0 ];
    then
        break
    fi
    echo "still down"
    sleep 1
done
echo "great success"
