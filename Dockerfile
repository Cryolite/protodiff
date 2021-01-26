FROM ubuntu:latest

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
      protobuf-compiler \
      python3 \
      python3-pip \
      wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    pip3 install -U pip && pip3 install -U \
      protobuf && \
    useradd -ms /bin/bash ubuntu && \
    mkdir -p /opt/protodiff && \
    chown -R ubuntu /opt/protodiff

COPY --chown=ubuntu protodiff.sh /opt/protodiff/
COPY --chown=ubuntu normalize.py /opt/protodiff/

USER ubuntu

WORKDIR /opt/protodiff

ENTRYPOINT ["/opt/protodiff/protodiff.sh"]
