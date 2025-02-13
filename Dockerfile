FROM python:3.9-slim

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

ENV NIXPACKS_PATH=/opt/venv/bin:$NIXPACKS_PATH

EXPOSE 8080

CMD ["python", "tg_liza_music_bot.py"]
