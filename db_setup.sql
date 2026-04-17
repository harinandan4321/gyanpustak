CREATE DATABASE IF NOT EXISTS gyanpustak;
USE gyanpustak;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'support', 'admin', 'superadmin') NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    date_of_birth DATE,
    university VARCHAR(255),
    major VARCHAR(255),
    student_status ENUM('graduate', 'undergraduate') DEFAULT 'undergraduate',
    year_of_study INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id VARCHAR(50) PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    gender ENUM('male', 'female', 'other'),
    salary DECIMAL(12, 2),
    aadhaar VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS universities (
    university_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    rep_first_name VARCHAR(100),
    rep_last_name VARCHAR(100),
    rep_email VARCHAR(255),
    rep_phone VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    university_id INT NOT NULL,
    FOREIGN KEY (university_id) REFERENCES universities(university_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS instructors (
    instructor_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    university_id INT,
    department_id INT,
    FOREIGN KEY (university_id) REFERENCES universities(university_id),
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INT DEFAULT NULL,
    FOREIGN KEY (parent_id) REFERENCES categories(category_id)
);

CREATE TABLE IF NOT EXISTS books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    publisher VARCHAR(255),
    publication_date DATE,
    edition INT DEFAULT 1,
    language VARCHAR(50) DEFAULT 'English',
    format ENUM('hardcover', 'softcover', 'electronic') DEFAULT 'hardcover',
    book_type ENUM('new', 'used') DEFAULT 'new',
    purchase_option ENUM('rent', 'buy', 'both') DEFAULT 'both',
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    rent_price DECIMAL(10, 2),
    quantity INT DEFAULT 0,
    category_id INT,
    avg_rating DECIMAL(3,2) DEFAULT 0.00,
    description TEXT,
    cover_image VARCHAR(500),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE IF NOT EXISTS book_authors (
    book_id INT NOT NULL,
    author_name VARCHAR(255) NOT NULL,
    PRIMARY KEY (book_id, author_name),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS book_keywords (
    book_id INT NOT NULL,
    keyword VARCHAR(100) NOT NULL,
    PRIMARY KEY (book_id, keyword),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(50) NOT NULL,
    course_name VARCHAR(255) NOT NULL,
    university_id INT NOT NULL,
    year INT,
    semester ENUM('fall', 'spring', 'summer'),
    FOREIGN KEY (university_id) REFERENCES universities(university_id)
);

CREATE TABLE IF NOT EXISTS course_departments (
    course_id INT NOT NULL,
    department_id INT NOT NULL,
    PRIMARY KEY (course_id, department_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS course_instructors (
    course_id INT NOT NULL,
    instructor_id INT NOT NULL,
    PRIMARY KEY (course_id, instructor_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS course_books (
    course_id INT NOT NULL,
    book_id INT NOT NULL,
    requirement_type ENUM('required', 'recommended') DEFAULT 'required',
    PRIMARY KEY (course_id, book_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS carts (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL UNIQUE,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cart_items (
    cart_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT DEFAULT 1,
    purchase_option ENUM('rent', 'buy') DEFAULT 'buy',
    PRIMARY KEY (cart_id, book_id),
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_fulfilled TIMESTAMP NULL,
    shipping_type ENUM('standard', '2-day', '1-day') DEFAULT 'standard',
    credit_card_number VARCHAR(20),
    credit_card_expiry VARCHAR(10),
    credit_card_holder VARCHAR(255),
    credit_card_type ENUM('visa', 'mastercard', 'amex', 'discover'),
    order_status ENUM('new', 'processed', 'awaiting shipping', 'shipped', 'canceled') DEFAULT 'new',
    total_amount DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT DEFAULT 1,
    price_each DECIMAL(10, 2) NOT NULL,
    purchase_option ENUM('rent', 'buy') DEFAULT 'buy',
    PRIMARY KEY (order_id, book_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    student_id INT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_student_book (student_id, book_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trouble_tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    problem_description TEXT NOT NULL,
    solution_description TEXT,
    category ENUM('user profile', 'products', 'cart', 'orders', 'other') DEFAULT 'other',
    status ENUM('new', 'assigned', 'in-process', 'completed') DEFAULT 'new',
    created_by_user_id INT NOT NULL,
    assigned_admin_id INT,
    date_logged TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completion_date TIMESTAMP NULL,
    FOREIGN KEY (created_by_user_id) REFERENCES users(user_id),
    FOREIGN KEY (assigned_admin_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS ticket_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    changed_by_user_id INT NOT NULL,
    old_status ENUM('new', 'assigned', 'in-process', 'completed'),
    new_status ENUM('new', 'assigned', 'in-process', 'completed'),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note TEXT,
    FOREIGN KEY (ticket_id) REFERENCES trouble_tickets(ticket_id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by_user_id) REFERENCES users(user_id)
);
