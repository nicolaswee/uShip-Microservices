FROM python:3.5.2-slim
ADD user.py /
ADD requirements.txt /
ADD .env /
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 5007
CMD [ "python", "./user.py" ]