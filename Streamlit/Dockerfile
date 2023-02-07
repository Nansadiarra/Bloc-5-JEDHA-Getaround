FROM continuumio/miniconda3

WORKDIR /home/app

RUN apt-get update

RUN pip install pandas numpy streamlit plotly openpyxl
COPY . /home/app

CMD streamlit run --server.port $PORT app.py