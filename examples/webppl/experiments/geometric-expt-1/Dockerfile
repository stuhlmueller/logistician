FROM node:boron

RUN apt-get update
RUN apt-get -y install curl build-essential git pkg-config
RUN apt-get -y install libcairo2-dev libjpeg-dev libgif-dev

RUN npm install -g nodeunit esprima grunt browserify uglifyjs mongodb
RUN npm install -g probmods/webppl#52714712bb8822983f472d4b4de5318aa46e50e1

RUN mkdir -p ~/.webppl
RUN npm install --prefix ~/.webppl webppl-timeit webppl-dp webppl-json
RUN npm install --prefix ~/.webppl null-a/webppl-nn#e7985a4fe790161b11be0699c7a6ddf82e258b8b
RUN npm install --prefix ~/.webppl null-a/webppl-fs#1801afea46148aceace9cf3fd983ae928747df04


ENV project_git_url https://github.com/stuhlmueller/logistician.git
ENV experiment_cmd "webppl examples/webppl/main.wppl --require webppl-fs"

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