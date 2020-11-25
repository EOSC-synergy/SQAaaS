FROM python

RUN git clone https://github.com/eosc-synergy/sqaaas-api-server \
    /sqaaas-api-server

WORKDIR /sqaaas-api-server
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "-m", "openapi_server"]
EXPOSE 8080
