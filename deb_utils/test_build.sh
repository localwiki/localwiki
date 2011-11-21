vm_host="172.16.180.132"
clean_vm="/home/mivanov/vmware/Ubuntu with vmware tools/Ubuntu-1"
test_vm="/home/mivanov/temp/Ubuntu-1"
vmx_name="Ubuntu.vmx"
transfer_dir="/home/mivanov/transfer/"

./makedeb.sh
if [ $? -ne 0 ]; then
  notify-send "Build failed!"
  exit 1
fi

result=$(cp -v ../deb_dist/*.deb "$transfer_dir")
notify-send "Copied .deb" "$result"

rm -r "$test_vm"
cp -r "$clean_vm" "$test_vm"
notify-send "VM copied"

vmplayer "$test_vm/$vmx_name" &
./waitforhost.sh $vm_host
gnome-terminal -e "ssh ubuntu@$vm_host"
