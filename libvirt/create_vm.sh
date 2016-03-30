if [ $# -ne 3  ]; then
    echo "Usage:"
    echo "sh $0 image vm_name"
fi
source_image=/var/lib/libvirt/images/$1
target_image=/home/fg/workspace/libvirt/$2.qcow2
vm_name=$2
vm_xml=/tmp/${2}.xml

sed -e "s#VM_NAME#${vm_name}#g" -e "s#VM_IMG#${source_image}#g" template.xml >/tmp/$2.xml
virsh define ${vm_xml} && cp -rf ${source_image} ${target_image} && virsh start ${vm_name}

