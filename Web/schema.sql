DROP TABLE IF EXISTS usuarios;

CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name TEXT NOT NULL,
    mail TEXT NOT NULL,
    password TEXT NOT NULL,
    tipo TEXT NOT NULL,
    robotica BIT NOT NULL
);