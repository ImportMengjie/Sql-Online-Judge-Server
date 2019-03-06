CREATE TABLE `sql_online_judge`.`student` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `gender` VARCHAR(10) NULL,
  `class` VARCHAR(45) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idstudent_UNIQUE` (`id` ASC) VISIBLE);

