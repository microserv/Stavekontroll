FROM localhost:5000/backend-comm
MAINTAINER Pål Karlsrud <paal@128.no>

ENV BASE_DIR /var/spell-check

RUN git clone https://github.com/microserv/spell-check ${BASE_DIR}

RUN cp ${BASE_DIR}/spell-check.ini /etc/supervisor.d/

RUN virtualenv ${BASE_DIR}/venv
ENV PATH ${BASE_DIR}/venv/bin:$PATH

WORKDIR ${BASE_DIR}
RUN pip install -r requirements.txt
RUN mv ${BASE_DIR}/local_config.py.example ${BASE_DIR}/local_config.py

EXPOSE 80
