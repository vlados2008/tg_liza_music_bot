import os
import yt_dlp
import logging
import glob
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Вставьте ваш токен Telegram-бота
TOKEN = "7170536524:AAHRSLkj7e2KZD7iWYC6Q7_sA2LNBk9S1hk"

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Привет! Отправь мне название песни, и я найду её для тебя.")

async def search_music(update: Update, context: CallbackContext) -> None:
    query = update.message.text
    logging.info(f"Пользователь запросил песню: {query}")
    await update.message.reply_text(f"Ищу: {query}...")

    # Папка для сохранения файлов
    download_dir = "music"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'default_search': 'ytsearch1',
        'outtmpl': f'{download_dir}/%(title)s.%(ext)s',  # Указываем папку и имя файла
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            
            if not info:
                await update.message.reply_text("Не удалось найти песню. Попробуйте другое название.")
                return
            
            # Находим скачанный файл в папке music
            downloaded_files = glob.glob(os.path.join(download_dir, "*.mp3"))
            if not downloaded_files:
                await update.message.reply_text("Произошла ошибка при загрузке файла.")
                logging.error("Файл не найден после загрузки.")
                return

            downloaded_file = downloaded_files[0]  # Берём первый найденный mp3-файл
            logging.info(f"Ожидаемое имя файла: {downloaded_file}")

            # Проверяем, существует ли файл
            if not os.path.exists(downloaded_file):
                await update.message.reply_text("Произошла ошибка при загрузке файла.")
                logging.error(f"Файл {downloaded_file} не найден после загрузки.")
                return

        # Отправляем аудио
        with open(downloaded_file, "rb") as audio:
            await update.message.reply_audio(audio)

        # Удаляем файл после отправки
        os.remove(downloaded_file)
        logging.info(f"Файл {downloaded_file} успешно отправлен и удален.")

    except Exception as e:
        logging.error(f"Ошибка при скачивании или отправке: {e}")
        await update.message.reply_text(f"Ошибка: {str(e)}")

def main() -> None:
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))

    logging.info("Бот запущен.")
    app.run_polling()

if __name__ == "__main__":
    main()