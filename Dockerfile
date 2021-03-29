FROM python:3.9-slim

RUN apt update && apt install -y \
        git \
    && rm -rf /var/lib/apt/lists/*
     

RUN git clone https://github.com/atlas0fd00m/rfcat.git && \
    cd rfcat && \
    pip3 install .

RUN pip3 install ooktools

ENTRYPOINT [ "ooktools" ]
