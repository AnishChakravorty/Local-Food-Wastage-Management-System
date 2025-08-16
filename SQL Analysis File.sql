CREATE DATABASE food_wastage_db;
USE food_wastage_db;

-- Data Cleaning

SET SQL_SAFE_UPDATES = 0;

-- Remove all non-digit characters
UPDATE providers_data
SET Contact = REGEXP_REPLACE(Contact, '[^0-9]', '');

UPDATE receivers_data
SET Contact = REGEXP_REPLACE(Contact, '[^0-9]', '');

-- Format numbers with country code +1 if missing
UPDATE providers_data
SET Contact = CONCAT('+1-', 
                     SUBSTRING(Contact, 1, 3), '-', 
                     SUBSTRING(Contact, 4, 3), '-', 
                     SUBSTRING(Contact, 7, 4))
WHERE LENGTH(Contact) = 10;

UPDATE receivers_data
SET Contact = CONCAT('+1-', 
                     SUBSTRING(Contact, 1, 3), '-', 
                     SUBSTRING(Contact, 4, 3), '-', 
                     SUBSTRING(Contact, 7, 4))
WHERE LENGTH(Contact) = 10;

-- Add country code +1 if length = 10 (US standard)
UPDATE providers_data
SET Contact = CONCAT('+1', Contact)
WHERE LENGTH(Contact) = 10;

UPDATE receivers_data
SET Contact = CONCAT('+1', Contact)
WHERE LENGTH(Contact) = 10;

-- Trim numbers longer than 12 digits (keep first 12 for country code + number)

UPDATE providers_data
SET Contact = LEFT(Contact, 12)
WHERE LENGTH(Contact) > 12;

UPDATE receivers_data
SET Contact = LEFT(Contact, 12)
WHERE LENGTH(Contact) > 12;

-- Convert the string to DATETIME

UPDATE claims_data
SET Timestamp = STR_TO_DATE(Timestamp, '%m/%d/%Y %H:%i');

ALTER TABLE claims_data
MODIFY COLUMN Timestamp DATETIME;

-- Convert string to DATE

UPDATE food_listings_data
SET Expiry_Date = STR_TO_DATE(Expiry_Date, '%m/%d/%Y');

ALTER TABLE food_listings_data
MODIFY COLUMN Expiry_Date DATE;


-- 1. How many food providers and receivers are there in each city?

SELECT 
    City,
    (SELECT COUNT(*) FROM providers_data p WHERE p.City = r.City) AS Total_Providers,
    (SELECT COUNT(*) FROM receivers_data rc WHERE rc.City = r.City) AS Total_Receivers
FROM receivers_data r
GROUP BY City;

-- 2. Which type of food provider contributes the most food?

SELECT 
    Provider_Type, 
    SUM(Quantity) AS Total_Quantity
FROM food_listings_data
GROUP BY Provider_Type
ORDER BY Total_Quantity DESC;

-- 3. Contact information of food providers in a specific city

SELECT 
    Name, 
    Contact
FROM providers_data
WHERE City = 'Lake Monique';

-- 4. Which receivers have claimed the most food?

SELECT 
    r.Name, 
    SUM(f.Quantity) AS Total_Claimed
FROM claims_data c
JOIN receivers_data r ON c.Receiver_ID = r.Receiver_ID
JOIN food_listings_data f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Completed'
GROUP BY r.Name
ORDER BY Total_Claimed DESC;

-- 5. Total quantity of food available from all providers

SELECT SUM(Quantity) AS Total_Food_Quantity
FROM food_listings_data;

-- 6. Which city has the highest number of food listings?

SELECT 
    Location, 
    COUNT(*) AS Total_Listings
FROM food_listings_data
GROUP BY Location
ORDER BY Total_Listings DESC
LIMIT 1;

-- 7. Most commonly available food types

SELECT 
    Food_Type, 
    COUNT(*) AS Count
FROM food_listings_data
GROUP BY Food_Type
ORDER BY Count DESC;

-- 8. How many food claims have been made for each food item?

SELECT 
    Food_ID, 
    COUNT(*) AS Claim_Count
FROM claims_data
GROUP BY Food_ID
ORDER BY Claim_Count DESC;

-- 9. Provider with the highest number of successful food claims

SELECT 
    p.Name, 
    COUNT(*) AS Successful_Claims
FROM claims_data c
JOIN food_listings_data f ON c.Food_ID = f.Food_ID
JOIN providers_data p ON f.Provider_ID = p.Provider_ID
WHERE c.Status = 'Completed'
GROUP BY p.Name
ORDER BY Successful_Claims DESC
LIMIT 1;

-- 10. Percentage of claims by status

SELECT 
    Status, 
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims_data), 2) AS Percentage
FROM claims_data
GROUP BY Status;

-- 11. Average quantity of food claimed per receiver

SELECT 
    r.Name, 
    ROUND(AVG(f.Quantity), 2) AS Avg_Quantity_Claimed
FROM claims_data c
JOIN receivers_data r ON c.Receiver_ID = r.Receiver_ID
JOIN food_listings_data f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Completed'
GROUP BY r.Name;

-- 12. Which meal type is claimed the most

SELECT 
    f.Meal_Type, 
    COUNT(*) AS Claim_Count
FROM claims_data c
JOIN food_listings_data f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Completed'
GROUP BY f.Meal_Type
ORDER BY Claim_Count DESC;

-- 13. Total quantity of food donated by each provider

SELECT 
    p.Name, 
    SUM(f.Quantity) AS Total_Donated
FROM food_listings_data f
JOIN providers_data p ON f.Provider_ID = p.Provider_ID
GROUP BY p.Name
ORDER BY Total_Donated DESC;

-- 14. Which city has the highest unclaimed (pending) food quantity?

SELECT 
    f.Location, 
    SUM(f.Quantity) AS Pending_Quantity
FROM claims_data c
JOIN food_listings_data f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Pending'
GROUP BY f.Location
ORDER BY Pending_Quantity DESC
LIMIT 1;

-- 15. Which food type has the highest wastage risk (near expiry and still unclaimed)?

SELECT 
    f.Food_Type, 
    COUNT(*) AS Near_Expiry_Unclaimed
FROM food_listings_data f
LEFT JOIN claims_data c ON f.Food_ID = c.Food_ID AND c.Status = 'Completed'
WHERE f.Expiry_Date <= DATE_ADD(CURDATE(), INTERVAL 2 DAY)
  AND (c.Claim_ID IS NULL OR c.Status != 'Completed')
GROUP BY f.Food_Type
ORDER BY Near_Expiry_Unclaimed DESC;
