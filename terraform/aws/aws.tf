variable aws_instance_type {
  default = "t2.micro"
}

variable aws_region {
  default = "us-west-1"
}

variable aws_ami {
  default = "ami-e9643d89"  # ubuntu 16.10, us-west-1
}

variable aws_ami_user {
  default = "ubuntu"
}

variable experiment_name {}


resource "null_resource" "build_docker_image" {
  provisioner "local-exec" {
    command = "docker build -t ${var.experiment_name} ."
  }
}

resource "null_resource" "push_docker_image" {
  provisioner "local-exec" {
    command = <<EOF
      export DOCKER_USER_ID="${file("${path.module}/../../config/docker/username.txt")}" &&
      export DOCKER_REPOSITORY="${file("${path.module}/../../config/docker/repository.txt")}" && 
      docker tag ${var.experiment_name} $DOCKER_USER_ID/$DOCKER_REPOSITORY:${var.experiment_name} && 
      docker push $DOCKER_USER_ID/$DOCKER_REPOSITORY:${var.experiment_name}
    EOF
  }
  depends_on = ["null_resource.build_docker_image"]
}

provider "aws" {
  region = "${var.aws_region}"
}

resource "aws_key_pair" "logistician" {
  key_name   = "logistician-ssh-key"
  public_key = "${file("${path.module}/../../config/ssh-keys/ssh-key.pub")}"
}

resource "aws_security_group" "logistician" {
  name = "logistician_group"

  ingress {
    from_port = 0
    to_port = 65535
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port = 65535
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags {
    Name = "allow_all"
  }
}

resource "aws_instance" "logistician" {
  ami           = "${var.aws_ami}"
  instance_type = "${var.aws_instance_type}"
  key_name      = "logistician-ssh-key"
  vpc_security_group_ids = ["${aws_security_group.logistician.id}"]

  connection {
    type        = "ssh"
    user        = "${var.aws_ami_user}"
    private_key = "${file("${path.module}/../../config/ssh-keys/ssh-key")}"
    agent       = false
  }  

  provisioner "local-exec" {
    command = "echo ${aws_instance.logistician.public_ip} > ip-addresses.txt"
  }
  
  provisioner "remote-exec" {
    script = "${path.module}/../../scripts/setup-docker"
  }

  provisioner "remote-exec" {
    inline = [
      "export DOCKER_REPOSITORY=\"${file("${path.module}/../../config/docker/repository.txt")}\"",      
      "export DOCKER_USER_ID=\"${file("${path.module}/../../config/docker/username.txt")}\"",
      "sudo docker pull $DOCKER_USER_ID/$DOCKER_REPOSITORY:${var.experiment_name}",
      "sudo docker run -e OPTIONS=\"1 2\" -it $DOCKER_USER_ID/$DOCKER_REPOSITORY:${var.experiment_name}",
    ]
  }  
    
  # provisioner on destroy

  depends_on = ["null_resource.push_docker_image"]
}
