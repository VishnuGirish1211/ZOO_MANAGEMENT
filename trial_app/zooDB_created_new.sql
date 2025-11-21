CREATE DATABASE ZooDB;
USE ZooDB;

CREATE TABLE Habitat (
    habitat_id INT PRIMARY KEY,
    name VARCHAR(100),
    type VARCHAR(50),
    capacity INT
);

CREATE TABLE Animal (
    animal_id INT PRIMARY KEY,
    name VARCHAR(100),
    species VARCHAR(100),
    gender VARCHAR(10),
    age INT,
    habitat_id INT,
    FOREIGN KEY (habitat_id) REFERENCES Habitat(habitat_id)
);

CREATE TABLE Diet (
    diet_id INT PRIMARY KEY,
    type VARCHAR(50),
    description TEXT
);

CREATE TABLE Feeding_Log (
    log_id INT,
    animal_id INT,
    diet_id INT,
    date_time DATETIME,
    qty INT,
    PRIMARY KEY (log_id, animal_id, diet_id),
    FOREIGN KEY (animal_id) REFERENCES Animal(animal_id),
    FOREIGN KEY (diet_id) REFERENCES Diet(diet_id)
);

CREATE TABLE Visitor (
    visitor_id INT PRIMARY KEY,
    f_name VARCHAR(50),
    l_name VARCHAR(50),
    age INT,
    phone_no VARCHAR(20)
);

CREATE TABLE Ticket (
    ticket_id INT PRIMARY KEY,
    transaction_id VARCHAR(50),
    price DECIMAL(10,2),
    date DATE,
    pay_mode VARCHAR(50),
    visitor_id INT UNIQUE,
    FOREIGN KEY (visitor_id) REFERENCES Visitor(visitor_id)
);

CREATE TABLE Employee (
    employee_id INT PRIMARY KEY,
    name VARCHAR(100),
    phone_no VARCHAR(20),
    role VARCHAR(50),
    start_date DATE,
    supervisor_id INT,
    FOREIGN KEY (supervisor_id) REFERENCES Employee(employee_id)
);

CREATE TABLE Visits (
    visitor_id INT,
    animal_id INT,
    PRIMARY KEY (visitor_id, animal_id),
    FOREIGN KEY (visitor_id) REFERENCES Visitor(visitor_id),
    FOREIGN KEY (animal_id) REFERENCES Animal(animal_id)
);

CREATE TABLE Assigned (
    employee_id INT,
    habitat_id INT,
    PRIMARY KEY (employee_id, habitat_id),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id),
    FOREIGN KEY (habitat_id) REFERENCES Habitat(habitat_id)
);

-- Habitats values
INSERT INTO Habitat (habitat_id, name, type, capacity) VALUES
(1, 'Lion Den', 'Savannah', 5),
(2, 'Reptile House', 'Tropical', 20);

-- Insert Animals 
INSERT INTO Animal (animal_id, name, species, gender, age, habitat_id) VALUES
(101, 'Simba', 'Lion', 'Male', 5, 1),
(102, 'Nala', 'Lion', 'Female', 4, 1),
(201, 'Rango', 'Chameleon', 'Male', 2, 2);

-- Insert Diets
INSERT INTO Diet (diet_id, type, description) VALUES
(1, 'Meat', 'Raw meat diet for carnivores'),
(2, 'Insects', 'Insect diet for reptiles and birds');

-- Insert Visitors
INSERT INTO Visitor (visitor_id, f_name, l_name, age, phone_no) VALUES
(1, 'John', 'Doe', 30, '555-1234'),
(2, 'Jane', 'Smith', 28, '555-5678');

-- Insert Tickets (reference visitor_id)
INSERT INTO Ticket (ticket_id, transaction_id, price, date, pay_mode, visitor_id) VALUES
(1, 'TXN1001', 25.00, '2025-10-01', 'Card', 1),
(2, 'TXN1002', 25.00, '2025-10-01', 'Cash', 2);

