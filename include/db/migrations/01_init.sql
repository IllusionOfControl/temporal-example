-- 1. Таблица Пользователей
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL
);

-- 2. Таблица Отзывов
CREATE TABLE IF NOT EXISTS reviews (
    id VARCHAR(255) PRIMARY KEY,
    text TEXT NOT NULL,
    sentiment VARCHAR(50),
    summary TEXT,
    status VARCHAR(50) NOT NULL
);