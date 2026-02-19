# /modules/ec2/variables.tf

# --- Instance Configuration ---
variable "name_prefix" {
  description = "A unique name prefix for the instance and related resources."
  type        = string
}

variable "ami_id" {
  description = "The AMI ID for the instance. Can be from a data source or a static value."
  type        = string
}

variable "instance_type" {
  description = "The EC2 instance type."
  type        = string
}

variable "key_name" {
  description = "The name of the SSH key pair to associate with the instance."
  type        = string
  default     = null
}

variable "iam_instance_profile" {
  description = "The name of the IAM instance profile to associate with the instance."
  type        = string
  default     = null
}

variable "user_data" {
  description = "The user data script to run on instance launch. Will be base64 encoded."
  type        = string
  default     = null
}

# --- Networking Configuration ---
variable "vpc_id" {
  description = "The ID of the VPC to launch the instance in."
  type        = string
}

variable "subnet_id" {
  description = "The ID of the subnet to launch the instance into."
  type        = string
}

variable "associate_public_ip_address" {
  description = "Set to true to associate an ephemeral public IP. Ignored if associate_eip is true."
  type        = bool
  default     = false
}

variable "associate_eip" {
  description = "Set to true to allocate and associate a persistent Elastic IP."
  type        = bool
  default     = false
}

variable "source_dest_check" {
  description = "Controls whether source/destination checking is enabled. Should be false for NAT instances."
  type        = bool
  default     = true
}

# --- Security Group Configuration ---
variable "create_security_group" {
  description = "Set to true to create a new security group for this instance."
  type        = bool
  default     = true
}

variable "existing_security_group_ids" {
  description = "A list of existing security group IDs to attach to the instance."
  type        = list(string)
  default     = []
}

variable "sg_ingress_rules" {
  description = "A list of ingress rule objects for the created security group."
  type        = any
  default     = []
}

variable "sg_egress_rules" {
  description = "A list of egress rule objects for the created security group."
  type        = any
  default = [{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }]
}

# --- Storage Configuration ---
variable "root_volume_size" {
  description = "The size of the root EBS volume in GiB."
  type        = number
  default     = 25
}

variable "root_volume_type" {
  description = "The type of the root EBS volume (e.g., gp3, io2)."
  type        = string
  default     = "gp3"
}

# --- General ---
variable "tags" {
  description = "A map of tags to apply to all created resources."
  type        = map(string)
  default     = {}
}