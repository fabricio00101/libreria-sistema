-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: biblioteca_personal
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `autores`
--

DROP TABLE IF EXISTS `autores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `autores` (
  `id_autor` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `nacionalidad` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_autor`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `autores`
--

LOCK TABLES `autores` WRITE;
/*!40000 ALTER TABLE `autores` DISABLE KEYS */;
INSERT INTO `autores` VALUES (1,'Franz Kafka','Checo'),(2,'Germán Beder','Argentino'),(3,'Alejandro Dolina','argentino'),(4,'Friedrich Nietzsche','alemán'),(5,'Quentin Tarantino','Estadounidense'),(6,'Alfonsina Storni','Argentina'),(8,'Felipe Pigna','Argentino'),(9,'María del Carmen Calvo','Argentina'),(10,'Osvaldo Soriano','Argentino'),(11,'William Shakespeare','Inglés'),(12,'Arthur Rimbaud','Frances'),(13,'José Hernández','Argentino'),(14,'Juan Domingo Perón','Argentino'),(15,'Hermann Hesse','Alemán'),(16,'Domingo Faustino Sarmiento','Argentino'),(17,'Roberto Arlt','Argentino'),(18,'Lao Tse','Chino'),(19,'Stendahl','Francés'),(20,'Gustave Flaubert','Francés'),(21,'Enrique González Lonzieme','Argentino'),(22,'Adolfo Bioy Casares','Argentino'),(23,'Nicolás Schuff','Argentino'),(24,'Juan José Panno','Argentino');
/*!40000 ALTER TABLE `autores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `libros`
--

DROP TABLE IF EXISTS `libros`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `libros` (
  `id_libro` int NOT NULL AUTO_INCREMENT,
  `titulo` varchar(255) NOT NULL,
  `anio_publicacion` int DEFAULT NULL,
  `leido` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id_libro`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `libros`
--

LOCK TABLES `libros` WRITE;
/*!40000 ALTER TABLE `libros` DISABLE KEYS */;
INSERT INTO `libros` VALUES (1,'La metamorfosis',1915,0),(2,'El proceso',1925,0),(3,'La muralla china',1917,0),(4,'El hombre que daba charla a los call center',2022,0),(5,'Crónicas del ángel gris',1987,0),(6,'Así hablaba zaratustra',1883,0),(7,'El caminante y su sombra',1880,0),(8,'Once Upon a Time in Hollywood',2021,0),(9,'Antología poética',2009,0),(10,'Mujeres tenían que ser',2012,0),(11,'El origen de la tragedia',1871,0),(12,'Signos del espíritu en el arte',2023,0),(13,'Cuentos fantásticos',2013,0),(14,'El ojo de la patria',2014,0),(15,'Antología poética',2017,0),(16,'Antología poética',2017,0),(17,'Martin Fierro',1872,0),(18,'Doctrina Peronista',1948,0),(19,'Escritos políticos 1914/1938',1978,0),(20,'Recuerdos de provincia',1850,0),(21,'Los Siete Locos',1929,0),(22,'Tao Te King',1928,0),(23,'Enamorado',1822,0),(24,'Madame Bovary',1856,0),(25,'Breve Hisotira de las Batallas Navales',1994,0),(26,'La aventura de un fotógrafo en La Plata',2005,0),(27,'Seres que hacen temblar. Historias de bestias criaturas y monstruos de todos los tiempos',2009,0),(28,'100x100 Mundiales. Postales de las copas',2014,0);
/*!40000 ALTER TABLE `libros` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `libros_autores`
--

DROP TABLE IF EXISTS `libros_autores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `libros_autores` (
  `id_libro` int NOT NULL,
  `id_autor` int NOT NULL,
  PRIMARY KEY (`id_libro`,`id_autor`),
  KEY `id_autor` (`id_autor`),
  CONSTRAINT `libros_autores_ibfk_1` FOREIGN KEY (`id_libro`) REFERENCES `libros` (`id_libro`),
  CONSTRAINT `libros_autores_ibfk_2` FOREIGN KEY (`id_autor`) REFERENCES `autores` (`id_autor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `libros_autores`
--

LOCK TABLES `libros_autores` WRITE;
/*!40000 ALTER TABLE `libros_autores` DISABLE KEYS */;
INSERT INTO `libros_autores` VALUES (1,1),(2,1),(3,1),(13,1),(4,2),(5,3),(6,4),(7,4),(11,4),(8,5),(9,6),(10,8),(12,9),(14,10),(15,11),(16,12),(17,13),(18,14),(19,15),(20,16),(21,17),(22,18),(23,19),(24,20),(25,21),(26,22),(27,23),(28,24);
/*!40000 ALTER TABLE `libros_autores` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-19 12:40:28
