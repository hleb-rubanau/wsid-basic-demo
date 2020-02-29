#!/bin/bash

LETSENCRYPT_ACCOUNT=${ letsencrypt_account }
FQDN_HOSTNAME=${ fqdn_hostname }

function say() { echo "$*" >&2 }


say "Installing minimal packages"
apt-get update && apt-get install -y python3 ansible git curl

say "Configuring local ansible"
curl -s https://gitlab.com/Rubanau/cloud-tools/raw/master/configure_local_ansible.sh | /bin/bash

#say "Installing trusted keys for major git platforms"
#curl -s https://gitlab.com/Rubanau/cloud-tools/raw/master/ssh_validate_git_providers_fingerprints.sh | /bin/bash | tee -a /etc/ssh/ssh_known_hosts

say "Cloning recipes"
git clone 'https://github.com/hleb-rubanau/wsid-basic-demo.git' /usr/src/wsid-basic-demo

say "Storing ansible parameters"
tee /etc/ansible/host_vars/localhost <<ANSIBLECONFIG
nginx_le_account=$LETSENCRYPT_ACCOUNT
nginx_le_primary_domain=$FQDN_HOSTNAME
nginx_le_mode=prod
ANSIBLECONFIG

cd /usr/src/wsid-basic-demo/playbooks/client
say "Installing roles"
ansible-galaxy install -r requirements.yml --roles-path ./roles

say "Running playbook"
exec ansible-playbook playbook.yml 

