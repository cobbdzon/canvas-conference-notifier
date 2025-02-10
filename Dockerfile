FROM python:3.12.9-alpine3.21
ADD init.py .
RUN pip install python-dotenv requests discord-webhook
CMD python init.py