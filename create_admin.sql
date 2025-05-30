-- Insert admin user with hashed password (password is 'admin123')
INSERT INTO `user` (`username`, `email`, `password_hash`, `first_name`, `last_name`, `role`, `is_active`, `date_created`)
VALUES (
    'admin',
    'admin@hospital.com',
    'pbkdf2:sha256:600000$X7URHhJt$c8c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1',
    'Admin',
    'User',
    'admin',
    1,
    NOW()
)
ON DUPLICATE KEY UPDATE
    `email` = VALUES(`email`),
    `password_hash` = VALUES(`password_hash`),
    `first_name` = VALUES(`first_name`),
    `last_name` = VALUES(`last_name`),
    `role` = VALUES(`role`),
    `is_active` = VALUES(`is_active`); 