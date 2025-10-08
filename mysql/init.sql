ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'password123';
FLUSH PRIVILEGES;


CREATE DATABASE IF NOT EXISTS classdj;
USE classdj;

CREATE TABLE IF NOT EXISTS class_periods (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  artist VARCHAR(100),
  class_id INT,
  position INT DEFAULT 0,
  FOREIGN KEY (class_id) REFERENCES class_periods(id)
);

CREATE TABLE IF NOT EXISTS play_history (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT,
  played_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students(id)
);
