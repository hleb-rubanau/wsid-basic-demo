#!/bin/bash

export ANSIBLE_VAR_NGINX_LE_ACCOUNT=${ letsencrypt_account }
export ANSIBLE_VAR_NGINX_LE_PRIMARY_DOMAIN=${ fqdn_hostname }
export ANSIBLE_VAR_NGINX_LE_MODE=prod
export ANSIBLE_VAR_WSID_DEMO_CLIENT_DOMAIN="${ wsid_demo_client_domain }"
export ANSIBLE_VAR_WSID_DEMO_CLIENT_IDENTITY="$ANSIBLE_VAR_WSID_DEMO_CLIENT_DOMAIN/.wsid/demo"

function say() { echo "$*" >&2 ; }


say "Installing minimal packages"
apt-get update && apt-get install -y python3 ansible git curl

say "Configuring local ansible"
curl -s https://gitlab.com/Rubanau/cloud-tools/raw/master/configure_local_ansible.sh | /bin/bash

#say "Installing trusted keys for major git platforms"
#curl -s https://gitlab.com/Rubanau/cloud-tools/raw/master/ssh_validate_git_providers_fingerprints.sh | /bin/bash | tee -a /etc/ssh/ssh_known_hosts

say "Cloning recipes"
git clone 'https://github.com/hleb-rubanau/wsid-basic-demo.git' /usr/src/wsid-basic-demo

cd /usr/src/wsid-basic-demo/playbooks/
say "Installing roles"
ansible-galaxy install -r requirements_base.yml --roles-path ./roles
ansible-galaxy install -r requirements_auth.yml --roles-path ./roles

# work around ansible bug
# https://github.com/ansible/ansible/issues/31617
if [ -z "$HOME" ]; then export HOME=/root ; fi

say "Running playbook"
exec ansible-playbook playbook_auth.yml 