-- Insert Employees (supervisor_id can be NULL)
INSERT INTO Employee (employee_id, name, phone_no, role, start_date, supervisor_id) VALUES
(1, 'Alice Johnson', '555-7890', 'Manager', '2020-01-01', NULL),
(2, 'Bob Lee', '555-2345', 'Zookeeper', '2022-06-15', 1);

-- Assign Employees to Habitats
INSERT INTO Assigned (employee_id, habitat_id) VALUES
(2, 1);

-- Insert Feeding Logs (reference animal_id and diet_id)
INSERT INTO Feeding_Log (log_id, animal_id, diet_id, date_time, qty) VALUES
(1, 101, 1, '2025-10-01 09:00:00', 10),
(2, 102, 1, '2025-10-01 09:15:00', 8),
(3, 201, 2, '2025-10-01 10:00:00', 5);

-- Visitor visits Animals
INSERT INTO Visits (visitor_id, animal_id) VALUES
(1, 101),
(2, 201);



SELECT * FROM Habitat;

SELECT * FROM Animal;

SELECT * FROM Diet;

SELECT * FROM Feeding_Log;

SELECT * FROM Visitor;

SELECT * FROM Ticket;

SELECT * FROM Employee;

SELECT * FROM Visits;

SELECT * FROM Assigned;

-- 🌍 More Habitats (new IDs: 11–18)
INSERT INTO Habitat (habitat_id, name, type, capacity) VALUES
(11, 'Panda Valley', 'Temperate', 6),
(12, 'Wolf Ridge', 'Mountain', 12),
(13, 'Tiger Territory', 'Jungle', 8),
(14, 'Shark Tank', 'Aquatic', 20),
(15, 'Flamingo Lake', 'Wetland', 25),
(16, 'Bear Cave', 'Forest', 10),
(17, 'Koala Grove', 'Eucalyptus', 15),
(18, 'Camel Dunes', 'Desert', 10);

-- 🐾 More Animals (new IDs: 701–710)
INSERT INTO Animal (animal_id, name, species, gender, age, habitat_id) VALUES
(701, 'Po', 'Panda', 'Male', 5, 11),
(702, 'Luna', 'Wolf', 'Female', 6, 12),
(703, 'Rajah', 'Tiger', 'Male', 7, 13),
(704, 'Shere Khan', 'Tiger', 'Male', 10, 13),
(705, 'Jaws', 'Shark', 'Male', 15, 14),
(706, 'Coral', 'Shark', 'Female', 12, 14),
(707, 'Pinkie', 'Flamingo', 'Female', 4, 15),
(708, 'Baloo', 'Bear', 'Male', 9, 16),
(709, 'Koko', 'Koala', 'Male', 3, 17),
(710, 'Sahara', 'Camel', 'Female', 8, 18);

-- 🍽 More Diets (new IDs: 11–18)
INSERT INTO Diet (diet_id, type, description) VALUES
(11, 'Bamboo', 'Diet of bamboo for pandas'),
(12, 'Meat Mix', 'Raw meat and bones for wolves'),
(13, 'Big Cat Meat', 'Special carnivore diet for tigers'),
(14, 'Fish & Seal', 'Shark diet with fish and seals'),
(15, 'Algae & Crustaceans', 'Supplement diet for aquatic animals'),
(16, 'Shrimp & Krill', 'Small fish and krill for flamingos'),
(17, 'Honey & Berries', 'Bear diet with fruits and honey'),
(18, 'Eucalyptus Leaves', 'Fresh eucalyptus leaves for koalas');

-- 📖 More Feeding Logs (new IDs: 20–29)
INSERT INTO Feeding_Log (log_id, animal_id, diet_id, date_time, qty) VALUES
(20, 701, 11, '2025-10-05 09:00:00', 30),
(21, 702, 12, '2025-10-05 10:00:00', 12),
(22, 703, 13, '2025-10-05 11:00:00', 14),
(23, 704, 13, '2025-10-05 11:30:00', 16),
(24, 705, 14, '2025-10-05 12:00:00', 20),
(25, 706, 15, '2025-10-05 12:30:00', 18),
(26, 707, 16, '2025-10-05 13:00:00', 10),
(27, 708, 17, '2025-10-05 13:30:00', 25),
(28, 709, 18, '2025-10-05 14:00:00', 8),
(29, 710, 16,  '2025-10-05 14:30:00', 40);

