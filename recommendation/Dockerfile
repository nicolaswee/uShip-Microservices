FROM python:3.5.2-slim
ADD recommendation.py /
ADD requirements.txt /
ADD .env /
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 5005
CMD [ "python", "./recommendation.py" ]