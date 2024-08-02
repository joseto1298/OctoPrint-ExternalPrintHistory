SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;


CREATE TABLE `Customer` (
  `customer_id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Design` (
  `design_id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `model_file` blob DEFAULT NULL,
  `model_url` varchar(255) DEFAULT NULL,
  `license` varchar(50) DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Maintenance` (
  `maintenance_id` int(11) NOT NULL,
  `printer_id` int(11) DEFAULT NULL,
  `subject` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `cost` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Order` (
  `order_id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `order_date` date DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `delivery_date` date DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Print` (
  `print_id` int(11) NOT NULL,
  `order_id` int(11) DEFAULT NULL,
  `printer_id` int(11) DEFAULT NULL,
  `filament_id` int(11) DEFAULT NULL,
  `start_datetime` datetime DEFAULT NULL,
  `end_datetime` datetime DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `estimated_time` int(11) DEFAULT NULL,
  `image` blob DEFAULT NULL,
  `calculated_length` decimal(10,2) DEFAULT NULL,
  `total_length` decimal(10,2) DEFAULT NULL,
  `calculated_height` decimal(10,2) DEFAULT NULL,
  `total_height` decimal(10,2) DEFAULT NULL,
  `calculated_layers` int(11) DEFAULT NULL,
  `total_layers` int(11) DEFAULT NULL,
  `calculated_weight` decimal(10,2) DEFAULT NULL,
  `total_weight` decimal(10,2) DEFAULT NULL,
  `nozzle_temperature` decimal(5,2) DEFAULT NULL,
  `bed_temperature` decimal(5,2) DEFAULT NULL,
  `bed_type` varchar(50) DEFAULT NULL,
  `nozzle_diameter` decimal(5,2) DEFAULT NULL,
  `state` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Printer` (
  `printer_id` int(11) NOT NULL,
  `brand` varchar(100) DEFAULT NULL,
  `model` varchar(100) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `power_consumption` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Print_Design` (
  `print_id` int(11) NOT NULL,
  `design_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


ALTER TABLE `Customer`
  ADD PRIMARY KEY (`customer_id`);

ALTER TABLE `Design`
  ADD PRIMARY KEY (`design_id`);

ALTER TABLE `Maintenance`
  ADD PRIMARY KEY (`maintenance_id`),
  ADD KEY `printer_id` (`printer_id`);

ALTER TABLE `Order`
  ADD PRIMARY KEY (`order_id`),
  ADD KEY `customer_id` (`customer_id`);

ALTER TABLE `Print`
  ADD PRIMARY KEY (`print_id`),
  ADD KEY `printer_id` (`printer_id`),
  ADD KEY `fk_order` (`order_id`);

ALTER TABLE `Printer`
  ADD PRIMARY KEY (`printer_id`);

ALTER TABLE `Print_Design`
  ADD PRIMARY KEY (`print_id`,`design_id`),
  ADD KEY `design_id` (`design_id`);


ALTER TABLE `Customer`
  MODIFY `customer_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Design`
  MODIFY `design_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Maintenance`
  MODIFY `maintenance_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Order`
  MODIFY `order_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Print`
  MODIFY `print_id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Printer`
  MODIFY `printer_id` int(11) NOT NULL AUTO_INCREMENT;


ALTER TABLE `Maintenance`
  ADD CONSTRAINT `Maintenance_ibfk_1` FOREIGN KEY (`printer_id`) REFERENCES `Printer` (`printer_id`);

ALTER TABLE `Order`
  ADD CONSTRAINT `Order_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `Customer` (`customer_id`);

ALTER TABLE `Print`
  ADD CONSTRAINT `Print_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `Order` (`order_id`),
  ADD CONSTRAINT `Print_ibfk_2` FOREIGN KEY (`printer_id`) REFERENCES `Printer` (`printer_id`),
  ADD CONSTRAINT `fk_order` FOREIGN KEY (`order_id`) REFERENCES `Order` (`order_id`);

ALTER TABLE `Print_Design`
  ADD CONSTRAINT `Print_Design_ibfk_1` FOREIGN KEY (`print_id`) REFERENCES `Print` (`print_id`),
  ADD CONSTRAINT `Print_Design_ibfk_2` FOREIGN KEY (`design_id`) REFERENCES `Design` (`design_id`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

DELIMITER //

CREATE PROCEDURE insert_or_update_print (
    IN p_print_id INT,
    IN p_order_id INT,
    IN p_printer_id INT,
    IN p_filament_id INT,
    IN p_start_datetime DATETIME,
    IN p_end_datetime DATETIME,
    IN p_duration INT,
    IN p_estimated_time INT,
    IN p_image BLOB,
    IN p_calculated_length DECIMAL(10,2),
    IN p_total_length DECIMAL(10,2),
    IN p_calculated_height DECIMAL(10,2),
    IN p_total_height DECIMAL(10,2),
    IN p_calculated_layers INT,
    IN p_total_layers INT,
    IN p_calculated_weight DECIMAL(10,2),
    IN p_total_weight DECIMAL(10,2),
    IN p_nozzle_temperature DECIMAL(5,2),
    IN p_bed_temperature DECIMAL(5,2),
    IN p_bed_type VARCHAR(50),
    IN p_nozzle_diameter DECIMAL(5,2),
    IN p_state VARCHAR(50),
    OUT p_result_id INT
)
BEGIN
    DECLARE v_existing_id INT;

    -- Check if the print_id already exists
    SELECT print_id INTO v_existing_id
    FROM Print
    WHERE print_id = p_print_id;

    IF v_existing_id IS NOT NULL THEN
        -- Update existing record
        UPDATE Print
        SET order_id = p_order_id,
            printer_id = p_printer_id,
            filament_id = p_filament_id,
            start_datetime = p_start_datetime,
            end_datetime = p_end_datetime,
            duration = p_duration,
            estimated_time = p_estimated_time,
            image = p_image,
            calculated_length = p_calculated_length,
            total_length = p_total_length,
            calculated_height = p_calculated_height,
            total_height = p_total_height,
            calculated_layers = p_calculated_layers,
            total_layers = p_total_layers,
            calculated_weight = p_calculated_weight,
            total_weight = p_total_weight,
            nozzle_temperature = p_nozzle_temperature,
            bed_temperature = p_bed_temperature,
            bed_type = p_bed_type,
            nozzle_diameter = p_nozzle_diameter,
            state = p_state
        WHERE print_id = p_print_id;
        
        -- Set result ID to the existing print_id
        SET p_result_id = p_print_id;
    ELSE
        -- Insert new record
        INSERT INTO Print (
            order_id,
            printer_id,
            filament_id,
            start_datetime,
            end_datetime,
            duration,
            estimated_time,
            image,
            calculated_length,
            total_length,
            calculated_height,
            total_height,
            calculated_layers,
            total_layers,
            calculated_weight,
            total_weight,
            nozzle_temperature,
            bed_temperature,
            bed_type,
            nozzle_diameter,
            state
        )
        VALUES (
            p_order_id,
            p_printer_id,
            p_filament_id,
            p_start_datetime,
            p_end_datetime,
            p_duration,
            p_estimated_time,
            p_image,
            p_calculated_length,
            p_total_length,
            p_calculated_height,
            p_total_height,
            p_calculated_layers,
            p_total_layers,
            p_calculated_weight,
            p_total_weight,
            p_nozzle_temperature,
            p_bed_temperature,
            p_bed_type,
            p_nozzle_diameter,
            p_state
        );

        -- Get the last inserted ID
        SET p_result_id = LAST_INSERT_ID();
    END IF;
END //

DELIMITER ;
