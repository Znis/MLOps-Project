variable "ami_id" {
  description = "The AMI ID for the main application EC2 instance."
  type        = string
}

variable "instance_type" {
  description = "The instance type for the main application EC2 instance."
  type        = string
}

variable "key_name" {
  description = "The name of the SSH key pair for the application instance."
  type        = string
}



