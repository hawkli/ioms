/*
SQLyog 企业版 - MySQL GUI v8.14 
MySQL - 5.1.31-community : Database - ioms_info
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`ioms_info` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `ioms_info`;

/*Table structure for table `dir_list` */

DROP TABLE IF EXISTS `dir_list`;

CREATE TABLE `dir_list` (
  `dir1_id` int(10) NOT NULL COMMENT '一级目录ID',
  `dir1_name` varchar(50) DEFAULT NULL COMMENT '一级目录名字',
  `dir2_id` int(10) NOT NULL AUTO_INCREMENT COMMENT '二级目录ID',
  `dir2_name` varchar(50) DEFAULT NULL COMMENT '二级目录名字',
  `dir_template` int(50) NOT NULL DEFAULT '0' COMMENT '目录对应的显示模板',
  PRIMARY KEY (`dir2_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2006 DEFAULT CHARSET=utf8;

/*Data for the table `dir_list` */

LOCK TABLES `dir_list` WRITE;

insert  into `dir_list`(`dir1_id`,`dir1_name`,`dir2_id`,`dir2_name`,`dir_template`) values (1000,'未分配服务器',2000,'未分配设备',1),(1001,'物理显示模式',2001,'沈阳机房',2),(1001,'物理显示模式',2002,'上海机房',2),(1001,'物理显示模式',2003,'南京机房',2),(1002,'监控显示模式',2004,'查询',3),(1003,'回收站',2005,'我的回收站',0);

UNLOCK TABLES;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
