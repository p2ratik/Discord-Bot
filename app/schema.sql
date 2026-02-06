-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);

-- Role table already exists from tables.sql
-- Just ensuring it has the correct structure
CREATE TABLE IF NOT EXISTS role (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    user_name VARCHAR(255),
    role JSON,
    INDEX idx_role_user_id (user_id)
);

-- Sample data for testing
-- INSERT INTO users (user_id, username) VALUES ('test_user_1', 'Test User 1');
-- INSERT INTO role (user_id, user_name, role) VALUES 
--   ('test_user_1', 'Test User 1', '{"relation": ["friend"], "nicknames": ["buddy"], "age": [25]}');
--Admin Table Schema :
CREATE TABLE IF NOT EXISTS admin(
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    role JSON,
    INDEX idx_role_admin (user_id)
)

