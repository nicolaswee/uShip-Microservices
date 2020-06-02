FROM python:3.5.2-slim
ADD product.py /
ADD requirements.txt /
ADD .env /
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 5001
CMD [ "python", "./product.py" ]