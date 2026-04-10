CREATE TABLE article_queue (
    id                       INT           IDENTITY(1,1) PRIMARY KEY,
    source_type              VARCHAR(50)   NOT NULL,
    source_name              VARCHAR(255)  NOT NULL,
    source_record_id         VARCHAR(255)  NOT NULL,
    source_url               VARCHAR(1000) NULL,
    title                    VARCHAR(500)  NULL,
    body_text                NVARCHAR(MAX) NULL,
    published_at             VARCHAR(100)  NULL,
    sector                   VARCHAR(100)  NULL,
    market_region            VARCHAR(100)  NULL,
    commodity_group          VARCHAR(100)  NULL,
    commodity_classification VARCHAR(100)  NULL,
    commodity_name           VARCHAR(100)  NULL,
    status                   VARCHAR(50)   NOT NULL DEFAULT 'pending',
    created_at               DATETIME2     DEFAULT GETUTCDATE(),
    CONSTRAINT uq_candidates_source UNIQUE (source_type, source_name, source_record_id)
);
