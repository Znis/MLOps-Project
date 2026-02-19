terraform {
  backend "s3" {
    bucket       = "mlops1234-terraform-state-bucket"
    key          = "terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}