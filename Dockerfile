FROM python:3.11

WORKDIR /spotify_proj

COPY ./requirements.txt /spotify_proj/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /spotify_proj

CMD ["python", "project.py"]