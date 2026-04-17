USE gyanpustak;

INSERT INTO users (email, password_hash, role, first_name, last_name, phone, address) VALUES
('superadmin@demo.com', 'scrypt:32768:8:1$kCCAa4KXHsJW1vZs$8809df2f844a6f6268e007a8b843161b8e95d3df447502178886963a83fe2f6805a9ed568662a4e73c64944fa6cb39852730c260689dcd28e5ddc946152658dc', 'superadmin', 'Super', 'Admin', '9876543210', 'GyanPustak HQ, Bangalore'),
('admin@demo.com', 'scrypt:32768:8:1$kCCAa4KXHsJW1vZs$8809df2f844a6f6268e007a8b843161b8e95d3df447502178886963a83fe2f6805a9ed568662a4e73c64944fa6cb39852730c260689dcd28e5ddc946152658dc', 'admin', 'Arun', 'Sharma', '9876543211', 'GyanPustak HQ, Bangalore'),
('support@demo.com', 'scrypt:32768:8:1$kCCAa4KXHsJW1vZs$8809df2f844a6f6268e007a8b843161b8e95d3df447502178886963a83fe2f6805a9ed568662a4e73c64944fa6cb39852730c260689dcd28e5ddc946152658dc', 'support', 'Priya', 'Patel', '9876543212', 'GyanPustak HQ, Mumbai'),
('student@demo.com', 'scrypt:32768:8:1$kCCAa4KXHsJW1vZs$8809df2f844a6f6268e007a8b843161b8e95d3df447502178886963a83fe2f6805a9ed568662a4e73c64944fa6cb39852730c260689dcd28e5ddc946152658dc', 'student', 'Rahul', 'Verma', '9876543213', 'IIT Bombay Campus, Mumbai'),
('alice@demo.com', 'scrypt:32768:8:1$kCCAa4KXHsJW1vZs$8809df2f844a6f6268e007a8b843161b8e95d3df447502178886963a83fe2f6805a9ed568662a4e73c64944fa6cb39852730c260689dcd28e5ddc946152658dc', 'student', 'Alice', 'Johnson', '9876543214', 'BITS Pilani Campus');

INSERT INTO employees (employee_id, user_id, gender, salary, aadhaar) VALUES
('SA001', 1, 'male', 150000.00, '123456789012'),
('ADM001', 2, 'male', 80000.00, '234567890123'),
('SUP001', 3, 'female', 50000.00, '345678901234');

INSERT INTO students (user_id, date_of_birth, university, major, student_status, year_of_study) VALUES
(4, '2002-05-15', 'IIT Bombay', 'Computer Science and Engineering', 'undergraduate', 3),
(5, '2001-08-22', 'BITS Pilani', 'Electronics and Communication', 'undergraduate', 4);

INSERT INTO universities (name, address, rep_first_name, rep_last_name, rep_email, rep_phone) VALUES
('Indian Institute of Technology Bombay', 'Powai, Mumbai - 400076', 'Dr. Ramesh', 'Kumar', 'ramesh.kumar@iitb.ac.in', '022-25722545'),
('BITS Pilani', 'Vidya Vihar, Pilani - 333031', 'Prof. Suresh', 'Mehta', 'suresh@bits-pilani.ac.in', '01596-242192'),
('Delhi University', 'North Campus, New Delhi - 110007', 'Dr. Anita', 'Singh', 'anita@du.ac.in', '011-27667853');

INSERT INTO departments (name, university_id) VALUES
('Computer Science & Engineering', 1),
('Electrical Engineering', 1),
('Computer Science', 2),
('Electronics & Communication', 2),
('Computer Science', 3);

INSERT INTO categories (name, parent_id) VALUES
('Computer Science', NULL),
('Mathematics', NULL),
('Physics', NULL),
('Engineering', NULL),
('Business', NULL),
('Programming', 1),
('Data Structures & Algorithms', 1),
('Machine Learning & AI', 1),
('Databases', 1),
('Networking', 1),
('Calculus', 2),
('Linear Algebra', 2);

