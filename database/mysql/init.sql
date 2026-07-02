CREATE DATABASE IF NOT EXISTS trading_demo;
USE trading_demo;

CREATE TABLE IF NOT EXISTS orders (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  order_id VARCHAR(64) NOT NULL UNIQUE,
  account_id VARCHAR(32) NOT NULL,
  symbol VARCHAR(32) NOT NULL,
  side VARCHAR(8) NOT NULL,
  quantity INT NOT NULL,
  price DECIMAL(18, 4) NOT NULL,
  status VARCHAR(16) NOT NULL,
  reject_reason VARCHAR(255),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_orders_account_id (account_id),
  INDEX idx_orders_status (status),
  INDEX idx_orders_symbol (symbol),
  INDEX idx_orders_created_at (created_at)
);

CREATE TABLE IF NOT EXISTS accounts (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  account_id VARCHAR(32) NOT NULL UNIQUE,
  cash_balance DECIMAL(18, 2) NOT NULL,
  risk_limit DECIMAL(18, 2) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS positions (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  account_id VARCHAR(32) NOT NULL,
  symbol VARCHAR(32) NOT NULL,
  quantity INT NOT NULL,
  average_price DECIMAL(18, 4) NOT NULL,
  market_value DECIMAL(18, 2) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_positions_account_symbol (account_id, symbol),
  INDEX idx_positions_account_id (account_id)
);

INSERT INTO orders (order_id, account_id, symbol, side, quantity, price, status, reject_reason)
VALUES
  ('ORD-SEED-001', 'ACC001', 'LME-CA', 'BUY', 120, 9124.5000, 'ACCEPTED', NULL),
  ('ORD-SEED-002', 'ACC001', 'LME-AL', 'SELL', 60, 2380.2500, 'CANCELLED', NULL),
  ('ORD-SEED-003', 'ACC002', 'LME-ZN', 'BUY', 15000, 2740.0000, 'REJECTED', 'Quantity exceeds limit'),
  ('ORD-SEED-004', 'ACC003', 'LME-NI', 'BUY', 25, 18550.7500, 'ACCEPTED', NULL)
ON DUPLICATE KEY UPDATE order_id = VALUES(order_id);

INSERT INTO accounts (account_id, cash_balance, risk_limit)
VALUES
  ('ACC001', 1250000.00, 3000000.00),
  ('ACC002', 860000.00, 1500000.00),
  ('ACC003', 540000.00, 1000000.00)
ON DUPLICATE KEY UPDATE account_id = VALUES(account_id);

INSERT INTO positions (account_id, symbol, quantity, average_price, market_value)
VALUES
  ('ACC001', 'LME-CA', 100, 9080.5000, 908050.00),
  ('ACC001', 'LME-AL', 200, 2365.0000, 473000.00),
  ('ACC002', 'LME-ZN', 120, 2722.2500, 326670.00),
  ('ACC003', 'LME-NI', 30, 18520.0000, 555600.00)
ON DUPLICATE KEY UPDATE market_value = VALUES(market_value);

