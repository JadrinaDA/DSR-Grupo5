DROP TABLE IF EXISTS usuarios;

CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name TEXT NOT NULL,
    lastname TEXT NOT NULL,
    mail TEXT NOT NULL,
    password TEXT NOT NULL,
    tipo TEXT NOT NULL,
    inst TEXT NOT NULL,
    carrera TEXT NOT NULL,
    robotica BIT NOT NULL
);

DROP TABLE IF EXISTS experiencias;

CREATE TABLE experiencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    nombre TEXT NOT NULL,
    duracion INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    descripcion TEXT NOT NULL
);

DROP TABLE IF EXISTS reservas;

CREATE TABLE reservas (
    id_user INTEGER,
    id_exp INTEGER,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha TIMESTAMP NOT NULL,
    FOREIGN KEY (id_user) REFERENCES usuarios(id),
    FOREIGN KEY (id_exp) REFERENCES experiencias(id),
    PRIMARY KEY (id_user, id_exp)
);