FROM nvidia/cuda

RUN apt-get update
RUN apt-get install -y git-all
RUN apt-get install -y python3


## Conda
## - https://github.com/ContinuumIO/docker-images/blob/master/anaconda3/Dockerfile

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1 \
    git mercurial subversion

RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/archive/Anaconda3-4.4.0-Linux-x86_64.sh -O ~/anaconda.sh && \
    /bin/bash ~/anaconda.sh -b -p /opt/conda && \
    rm ~/anaconda.sh

RUN apt-get install -y curl grep sed dpkg && \
    TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
    curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
    dpkg -i tini.deb && \
    rm tini.deb && \
    apt-get clean

ENV PATH /opt/conda/bin:$PATH


## PyTorch

RUN conda install pytorch torchvision -c soumith -y
RUN conda install jupyter -y


ENV project_git_url https://github.com/stuhlmueller/logistician.git
ENV experiment_cmd "python examples/pytorch-gpu/main.py"

# Placeholders in case this Docker image isn't mounted with an appropriate volume at /data
RUN mkdir /data
RUN mkdir /data/logs
RUN mkdir /data/config
RUN mkdir /data/results

CMD if [ ! -d "/project" ]; then \
      git clone ${project_git_url} /project; \
    fi && \
    cd /project && \
    git log -1 > /data/config/git.txt && \
    echo "$OPTIONS" > /data/config/options.txt && \
    eval "$experiment_cmd $OPTIONS"