CREATE DATABASE IF NOT EXISTS heartdb;
USE heartdb;

-- USERS TABLE
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PREDICTIONS TABLE
DROP TABLE IF EXISTS predictions;
CREATE TABLE predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,

    age INT,
    gender INT,
    height FLOAT,
    weight FLOAT,
    ap_hi FLOAT,
    ap_lo FLOAT,
    cholesterol INT,
    gluc INT,
    smoke INT,
    alco INT,
    active INT,

    prediction VARCHAR(255),
    created_at DATETIME,

    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_predictions ON predictions(user_id);
