#!/bin/bash
set -e

yum update -y
yum install -y docker git
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu

mkdir -p /usr/lib/docker/cli-plugins
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/lib/docker/cli-plugins/docker-compose
chmod +x /usr/lib/docker/cli-plugins/docker-compose

curl -L https://github.com/docker/buildx/releases/download/v0.17.1/buildx-v0.17.1.linux-amd64 -o /usr/lib/docker/cli-plugins/docker-buildx
chmod +x /usr/lib/docker/cli-plugins/docker-buildx

mkdir -p /home/ubuntu/MLOps-Project
chown -R ubuntu:ubuntu /home/ubuntu/MLOps-Project
