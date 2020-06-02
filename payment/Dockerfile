FROM python:3.5.2-slim
ADD payment.py /
ADD /templates /templates
ADD /static /static
ADD requirements.txt /
ADD .env /
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 5006
CMD [ "python", "./payment.py" ]