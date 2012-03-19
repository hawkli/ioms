/*
SQLyog 企业版 - MySQL GUI v8.14 
MySQL - 5.1.31-community : Database - ioms_user
*********************************************************************
*/
/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`ioms_user` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `ioms_user`;

/*Table structure for table `user` */

DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
  `account` char(20) NOT NULL COMMENT '登录账号',
  `password` char(100) DEFAULT NULL COMMENT '密码',
  `access` char(100) DEFAULT '0' COMMENT '权限，默认为0无任何权限',
  `owner` char(200) DEFAULT NULL COMMENT '账号属主，各组之间用|分开',
  `IP_address` char(100) DEFAULT '127.0.0.1' COMMENT '此账号允许从何IP登录，默认127.0.0.1不允许登录',
  PRIMARY KEY (`account`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

insert  into `user`(`account`,`password`,`access`,`owner`,`IP_address`) values ('admin','admin','1',NULL,'192.168.1.1');

/*Table structure for table `user_action_log` */

DROP TABLE IF EXISTS `user_action_log`;

CREATE TABLE `user_action_log` (
  `serial` int(10) NOT NULL AUTO_INCREMENT COMMENT '流水号',
  `account` char(20) DEFAULT NULL COMMENT '登录登出账号',
  `action` char(100) DEFAULT NULL COMMENT '动作：（login/logout/cmd=xxx）',
  `result` text COMMENT 'cmd返回的结果（过长可截尾）',
  `ip_address` char(20) DEFAULT NULL COMMENT '客户端IP',
  `time` datetime DEFAULT NULL COMMENT '插入本记录的时间',
  UNIQUE KEY `serial` (`serial`),
  KEY `account` (`account`),
  KEY `action` (`action`,`ip_address`,`time`)
) ENGINE=MyISAM AUTO_INCREMENT=177 DEFAULT CHARSET=utf8;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
