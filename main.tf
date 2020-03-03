provider "digitalocean" {
  token = var.do_token
}

module "do_ssh_keys" {
  source = "github.com/hleb-rubanau/terraform-module-digitalocean-ssh-key-ids"
  keys   = var.keys
}

locals {
  do_ssh_key_ids = values(module.do_ssh_keys.data)[*].id
  ubuntu_image     = "ubuntu-18-04-x64"
  demo_client_fqdn = join(".", [ var.demo_client_subdomain, var.demo_domain ] )
  demo_server_fqdn = join(".", [ var.demo_server_subdomain, var.demo_domain ] )
}


resource "digitalocean_droplet" "client" {
  image              = local.ubuntu_image
  name               = local.demo_client_fqdn 
  region             = var.region
  ssh_keys           = local.do_ssh_key_ids 
  user_data          = templatefile ( "${path.module}/cloud-init/client.sh", 
                                         {
                                            letsencrypt_account = var.letsencrypt_account
                                            fqdn_hostname=local.demo_client_fqdn
                                            wsid_demo_upstream=local.demo_server_fqdn
                                            wsid_demo_protection_user = var.demo_protection_user 
                                            wsid_demo_protection_password = base64encode( var.demo_protection_password )
                                         }
                                     )

  size               = "s-1vcpu-1gb"
}

output "result" {
  value = local.do_ssh_key_ids
}
