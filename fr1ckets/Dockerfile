FROM python:2

WORKDIR /src

# install the deps first, creates a nice snapshot
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

COPY src /src

EXPOSE 8080

#CMD [ "python", "./wsgi.py" ]
CMD [ "gunicorn", "-b", "0.0.0.0:8080", "-w", "8", "wsgi:app" ]
