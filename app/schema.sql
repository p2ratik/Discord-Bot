-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on users
CREATE INDEX IF NOT EXISTS idx_user_id ON users (user_id);

-- Role table
CREATE TABLE IF NOT EXISTS role (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    user_name VARCHAR(255),
    role JSONB
);

-- Create index on role
CREATE INDEX IF NOT EXISTS idx_role_user_id ON role (user_id);

-- Sample data for testing
-- INSERT INTO users (user_id, username) VALUES ('test_user_1', 'Test User 1');
-- INSERT INTO role (user_id, user_name, role) VALUES 
--   ('test_user_1', 'Test User 1', '{"relation": ["friend"], "nicknames": ["buddy"], "age": [25]}');

-- Admin Table Schema
CREATE TABLE IF NOT EXISTS admin (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    role JSONB
);

-- Create index on admin
CREATE INDEX IF NOT EXISTS idx_role_admin ON admin (user_id);

-- Trigger function to auto-update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to users table
DROP TRIGGER IF EXISTS trigger_update_users_updated_at ON users;
CREATE TRIGGER trigger_update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Vector chats
CREATE TABLE chat_vectors (
    id SERIAL PRIMARY KEY,
    user_id TEXT,
    incoming TEXT,
    reply TEXT,
    embedding vector(384)
);