CREATE TYPE user_role AS ENUM ('admin', 'customer');

CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(192) NOT NULL,
    role user_role NOT NULL,
    key VARCHAR(100) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_customer_key ON users (key);

-- Insert initial admin user
INSERT INTO users (username, password_hash, role, key)
VALUES ('admin', 'scrypt:32768:8:1$UgRrpFHaOT1iP11n$03cb6fa5fb8bc5b036da53f7665e7a258e99a4f54d0db591e58649d33e2f227ba7dc2bc6f9d20d72346a5fc74fdb3bd70a89adb9e02ca21662183670138ae87a', 'admin', '00000000000000000000');