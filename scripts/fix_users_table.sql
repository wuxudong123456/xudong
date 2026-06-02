-- 用户表补全脚本
-- 如果 users 表是从旧版 SQL 创建的（只有5列），运行此脚本添加缺失列
-- 新部署无需运行，Base.metadata.create_all() 会自动创建完整表

ALTER TABLE `users`
  MODIFY COLUMN `role` varchar(20) NOT NULL COMMENT '角色：super_admin/admin/teacher/student',
  ADD COLUMN IF NOT EXISTS `real_name` varchar(50) DEFAULT NULL COMMENT '真实姓名' AFTER `role`,
  ADD COLUMN IF NOT EXISTS `email` varchar(100) DEFAULT NULL COMMENT '邮箱' AFTER `real_name`,
  ADD COLUMN IF NOT EXISTS `phone` varchar(20) DEFAULT NULL COMMENT '手机号' AFTER `email`,
  ADD COLUMN IF NOT EXISTS `avatar` varchar(255) DEFAULT NULL COMMENT '头像URL' AFTER `phone`,
  ADD COLUMN IF NOT EXISTS `status` smallint NOT NULL DEFAULT 1 COMMENT '状态：0=禁用 1=启用' AFTER `avatar`,
  ADD COLUMN IF NOT EXISTS `last_login_time` datetime DEFAULT NULL COMMENT '最后登录时间' AFTER `status`,
  MODIFY COLUMN `is_deleted` smallint NOT NULL DEFAULT 0 COMMENT '逻辑删除',
  ADD COLUMN IF NOT EXISTS `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间' AFTER `is_deleted`,
  ADD COLUMN IF NOT EXISTS `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间' AFTER `create_time`;

-- 更新种子数据：将旧角色名映射为新角色名，添加真实姓名
UPDATE `users` SET `role` = 'super_admin' WHERE `username` = 'admin1';
UPDATE `users` SET `role` = 'admin' WHERE `username` IN ('admin2', 'admin3', 'admin4', 'admin5');