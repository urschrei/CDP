# ************************************************************
# Sequel Pro SQL dump
# Version 4096
#
# http://www.sequelpro.com/
# http://code.google.com/p/sequel-pro/
#
# Host: 127.0.0.1 (MySQL 5.6.20)
# Database: glyph
# Generation Time: 2014-09-08 16:18:52 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Dump of table alembic_version
# ------------------------------------------------------------

DROP TABLE IF EXISTS `alembic_version`;

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



# Dump of table author
# ------------------------------------------------------------

DROP TABLE IF EXISTS `author`;

CREATE TABLE `author` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(75) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_author_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table cdli
# ------------------------------------------------------------

DROP TABLE IF EXISTS `cdli`;

CREATE TABLE `cdli` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sign_ref` varchar(150) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_cdli_sign_ref` (`sign_ref`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table cdp
# ------------------------------------------------------------

DROP TABLE IF EXISTS `cdp`;

CREATE TABLE `cdp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sign_id` int(11) NOT NULL,
  `description_id` int(11) DEFAULT NULL,
  `oracc_id` int(11) DEFAULT NULL,
  `cdli_id` int(11) DEFAULT NULL,
  `form_name` varchar(5) COLLATE utf8mb4_bin DEFAULT NULL,
  `variant_name` varchar(5) COLLATE utf8mb4_bin DEFAULT NULL,
  `form_description` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `notes` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `MesZL` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `ELLes` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `ZATU` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `LAK` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `UET_2` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `ARM_XV` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `Hinke` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `Clay_BE_A_14` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `Koenig_AfO_Bei_16` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `Ranke_BE_A_61` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `Schroeder_VS_12` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `Clay_BE_A_10` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `RSP` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `Emar` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `Schroder_VS_15` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `HZL` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `HA` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `aBZL` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `REC` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `Labat` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `KWU` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  `Fossey_pp` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_cdp_sign_id_sign` (`sign_id`),
  KEY `fk_cdp_description_id_description` (`description_id`),
  KEY `fk_cdp_oracc_id_oracc` (`oracc_id`),
  KEY `fk_cdp_cdli_id_cdli` (`cdli_id`),
  CONSTRAINT `fk_cdp_cdli_id_cdli` FOREIGN KEY (`cdli_id`) REFERENCES `cdli` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cdp_description_id_description` FOREIGN KEY (`description_id`) REFERENCES `description` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cdp_oracc_id_oracc` FOREIGN KEY (`oracc_id`) REFERENCES `oracc` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cdp_sign_id_sign` FOREIGN KEY (`sign_id`) REFERENCES `sign` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table city
# ------------------------------------------------------------

DROP TABLE IF EXISTS `city`;

CREATE TABLE `city` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_bin NOT NULL,
  `locality_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_city_name` (`name`),
  KEY `fk_city_locality_id_locality` (`locality_id`),
  CONSTRAINT `fk_city_locality_id_locality` FOREIGN KEY (`locality_id`) REFERENCES `locality` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table city_site
# ------------------------------------------------------------

DROP TABLE IF EXISTS `city_site`;

CREATE TABLE `city_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_bin NOT NULL,
  `city_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_city_site_name` (`name`),
  KEY `fk_city_site_city_id_city` (`city_id`),
  CONSTRAINT `fk_city_site_city_id_city` FOREIGN KEY (`city_id`) REFERENCES `city` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table column
# ------------------------------------------------------------

DROP TABLE IF EXISTS `column`;

CREATE TABLE `column` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `number` varchar(5) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_column_number` (`number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table correspondent
# ------------------------------------------------------------

DROP TABLE IF EXISTS `correspondent`;

CREATE TABLE `correspondent` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ruler_id` int(11) DEFAULT NULL,
  `non_ruler_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_correspondent_ruler_id_ruler` (`ruler_id`),
  KEY `fk_correspondent_non_ruler_id_non_ruler_corresp` (`non_ruler_id`),
  CONSTRAINT `fk_correspondent_non_ruler_id_non_ruler_corresp` FOREIGN KEY (`non_ruler_id`) REFERENCES `non_ruler_corresp` (`id`),
  CONSTRAINT `fk_correspondent_ruler_id_ruler` FOREIGN KEY (`ruler_id`) REFERENCES `ruler` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table description
# ------------------------------------------------------------

DROP TABLE IF EXISTS `description`;

CREATE TABLE `description` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sign_ref` varchar(150) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_description_sign_ref` (`sign_ref`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table dynasty
# ------------------------------------------------------------

DROP TABLE IF EXISTS `dynasty`;

CREATE TABLE `dynasty` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dynasty_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table eponym
# ------------------------------------------------------------

DROP TABLE IF EXISTS `eponym`;

CREATE TABLE `eponym` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_eponym_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table function
# ------------------------------------------------------------

DROP TABLE IF EXISTS `function`;

CREATE TABLE `function` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_function_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table genre
# ------------------------------------------------------------

DROP TABLE IF EXISTS `genre`;

CREATE TABLE `genre` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_genre_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table instance
# ------------------------------------------------------------

DROP TABLE IF EXISTS `instance`;

CREATE TABLE `instance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tablet_id` int(11) NOT NULL,
  `sign_id` int(11) NOT NULL,
  `surface_id` int(11) DEFAULT NULL,
  `column_id` int(11) DEFAULT NULL,
  `line_id` int(11) DEFAULT NULL,
  `function_id` int(11) DEFAULT NULL,
  `iteration_id` int(11) DEFAULT NULL,
  `notes` varchar(250) COLLATE utf8mb4_bin DEFAULT NULL,
  `jjt_notes` varchar(250) COLLATE utf8mb4_bin DEFAULT NULL,
  `filename` varchar(50) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_instance_filename` (`filename`),
  KEY `fk_instance_tablet_id_tablet` (`tablet_id`),
  KEY `fk_instance_sign_id_sign` (`sign_id`),
  KEY `fk_instance_surface_id_surface` (`surface_id`),
  KEY `fk_instance_column_id_column` (`column_id`),
  KEY `fk_instance_line_id_line` (`line_id`),
  KEY `fk_instance_function_id_function` (`function_id`),
  KEY `fk_instance_iteration_id_iteration` (`iteration_id`),
  CONSTRAINT `fk_instance_column_id_column` FOREIGN KEY (`column_id`) REFERENCES `column` (`id`),
  CONSTRAINT `fk_instance_function_id_function` FOREIGN KEY (`function_id`) REFERENCES `function` (`id`),
  CONSTRAINT `fk_instance_iteration_id_iteration` FOREIGN KEY (`iteration_id`) REFERENCES `iteration` (`id`),
  CONSTRAINT `fk_instance_line_id_line` FOREIGN KEY (`line_id`) REFERENCES `line` (`id`),
  CONSTRAINT `fk_instance_sign_id_sign` FOREIGN KEY (`sign_id`) REFERENCES `sign` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_instance_surface_id_surface` FOREIGN KEY (`surface_id`) REFERENCES `surface` (`id`),
  CONSTRAINT `fk_instance_tablet_id_tablet` FOREIGN KEY (`tablet_id`) REFERENCES `tablet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table instance_language
# ------------------------------------------------------------

DROP TABLE IF EXISTS `instance_language`;

CREATE TABLE `instance_language` (
  `instance_id` int(11) NOT NULL,
  `language_id` int(11) NOT NULL,
  PRIMARY KEY (`instance_id`,`language_id`),
  KEY `fk_instance_language_language_id_language` (`language_id`),
  CONSTRAINT `fk_instance_language_instance_id_instance` FOREIGN KEY (`instance_id`) REFERENCES `instance` (`id`),
  CONSTRAINT `fk_instance_language_language_id_language` FOREIGN KEY (`language_id`) REFERENCES `language` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



# Dump of table iteration
# ------------------------------------------------------------

DROP TABLE IF EXISTS `iteration`;

CREATE TABLE `iteration` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `number` varchar(5) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_iteration_number` (`number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table language
# ------------------------------------------------------------

DROP TABLE IF EXISTS `language`;

CREATE TABLE `language` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_language_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table line
# ------------------------------------------------------------

DROP TABLE IF EXISTS `line`;

CREATE TABLE `line` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `number` varchar(5) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_line_number` (`number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table locality
# ------------------------------------------------------------

DROP TABLE IF EXISTS `locality`;

CREATE TABLE `locality` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `area` varchar(100) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_locality_area` (`area`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table medium
# ------------------------------------------------------------

DROP TABLE IF EXISTS `medium`;

CREATE TABLE `medium` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_medium_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table method
# ------------------------------------------------------------

DROP TABLE IF EXISTS `method`;

CREATE TABLE `method` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_method_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table non_ruler_corresp
# ------------------------------------------------------------

DROP TABLE IF EXISTS `non_ruler_corresp`;

CREATE TABLE `non_ruler_corresp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_non_ruler_corresp_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table oracc
# ------------------------------------------------------------

DROP TABLE IF EXISTS `oracc`;

CREATE TABLE `oracc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sign_ref` varchar(150) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_oracc_sign_ref` (`sign_ref`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table period
# ------------------------------------------------------------

DROP TABLE IF EXISTS `period`;

CREATE TABLE `period` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_bin NOT NULL,
  `from_date` varchar(50) COLLATE utf8mb4_bin NOT NULL,
  `to_date` varchar(50) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_period_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table reign
# ------------------------------------------------------------

DROP TABLE IF EXISTS `reign`;

CREATE TABLE `reign` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ruler_id` int(11) NOT NULL,
  `rim_ref` varchar(50) COLLATE utf8mb4_bin NOT NULL,
  `city_id` int(11) DEFAULT NULL,
  `start_date` int(11) DEFAULT NULL,
  `end_date` int(11) DEFAULT NULL,
  `dynasty_id` int(11) DEFAULT NULL,
  `period_id` int(11) NOT NULL,
  `sub_period_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_reign_ruler_id_ruler` (`ruler_id`),
  KEY `fk_reign_city_id_city` (`city_id`),
  KEY `fk_reign_start_date_year` (`start_date`),
  KEY `fk_reign_end_date_year` (`end_date`),
  KEY `fk_reign_dynasty_id_dynasty` (`dynasty_id`),
  KEY `fk_reign_period_id_period` (`period_id`),
  KEY `fk_reign_sub_period_id_sub_period` (`sub_period_id`),
  CONSTRAINT `fk_reign_city_id_city` FOREIGN KEY (`city_id`) REFERENCES `city` (`id`),
  CONSTRAINT `fk_reign_dynasty_id_dynasty` FOREIGN KEY (`dynasty_id`) REFERENCES `dynasty` (`id`),
  CONSTRAINT `fk_reign_end_date_year` FOREIGN KEY (`end_date`) REFERENCES `year` (`id`),
  CONSTRAINT `fk_reign_period_id_period` FOREIGN KEY (`period_id`) REFERENCES `period` (`id`),
  CONSTRAINT `fk_reign_ruler_id_ruler` FOREIGN KEY (`ruler_id`) REFERENCES `ruler` (`id`),
  CONSTRAINT `fk_reign_start_date_year` FOREIGN KEY (`start_date`) REFERENCES `year` (`id`),
  CONSTRAINT `fk_reign_sub_period_id_sub_period` FOREIGN KEY (`sub_period_id`) REFERENCES `sub_period` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table ruler
# ------------------------------------------------------------

DROP TABLE IF EXISTS `ruler`;

CREATE TABLE `ruler` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_ruler_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table ruler_tablet
# ------------------------------------------------------------

DROP TABLE IF EXISTS `ruler_tablet`;

CREATE TABLE `ruler_tablet` (
  `ruler_id` int(11) NOT NULL,
  `tablet_id` int(11) NOT NULL,
  PRIMARY KEY (`ruler_id`,`tablet_id`),
  KEY `fk_ruler_tablet_tablet_id_tablet` (`tablet_id`),
  CONSTRAINT `fk_ruler_tablet_ruler_id_ruler` FOREIGN KEY (`ruler_id`) REFERENCES `ruler` (`id`),
  CONSTRAINT `fk_ruler_tablet_tablet_id_tablet` FOREIGN KEY (`tablet_id`) REFERENCES `tablet` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



# Dump of table script_type
# ------------------------------------------------------------

DROP TABLE IF EXISTS `script_type`;

CREATE TABLE `script_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `script` varchar(50) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_script_type_script` (`script`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table sign
# ------------------------------------------------------------

DROP TABLE IF EXISTS `sign`;

CREATE TABLE `sign` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sign_ref` varchar(150) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_sign_sign_ref` (`sign_ref`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table sub_locality
# ------------------------------------------------------------

DROP TABLE IF EXISTS `sub_locality`;

CREATE TABLE `sub_locality` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_bin NOT NULL,
  `locality_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_sub_locality_name` (`name`),
  KEY `fk_sub_locality_locality_id_locality` (`locality_id`),
  CONSTRAINT `fk_sub_locality_locality_id_locality` FOREIGN KEY (`locality_id`) REFERENCES `locality` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table sub_period
# ------------------------------------------------------------

DROP TABLE IF EXISTS `sub_period`;

CREATE TABLE `sub_period` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_bin NOT NULL,
  `period_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_sub_period_name` (`name`),
  KEY `fk_sub_period_period_id_period` (`period_id`),
  CONSTRAINT `fk_sub_period_period_id_period` FOREIGN KEY (`period_id`) REFERENCES `period` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table subperiod_dynasty
# ------------------------------------------------------------

DROP TABLE IF EXISTS `subperiod_dynasty`;

CREATE TABLE `subperiod_dynasty` (
  `subperiod_id` int(11) NOT NULL,
  `dynasty_id` int(11) NOT NULL,
  PRIMARY KEY (`subperiod_id`,`dynasty_id`),
  KEY `fk_subperiod_dynasty_dynasty_id_dynasty` (`dynasty_id`),
  CONSTRAINT `fk_subperiod_dynasty_dynasty_id_dynasty` FOREIGN KEY (`dynasty_id`) REFERENCES `dynasty` (`id`),
  CONSTRAINT `fk_subperiod_dynasty_subperiod_id_sub_period` FOREIGN KEY (`subperiod_id`) REFERENCES `sub_period` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



# Dump of table surface
# ------------------------------------------------------------

DROP TABLE IF EXISTS `surface`;

CREATE TABLE `surface` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_surface_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table tablet
# ------------------------------------------------------------

DROP TABLE IF EXISTS `tablet`;

CREATE TABLE `tablet` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime NOT NULL,
  `museum_number` varchar(75) COLLATE utf8mb4_bin NOT NULL,
  `medium_id` int(11) NOT NULL,
  `script_type_id` int(11) DEFAULT NULL,
  `city_id` int(11) DEFAULT NULL,
  `city_site_id` int(11) DEFAULT NULL,
  `origin_city_id` int(11) DEFAULT NULL,
  `publication` varchar(200) COLLATE utf8mb4_bin DEFAULT NULL,
  `period_id` int(11) NOT NULL,
  `sub_period_id` int(11) DEFAULT NULL,
  `from_id` int(11) DEFAULT NULL,
  `to_id` int(11) DEFAULT NULL,
  `language_id` int(11) DEFAULT NULL,
  `eponym_id` int(11) DEFAULT NULL,
  `year_id` int(11) DEFAULT NULL,
  `absolute_month` varchar(10) COLLATE utf8mb4_bin DEFAULT NULL,
  `absolute_day` varchar(10) COLLATE utf8mb4_bin DEFAULT NULL,
  `ancient_year` varchar(10) COLLATE utf8mb4_bin DEFAULT NULL,
  `ancient_month` varchar(10) COLLATE utf8mb4_bin DEFAULT NULL,
  `ancient_day` varchar(10) COLLATE utf8mb4_bin DEFAULT NULL,
  `dynasty_id` int(11) DEFAULT NULL,
  `text_vehicle_id` int(11) DEFAULT NULL,
  `locality_id` int(11) DEFAULT NULL,
  `sub_locality_id` int(11) DEFAULT NULL,
  `notes` varchar(500) COLLATE utf8mb4_bin DEFAULT NULL,
  `method_id` int(11) DEFAULT NULL,
  `genre_id` int(11) DEFAULT NULL,
  `function_id` int(11) DEFAULT NULL,
  `reign_id` int(11) DEFAULT NULL,
  `author_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_tablet_museum_number` (`museum_number`),
  KEY `fk_tablet_medium_id_medium` (`medium_id`),
  KEY `fk_tablet_script_type_id_script_type` (`script_type_id`),
  KEY `fk_tablet_city_id_city` (`city_id`),
  KEY `fk_tablet_city_site_id_city_site` (`city_site_id`),
  KEY `fk_tablet_origin_city_id_city` (`origin_city_id`),
  KEY `fk_tablet_period_id_period` (`period_id`),
  KEY `fk_tablet_sub_period_id_sub_period` (`sub_period_id`),
  KEY `fk_tablet_from_id_correspondent` (`from_id`),
  KEY `fk_tablet_to_id_correspondent` (`to_id`),
  KEY `fk_tablet_language_id_language` (`language_id`),
  KEY `fk_tablet_eponym_id_eponym` (`eponym_id`),
  KEY `fk_tablet_year_id_year` (`year_id`),
  KEY `fk_tablet_dynasty_id_dynasty` (`dynasty_id`),
  KEY `fk_tablet_text_vehicle_id_text_vehicle` (`text_vehicle_id`),
  KEY `fk_tablet_locality_id_locality` (`locality_id`),
  KEY `fk_tablet_sub_locality_id_sub_locality` (`sub_locality_id`),
  KEY `fk_tablet_method_id_method` (`method_id`),
  KEY `fk_tablet_genre_id_genre` (`genre_id`),
  KEY `fk_tablet_function_id_function` (`function_id`),
  KEY `fk_tablet_reign_id_reign` (`reign_id`),
  KEY `fk_tablet_author_id_author` (`author_id`),
  CONSTRAINT `fk_tablet_author_id_author` FOREIGN KEY (`author_id`) REFERENCES `author` (`id`),
  CONSTRAINT `fk_tablet_city_id_city` FOREIGN KEY (`city_id`) REFERENCES `city` (`id`),
  CONSTRAINT `fk_tablet_city_site_id_city_site` FOREIGN KEY (`city_site_id`) REFERENCES `city_site` (`id`),
  CONSTRAINT `fk_tablet_dynasty_id_dynasty` FOREIGN KEY (`dynasty_id`) REFERENCES `dynasty` (`id`),
  CONSTRAINT `fk_tablet_eponym_id_eponym` FOREIGN KEY (`eponym_id`) REFERENCES `eponym` (`id`),
  CONSTRAINT `fk_tablet_from_id_correspondent` FOREIGN KEY (`from_id`) REFERENCES `correspondent` (`id`),
  CONSTRAINT `fk_tablet_function_id_function` FOREIGN KEY (`function_id`) REFERENCES `function` (`id`),
  CONSTRAINT `fk_tablet_genre_id_genre` FOREIGN KEY (`genre_id`) REFERENCES `genre` (`id`),
  CONSTRAINT `fk_tablet_language_id_language` FOREIGN KEY (`language_id`) REFERENCES `language` (`id`),
  CONSTRAINT `fk_tablet_locality_id_locality` FOREIGN KEY (`locality_id`) REFERENCES `locality` (`id`),
  CONSTRAINT `fk_tablet_medium_id_medium` FOREIGN KEY (`medium_id`) REFERENCES `medium` (`id`),
  CONSTRAINT `fk_tablet_method_id_method` FOREIGN KEY (`method_id`) REFERENCES `method` (`id`),
  CONSTRAINT `fk_tablet_origin_city_id_city` FOREIGN KEY (`origin_city_id`) REFERENCES `city` (`id`),
  CONSTRAINT `fk_tablet_period_id_period` FOREIGN KEY (`period_id`) REFERENCES `period` (`id`),
  CONSTRAINT `fk_tablet_reign_id_reign` FOREIGN KEY (`reign_id`) REFERENCES `reign` (`id`),
  CONSTRAINT `fk_tablet_script_type_id_script_type` FOREIGN KEY (`script_type_id`) REFERENCES `script_type` (`id`),
  CONSTRAINT `fk_tablet_sub_locality_id_sub_locality` FOREIGN KEY (`sub_locality_id`) REFERENCES `sub_locality` (`id`),
  CONSTRAINT `fk_tablet_sub_period_id_sub_period` FOREIGN KEY (`sub_period_id`) REFERENCES `sub_period` (`id`),
  CONSTRAINT `fk_tablet_text_vehicle_id_text_vehicle` FOREIGN KEY (`text_vehicle_id`) REFERENCES `text_vehicle` (`id`),
  CONSTRAINT `fk_tablet_to_id_correspondent` FOREIGN KEY (`to_id`) REFERENCES `correspondent` (`id`),
  CONSTRAINT `fk_tablet_year_id_year` FOREIGN KEY (`year_id`) REFERENCES `year` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table tablet_correspondent
# ------------------------------------------------------------

DROP TABLE IF EXISTS `tablet_correspondent`;

CREATE TABLE `tablet_correspondent` (
  `tablet_id` int(11) NOT NULL,
  `correspondent_id` int(11) NOT NULL,
  PRIMARY KEY (`tablet_id`,`correspondent_id`),
  KEY `fk_tablet_correspondent_correspondent_id_correspondent` (`correspondent_id`),
  CONSTRAINT `fk_tablet_correspondent_correspondent_id_correspondent` FOREIGN KEY (`correspondent_id`) REFERENCES `correspondent` (`id`),
  CONSTRAINT `fk_tablet_correspondent_tablet_id_tablet` FOREIGN KEY (`tablet_id`) REFERENCES `tablet` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



# Dump of table text_vehicle
# ------------------------------------------------------------

DROP TABLE IF EXISTS `text_vehicle`;

CREATE TABLE `text_vehicle` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_bin NOT NULL,
  `bm_catalogue` varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  `cdli` varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_text_vehicle_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;



# Dump of table year
# ------------------------------------------------------------

DROP TABLE IF EXISTS `year`;

CREATE TABLE `year` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `year` varchar(14) COLLATE utf8mb4_bin NOT NULL,
  `eponym_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_year_year` (`year`),
  KEY `fk_year_eponym_id_eponym` (`eponym_id`),
  CONSTRAINT `fk_year_eponym_id_eponym` FOREIGN KEY (`eponym_id`) REFERENCES `eponym` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;




/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
