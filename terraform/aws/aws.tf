variable aws_instance_type {
  default = "t2.micro"
}

variable aws_region {
  default = "us-west-1"
}

variable aws_ami {
  default = "ami-a0edc8c0"  # ubuntu 16.10, us-west-1, +docker
  # default = "ami-e9643d89"  # ubuntu 16.10, us-west-1
}

variable aws_ami_user {
  default = "ubuntu"
}

variable experiment_name {}

variable experiment_conditions {
  default = []
}

variable aws_access_key {}
variable aws_secret_key {}
variable docker_username {}
variable docker_repository {}


resource "null_resource" "reset" {
  provisioner "local-exec" {
    command = "> machines.txt"
  }
}

resource "null_resource" "build_docker_image" {
  provisioner "local-exec" {
    command = "docker build -t ${var.experiment_name} ."
  }
  depends_on = ["null_resource.reset"]
}

resource "null_resource" "push_docker_image" {
  provisioner "local-exec" {
    command = <<EOF
      docker tag ${var.experiment_name} ${var.docker_username}/${var.docker_repository}:${var.experiment_name} && 
      docker push ${var.docker_username}/${var.docker_repository}:${var.experiment_name}
    EOF
  }
  depends_on = ["null_resource.build_docker_image"]
}

provider "aws" {
  region = "${var.aws_region}"
}

resource "aws_key_pair" "logistician" {
  key_name   = "logistician-ssh-key"
  public_key = "${file("~/.logistician/ssh-key.pub")}"
}

resource "aws_security_group" "logistician" {
  name = "logistician_group"

  ingress {
    from_port = 22  # ssh
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 2376  # docker
    to_port = 2376
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

  count = "${length(var.experiment_conditions)}"

  connection {
    type        = "ssh"
    user        = "${var.aws_ami_user}"
    private_key = "${file("~/.logistician/ssh-key")}"
    agent       = false
  }  

  provisioner "local-exec" {
    command = "echo ${self.public_ip}, ${element(var.experiment_conditions, count.index)} >> machines.txt"
  }  

  # only needed if image doesn't include docker:
  # provisioner "remote-exec" {
  #   script = "${path.module}/../../scripts/setup-docker"
  # }

  provisioner "remote-exec" {
    inline = [
      "sudo mkdir /data",
      "sudo mkdir /data/logs",
      "sudo mkdir /data/config",
      "sudo mkdir /data/results",
      "sudo docker pull ${var.docker_username}/${var.docker_repository}:${var.experiment_name}",
      "sudo docker run -d -v /data:/data -e OPTIONS=\"${element(var.experiment_conditions, count.index)}\" -it ${var.docker_username}/${var.docker_repository}:${var.experiment_name}",
    ]
  }

  # provisioner on destroy

  depends_on = ["null_resource.push_docker_image"]
}

resource "null_resource" "final" {
  provisioner "local-exec" {
    command = "echo 'All experiments running.'"
  }
  depends_on = ["aws_instance.logistician"]
}