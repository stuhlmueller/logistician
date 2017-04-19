# You can edit the environment setup up below

FROM python:3

ENV project_git_url %(project_git_url)s
ENV experiment_cmd "%(experiment_cmd)s"

# RUN apt-get -y install cmake



# --------------------------------------------------------------------
# Don't edit below this line
# --------------------------------------------------------------------

RUN mkdir /data
RUN mkdir /data/logs
RUN mkdir /data/config
RUN mkdir /data/results

CMD if [ ! -d "/project" ]; then \
      git clone ${project_git_url} /project; \
    fi && \
    cd /project && \
    if [ -w /data/ ]; then \
      git log -1 > /data/config/git.txt && \
      echo "$OPTIONS" > /data/config/options.txt; \
    fi && \    
    eval "$experiment_cmd $OPTIONS"