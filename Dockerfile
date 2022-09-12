FROM python:3.8-slim-bullseye
LABEL maintainer="William Arias"
COPY ./tech-trends  app/
WORKDIR /app
RUN rm myapp.log
RUN pip install -r requirements.txt
RUN python init_db.py
EXPOSE 7111
CMD ["python", "app.py"]


