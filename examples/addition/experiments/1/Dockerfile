FROM python:3

ENV project_git_url https://github.com/stuhlmueller/logistician.git
ENV experiment_cmd "python examples/addition/main.py"

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