"""
Seed the GyanPustak database with sample data.
Run this once after database schema is created.
"""
import mysql.connector
from werkzeug.security import generate_password_hash

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'gyanpustak',
}

def seed():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    pw = generate_password_hash('password')

    users = [
        ('superadmin@demo.com', pw, 'superadmin', 'Super', 'Admin', '9876543210', 'GyanPustak HQ, Bangalore'),
        ('admin@demo.com', pw, 'admin', 'Arun', 'Sharma', '9876543211', 'GyanPustak HQ, Bangalore'),
        ('support@demo.com', pw, 'support', 'Priya', 'Patel', '9876543212', 'GyanPustak HQ, Mumbai'),
        ('student@demo.com', pw, 'student', 'Rahul', 'Verma', '9876543213', 'IIT Bombay Campus, Mumbai'),
        ('alice@demo.com', pw, 'student', 'Alice', 'Johnson', '9876543214', 'BITS Pilani Campus'),
    ]

    for u in users:
        try:
            cursor.execute('INSERT INTO users (email, password_hash, role, first_name, last_name, phone, address) VALUES (%s,%s,%s,%s,%s,%s,%s)', u)
        except Exception:
            pass

    conn.commit()
    cursor.execute('SELECT user_id, role FROM users ORDER BY user_id')
    user_rows = cursor.fetchall()
    uid_map = {r[1]: r[0] for r in user_rows}

    for role, eid, gender, salary, aadhaar in [
        ('superadmin', 'SA001', 'male', 150000, '123456789012'),
        ('admin', 'ADM001', 'male', 80000, '234567890123'),
        ('support', 'SUP001', 'female', 50000, '345678901234'),
    ]:
        uid = uid_map.get(role)
        if uid:
            try:
                cursor.execute('INSERT INTO employees (employee_id, user_id, gender, salary, aadhaar) VALUES (%s,%s,%s,%s,%s)',
                               (eid, uid, gender, salary, aadhaar))
            except Exception:
                pass

    conn.commit()

    cursor.execute("SELECT user_id FROM users WHERE role='student' ORDER BY user_id")
    student_users = [r[0] for r in cursor.fetchall()]
    for i, uid in enumerate(student_users):
        try:
            dob = '2002-05-15' if i == 0 else '2001-08-22'
            univ = 'IIT Bombay' if i == 0 else 'BITS Pilani'
            major = 'Computer Science and Engineering' if i == 0 else 'Electronics and Communication'
            year = 3 if i == 0 else 4
            cursor.execute('INSERT INTO students (user_id, date_of_birth, university, major, student_status, year_of_study) VALUES (%s,%s,%s,%s,%s,%s)',
                           (uid, dob, univ, major, 'undergraduate', year))
        except Exception:
            pass
    conn.commit()

    for name, addr, rf, rl, re, rp in [
        ('Indian Institute of Technology Bombay', 'Powai, Mumbai - 400076', 'Dr. Ramesh', 'Kumar', 'ramesh@iitb.ac.in', '022-25722545'),
        ('BITS Pilani', 'Vidya Vihar, Pilani - 333031', 'Prof. Suresh', 'Mehta', 'suresh@bits-pilani.ac.in', '01596-242192'),
        ('Delhi University', 'North Campus, New Delhi - 110007', 'Dr. Anita', 'Singh', 'anita@du.ac.in', '011-27667853'),
    ]:
        try:
            cursor.execute('INSERT INTO universities (name, address, rep_first_name, rep_last_name, rep_email, rep_phone) VALUES (%s,%s,%s,%s,%s,%s)',
                           (name, addr, rf, rl, re, rp))
        except Exception:
            pass
    conn.commit()

    for dname, uid in [
        ('Computer Science & Engineering', 1), ('Electrical Engineering', 1),
        ('Computer Science', 2), ('Electronics & Communication', 2), ('Computer Science', 3)
    ]:
        try:
            cursor.execute('INSERT INTO departments (name, university_id) VALUES (%s,%s)', (dname, uid))
        except Exception:
            pass
    conn.commit()

    categories = [
        ('Computer Science', None), ('Mathematics', None), ('Physics', None),
        ('Engineering', None), ('Business', None),
    ]
    for name, pid in categories:
        try:
            cursor.execute('INSERT INTO categories (name, parent_id) VALUES (%s,%s)', (name, pid))
        except Exception:
            pass
    conn.commit()

    cursor.execute('SELECT category_id FROM categories WHERE name=%s', ('Computer Science',))
    cs_id = cursor.fetchone()
    if cs_id:
        cs_id = cs_id[0]
        for name in ['Programming', 'Data Structures & Algorithms', 'Machine Learning & AI', 'Databases', 'Networking']:
            try:
                cursor.execute('INSERT INTO categories (name, parent_id) VALUES (%s,%s)', (name, cs_id))
            except Exception:
                pass
    cursor.execute('SELECT category_id FROM categories WHERE name=%s', ('Mathematics',))
    math_id = cursor.fetchone()
    if math_id:
        math_id = math_id[0]
        for name in ['Calculus', 'Linear Algebra']:
            try:
                cursor.execute('INSERT INTO categories (name, parent_id) VALUES (%s,%s)', (name, math_id))
            except Exception:
                pass
    conn.commit()

    cursor.execute("SELECT category_id FROM categories WHERE name='Data Structures & Algorithms'")
    dsa_id = (cursor.fetchone() or [7])[0]
    cursor.execute("SELECT category_id FROM categories WHERE name='Programming'")
    prog_id = (cursor.fetchone() or [6])[0]
    cursor.execute("SELECT category_id FROM categories WHERE name='Databases'")
    db_id = (cursor.fetchone() or [9])[0]
    cursor.execute("SELECT category_id FROM categories WHERE name='Machine Learning & AI'")
    ml_id = (cursor.fetchone() or [8])[0]
    cursor.execute("SELECT category_id FROM categories WHERE name='Networking'")
    net_id = (cursor.fetchone() or [10])[0]
    cursor.execute("SELECT category_id FROM categories WHERE name='Linear Algebra'")
    la_id = (cursor.fetchone() or [12])[0]

    books = [
        ('Introduction to Algorithms', '978-0262046305', 'MIT Press', '2022-04-05', 4, 'English', 'hardcover', 'new', 'both', 1299.00, 299.00, 50, dsa_id, 'The leading algorithms textbook, known as CLRS.'),
        ('Clean Code', '978-0132350884', 'Prentice Hall', '2008-08-01', 1, 'English', 'softcover', 'new', 'both', 899.00, 199.00, 30, prog_id, 'A handbook of agile software craftsmanship.'),
        ('Database System Concepts', '978-0078022159', 'McGraw-Hill', '2019-03-01', 7, 'English', 'hardcover', 'new', 'buy', 1599.00, None, 20, db_id, 'Comprehensive database systems textbook.'),
        ('Python Crash Course', '978-1593279288', 'No Starch Press', '2019-05-01', 2, 'English', 'softcover', 'new', 'both', 699.00, 149.00, 100, prog_id, 'Hands-on introduction to Python.'),
        ('The Art of Computer Programming Vol. 1', '978-0201896831', 'Addison-Wesley', '1997-07-01', 3, 'English', 'hardcover', 'new', 'buy', 2499.00, None, 10, dsa_id, 'Fundamental algorithms by Donald Knuth.'),
        ('Discrete Mathematics and Its Applications', '978-0073383095', 'McGraw-Hill', '2018-01-01', 8, 'English', 'hardcover', 'new', 'both', 1199.00, 249.00, 40, cs_id if cs_id else 1, 'Comprehensive discrete mathematics textbook.'),
        ('Machine Learning: A Probabilistic Perspective', '978-0262018029', 'MIT Press', '2012-09-01', 1, 'English', 'hardcover', 'new', 'buy', 1799.00, None, 15, ml_id, "Murphy's ML textbook."),
        ('Computer Networks', '978-0133594164', 'Pearson', '2021-01-01', 6, 'English', 'hardcover', 'new', 'both', 1099.00, 229.00, 25, net_id, "Tanenbaum's networking textbook."),
        ('Operating System Concepts', '978-1119320913', 'Wiley', '2018-06-01', 10, 'English', 'hardcover', 'new', 'both', 1399.00, 279.00, 35, cs_id if cs_id else 1, 'The Dinosaur Book - classic OS textbook.'),
        ('Linear Algebra Done Right', '978-3319110790', 'Springer', '2015-07-01', 3, 'English', 'softcover', 'new', 'both', 799.00, 169.00, 20, la_id, "Axler's approach to linear algebra."),
        ('Deep Learning', '978-0262035613', 'MIT Press', '2016-11-18', 1, 'English', 'hardcover', 'new', 'both', 1499.00, 319.00, 18, ml_id, "Goodfellow, Bengio, Courville's deep learning text."),
        ('The Pragmatic Programmer', '978-0135957059', 'Addison-Wesley', '2019-09-30', 2, 'English', 'softcover', 'new', 'both', 849.00, 179.00, 45, prog_id, 'Essential developer career guide.'),
        ('Data Structures Using C', '978-0198065097', 'Oxford University Press', '2014-01-01', 2, 'English', 'softcover', 'used', 'both', 499.00, 99.00, 60, dsa_id, 'Popular data structures book for CS students.'),
        ('Engineering Mathematics', '978-1259064449', 'McGraw-Hill', '2017-01-01', 4, 'English', 'hardcover', 'new', 'both', 699.00, 149.00, 55, math_id if math_id else 2, 'Comprehensive mathematics for engineering students.'),
        ('Artificial Intelligence: A Modern Approach', '978-0134610993', 'Pearson', '2020-04-28', 4, 'English', 'hardcover', 'new', 'buy', 1899.00, None, 12, ml_id, "Russell and Norvig's definitive AI textbook."),
    ]
    book_ids = []
    for b in books:
        try:
            cursor.execute('''INSERT INTO books (title, isbn, publisher, publication_date, edition, language, format, book_type, purchase_option, price, rent_price, quantity, category_id, description)
                              VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', b)
            book_ids.append(cursor.lastrowid)
        except Exception as e:
            cursor.execute('SELECT book_id FROM books WHERE title=%s', (b[0],))
            row = cursor.fetchone()
            book_ids.append(row[0] if row else None)
    conn.commit()

    authors_map = {
        0: ['Thomas H. Cormen', 'Charles E. Leiserson', 'Ronald L. Rivest', 'Clifford Stein'],
        1: ['Robert C. Martin'],
        2: ['Abraham Silberschatz', 'Henry F. Korth', 'S. Sudarshan'],
        3: ['Eric Matthes'],
        4: ['Donald E. Knuth'],
        5: ['Kenneth H. Rosen'],
        6: ['Kevin P. Murphy'],
        7: ['Andrew S. Tanenbaum', 'David J. Wetherall'],
        8: ['Abraham Silberschatz', 'Greg Gagne', 'Peter Galvin'],
        9: ['Sheldon Axler'],
        10: ['Ian Goodfellow', 'Yoshua Bengio', 'Aaron Courville'],
        11: ['David Thomas', 'Andrew Hunt'],
        12: ['Reema Thareja'],
        13: ['B.S. Grewal'],
        14: ['Stuart Russell', 'Peter Norvig'],
    }
    keywords_map = {
        0: ['algorithms', 'sorting', 'data structures', 'CLRS'],
        1: ['clean code', 'software engineering', 'best practices'],
        2: ['database', 'SQL', 'DBMS', 'transactions'],
        3: ['python', 'programming', 'beginner'],
        4: ['algorithms', 'Knuth', 'TAOCP'],
        5: ['discrete math', 'logic', 'combinatorics'],
        6: ['machine learning', 'probabilistic', 'ML'],
        7: ['networking', 'TCP/IP', 'protocols'],
        8: ['operating systems', 'OS', 'processes'],
        9: ['linear algebra', 'vectors', 'matrices'],
        10: ['deep learning', 'neural networks', 'AI'],
        11: ['programming', 'pragmatic', 'developer'],
        12: ['data structures', 'C language', 'programming'],
        13: ['mathematics', 'engineering math', 'calculus'],
        14: ['AI', 'artificial intelligence', 'search'],
    }
    for i, bid in enumerate(book_ids):
        if not bid:
            continue
        for author in authors_map.get(i, []):
            try:
                cursor.execute('INSERT INTO book_authors (book_id, author_name) VALUES (%s,%s)', (bid, author))
            except Exception:
                pass
        for kw in keywords_map.get(i, []):
            try:
                cursor.execute('INSERT INTO book_keywords (book_id, keyword) VALUES (%s,%s)', (bid, kw))
            except Exception:
                pass
    conn.commit()

    cursor.execute("SELECT university_id FROM universities ORDER BY university_id LIMIT 1")
    uni1 = cursor.fetchone()
    if uni1:
        uni1 = uni1[0]
        for code, name, year, sem in [
            ('CS601', 'Database Management Systems', 2025, 'fall'),
            ('CS602', 'Design and Analysis of Algorithms', 2025, 'fall'),
            ('CS603', 'Machine Learning', 2025, 'spring'),
        ]:
            try:
                cursor.execute('INSERT INTO courses (course_code, course_name, university_id, year, semester) VALUES (%s,%s,%s,%s,%s)',
                               (code, name, uni1, year, sem))
                cid = cursor.lastrowid
                if book_ids and len(book_ids) > 2:
                    bid = book_ids[0] if code == 'CS602' else (book_ids[2] if code == 'CS601' else book_ids[6])
                    try:
                        cursor.execute('INSERT INTO course_books (course_id, book_id, requirement_type) VALUES (%s,%s,%s)',
                                       (cid, bid, 'required'))
                    except Exception:
                        pass
            except Exception:
                pass
    conn.commit()
    cursor.close()
    conn.close()
    print("Seed data inserted successfully!")

if __name__ == '__main__':
    seed()
