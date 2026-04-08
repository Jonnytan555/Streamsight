CREATE TABLE blocked_domains (
    id                    INT          IDENTITY(1,1) PRIMARY KEY,
    domain                VARCHAR(255) NOT NULL UNIQUE,
    consecutive_zero_runs INT          NOT NULL DEFAULT 0,
    blocked_at            DATETIME2    NULL,
    reason                VARCHAR(500) NULL,
    last_checked_at       DATETIME2    NOT NULL DEFAULT GETUTCDATE()
);
