CREATE TABLE llm_usage (
    id                 INT          IDENTITY(1,1) PRIMARY KEY,
    called_at          DATETIME2    NOT NULL DEFAULT GETUTCDATE(),
    provider           VARCHAR(50)  NOT NULL,
    model              VARCHAR(100) NOT NULL,
    caller             VARCHAR(255) NULL,
    input_tokens       INT          DEFAULT 0,
    output_tokens      INT          DEFAULT 0,
    estimated_cost_usd FLOAT        DEFAULT 0.0
);
