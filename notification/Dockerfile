FROM python:3.5.2-slim
ADD notification.py /
ADD requirements.txt /
ADD .env /
RUN pip install --upgrade pip && pip install -r requirements.txt    
CMD [ "python", "./notification.py" ]