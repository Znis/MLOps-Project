provider "aws" {
  region = "us-east-1" 
}

data "aws_vpc" "default" {
  id = "vpc-0d4d9002a7a841ad3"
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

module "ec2" {
  source                      = "./ec2"
  name_prefix                      = "MLOps-app"
  ami_id                      =  var.ami_id
  instance_type               = var.instance_type
  key_name                    = var.key_name
  root_volume_size = 50
  associate_public_ip_address = true
  vpc_id                      = data.aws_vpc.default.id
  subnet_id = data.aws_subnets.default.ids[0]
  user_data                   = file("./user-data.sh")
  sg_ingress_rules = [
    {
      description = "Allow HTTPS"
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    },
    {
      description = "Allow HTTP"
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    },
    {
      description = "Allow SSH"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"] 
    },
    {
      description = "Allow Backend API"
      from_port   = 8000
      to_port     = 8000
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    },
    {
      description = "Allow Custom App Port"
      from_port   = 6333
      to_port     = 6333
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  ]
}
