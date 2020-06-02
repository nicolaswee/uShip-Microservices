FROM python:3.5.2-slim
ADD news.py /
ADD requirements.txt /
ADD .env /
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN [ "python", "-c", "import nltk; nltk.download('all', download_dir='/usr/local/nltk_data')" ]
EXPOSE 5003
CMD [ "python", "./news.py" ]