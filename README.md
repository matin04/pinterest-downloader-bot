# 📌 Pinterest Downloader Telegram Bot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Aiogram-3.x-orange?style=for-the-badge&logo=telegram&logoColor=white" alt="Aiogram">
  <img src="https://img.shields.io/badge/Database-SQLite-green?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/License-MIT-red?style=for-the-badge" alt="License">
</p>

---

## 📖 Описание лоиҳа (About)

Асинхронный и высокопроизводительный Telegram-бот для автоматического скачивания видео и изображений из социальной сети **Pinterest**. Бот построен на современной архитектуре роутеров (Router Architecture), поддерживает мультиязычность и оптимизирован для работы под высокой нагрузкой.

---

## ✨ Ключевые Возможности (Features)

| Функция | Описание |
| :--- | :--- |
| ⚡ **Умный Парсинг** | Работает как с короткими ссылками (`pin.it`), так и с длинными (`pinterest.com`). |
| 🌍 **Мультиязычность** | Полная поддержка 3 языков: **Таджикский, Русский и Английский**. |
| 🛡 **Безопасный Кэш** | Технология *Stateless File Processing* — файлы удаляются с сервера сразу после отправки пользователю. Память сервера всегда свободна! |
| 🎛 **Админ-Панель** | Встроенная статистика пользователей и функция массовой рассылки рекламы (`📢 Рассылка`). |
| 🛑 **Валидация Ссылок** | Защита от дурака — бот автоматически проверяет чистоту ссылки и предупреждает пользователя при ошибках. |

---

## 🛠 Технологический Стек (Tech Stack)

* **Язык программирования:** `Python 3.10+`
* **Фреймворк:** `Aiogram 3.x` (Асинхронное Telegram Bot API)
* **Парсинг данных:** `BeautifulSoup4` + `Async HTTPX`
* **База данных:** `SQLite` (через асинхронную библиотеку `aiosqlite`)

---

## 📦 Инструкция по Установке и Запуску (Installation)

Вы можете развернуть этого бота на своем компьютере или сервере всего за 5 шагов:

### 1. Клонирование репозитория
```bash
git clone [https://github.com/matin04/pinterest-downloader-bot.git](https://github.com/matin04/pinterest-downloader-bot.git)
cd pinterest-downloader-bot