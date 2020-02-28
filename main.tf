provider "digitalocean" {
  token = var.do_token
}

module "do_ssh_keys" {
  source = "github.com/hleb-rubanau/terraform-module-digitalocean-ssh-key-ids"
  keys   = var.keys
}

locals {
  do_ssh_key_ids = values(module.do_ssh_keys.data)[*].id
}

output "result" {
  value = local.do_ssh_key_ids
}
