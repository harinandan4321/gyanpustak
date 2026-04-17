import os
import mysql.connector
from mysql.connector import Error
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')

DB_CONFIG = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'unix_socket': os.getenv('MYSQL_SOCKET'),
}

def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def query_db(query, args=(), one=False, commit=False):
    conn = get_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, args)
        if commit:
            conn.commit()
            result = cursor.lastrowid
        else:
            result = cursor.fetchone() if one else cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Error as e:
        print(f"Query error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return None

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                flash('Access denied.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.context_processor
def inject_user():
    return dict(
        current_user=session,
        cart_count=get_cart_count()
    )

def get_cart_count():
    if session.get('role') == 'student' and 'student_id' in session:
        row = query_db('SELECT COUNT(*) as cnt FROM cart_items ci JOIN carts c ON ci.cart_id=c.cart_id WHERE c.student_id=%s', (session['student_id'],), one=True)
        return row['cnt'] if row else 0
    return 0

@app.route('/')
def index():
    featured_books = query_db('SELECT b.*, GROUP_CONCAT(ba.author_name SEPARATOR ", ") as authors FROM books b LEFT JOIN book_authors ba ON b.book_id=ba.book_id GROUP BY b.book_id ORDER BY b.avg_rating DESC LIMIT 8') or []
    categories = query_db('SELECT * FROM categories WHERE parent_id IS NULL') or []
    stats = query_db('SELECT COUNT(*) as total_books FROM books', one=True)
    return render_template('shared/index.html', featured_books=featured_books, categories=categories, stats=stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = query_db('SELECT * FROM users WHERE email=%s', (email,), one=True)
        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['user_id']
            session['email'] = user['email']
            session['first_name'] = user['first_name']
            session['last_name'] = user['last_name']
            session['role'] = user['role']
            if user['role'] == 'student':
                st = query_db('SELECT * FROM students WHERE user_id=%s', (user['user_id'],), one=True)
                if st:
                    session['student_id'] = st['student_id']
            flash(f'Welcome back, {user["first_name"]}!', 'success')
            role = user['role']
            if role == 'student':
                return redirect(url_for('student_dashboard'))
            elif role in ('admin', 'superadmin'):
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('support_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    universities = query_db('SELECT * FROM universities') or []
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        university = request.form.get('university', '')
        major = request.form.get('major', '')
        student_status = request.form.get('student_status', 'undergraduate')
        year_of_study = request.form.get('year_of_study', 1)
        dob = request.form.get('date_of_birth', None)
        existing = query_db('SELECT user_id FROM users WHERE email=%s', (email,), one=True)
        if existing:
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html', universities=universities)
        pw_hash = generate_password_hash(password)
        conn = get_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('INSERT INTO users (email, password_hash, role, first_name, last_name, phone, address) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                           (email, pw_hash, 'student', first_name, last_name, phone, address))
            user_id = cursor.lastrowid
            dob_val = dob if dob else None
            cursor.execute('INSERT INTO students (user_id, date_of_birth, university, major, student_status, year_of_study) VALUES (%s,%s,%s,%s,%s,%s)',
                           (user_id, dob_val, university, major, student_status, year_of_study))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Database error. Try again.', 'danger')
    return render_template('auth/register.html', universities=universities)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

# ============== BOOKS ==============

@app.route('/books')
def books():
    search = request.args.get('q', '')
    category_id = request.args.get('category', '')
    book_type = request.args.get('type', '')
    purchase_option = request.args.get('option', '')
    page = int(request.args.get('page', 1))
    per_page = 12
    offset = (page - 1) * per_page
    where_clauses = ['1=1']
    params = []
    if search:
        where_clauses.append('(b.title LIKE %s OR ba.author_name LIKE %s OR bk.keyword LIKE %s)')
        params += [f'%{search}%', f'%{search}%', f'%{search}%']
    if category_id:
        where_clauses.append('b.category_id=%s')
        params.append(category_id)
    if book_type:
        where_clauses.append('b.book_type=%s')
        params.append(book_type)
    if purchase_option:
        where_clauses.append('(b.purchase_option=%s OR b.purchase_option="both")')
        params.append(purchase_option)
    where_str = ' AND '.join(where_clauses)
    books_list = query_db(f'''
        SELECT DISTINCT b.*, GROUP_CONCAT(DISTINCT ba.author_name SEPARATOR ", ") as authors,
               c.name as category_name
        FROM books b
        LEFT JOIN book_authors ba ON b.book_id=ba.book_id
        LEFT JOIN book_keywords bk ON b.book_id=bk.book_id
        LEFT JOIN categories c ON b.category_id=c.category_id
        WHERE {where_str}
        GROUP BY b.book_id
        ORDER BY b.title
        LIMIT %s OFFSET %s
    ''', params + [per_page, offset]) or []
    count_row = query_db(f'''
        SELECT COUNT(DISTINCT b.book_id) as cnt
        FROM books b
        LEFT JOIN book_authors ba ON b.book_id=ba.book_id
        LEFT JOIN book_keywords bk ON b.book_id=bk.book_id
        WHERE {where_str}
    ''', params, one=True)
    total = count_row['cnt'] if count_row else 0
    total_pages = (total + per_page - 1) // per_page
    categories = query_db('SELECT * FROM categories WHERE parent_id IS NULL') or []
    return render_template('shared/books.html', books=books_list, categories=categories,
                           search=search, category_id=category_id, page=page, total_pages=total_pages)

@app.route('/books/<int:book_id>')
def book_detail(book_id):
    book = query_db('''
        SELECT b.*, GROUP_CONCAT(DISTINCT ba.author_name SEPARATOR ", ") as authors,
               c.name as category_name
        FROM books b
        LEFT JOIN book_authors ba ON b.book_id=ba.book_id
        LEFT JOIN categories c ON b.category_id=c.category_id
        WHERE b.book_id=%s
        GROUP BY b.book_id
    ''', (book_id,), one=True)
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('books'))
    keywords = query_db('SELECT keyword FROM book_keywords WHERE book_id=%s', (book_id,)) or []
    reviews = query_db('''
        SELECT r.*, u.first_name, u.last_name
        FROM reviews r
        JOIN students s ON r.student_id=s.student_id
        JOIN users u ON s.user_id=u.user_id
        WHERE r.book_id=%s
        ORDER BY r.created_at DESC
    ''', (book_id,)) or []
    related_books = query_db('''
        SELECT b.*, GROUP_CONCAT(ba.author_name SEPARATOR ", ") as authors
        FROM books b
        LEFT JOIN book_authors ba ON b.book_id=ba.book_id
        WHERE b.category_id=%s AND b.book_id != %s
        GROUP BY b.book_id LIMIT 4
    ''', (book['category_id'], book_id)) or []
    return render_template('shared/book_detail.html', book=book, keywords=keywords,
                           reviews=reviews, related_books=related_books)

# ============== CART ==============

@app.route('/cart')
@login_required
def cart():
    if session.get('role') != 'student':
        return redirect(url_for('index'))
    student_id = session.get('student_id')
    cart = query_db('SELECT * FROM carts WHERE student_id=%s', (student_id,), one=True)
    if not cart:
        query_db('INSERT INTO carts (student_id) VALUES (%s)', (student_id,), commit=True)
        cart = query_db('SELECT * FROM carts WHERE student_id=%s', (student_id,), one=True)
    items = query_db('''
        SELECT ci.*, b.title, b.price, b.rent_price, b.cover_image,
               GROUP_CONCAT(ba.author_name SEPARATOR ", ") as authors
        FROM cart_items ci
        JOIN books b ON ci.book_id=b.book_id
        LEFT JOIN book_authors ba ON b.book_id=ba.book_id
        WHERE ci.cart_id=%s
        GROUP BY ci.book_id, ci.cart_id
    ''', (cart['cart_id'],)) or []
    total = sum((item['rent_price'] if item['purchase_option']=='rent' and item['rent_price'] else item['price']) * item['quantity'] for item in items)
    return render_template('student/cart.html', cart=cart, items=items, total=total)

@app.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    if session.get('role') != 'student':
        flash('Only students can add to cart.', 'danger')
        return redirect(url_for('books'))
    student_id = session.get('student_id')
    book_id = request.form.get('book_id')
    purchase_option = request.form.get('purchase_option', 'buy')
    quantity = int(request.form.get('quantity', 1))
    cart = query_db('SELECT * FROM carts WHERE student_id=%s', (student_id,), one=True)
    if not cart:
        query_db('INSERT INTO carts (student_id) VALUES (%s)', (student_id,), commit=True)
        cart = query_db('SELECT * FROM carts WHERE student_id=%s', (student_id,), one=True)
    existing = query_db('SELECT * FROM cart_items WHERE cart_id=%s AND book_id=%s', (cart['cart_id'], book_id), one=True)
    if existing:
        query_db('UPDATE cart_items SET quantity=quantity+%s WHERE cart_id=%s AND book_id=%s',
                 (quantity, cart['cart_id'], book_id), commit=True)
    else:
        query_db('INSERT INTO cart_items (cart_id, book_id, quantity, purchase_option) VALUES (%s,%s,%s,%s)',
                 (cart['cart_id'], book_id, quantity, purchase_option), commit=True)
    flash('Book added to cart!', 'success')
    return redirect(request.referrer or url_for('cart'))

@app.route('/cart/remove/<int:book_id>', methods=['POST'])
@login_required
def remove_from_cart(book_id):
    student_id = session.get('student_id')
    cart = query_db('SELECT * FROM carts WHERE student_id=%s', (student_id,), one=True)
    if cart:
        query_db('DELETE FROM cart_items WHERE cart_id=%s AND book_id=%s', (cart['cart_id'], book_id), commit=True)
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart'))

# ============== ORDERS ==============

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
@role_required('student')
def checkout():
    student_id = session.get('student_id')
    cart = query_db('SELECT * FROM carts WHERE student_id=%s', (student_id,), one=True)
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart'))
    items = query_db('''
        SELECT ci.*, b.title, b.price, b.rent_price, b.quantity as stock
        FROM cart_items ci
        JOIN books b ON ci.book_id=b.book_id
        WHERE ci.cart_id=%s
    ''', (cart['cart_id'],)) or []
    if not items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart'))
    total = sum((item['rent_price'] if item['purchase_option']=='rent' and item['rent_price'] else item['price']) * item['quantity'] for item in items)
    if request.method == 'POST':
        shipping = request.form.get('shipping_type', 'standard')
        cc_num = request.form.get('cc_number', '')
        cc_exp = request.form.get('cc_expiry', '')
        cc_holder = request.form.get('cc_holder', '')
        cc_type = request.form.get('cc_type', 'visa')
        conn = get_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('''INSERT INTO orders (student_id, shipping_type, credit_card_number, credit_card_expiry,
                              credit_card_holder, credit_card_type, total_amount) VALUES (%s,%s,%s,%s,%s,%s,%s)''',
                           (student_id, shipping, cc_num[-4:], cc_exp, cc_holder, cc_type, total))
            order_id = cursor.lastrowid
            for item in items:
                price = item['rent_price'] if item['purchase_option']=='rent' and item['rent_price'] else item['price']
                cursor.execute('INSERT INTO order_items (order_id, book_id, quantity, price_each, purchase_option) VALUES (%s,%s,%s,%s,%s)',
                               (order_id, item['book_id'], item['quantity'], price, item['purchase_option']))
                cursor.execute('UPDATE books SET quantity=quantity-%s WHERE book_id=%s', (item['quantity'], item['book_id']))
            cursor.execute('DELETE FROM cart_items WHERE cart_id=%s', (cart['cart_id'],))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Order placed successfully!', 'success')
            return redirect(url_for('order_detail', order_id=order_id))
    return render_template('student/checkout.html', items=items, total=total)

@app.route('/orders')
@login_required
@role_required('student')
def orders():
    student_id = session.get('student_id')
    orders_list = query_db('''
        SELECT o.*, COUNT(oi.book_id) as item_count
        FROM orders o
        LEFT JOIN order_items oi ON o.order_id=oi.order_id
        WHERE o.student_id=%s
        GROUP BY o.order_id
        ORDER BY o.date_created DESC
    ''', (student_id,)) or []
    return render_template('student/orders.html', orders=orders_list)

@app.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    order = query_db('SELECT * FROM orders WHERE order_id=%s', (order_id,), one=True)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('orders'))
    if session.get('role') == 'student' and order['student_id'] != session.get('student_id'):
        flash('Access denied.', 'danger')
        return redirect(url_for('orders'))
    items = query_db('''
        SELECT oi.*, b.title, b.cover_image,
               GROUP_CONCAT(ba.author_name SEPARATOR ", ") as authors
        FROM order_items oi
        JOIN books b ON oi.book_id=b.book_id
        LEFT JOIN book_authors ba ON b.book_id=ba.book_id
        WHERE oi.order_id=%s
        GROUP BY oi.book_id
    ''', (order_id,)) or []
    return render_template('student/order_detail.html', order=order, items=items)

@app.route('/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
@role_required('student')
def cancel_order(order_id):
    student_id = session.get('student_id')
    order = query_db('SELECT * FROM orders WHERE order_id=%s AND student_id=%s', (order_id, student_id), one=True)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('orders'))
    if order['order_status'] in ('new', 'processed'):
        query_db("UPDATE orders SET order_status='canceled' WHERE order_id=%s", (order_id,), commit=True)
        flash('Order canceled successfully.', 'info')
    else:
        flash('Cannot cancel this order at this stage.', 'warning')
    return redirect(url_for('order_detail', order_id=order_id))

# ============== REVIEWS ==============

@app.route('/books/<int:book_id>/review', methods=['POST'])
@login_required
@role_required('student')
def add_review(book_id):
    student_id = session.get('student_id')
    rating = int(request.form.get('rating', 3))
    review_text = request.form.get('review_text', '')
    existing = query_db('SELECT * FROM reviews WHERE book_id=%s AND student_id=%s', (book_id, student_id), one=True)
    if existing:
        query_db('UPDATE reviews SET rating=%s, review_text=%s WHERE book_id=%s AND student_id=%s',
                 (rating, review_text, book_id, student_id), commit=True)
        flash('Review updated.', 'success')
    else:
        query_db('INSERT INTO reviews (book_id, student_id, rating, review_text) VALUES (%s,%s,%s,%s)',
                 (book_id, student_id, rating, review_text), commit=True)
        flash('Review submitted.', 'success')
    query_db('UPDATE books SET avg_rating=(SELECT AVG(rating) FROM reviews WHERE book_id=%s) WHERE book_id=%s',
             (book_id, book_id), commit=True)
    return redirect(url_for('book_detail', book_id=book_id))

# ============== STUDENT DASHBOARD ==============

@app.route('/student/dashboard')
@login_required
@role_required('student')
def student_dashboard():
    student_id = session.get('student_id')
    recent_orders = query_db('SELECT * FROM orders WHERE student_id=%s ORDER BY date_created DESC LIMIT 5', (student_id,)) or []
    recent_tickets = query_db('SELECT * FROM trouble_tickets WHERE created_by_user_id=%s ORDER BY date_logged DESC LIMIT 5', (session['user_id'],)) or []
    return render_template('student/dashboard.html', recent_orders=recent_orders, recent_tickets=recent_tickets)

@app.route('/student/profile', methods=['GET', 'POST'])
@login_required
@role_required('student')
def student_profile():
    user_id = session['user_id']
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        query_db('UPDATE users SET first_name=%s, last_name=%s, phone=%s, address=%s WHERE user_id=%s',
                 (first_name, last_name, phone, address, user_id), commit=True)
        session['first_name'] = first_name
        session['last_name'] = last_name
        flash('Profile updated.', 'success')
    user = query_db('SELECT u.*, s.* FROM users u JOIN students s ON u.user_id=s.user_id WHERE u.user_id=%s', (user_id,), one=True)
    return render_template('student/profile.html', user=user)

# ============== TROUBLE TICKETS ==============

@app.route('/tickets')
@login_required
def tickets():
    role = session.get('role')
    if role == 'student':
        tickets_list = query_db('SELECT * FROM trouble_tickets WHERE created_by_user_id=%s ORDER BY date_logged DESC', (session['user_id'],)) or []
    elif role in ('support',):
        tickets_list = query_db('SELECT t.*, u.first_name, u.last_name FROM trouble_tickets t JOIN users u ON t.created_by_user_id=u.user_id ORDER BY t.date_logged DESC') or []
    else:
        tickets_list = query_db('''SELECT t.*, u.first_name, u.last_name 
            FROM trouble_tickets t JOIN users u ON t.created_by_user_id=u.user_id 
            WHERE t.status IN ("assigned","in-process","completed")
            ORDER BY t.date_logged DESC''') or []
    return render_template('shared/tickets.html', tickets=tickets_list, role=role)

@app.route('/tickets/new', methods=['GET', 'POST'])
@login_required
def create_ticket():
    role = session.get('role')
    if role == 'admin':
        flash('Admins cannot create tickets.', 'danger')
        return redirect(url_for('tickets'))
    if request.method == 'POST':
        title = request.form['title']
        problem = request.form['problem_description']
        category = request.form.get('category', 'other')
        query_db('INSERT INTO trouble_tickets (title, problem_description, category, created_by_user_id) VALUES (%s,%s,%s,%s)',
                 (title, problem, category, session['user_id']), commit=True)
        flash('Ticket submitted successfully.', 'success')
        return redirect(url_for('tickets'))
    return render_template('shared/create_ticket.html')

@app.route('/tickets/<int:ticket_id>')
@login_required
def ticket_detail(ticket_id):
    ticket = query_db('SELECT t.*, u.first_name, u.last_name FROM trouble_tickets t JOIN users u ON t.created_by_user_id=u.user_id WHERE t.ticket_id=%s', (ticket_id,), one=True)
    if not ticket:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('tickets'))
    history = query_db('SELECT h.*, u.first_name, u.last_name FROM ticket_history h JOIN users u ON h.changed_by_user_id=u.user_id WHERE h.ticket_id=%s ORDER BY h.changed_at', (ticket_id,)) or []
    return render_template('shared/ticket_detail.html', ticket=ticket, history=history)

@app.route('/tickets/<int:ticket_id>/update', methods=['POST'])
@login_required
def update_ticket(ticket_id):
    ticket = query_db('SELECT * FROM trouble_tickets WHERE ticket_id=%s', (ticket_id,), one=True)
    if not ticket:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('tickets'))
    role = session.get('role')
    old_status = ticket['status']
    new_status = request.form.get('status', old_status)
    note = request.form.get('note', '')
    solution = request.form.get('solution_description', '')
    if role == 'support':
        if old_status != 'new':
            flash('Customer support can only modify new tickets.', 'danger')
            return redirect(url_for('ticket_detail', ticket_id=ticket_id))
        if new_status == 'assigned':
            query_db('UPDATE trouble_tickets SET status=%s WHERE ticket_id=%s', (new_status, ticket_id), commit=True)
    elif role in ('admin', 'superadmin'):
        if old_status == 'new':
            flash('Admins cannot edit new tickets.', 'danger')
            return redirect(url_for('ticket_detail', ticket_id=ticket_id))
        query_db('UPDATE trouble_tickets SET status=%s, solution_description=%s, assigned_admin_id=%s WHERE ticket_id=%s',
                 (new_status, solution, session['user_id'], ticket_id), commit=True)
        if new_status == 'completed':
            query_db('UPDATE trouble_tickets SET completion_date=NOW() WHERE ticket_id=%s', (ticket_id,), commit=True)
    query_db('INSERT INTO ticket_history (ticket_id, changed_by_user_id, old_status, new_status, note) VALUES (%s,%s,%s,%s,%s)',
             (ticket_id, session['user_id'], old_status, new_status, note), commit=True)
    flash('Ticket updated.', 'success')
    return redirect(url_for('ticket_detail', ticket_id=ticket_id))

# ============== ADMIN ==============

@app.route('/admin/dashboard')
@login_required
@role_required('admin', 'superadmin')
def admin_dashboard():
    total_books = query_db('SELECT COUNT(*) as cnt FROM books', one=True)
    total_orders = query_db('SELECT COUNT(*) as cnt FROM orders', one=True)
    total_students = query_db('SELECT COUNT(*) as cnt FROM students', one=True)
    pending_tickets = query_db('SELECT COUNT(*) as cnt FROM trouble_tickets WHERE status IN ("assigned","in-process")', one=True)
    recent_orders = query_db('SELECT o.*, u.first_name, u.last_name FROM orders o JOIN students s ON o.student_id=s.student_id JOIN users u ON s.user_id=u.user_id ORDER BY o.date_created DESC LIMIT 5') or []
    return render_template('admin/dashboard.html',
                           total_books=total_books, total_orders=total_orders,
                           total_students=total_students, pending_tickets=pending_tickets,
                           recent_orders=recent_orders)

@app.route('/admin/books')
@login_required
@role_required('admin', 'superadmin')
def admin_books():
    books_list = query_db('''
        SELECT b.*, c.name as category_name, GROUP_CONCAT(ba.author_name SEPARATOR ", ") as authors
        FROM books b
        LEFT JOIN categories c ON b.category_id=c.category_id
        LEFT JOIN book_authors ba ON b.book_id=ba.book_id
        GROUP BY b.book_id ORDER BY b.book_id DESC
    ''') or []
    categories = query_db('SELECT * FROM categories') or []
    return render_template('admin/books.html', books=books_list, categories=categories)

@app.route('/admin/books/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'superadmin')
def admin_add_book():
    categories = query_db('SELECT * FROM categories') or []
    if request.method == 'POST':
        title = request.form['title']
        isbn = request.form.get('isbn', '')
        publisher = request.form.get('publisher', '')
        pub_date = request.form.get('publication_date', None)
        edition = request.form.get('edition', 1)
        language = request.form.get('language', 'English')
        fmt = request.form.get('format', 'hardcover')
        book_type = request.form.get('book_type', 'new')
        purchase_option = request.form.get('purchase_option', 'both')
        price = float(request.form.get('price', 0))
        rent_price = request.form.get('rent_price', None)
        quantity = int(request.form.get('quantity', 0))
        category_id = request.form.get('category_id', None)
        description = request.form.get('description', '')
        authors = request.form.get('authors', '')
        keywords = request.form.get('keywords', '')
        conn = get_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO books (title, isbn, publisher, publication_date, edition, language, format, book_type, 
                              purchase_option, price, rent_price, quantity, category_id, description) VALUES 
                              (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                           (title, isbn or None, publisher, pub_date or None, edition, language, fmt,
                            book_type, purchase_option, price, rent_price or None, quantity, category_id or None, description))
            book_id = cursor.lastrowid
            for author in [a.strip() for a in authors.split(',') if a.strip()]:
                cursor.execute('INSERT INTO book_authors (book_id, author_name) VALUES (%s,%s)', (book_id, author))
            for kw in [k.strip() for k in keywords.split(',') if k.strip()]:
                cursor.execute('INSERT INTO book_keywords (book_id, keyword) VALUES (%s,%s)', (book_id, kw))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Book added successfully.', 'success')
            return redirect(url_for('admin_books'))
    return render_template('admin/add_book.html', categories=categories)

@app.route('/admin/books/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'superadmin')
def admin_edit_book(book_id):
    book = query_db('SELECT * FROM books WHERE book_id=%s', (book_id,), one=True)
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('admin_books'))
    categories = query_db('SELECT * FROM categories') or []
    authors = query_db('SELECT author_name FROM book_authors WHERE book_id=%s', (book_id,)) or []
    keywords = query_db('SELECT keyword FROM book_keywords WHERE book_id=%s', (book_id,)) or []
    if request.method == 'POST':
        title = request.form['title']
        price = float(request.form.get('price', 0))
        rent_price = request.form.get('rent_price', None)
        quantity = int(request.form.get('quantity', 0))
        book_type = request.form.get('book_type', 'new')
        purchase_option = request.form.get('purchase_option', 'both')
        fmt = request.form.get('format', 'hardcover')
        category_id = request.form.get('category_id', None)
        description = request.form.get('description', '')
        new_authors = request.form.get('authors', '')
        new_keywords = request.form.get('keywords', '')
        conn = get_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''UPDATE books SET title=%s, price=%s, rent_price=%s, quantity=%s, book_type=%s,
                              purchase_option=%s, format=%s, category_id=%s, description=%s WHERE book_id=%s''',
                           (title, price, rent_price or None, quantity, book_type, purchase_option, fmt, category_id or None, description, book_id))
            cursor.execute('DELETE FROM book_authors WHERE book_id=%s', (book_id,))
            for author in [a.strip() for a in new_authors.split(',') if a.strip()]:
                cursor.execute('INSERT INTO book_authors (book_id, author_name) VALUES (%s,%s)', (book_id, author))
            cursor.execute('DELETE FROM book_keywords WHERE book_id=%s', (book_id,))
            for kw in [k.strip() for k in new_keywords.split(',') if k.strip()]:
                cursor.execute('INSERT INTO book_keywords (book_id, keyword) VALUES (%s,%s)', (book_id, kw))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Book updated.', 'success')
            return redirect(url_for('admin_books'))
    author_str = ', '.join(a['author_name'] for a in authors)
    kw_str = ', '.join(k['keyword'] for k in keywords)
    return render_template('admin/edit_book.html', book=book, categories=categories,
                           author_str=author_str, kw_str=kw_str)

@app.route('/admin/books/<int:book_id>/delete', methods=['POST'])
@login_required
@role_required('admin', 'superadmin')
def admin_delete_book(book_id):
    query_db('DELETE FROM books WHERE book_id=%s', (book_id,), commit=True)
    flash('Book deleted.', 'info')
    return redirect(url_for('admin_books'))

@app.route('/admin/users')
@login_required
@role_required('superadmin')
def admin_users():
    users = query_db('SELECT * FROM users ORDER BY role, created_at DESC') or []
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
@role_required('superadmin')
def admin_add_user():
    if request.method == 'POST':
        role = request.form.get('role', 'support')
        if role not in ('support', 'admin'):
            flash('Invalid role.', 'danger')
            return redirect(url_for('admin_add_user'))
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        gender = request.form.get('gender', 'other')
        salary = request.form.get('salary', 0)
        aadhaar = request.form.get('aadhaar', '')
        employee_id = request.form.get('employee_id', '')
        pw_hash = generate_password_hash(password)
        conn = get_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (email, password_hash, role, first_name, last_name, phone, address) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                           (email, pw_hash, role, first_name, last_name, phone, address))
            user_id = cursor.lastrowid
            cursor.execute('INSERT INTO employees (employee_id, user_id, gender, salary, aadhaar) VALUES (%s,%s,%s,%s,%s)',
                           (employee_id, user_id, gender, salary or 0, aadhaar))
            conn.commit()
            cursor.close()
            conn.close()
            flash(f'{role.capitalize()} user added.', 'success')
            return redirect(url_for('admin_users'))
    return render_template('admin/add_user.html')

@app.route('/admin/orders')
@login_required
@role_required('admin', 'superadmin')
def admin_orders():
    orders_list = query_db('''
        SELECT o.*, u.first_name, u.last_name, COUNT(oi.book_id) as item_count
        FROM orders o
        JOIN students s ON o.student_id=s.student_id
        JOIN users u ON s.user_id=u.user_id
        LEFT JOIN order_items oi ON o.order_id=oi.order_id
        GROUP BY o.order_id
        ORDER BY o.date_created DESC
    ''') or []
    return render_template('admin/orders.html', orders=orders_list)

@app.route('/admin/orders/<int:order_id>/update', methods=['POST'])
@login_required
@role_required('admin', 'superadmin')
def admin_update_order(order_id):
    new_status = request.form.get('status')
    query_db('UPDATE orders SET order_status=%s WHERE order_id=%s', (new_status, order_id), commit=True)
    flash('Order status updated.', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/tickets')
@login_required
@role_required('admin', 'superadmin')
def admin_tickets():
    tickets_list = query_db('''
        SELECT t.*, u.first_name, u.last_name
        FROM trouble_tickets t JOIN users u ON t.created_by_user_id=u.user_id
        WHERE t.status IN ("assigned","in-process","completed")
        ORDER BY t.date_logged DESC
    ''') or []
    return render_template('admin/tickets.html', tickets=tickets_list)

@app.route('/admin/universities')
@login_required
@role_required('admin', 'superadmin')
def admin_universities():
    universities = query_db('SELECT * FROM universities ORDER BY name') or []
    return render_template('admin/universities.html', universities=universities)

@app.route('/admin/universities/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'superadmin')
def admin_add_university():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form.get('address', '')
        rep_first = request.form.get('rep_first_name', '')
        rep_last = request.form.get('rep_last_name', '')
        rep_email = request.form.get('rep_email', '')
        rep_phone = request.form.get('rep_phone', '')
        query_db('INSERT INTO universities (name, address, rep_first_name, rep_last_name, rep_email, rep_phone) VALUES (%s,%s,%s,%s,%s,%s)',
                 (name, address, rep_first, rep_last, rep_email, rep_phone), commit=True)
        flash('University added.', 'success')
        return redirect(url_for('admin_universities'))
    return render_template('admin/add_university.html')

@app.route('/admin/courses')
@login_required
@role_required('admin', 'superadmin')
def admin_courses():
    courses = query_db('''
        SELECT c.*, u.name as university_name
        FROM courses c JOIN universities u ON c.university_id=u.university_id
        ORDER BY c.course_name
    ''') or []
    return render_template('admin/courses.html', courses=courses)

@app.route('/admin/courses/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'superadmin')
def admin_add_course():
    universities = query_db('SELECT * FROM universities') or []
    books_list = query_db('SELECT b.book_id, b.title FROM books b') or []
    if request.method == 'POST':
        course_code = request.form['course_code']
        course_name = request.form['course_name']
        university_id = request.form['university_id']
        year = request.form.get('year', None)
        semester = request.form.get('semester', None)
        book_ids = request.form.getlist('book_ids')
        conn = get_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO courses (course_code, course_name, university_id, year, semester) VALUES (%s,%s,%s,%s,%s)',
                           (course_code, course_name, university_id, year or None, semester or None))
            course_id = cursor.lastrowid
            for bid in book_ids:
                req_type = request.form.get(f'req_type_{bid}', 'required')
                cursor.execute('INSERT INTO course_books (course_id, book_id, requirement_type) VALUES (%s,%s,%s)', (course_id, bid, req_type))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Course added.', 'success')
            return redirect(url_for('admin_courses'))
    return render_template('admin/add_course.html', universities=universities, books=books_list)

# ============== SUPPORT DASHBOARD ==============

@app.route('/support/dashboard')
@login_required
@role_required('support')
def support_dashboard():
    new_tickets = query_db('''
        SELECT t.*, u.first_name, u.last_name
        FROM trouble_tickets t JOIN users u ON t.created_by_user_id=u.user_id
        WHERE t.status="new"
        ORDER BY t.date_logged DESC
    ''') or []
    all_tickets = query_db('''
        SELECT t.*, u.first_name, u.last_name
        FROM trouble_tickets t JOIN users u ON t.created_by_user_id=u.user_id
        ORDER BY t.date_logged DESC LIMIT 20
    ''') or []
    return render_template('support/dashboard.html', new_tickets=new_tickets, all_tickets=all_tickets)

# ============== CATEGORIES ==============

@app.route('/admin/categories')
@login_required
@role_required('admin', 'superadmin')
def admin_categories():
    cats = query_db('''
        SELECT c.*, p.name as parent_name
        FROM categories c LEFT JOIN categories p ON c.parent_id=p.category_id
        ORDER BY COALESCE(c.parent_id, c.category_id), c.name
    ''') or []
    return render_template('admin/categories.html', categories=cats)

@app.route('/admin/categories/add', methods=['POST'])
@login_required
@role_required('admin', 'superadmin')
def admin_add_category():
    name = request.form['name']
    parent_id = request.form.get('parent_id', None)
    query_db('INSERT INTO categories (name, parent_id) VALUES (%s,%s)', (name, parent_id or None), commit=True)
    flash('Category added.', 'success')
    return redirect(url_for('admin_categories'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
