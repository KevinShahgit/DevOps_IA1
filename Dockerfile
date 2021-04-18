FROM python:3.7.1-alpine
WORKDIR /DevOps_IA1
ADD . /DevOps_IA1
RUN pip install -r requirements.txt
CMD ["python","app.py"]
EXPOSE 5000