INSERT INTO books (title, isbn, publisher, publication_date, edition, language, format, book_type, purchase_option, price, rent_price, quantity, category_id, description) VALUES
('Introduction to Algorithms', '978-0262046305', 'MIT Press', '2022-04-05', 4, 'English', 'hardcover', 'new', 'both', 1299.00, 299.00, 50, 7, 'The leading algorithms textbook, known as CLRS.'),
('Clean Code: A Handbook of Agile Software Craftsmanship', '978-0132350884', 'Prentice Hall', '2008-08-01', 1, 'English', 'softcover', 'new', 'both', 899.00, 199.00, 30, 6, 'A handbook of agile software craftsmanship.'),
('Database System Concepts', '978-0078022159', 'McGraw-Hill', '2019-03-01', 7, 'English', 'hardcover', 'new', 'buy', 1599.00, NULL, 20, 9, 'Comprehensive database systems textbook.'),
('Python Crash Course', '978-1593279288', 'No Starch Press', '2019-05-01', 2, 'English', 'softcover', 'new', 'both', 699.00, 149.00, 100, 6, 'A hands-on, project-based introduction to Python.'),
('The Art of Computer Programming Vol. 1', '978-0201896831', 'Addison-Wesley', '1997-07-01', 3, 'English', 'hardcover', 'new', 'buy', 2499.00, NULL, 10, 1, 'Fundamental algorithms by Donald Knuth.'),
('Discrete Mathematics and Its Applications', '978-0073383095', 'McGraw-Hill', '2018-01-01', 8, 'English', 'hardcover', 'new', 'both', 1199.00, 249.00, 40, 2, 'Comprehensive discrete mathematics textbook.'),
('Machine Learning: A Probabilistic Perspective', '978-0262018029', 'MIT Press', '2012-09-01', 1, 'English', 'hardcover', 'new', 'buy', 1799.00, NULL, 15, 8, 'Murphy\'s comprehensive ML textbook.'),
('Computer Networks', '978-0133594164', 'Pearson', '2021-01-01', 6, 'English', 'hardcover', 'new', 'both', 1099.00, 229.00, 25, 10, 'Tanenbaum\'s classic networking textbook.'),
('Operating System Concepts', '978-1119320913', 'Wiley', '2018-06-01', 10, 'English', 'hardcover', 'new', 'both', 1399.00, 279.00, 35, 1, 'The Dinosaur Book - classic OS textbook.'),
('Linear Algebra Done Right', '978-3319110790', 'Springer', '2015-07-01', 3, 'English', 'softcover', 'new', 'both', 799.00, 169.00, 20, 12, 'Axler\'s approach to linear algebra without determinants.'),
('Deep Learning', '978-0262035613', 'MIT Press', '2016-11-18', 1, 'English', 'hardcover', 'new', 'both', 1499.00, 319.00, 18, 8, 'Goodfellow, Bengio, and Courville\'s definitive deep learning text.'),
('The Pragmatic Programmer', '978-0135957059', 'Addison-Wesley', '2019-09-30', 2, 'English', 'softcover', 'new', 'both', 849.00, 179.00, 45, 6, 'From journeyman to master - essential developer career guide.'),
('Data Structures Using C', '978-0198065097', 'Oxford University Press', '2014-01-01', 2, 'English', 'softcover', 'used', 'both', 499.00, 99.00, 60, 7, 'Popular data structures book for CS students.'),
('Engineering Mathematics', '978-1259064449', 'McGraw-Hill', '2017-01-01', 4, 'English', 'hardcover', 'new', 'both', 699.00, 149.00, 55, 2, 'Comprehensive mathematics for engineering students.'),
('Artificial Intelligence: A Modern Approach', '978-0134610993', 'Pearson', '2020-04-28', 4, 'English', 'hardcover', 'new', 'buy', 1899.00, NULL, 12, 8, 'Russell and Norvig\'s definitive AI textbook.');

