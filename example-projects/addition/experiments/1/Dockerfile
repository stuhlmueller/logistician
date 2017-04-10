FROM python:3

ENV project_git_url https://github.com/stuhlmueller/logistician.git
ENV project_main_file example-projects/addition/main.py

CMD if [ ! -d "/project" ]; then \
      git clone ${project_git_url} /project; \
    fi && \
    python /project/${project_main_file} $OPTIONS