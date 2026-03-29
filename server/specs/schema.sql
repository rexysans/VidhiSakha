CREATE TABLE parts (
    part_uid INTEGER PRIMARY KEY,
    part_id TEXT,
    part_name TEXT,
    article_start TEXT,
    article_end TEXT
);


CREATE TABLE articles (
    article_uid INTEGER PRIMARY KEY,
    article_id TEXT,
    title TEXT,
    full_text TEXT,
    part_uid INTEGER,
    FOREIGN KEY (part_uid) REFERENCES parts(part_uid)
);




CREATE INDEX idx_articles_article_id ON articles(article_id);
CREATE INDEX idx_articles_part_uid ON articles(part_uid);


