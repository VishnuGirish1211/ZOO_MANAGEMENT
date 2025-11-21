use zoodb;
-- 1. Add columns for login
ALTER TABLE Employee
ADD COLUMN username VARCHAR(50) UNIQUE,
ADD COLUMN password VARCHAR(255); -- In a real app, this MUST be a hashed password

-- 2. Add sample login info for our key roles
-- We'll use simple passwords for this project.
-- User: 'ajohnson' (Manager), Pass: 'manager123'
UPDATE Employee 
SET username = 'ajohnson', password = 'manager123' 
WHERE employee_id = 1; -- Alice Johnson (Manager)

-- User: 'ballen' (Zookeeper), Pass: 'zoo123'
UPDATE Employee 
SET username = 'ballen', password = 'zoo123' 
WHERE employee_id = 13; -- Barry Allen (Zookeeper)
