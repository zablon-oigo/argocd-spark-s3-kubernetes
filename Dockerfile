FROM apache/spark:3.5.1

USER root

WORKDIR /app

COPY spark-job.py /app/spark-job.py

RUN chown -R 185:0 /app && \
    chmod -R g+rwX /app

USER 185

CMD ["python", "/app/spark-job.py"]