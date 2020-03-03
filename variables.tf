variable "do_token" {}
variable "keys" {
  type    = list(string)
  default = []
}

variable "letsencrypt_account" {}

variable "demo_domain"  {}
variable "demo_client_subdomain" { default="client" }
variable "demo_server_subdomain" { default="target" }

variable "demo_protection_password" {} 
