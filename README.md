# Prerequisites

1. Account on DigitalOcean, and API token attached to it
2. Domain zone managed by DigitalOcean -- could be top-level domain, or a third+ level. Demo would create DNS records under the domain.
3. Terraform 0.12 installed on your machine

# Demo configuration

1. Copy terraform.tfvars.example under the name terraform.tfvars, and fill the values. 

* `do_token` -- DigitalOcean's API token for your account
* `letsencrypt_account` -- your email, used to represent your account on letsencrypt.org. No registration needed.
* `demo_domain` -- domain zone under which demo would create subdomains (you must own the domain and have zone managed by DigitalOcean)
* `demo_client_subdomain` (default: `client`), `demo_server_subdomain` (default: `target`) -- subdomains to be created under the zone specified
* `demo_protection_user`, `demo_protection_password` -- pair of static login credentials, used to protect demo web page from random bots and strangers

# Demo
1. Run `terraform apply`, and confirm creation of resources set (2 droplets, 2 domain names).
2. Few minutes after provisioning success, visit `https://<demo_client_subdomain>.<demo_domain>`. Enter credentials specified in `terraform.tfvars`, and follow the instructions
