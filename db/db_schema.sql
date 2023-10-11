CREATE SCHEMA IF NOT EXISTS content;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS content.users (
    id INT PRIMARY KEY,
    name TEXT NOT NULL,
    created timestamp with time zone DEFAULT now(),
    modified timestamp with time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS content.task (
    id uuid DEFAULT uuid_generate_v4(),
    user_id int NOT NULL,
    task TEXT NOT NULL,
    target_date DATE NOT NULL,
    created timestamp with time zone DEFAULT now(),
    modified timestamp with time zone DEFAULT now(),
    task_status TEXT DEFAULT 'active',
    PRIMARY KEY (id),
    CONSTRAINT fk_user_id
        FOREIGN KEY(user_id)
            REFERENCES content.users(id)
            ON DELETE CASCADE
);

ALTER ROLE sam SET search_path TO content,public;
CREATE UNIQUE INDEX user_id_task_date_idx ON content.task (user_id, task, target_date);