INSERT INTO book_authors (book_id, author_name) VALUES
(1, 'Thomas H. Cormen'), (1, 'Charles E. Leiserson'), (1, 'Ronald L. Rivest'), (1, 'Clifford Stein'),
(2, 'Robert C. Martin'),
(3, 'Abraham Silberschatz'), (3, 'Henry F. Korth'), (3, 'S. Sudarshan'),
(4, 'Eric Matthes'),
(5, 'Donald E. Knuth'),
(6, 'Kenneth H. Rosen'),
(7, 'Kevin P. Murphy'),
(8, 'Andrew S. Tanenbaum'), (8, 'David J. Wetherall'),
(9, 'Abraham Silberschatz'), (9, 'Greg Gagne'), (9, 'Peter Galvin'),
(10, 'Sheldon Axler'),
(11, 'Ian Goodfellow'), (11, 'Yoshua Bengio'), (11, 'Aaron Courville'),
(12, 'David Thomas'), (12, 'Andrew Hunt'),
(13, 'Reema Thareja'),
(14, 'B.S. Grewal'),
(15, 'Stuart Russell'), (15, 'Peter Norvig');

INSERT INTO book_keywords (book_id, keyword) VALUES
(1, 'algorithms'), (1, 'sorting'), (1, 'data structures'), (1, 'CLRS'),
(2, 'clean code'), (2, 'software engineering'), (2, 'best practices'),
(3, 'database'), (3, 'SQL'), (3, 'DBMS'), (3, 'transactions'),
(4, 'python'), (4, 'programming'), (4, 'beginner'),
(5, 'algorithms'), (5, 'Knuth'), (5, 'TAOCP'),
(6, 'discrete math'), (6, 'logic'), (6, 'combinatorics'),
(7, 'machine learning'), (7, 'probabilistic'), (7, 'ML'),
(8, 'networking'), (8, 'TCP/IP'), (8, 'protocols'),
(9, 'operating systems'), (9, 'OS'), (9, 'processes'),
(10, 'linear algebra'), (10, 'vectors'), (10, 'matrices'),
(11, 'deep learning'), (11, 'neural networks'), (11, 'AI'),
(12, 'programming'), (12, 'pragmatic'), (12, 'developer'),
(13, 'data structures'), (13, 'C language'), (13, 'programming'),
(14, 'mathematics'), (14, 'engineering math'), (14, 'calculus'),
(15, 'AI'), (15, 'artificial intelligence'), (15, 'search');

INSERT INTO instructors (first_name, last_name, university_id, department_id) VALUES
('Prof. Pradeep', 'Sinha', 1, 1),
('Dr. Sunita', 'Sarawagi', 1, 1),
('Prof. Pushpak', 'Bhattacharyya', 1, 1),
('Dr. Manish', 'Gupta', 2, 3);

INSERT INTO courses (course_code, course_name, university_id, year, semester) VALUES
('CS601', 'Database Management Systems', 1, 2025, 'fall'),
('CS602', 'Design and Analysis of Algorithms', 1, 2025, 'fall'),
('CS603', 'Machine Learning', 1, 2025, 'spring'),
('CS301', 'Data Structures and Algorithms', 2, 2025, 'fall'),
('MATH201', 'Engineering Mathematics II', 1, 2025, 'spring');

INSERT INTO course_departments (course_id, department_id) VALUES
(1, 1), (2, 1), (3, 1), (4, 3), (5, 1), (5, 2);

INSERT INTO course_instructors (course_id, instructor_id) VALUES
(1, 2), (2, 1), (3, 3), (4, 4), (5, 1);

INSERT INTO course_books (course_id, book_id, requirement_type) VALUES
(1, 3, 'required'), (2, 1, 'required'), (2, 13, 'recommended'),
(3, 7, 'required'), (3, 11, 'recommended'), (3, 15, 'recommended'),
(4, 1, 'required'), (4, 13, 'required'), (5, 6, 'required'), (5, 14, 'required');
