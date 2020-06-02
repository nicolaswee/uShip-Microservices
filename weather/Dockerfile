FROM python:3.5.2-slim
ADD weather.py /
ADD requirements.txt /
ADD .env /
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 5004
CMD [ "python", "./weather.py" ]