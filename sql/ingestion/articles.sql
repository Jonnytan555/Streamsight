CREATE TABLE dbo.articles (
    id                       INT           IDENTITY(1,1) PRIMARY KEY,
    article_id               INT           NULL,
    record_id                VARCHAR(255)  NOT NULL,
    source_type              VARCHAR(50)   NOT NULL,
    source_name              VARCHAR(255)  NOT NULL,
    url                      VARCHAR(1000) NULL,
    title                    VARCHAR(500)  NULL,
    summary                  NVARCHAR(MAX) NULL,
    published_at             VARCHAR(100)  NULL,
    sector                   VARCHAR(100)  NULL,
    commodity_group          VARCHAR(100)  NULL,
    commodity_classification VARCHAR(100)  NULL,
    commodity_name           VARCHAR(100)  NULL,
    created_at               DATETIME2     DEFAULT GETUTCDATE(),
    CONSTRAINT uq_articles_source UNIQUE (source_type, source_name, record_id)
);
