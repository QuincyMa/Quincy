virsh destroy $1
virsh undefine $1
rm -rf /var/lib/libvirt/images/$1.qcow2
