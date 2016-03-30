FROM docker.io/richxsl/rhel7
ADD rhel7.repo /etc/yum.repos.d/
RUN yum install http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm  -y
RUN yum install python python-devel python-pip git PyYAML python-crypto ansible -y
RUN yum install openssl gcc openssl-devel libffi-devel pyOpenSSL  -y
RUN pip install --upgrade boto3 google-api-python-client
ENV qe_openshift_kerberos_user=xiama
ENV qe_openshift_token="vmXp1ptqJcYdMcqSpc3IX2noKZehfZgXytNUP7FdrCA"
ADD .ssh /root/.ssh
ADD .gce /root/.gce
ADD .aws /root/.aws
ADD ./Installation /root/Installation
WORKDIR /root/Installation/
RUN git clone https://github.com/openshift/openshift-ansible
ENTRYPOINT ["./launcher.py"]
CMD ["--help"]
