use zoodb;
-- A Stored Procedure to add a new animal with capacity check
DELIMITER $$
CREATE PROCEDURE sp_AddNewAnimal(
    IN p_animal_id INT,
    IN p_name VARCHAR(100),
    IN p_species VARCHAR(100),
    IN p_gender VARCHAR(10),
    IN p_age INT,
    IN p_habitat_id INT
)
BEGIN
    DECLARE current_occupancy INT;
    DECLARE max_capacity INT;

    -- 1. Find the maximum capacity of the chosen habitat
    SELECT capacity INTO max_capacity 
    FROM Habitat 
    WHERE habitat_id = p_habitat_id;

    -- 2. Find the current number of animals in that habitat
    SELECT COUNT(*) INTO current_occupancy 
    FROM Animal 
    WHERE habitat_id = p_habitat_id;

    -- 3. Check if there is space
    IF current_occupancy < max_capacity THEN
        -- If space is available, insert the new animal
        INSERT INTO Animal (animal_id, name, species, gender, age, habitat_id)
        VALUES (p_animal_id, p_name, p_species, p_gender, p_age, p_habitat_id);
        
        SELECT 'Success: Animal added.' AS message;
    ELSE
        -- If full, return an error message
        SELECT 'Error: Habitat is full. Cannot add animal.' AS message;
    END IF;
END$$
DELIMITER ;


-- trigger
-- A Trigger to prevent deleting a habitat that still contains animals
DELIMITER $$
CREATE TRIGGER trg_Before_Habitat_Delete
BEFORE DELETE ON Habitat
FOR EACH ROW
BEGIN
    DECLARE animal_count INT;

    -- Check if any animals are in the habitat being deleted
    SELECT COUNT(*) INTO animal_count 
    FROM Animal 
    WHERE habitat_id = OLD.habitat_id;

    -- If animals are found (count > 0), block the deletion
    IF animal_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Cannot delete habitat. It still contains animals.';
    END IF;
END$$
DELIMITER ;

-- function 
-- A Function to calculate total revenue for a given date
DELIMITER $$
CREATE FUNCTION fn_GetDailyRevenue(
    p_date DATE
)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total_revenue DECIMAL(10,2);

    SELECT SUM(price) INTO total_revenue
    FROM Ticket
    WHERE date = p_date;

    IF total_revenue IS NULL THEN
        SET total_revenue = 0.00;
    END IF;
    
    RETURN total_revenue;
END$$
DELIMITER ;

-- A Function to get the total number of animals currently in the zoo
DELIMITER $$
CREATE FUNCTION fn_GetTotalAnimalCount()
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE total_animals INT;
    SELECT COUNT(*) INTO total_animals FROM Animal;
    RETURN total_animals;
END$$
DELIMITER ;

-- A Function to get the total combined capacity of all habitats
DELIMITER $$
CREATE FUNCTION fn_GetTotalCapacity()
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE total_capacity INT;
    SELECT SUM(capacity) INTO total_capacity FROM Habitat;
    RETURN total_capacity;
END$$
DELIMITER ;

-- Complex Queries
-- 1. Aggregate Query
-- An Aggregate Query to find the average ticket price per day
SELECT 
    date, 
    AVG(price) AS average_price,
    COUNT(ticket_id) AS tickets_sold
FROM 
    Ticket
GROUP BY 
    date
ORDER BY 
    date DESC;
    
-- 2. Join Query
-- A Join Query to show animals and their habitat names
SELECT 
    A.name AS animal_name,
    A.species,
    H.name AS habitat_name,
    H.type AS habitat_type
FROM 
    Animal A
JOIN 
    Habitat H ON A.habitat_id = H.habitat_id;

-- 3. Nested Query
-- A Nested Query (Subquery) to find visitors who have not visited any animals
SELECT 
    visitor_id, 
    f_name, 
    l_name
FROM 
    Visitor
WHERE 
    visitor_id NOT IN (SELECT DISTINCT visitor_id FROM Visits);