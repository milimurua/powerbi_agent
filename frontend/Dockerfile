FROM python:3.12-slim

WORKDIR /app

RUN pip install streamlit requests

COPY frontend .

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]