-- Database schema version 0.0.1
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE app_details (
  detail_id INTEGER PRIMARY KEY CHECK (detail_id = 0),
  db_version TEXT NOT NULL,
  app_version TEXT NOT NULL
);

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  displayname TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE csrf (
  id INTEGER UNIQUE PRIMARY KEY,
  token TEXT UNIQUE NOT NULL,
  expire INTEGER NOT NULL
);