-- 👥 More Visitors (new IDs: 11–20)
INSERT INTO Visitor (visitor_id, f_name, l_name, age, phone_no) VALUES
(11, 'Bruce', 'Banner', 42, '555-3001'),
(12, 'Clint', 'Barton', 39, '555-3002'),
(13, 'Stephen', 'Strange', 45, '555-3003'),
(14, 'Wanda', 'Maximoff', 29, '555-3004'),
(15, 'Sam', 'Wilson', 34, '555-3005'),
(16, 'Bucky', 'Barnes', 38, '555-3006'),
(17, 'Carol', 'Danvers', 33, '555-3007'),
(18, 'TChalla', 'Udaku', 37, '555-3008'),
(19, 'Shuri', 'Udaku', 25, '555-3009'),
(20, 'Nick', 'Fury', 55, '555-3010');

-- 🎟 More Tickets (new IDs: 11–20)
INSERT INTO Ticket (ticket_id, transaction_id, price, date, pay_mode, visitor_id) VALUES
(11, 'TXN1011', 35.00, '2025-10-05', 'UPI', 11),
(12, 'TXN1012', 28.00, '2025-10-05', 'Card', 12),
(13, 'TXN1013', 40.00, '2025-10-05', 'Cash', 13),
(14, 'TXN1014', 30.00, '2025-10-05', 'Card', 14),
(15, 'TXN1015', 25.00, '2025-10-05', 'UPI', 15),
(16, 'TXN1016', 33.00, '2025-10-06', 'Cash', 16),
(17, 'TXN1017', 29.00, '2025-10-06', 'Card', 17),
(18, 'TXN1018', 50.00, '2025-10-06', 'UPI', 18),
(19, 'TXN1019', 45.00, '2025-10-06', 'Card', 19),
(20, 'TXN1020', 60.00, '2025-10-06', 'Cash', 20);

-- 🧑‍🌾 More Employees (new IDs: 11–20)
INSERT INTO Employee (employee_id, name, phone_no, role, start_date, supervisor_id) VALUES
(11, 'Steve Rogers', '555-4001', 'Guide', '2022-01-01', 1),
(12, 'Diana Prince', '555-4002', 'Veterinarian', '2021-04-04', 1),
(13, 'Barry Allen', '555-4003', 'Zookeeper', '2023-05-05', 1),
(14, 'Arthur Curry', '555-4004', 'Aquarist', '2022-06-06', 1),
(15, 'Victor Stone', '555-4005', 'Engineer', '2021-07-07', 1),
(16, 'Hal Jordan', '555-4006', 'Trainer', '2023-08-08', 1),
(17, 'Logan Howlett', '555-4007', 'Security', '2020-09-09', 1),
(18, 'Jean Grey', '555-4008', 'Biologist', '2022-10-10', 1),
(19, 'Charles Xavier', '555-4009', 'Manager', '2019-11-11', NULL),
(20, 'Erik Lehnsherr', '555-4010', 'Trainer', '2021-12-12', 19);

-- 🗂 More Assigned Employees (new unique pairs)
INSERT INTO Assigned (employee_id, habitat_id) VALUES
(11, 11),
(12, 12),
(13, 13),
(14, 14),
(15, 15),
(16, 16),
(17, 17),
(18, 18),
(19, 11),
(20, 13);

-- 🧍‍♂️ More Visits (new unique pairs)
INSERT INTO Visits (visitor_id, animal_id) VALUES
(11, 701),
(12, 702),
(13, 703),
(14, 704),
(15, 705),
(16, 706),
(17, 707),
(18, 708),
(19, 709),
(20, 710);





--





