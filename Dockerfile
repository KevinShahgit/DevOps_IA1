FROM python:3.7.1-alpine
WORKDIR /DevOps_IA1/app
ADD . /DevOps_IA1/app
RUN pip install -r requirements.txt
CMD ["python","app.py"]
EXPOSE 5000