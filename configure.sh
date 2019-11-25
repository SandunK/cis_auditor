#/bin/bash

yum install epel-release
yum install https://centos7.iuscommunity.org/ius-release.rpm
yum install python36u python36u-devel python36u-pip
yum install python-pip
pip install -r dependencies.txt
pip3 install -r dependencies.txt
