CREATE TABLE support_chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT NOT NULL,
    admin_response TEXT,
    timestamp DATETIME NOT NULL,
    response_timestamp DATETIME,
    FOREIGN KEY (user_id) REFERENCES user (id)
);