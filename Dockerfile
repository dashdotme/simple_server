FROM python:3.8-slim-buster
RUN pip3 install requests
WORKDIR /assignment1
COPY . .
CMD python assign1server.py $PORT
#CMD ["python3", "assign1server.py", "8080"]