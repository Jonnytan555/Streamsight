CREATE TABLE article_likes (
    id         INT          IDENTITY(1,1) PRIMARY KEY,
    article_id INT          NOT NULL REFERENCES articles(id),
    user_id    VARCHAR(255) NOT NULL,
    created_at DATETIME2    NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT uq_article_like UNIQUE (article_id, user_id)
);
