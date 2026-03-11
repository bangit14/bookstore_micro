-- Initialize MySQL databases for all MySQL services

CREATE DATABASE IF NOT EXISTS customer_db;
CREATE DATABASE IF NOT EXISTS cart_db;
CREATE DATABASE IF NOT EXISTS staff_db;
CREATE DATABASE IF NOT EXISTS manager_db;
CREATE DATABASE IF NOT EXISTS ship_db;
CREATE DATABASE IF NOT EXISTS book_db;
CREATE DATABASE IF NOT EXISTS catalog_db;
CREATE DATABASE IF NOT EXISTS order_db;
CREATE DATABASE IF NOT EXISTS pay_db;
CREATE DATABASE IF NOT EXISTS comment_rate_db;
CREATE DATABASE IF NOT EXISTS recommender_ai_db;

-- Grant privileges (optional, but recommended for security)
-- You can create separate users for each service here
-- Example:
-- CREATE USER 'customer_user'@'%' IDENTIFIED BY 'password';
-- GRANT ALL PRIVILEGES ON customer_db.* TO 'customer_user'@'%';

FLUSH PRIVILEGES;
