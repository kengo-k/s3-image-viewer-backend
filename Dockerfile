FROM amazon/aws-cli:2.7.35

WORKDIR /app/scripts
COPY scripts /app/scripts

ENTRYPOINT [ "/bin/bash" ]
