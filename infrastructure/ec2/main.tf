resource "aws_instance" "ec2_instance" {
  ami                         = var.ami_id
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  associate_public_ip_address = var.associate_public_ip_address
  key_name                    = var.key_name
  iam_instance_profile        = var.iam_instance_profile
  vpc_security_group_ids      = local.security_group_ids
  source_dest_check           = var.source_dest_check
  user_data                   = var.user_data

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = var.root_volume_type
  }
  

  tags = merge(
    var.tags,
    {
      Name = var.name_prefix
    }
  )
}

resource "aws_eip" "eip" {
  count = var.associate_eip ? 1 : 0
  tags = merge(
    var.tags,
    {
      Name = var.name_prefix
    }
  )
}

resource "aws_eip_association" "eip_association" {
  count = var.associate_eip ? 1 : 0
  instance_id   = aws_instance.ec2_instance.id
  allocation_id = aws_eip.eip[0].id
}

