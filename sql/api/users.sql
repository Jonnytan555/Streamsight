CREATE TABLE users (
    id            INT           IDENTITY(1,1) PRIMARY KEY,
    username      VARCHAR(255)  NOT NULL UNIQUE,
    password_hash VARCHAR(255)  NOT NULL,
    name          VARCHAR(255)  NOT NULL,
    email         VARCHAR(255)  NULL,
    created_at    DATETIME2     NOT NULL DEFAULT GETUTCDATE()
);
