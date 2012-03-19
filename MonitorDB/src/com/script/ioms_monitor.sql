/*
SQLyog 企业版 - MySQL GUI v8.14 
MySQL - 5.1.31-community : Database - ioms_monitor
*********************************************************************
*/
/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`ioms_monitor` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `ioms_monitor`;

/*Table structure for table `active_server` */

DROP TABLE IF EXISTS `active_server`;

CREATE TABLE `active_server` (
  `agent_id` char(60) DEFAULT NULL COMMENT '存活的agent唯一ID',
  `server_IP` char(20) DEFAULT NULL COMMENT '服务器IP',
  `HB_warning` char(250) DEFAULT NULL COMMENT '是否有异常，异常信息：正常为OK',
  `HB_time` datetime DEFAULT NULL COMMENT '最后一次心跳的客户端时间',
  `HB_status` int(2) DEFAULT NULL COMMENT '存活状态，0为不在线，1在线，2其他等等',
  KEY `agent_id` (`agent_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `command_list` */

DROP TABLE IF EXISTS `command_list`;

CREATE TABLE `command_list` (
  `commandName` char(20) NOT NULL COMMENT '可执行命令',
  `commandStatus` char(2) NOT NULL COMMENT '状态(0-停用,1-启用)',
  PRIMARY KEY (`commandName`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

insert  into `command_list`(`commandName`,`commandStatus`) values ('systeminfo','1'),('dir','1'),('tasklist','1'),('taskkill','1'),('net','1'),('start','1'),('ping','1'),('tracert','1'),('netstat','1'),('call','1'),('type','1'),('ls','1');

/*Table structure for table `process_monitor` */

DROP TABLE IF EXISTS `process_monitor`;

CREATE TABLE `process_monitor` (
  `serial` int(10) NOT NULL AUTO_INCREMENT COMMENT '流水号',
  `agent_ip` char(60) DEFAULT NULL COMMENT 'agentIP',
  `process_name` char(30) DEFAULT NULL COMMENT '受监控的进程名',
  `status` char(10) DEFAULT NULL,
  `process_id` char(100) DEFAULT NULL COMMENT '进程ID',
  `process_cpu` int(4) DEFAULT NULL COMMENT '受监控进程CPU使用率',
  `process_ram` int(10) DEFAULT NULL COMMENT '受监控进程RAM使用（KB）',
  `process_vram` int(10) DEFAULT NULL COMMENT '受监控进程虚拟RAM使用',
  `log_time` datetime DEFAULT NULL COMMENT 'log记录时间',
  UNIQUE KEY `serial` (`serial`),
  KEY `agent_ip` (`agent_ip`,`process_name`,`log_time`)
) ENGINE=MyISAM AUTO_INCREMENT=5097114 DEFAULT CHARSET=utf8;

/*Table structure for table `process_restart` */

DROP TABLE IF EXISTS `process_restart`;

CREATE TABLE `process_restart` (
  `serial` int(10) NOT NULL AUTO_INCREMENT COMMENT '流水号',
  `agent_ip` char(60) DEFAULT NULL COMMENT 'agentIP',
  `process_name` char(30) DEFAULT NULL COMMENT '重启的进程名',
  `process_executablepath` char(100) DEFAULT NULL COMMENT '重启进程的执行路径',
  `restart_time` char(30) DEFAULT NULL COMMENT '本地的重启时间',
  `log_time` datetime DEFAULT NULL COMMENT '服务端log记录时间',
  UNIQUE KEY `serial` (`serial`),
  KEY `log_time` (`log_time`),
  KEY `process_name` (`process_name`),
  KEY `agent_ip` (`agent_ip`)
) ENGINE=MyISAM AUTO_INCREMENT=1411 DEFAULT CHARSET=utf8;

/*Table structure for table `server_list` */

DROP TABLE IF EXISTS `server_list`;

CREATE TABLE `server_list` (
  `agent_id` char(60) DEFAULT NULL COMMENT 'agent唯一标识',
  `server_ip_lan` char(20) DEFAULT NULL COMMENT '服务器内网IP',
  `server_ip_wan` char(100) DEFAULT NULL COMMENT '服务器外网IP（如果有多个，用|分开',
  `server_mac_lan` char(20) DEFAULT NULL COMMENT '服务器内网MAC地址',
  `server_type` char(100) DEFAULT NULL COMMENT '服务器操作系统',
  `server_hostname` char(50) DEFAULT NULL COMMENT '服务器主机名',
  `server_codeset` char(20) DEFAULT NULL COMMENT '服务器语言代码',
  `server_systemdir` char(50) DEFAULT NULL COMMENT '服务器操作系统所在目录',
  `server_template` char(100) DEFAULT NULL COMMENT '服务器类型（手工填写）：mysql|gameserver|updateserver',
  `HW_CPU_num` int(2) DEFAULT NULL COMMENT 'CPU数量',
  `HW_CPU_info` text COMMENT 'CPU配置信息',
  `HW_RAM_info` text COMMENT '内存配置信息',
  `HW_DISK_info` text COMMENT '硬盘配置信息',
  `HW_sn` char(50) DEFAULT NULL COMMENT '服务器硬件SN（手工填写）',
  `HW_RACK` char(20) DEFAULT NULL COMMENT '服务器所在机柜和层数（手工填写）:N4机柜',
  `HW_IDC_address` text COMMENT '服务器硬件所在地址（手工填写）南京市XX路XX大楼X层',
  `HW_admin` char(50) DEFAULT NULL COMMENT '服务器负责人（手工填写）：张三',
  `HW_admin_phone` char(100) DEFAULT NULL COMMENT '服务器负责人联系电话（手工填写）',
  `HW_type` char(200) DEFAULT NULL COMMENT '服务器类型（手工填写）：Dell: PowerEdge R710',
  `HW_distribute` int(10) NOT NULL DEFAULT '0' COMMENT '服务器的分配状态，0为未分配，1为已经分配',
  `achieve_time` datetime DEFAULT NULL COMMENT 'agent安装时的时间，即捕获时间',
  KEY `agent_id` (`agent_id`),
  KEY `server_ip_lan` (`server_ip_lan`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `server_monitor` */

DROP TABLE IF EXISTS `server_monitor`;

CREATE TABLE `server_monitor` (
  `serial` int(10) NOT NULL AUTO_INCREMENT COMMENT '流水号',
  `agent_id` char(60) NOT NULL COMMENT 'agentID',
  `agent_ip` char(20) DEFAULT NULL,
  `CPU_load` int(4) DEFAULT NULL COMMENT 'CPU负荷',
  `RAM_load` int(10) DEFAULT NULL COMMENT '已用内存数(KB)',
  `DISK_load` char(50) DEFAULT NULL COMMENT '各盘符空闲空间',
  `network_load_in` int(10) DEFAULT NULL COMMENT '内网网卡带宽使用情况（KB）',
  `network_load_out` int(10) DEFAULT NULL COMMENT '外网网卡带宽使用情况（KB）',
  `HB_time` datetime DEFAULT NULL COMMENT '客户端本次上传心跳的时间（客户端时间）',
  `log_time` datetime DEFAULT NULL COMMENT '记录日志的时间',
  UNIQUE KEY `serial` (`serial`),
  KEY `log_time` (`log_time`),
  KEY `agent_ip` (`agent_ip`)
) ENGINE=MyISAM AUTO_INCREMENT=4929910 DEFAULT CHARSET=utf8;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
