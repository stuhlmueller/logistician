FROM python:3

ENV project_git_url https://github.com/stuhlmueller/logistician.git
ENV project_main_file examples/addition/main.py

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
    python /project/${project_main_file} $OPTIONS