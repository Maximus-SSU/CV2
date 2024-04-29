Создаем таблицы в PostgreSQL
CREATE TABLE IF NOT EXISTS LinksCategory (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    link VARCHAR(255),
    pagenum INT
);

CREATE TABLE IF NOT EXISTS linksimages (
    id SERIAL PRIMARY KEY,
    category VARCHAR(255),
    name VARCHAR(255),
    link VARCHAR(255),
    dwnloadlink VARCHAR(255)
);
