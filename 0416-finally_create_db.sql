-- 创建数据库（不存在则创建）
CREATE DATABASE IF NOT EXISTS student_management_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE student_management_system;

-- ----------------------------
-- 1. 老师表（新增 identity 身份字段）
-- ----------------------------
DROP TABLE IF EXISTS `teacher`;
CREATE TABLE `teacher` (
  `teacher_id` INT NOT NULL AUTO_INCREMENT COMMENT '老师编号',
  `teacher_name` VARCHAR(50) NOT NULL COMMENT '老师姓名',
  `gender` VARCHAR(10) DEFAULT NULL COMMENT '性别',
  `phone` VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
  `identity` VARCHAR(20) DEFAULT NULL COMMENT '身份：班主任/授课老师/助教/顾问',
  `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除 0-未删 1-已删',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`teacher_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='老师信息表';

INSERT INTO `teacher` (`teacher_name`, `gender`, `phone`, `identity`) VALUES
('张三', '男', '13800138001', '班主任'),
('李四', '女', '13800138002', '授课老师'),
('王五', '男', '13800138003', '班主任'),
('赵六', '女', '13800138004', '授课老师'),
('孙七', '男', '13800138005', '班主任'),
('周八', '女', '13800138006', '授课老师'),
('吴九', '男', '13800138007', '班主任'),
('郑十', '女', '13800138008', '授课老师'),
('冯十一', '男', '13800138009', '班主任'),
('陈十二', '女', '13800138010', '授课老师'),
('褚十三', '男', '13800138011', '班主任'),
('卫十四', '女', '13800138012', '授课老师'),
('蒋十五', '男', '13800138013', '班主任'),
('沈十六', '女', '13800138014', '授课老师'),
('韩十七', '男', '13800138015', '班主任'),
('杨十八', '女', '13800138016', '授课老师'),
('朱十九', '男', '13800138017', '顾问'),
('秦二十', '女', '13800138018', '助教'),
('尤二十一', '男', '13800138019', '顾问'),
('许二十二', '女', '13800138020', '助教');

-- ----------------------------
-- 2. 班级表（新增 close_time 闭班时间）
-- ----------------------------
DROP TABLE IF EXISTS `class_info`;
CREATE TABLE `class_info` (
  `class_id` INT NOT NULL AUTO_INCREMENT COMMENT '班级编号',
  `class_name` VARCHAR(50) NOT NULL COMMENT '班级名称',
  `start_time` DATE DEFAULT NULL COMMENT '开课时间',
  `close_time` DATE DEFAULT NULL COMMENT '闭班时间',
  `head_teacher_id` INT DEFAULT NULL COMMENT '班主任ID',
  `lecturer_id` INT DEFAULT NULL COMMENT '授课老师ID',
  `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`class_id`),
  KEY `idx_head_teacher` (`head_teacher_id`),
  KEY `idx_lecturer` (`lecturer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='班级信息表';

INSERT INTO `class_info` (`class_name`, `start_time`, `close_time`, `head_teacher_id`, `lecturer_id`) VALUES
('Java开发一班', '2024-02-26', '2025-02-26', 1, 2),
('Java开发二班', '2024-03-01', '2025-03-01', 3, 4),
('Python全栈一班', '2024-03-05', '2025-03-05', 5, 6),
('Python全栈二班', '2024-03-10', '2025-03-10', 7, 8),
('大数据开发一班', '2024-03-15', '2025-03-15', 9, 10),
('大数据开发二班', '2024-03-20', '2025-03-20', 11, 12),
('前端开发一班', '2024-03-25', '2025-03-25', 13, 14),
('前端开发二班', '2024-03-30', '2025-03-30', 15, 16),
('软件测试一班', '2024-04-01', '2025-04-01', 17, 18),
('软件测试二班', '2024-04-05', '2025-04-05', 19, 20),
('Java开发三班', '2024-04-10', '2025-04-10', 2, 1),
('Python全栈三班', '2024-04-15', '2025-04-15', 4, 3),
('大数据开发三班', '2024-04-20', '2025-04-20', 6, 5),
('前端开发三班', '2024-04-25', '2025-04-25', 8, 7),
('软件测试三班', '2024-05-01', '2025-05-01', 10, 9),
('Java开发四班', '2024-05-05', '2025-05-05', 12, 11),
('Python全栈四班', '2024-05-10', '2025-05-10', 14, 13),
('大数据开发四班', '2024-05-15', '2025-05-15', 16, 15),
('前端开发四班', '2024-05-20', '2025-05-20', 18, 17),
('软件测试四班', '2024-05-25', '2025-05-25', 20, 19);

-- ----------------------------
-- 3. 学生表
-- ----------------------------
DROP TABLE IF EXISTS `student`;
CREATE TABLE `student` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '学生编号',
  `student_no` VARCHAR(50) NOT NULL COMMENT '学生编号（业务号）',
  `class_id` INT NOT NULL COMMENT '班级ID',
  `student_name` VARCHAR(50) NOT NULL COMMENT '学生姓名',
  `gender` VARCHAR(10) DEFAULT NULL COMMENT '性别',
  `age` INT DEFAULT NULL COMMENT '年龄',
  `native_place` VARCHAR(100) DEFAULT NULL COMMENT '籍贯',
  `graduate_school` VARCHAR(100) DEFAULT NULL COMMENT '毕业院校',
  `major` VARCHAR(100) DEFAULT NULL COMMENT '专业',
  `education` VARCHAR(50) DEFAULT NULL COMMENT '学历',
  `admission_time` DATE DEFAULT NULL COMMENT '入学时间',
  `graduate_time` DATE DEFAULT NULL COMMENT '毕业时间',
  `advisor_id` INT DEFAULT NULL COMMENT '顾问编号',
  `job_open_time` DATE DEFAULT NULL COMMENT '就业开放时间',
  `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除 0-未删 1-已删',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_student_no` (`student_no`),
  KEY `idx_class_id` (`class_id`),
  KEY `idx_name` (`student_name`),
  KEY `idx_age` (`age`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生基本信息表';

INSERT INTO `student` (`student_no`, `class_id`, `student_name`, `gender`, `age`, `native_place`, `graduate_school`, `major`, `education`, `admission_time`, `graduate_time`, `advisor_id`, `job_open_time`) VALUES
('S2024001', 1, '李小明', '男', 22, '北京朝阳', '北京理工大学', '计算机科学', '本科', '2024-02-26', '2025-02-26', 1, '2025-01-01'),
('S2024002', 1, '王小红', '女', 21, '上海浦东', '上海大学', '软件工程', '本科', '2024-02-26', '2025-02-26', 2, '2025-01-02'),
('S2024003', 2, '张小刚', '男', 23, '广州天河', '华南理工', '大数据技术', '大专', '2024-03-01', '2025-03-01', 3, '2025-01-03'),
('S2024004', 2, '刘小丽', '女', 20, '深圳南山', '深圳大学', '前端开发', '大专', '2024-03-01', '2025-03-01', 4, '2025-01-04'),
('S2024005', 3, '陈小强', '男', 24, '杭州西湖', '浙江大学', 'Python开发', '本科', '2024-03-05', '2025-03-05', 5, '2025-01-05'),
('S2024006', 3, '杨小红', '女', 22, '南京鼓楼', '南京大学', '软件测试', '本科', '2024-03-05', '2025-03-05', 6, '2025-01-06'),
('S2024007', 4, '黄小强', '男', 25, '成都锦江', '四川大学', 'Java开发', '大专', '2024-03-10', '2025-03-10', 7, '2025-01-07'),
('S2024008', 4, '周小红', '女', 21, '重庆渝中', '重庆大学', '大数据', '本科', '2024-03-10', '2025-03-10', 8, '2025-01-08'),
('S2024009', 5, '吴小刚', '男', 23, '武汉洪山', '武汉大学', '全栈开发', '大专', '2024-03-15', '2025-03-15', 9, '2025-01-09'),
('S2024010', 5, '郑小红', '女', 20, '西安雁塔', '西安电子科大', '软件工程', '本科', '2024-03-15', '2025-03-15', 10, '2025-01-10'),
('S2024011', 6, '郭小刚', '男', 24, '济南历下', '山东大学', '计算机技术', '大专', '2024-03-20', '2025-03-20', 11, '2025-01-11'),
('S2024012', 6, '孙小红', '女', 22, '青岛崂山', '青岛大学', '前端开发', '本科', '2024-03-20', '2025-03-20', 12, '2025-01-12'),
('S2024013', 7, '马小刚', '男', 21, '长沙岳麓', '湖南大学', '软件测试', '大专', '2024-03-25', '2025-03-25', 13, '2025-01-13'),
('S2024014', 7, '朱小红', '女', 23, '郑州金水', '郑州大学', 'Java开发', '本科', '2024-03-25', '2025-03-25', 14, '2025-01-14'),
('S2024015', 8, '胡小刚', '男', 25, '合肥蜀山', '合肥工业大学', '大数据', '大专', '2024-03-30', '2025-03-30', 15, '2025-01-15'),
('S2024016', 8, '林小红', '女', 20, '福州鼓楼', '福州大学', 'Python开发', '本科', '2024-03-30', '2025-03-30', 16, '2025-01-16'),
('S2024017', 9, '彭小刚', '男', 22, '昆明五华', '云南大学', '全栈开发', '大专', '2024-04-01', '2025-04-01', 17, '2025-01-17'),
('S2024018', 9, '钟小红', '女', 24, '太原小店', '太原理工', '软件工程', '本科', '2024-04-01', '2025-04-01', 18, '2025-01-18'),
('S2024019', 10, '汪小刚', '男', 21, '南宁青秀', '广西大学', '前端开发', '大专', '2024-04-05', '2025-04-05', 19, '2025-01-19'),
('S2024020', 10, '田小红', '女', 23, '哈尔滨南岗', '哈工大', '软件测试', '本科', '2024-04-05', '2025-04-05', 20, '2025-01-20'),
('S2024021', 11, '夏小刚', '男', 26, '长春南关', '吉林大学', 'Java开发', '大专', '2024-04-10', '2025-04-10', 1, '2025-01-21'),
('S2024022', 12, '任小红', '女', 22, '兰州城关', '兰州大学', '大数据', '本科', '2024-04-15', '2025-04-15', 2, '2025-01-22'),
('S2024023', 13, '姜小刚', '男', 24, '乌鲁木齐新市', '新疆大学', 'Python开发', '大专', '2024-04-20', '2025-04-20', 3, '2025-01-23'),
('S2024024', 14, '薛小红', '女', 21, '贵阳南明', '贵州大学', '全栈开发', '本科', '2024-04-25', '2025-04-25', 4, '2025-01-24'),
('S2024025', 15, '白小刚', '男', 23, '海口龙华', '海南大学', '软件工程', '大专', '2024-05-01', '2025-05-01', 5, '2025-01-25');

-- ----------------------------
-- 4. 成绩表
-- ----------------------------
DROP TABLE IF EXISTS `score`;
CREATE TABLE `score` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '成绩ID',
  `student_no` VARCHAR(50) NOT NULL COMMENT '学生编号',
  `exam_order` INT NOT NULL COMMENT '考核序次',
  `score` DECIMAL(5,2) DEFAULT NULL COMMENT '成绩',
  `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_student_exam` (`student_no`,`exam_order`),
  KEY `idx_student_no` (`student_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生考核成绩表';

INSERT INTO `score` (`student_no`, `exam_order`, `score`) VALUES
('S2024001',1,85.5),('S2024001',2,92.0),('S2024002',1,78.0),('S2024002',2,88.5),
('S2024003',1,65.0),('S2024003',2,72.5),('S2024004',1,90.0),('S2024004',2,95.0),
('S2024005',1,82.5),('S2024005',2,89.0),('S2024006',1,75.0),('S2024006',2,81.5),
('S2024007',1,68.0),('S2024007',2,74.0),('S2024008',1,93.5),('S2024008',2,98.0),
('S2024009',1,80.0),('S2024009',2,86.5),('S2024010',1,72.0),('S2024010',2,79.0),
('S2024011',1,62.5),('S2024011',2,69.0),('S2024012',1,88.0),('S2024012',2,94.5),
('S2024013',1,76.5),('S2024013',2,83.0),('S2024014',1,70.0),('S2024014',2,77.5),
('S2024015',1,91.0),('S2024015',2,96.5),('S2024016',1,84.0),('S2024016',2,90.5),
('S2024017',1,66.0),('S2024017',2,73.0),('S2024018',1,79.5),('S2024018',2,85.0),
('S2024019',1,81.0),('S2024019',2,87.5),('S2024020',1,74.0),('S2024020',2,80.0),
('S2024021',1,59.0),('S2024021',2,65.5),('S2024022',1,92.5),('S2024022',2,97.0),
('S2024023',1,77.0),('S2024023',2,84.0),('S2024024',1,63.5),('S2024024',2,71.0),
('S2024025',1,86.0),('S2024025',2,91.5);

-- ----------------------------
-- 5. 就业表
-- ----------------------------
DROP TABLE IF EXISTS `employment`;
CREATE TABLE `employment` (
  `employment_id` INT NOT NULL AUTO_INCREMENT COMMENT '就业ID',
  `student_no` VARCHAR(50) NOT NULL COMMENT '学生编号',
  `student_name` VARCHAR(50) NOT NULL COMMENT '学生姓名（冗余）',
  `class_id` INT NOT NULL COMMENT '班级ID（冗余）',
  `offer_send_time` DATE DEFAULT NULL COMMENT 'offer下发时间',
  `company_name` VARCHAR(100) DEFAULT NULL COMMENT '就业公司',
  `offer_job` VARCHAR(50) DEFAULT NULL COMMENT 'offer岗位',
  `final_choice` INT DEFAULT NULL COMMENT '是否最终选择 0-否 1-是',
  `salary` INT DEFAULT NULL COMMENT '就业薪资',
  `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`employment_id`),
  UNIQUE KEY `uk_student_no` (`student_no`),
  KEY `idx_company` (`company_name`),
  KEY `idx_salary` (`salary`),
  KEY `idx_class_id` (`class_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生就业信息表';

INSERT INTO `employment` (`student_no`, `student_name`, `class_id`, `offer_send_time`, `company_name`, `offer_job`, `final_choice`, `salary`) VALUES
('S2024001','李小明',1,'2025-01-10','百度','后端开发工程师',1,12000),
('S2024002','王小红',1,'2025-01-12','阿里','测试开发工程师',1,11000),
('S2024003','张小刚',2,'2025-01-15','腾讯','后端开发工程师',1,13000),
('S2024004','刘小丽',2,'2025-01-18','字节','前端开发工程师',1,10000),
('S2024005','陈小强',3,'2025-01-20','美团','Python开发',0,9000),
('S2024006','杨小红',3,'2025-01-22','滴滴','测试工程师',1,8500),
('S2024007','黄小强',4,'2025-01-25','京东','Java开发',1,11500),
('S2024008','周小红',4,'2025-01-28','拼多多','大数据开发',1,12500),
('S2024009','吴小刚',5,'2025-02-01','网易','全栈开发',0,9500),
('S2024010','郑小红',5,'2025-02-03','新浪','前端开发',1,8000),
('S2024011','郭小刚',6,'2025-02-05','小米','Android开发',1,10500),
('S2024012','孙小红',6,'2025-02-08','华为','云计算工程师',1,14000),
('S2024013','马小刚',7,'2025-02-10','OPPO','测试工程师',0,7500),
('S2024014','朱小红',7,'2025-02-12','VIVO','前端开发',1,8800),
('S2024015','胡小刚',8,'2025-02-15','携程','Java开发',1,11800),
('S2024016','林小红',8,'2025-02-18','快手','大数据开发',1,10800),
('S2024017','彭小刚',9,'2025-02-20','B站','Python开发',0,9200),
('S2024018','钟小红',9,'2025-02-22','小红书','后端开发',1,13500),
('S2024019','汪小刚',10,'2025-02-25','用友','软件测试',1,7800),
('S2024020','田小红',10,'2025-02-28','金蝶','前端开发',1,8200),
('S2024021','夏小刚',11,'2025-03-01','科大讯飞','AI开发',1,11200),
('S2024022','任小红',12,'2025-03-03','奇安信','网络安全',1,10200),
('S2024023','姜小刚',13,'2025-03-05','深信服','安全工程师',0,9800),
('S2024024','薛小红',14,'2025-03-08','海康威视','嵌入式开发',1,12200),
('S2024025','白小刚',15,'2025-03-10','大华股份','运维工程师',1,8600);

-- ----------------------------
-- 6. 用户表
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '用户ID，自增主键',
  `username` varchar(255) NOT NULL COMMENT '用户名',
  `password` varchar(255) NOT NULL COMMENT '密码（建议加密存储）',
  `role` varchar(10) NOT NULL COMMENT '角色，例如：admin/student/teacher',
  `is_deleted` int NOT NULL DEFAULT '0' COMMENT '逻辑删除：0=未删除，1=已删除',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

INSERT INTO `users` (username, password, role) VALUES
('admin1', '123456', 'admin'),('admin2', '123456', 'admin'),('admin3', '123456', 'admin'),('admin4', '123456', 'admin'),('admin5', '123456', 'admin'),
('teacher1', '123456', 'teacher'),('teacher2', '123456', 'teacher'),('teacher3', '123456', 'teacher'),('teacher4', '123456', 'teacher'),('teacher5', '123456', 'teacher'),('teacher6', '123456', 'teacher'),('teacher7', '123456', 'teacher'),
('student1', '123456', 'student'),('student2', '123456', 'student'),('student3', '123456', 'student'),('student4', '123456', 'student'),('student5', '123456', 'student'),('student6', '123456', 'student'),('student7', '123456', 'student'),('student8', '123456', 'student');

SELECT '数据库更新完成：老师表加身份、班级表加闭班时间，均已填入20条测试数据' AS result;