FROM python:3.5.2-slim
ADD app.py /
ADD models.py /
ADD schema.py /
ADD requirements.txt /
ADD .env /
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 5000
CMD [ "python", "./app.py" ]