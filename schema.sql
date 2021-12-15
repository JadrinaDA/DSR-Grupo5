DROP TABLE IF EXISTS usuarios;

CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name TEXT NOT NULL,
    lastname TEXT NOT NULL,
    mail TEXT NOT NULL CHECK (LIKE('%@%.cl', mail) OR LIKE('%@%.com', mail)), 
    password TEXT NOT NULL CHECK (length(password) > 5),
    tipo TEXT NOT NULL,
    inst TEXT NOT NULL,
    carrera TEXT NOT NULL,
    robotica BIT NOT NULL,
    blacklist BIT NOT NULL DEFAULT 0
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
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    id_enc INTEGER NOT NULL,
    taken BIT NOT NULL DEFAULT 1,
    FOREIGN KEY (id_user) REFERENCES usuarios(id),
    FOREIGN KEY (id_exp) REFERENCES experiencias(id),
    FOREIGN KEY (id_enc) REFERENCES usuarios(id),
    PRIMARY KEY (id_user, id_exp, fecha, hora)
);

DROP TABLE IF EXISTS estudiante_de;

CREATE TABLE estudiante_de (
    id_est INTEGER,
    id_prof INTEGER,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_est) REFERENCES usuarios(id),
    FOREIGN KEY (id_prof) REFERENCES usuarios(id),
    PRIMARY KEY (id_est, id_prof)
);


DROP TABLE IF EXISTS mensajes;

CREATE TABLE mensajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL,
    asunto TEXT NOT NULL,
    comentario TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);