FROM python:3.5.2-slim
ADD cart.py /
ADD requirements.txt /
ADD .env /
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 5002
CMD [ "python", "./cart.py" ]