terraform {
  required_providers {
    aws = {
        source = "hashicorp/aws"
        version = "~> 4.16"
    }
  }
}

# Configure AWS provider
provider "aws" {
    region = "eu-west-3"
}

# Create S3 bucket
resource "aws_s3_bucket" "reddit_elt" {
  bucket = "bucket_name"
  force_destroy = true # will delete contents of bucket when we run terraform destroy
}

# Set access control of bucket to private
# resource "aws_s3_bucket_acl" "s3_reddit_bucket_acl" {
#   bucket = aws_s3_bucket.reddit_elt.id
#   acl    = "private"
# }

# Create S3 Read only access role. This is assigned to Redshift cluster so that it can read data from S3
resource "aws_iam_role" "redshift_role" {
  name = "RedshiftS3ReadAccess"
  managed_policy_arns = ["arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"]
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "redshift.amazonaws.com"
        }
      },
    ]
  })
}


# Configure redshift cluster.
resource "aws_redshift_cluster" "reddit_etl" {
  cluster_identifier = "cluster_identifier"
  database_name      = "mydb"
  skip_final_snapshot = true
  master_username    = "username"
  master_password    = var.redshift_password
  node_type          = "dc2.large"
  cluster_type       = "single-node"
  publicly_accessible = "true"
  iam_roles = [aws_iam_role.redshift_role.arn]
  vpc_security_group_ids = [aws_security_group.sg_redshift.id]
}

# Configure security group for Redshift allowing all inbound/outbound traffic
resource "aws_security_group" "sg_redshift" {
  name        = "sg_redshift"
  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }
  egress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }
}
