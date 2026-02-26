import sqlite3

def init_db():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY, status TEXT)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pending_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            action TEXT,
            status TEXT DEFAULT 'pending',
            notified INTEGER DEFAULT 0
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO orders VALUES ('ABC', 'Pending')")
    cursor.execute("INSERT OR IGNORE INTO orders VALUES ('FHE', 'Cancelled')")
    cursor.execute("INSERT OR IGNORE INTO orders VALUES ('XYZ', 'Delivered')")
    conn.commit()
    conn.close()

def get_order_full_context(order_id):
    if not order_id: return None, None
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id.upper(),))
    order_res = cursor.fetchone()
    order_status = order_res[0] if order_res else None
    
    cursor.execute("SELECT status FROM pending_actions WHERE order_id = ? ORDER BY id DESC LIMIT 1", (order_id.upper(),))
    req_res = cursor.fetchone()
    request_status = req_res[0] if req_res else None
    
    conn.close()
    return order_status, request_status
def get_all_products():
    conn = sqlite3.connect("orders.db")
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM orders")
    rows = cursor.fetchall()
    
    products = [dict(row) for row in rows]
    
    conn.close()
    return products

def create_request(order_id, action):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pending_actions (order_id, action) VALUES (?, ?)", (order_id.upper(), action))
    conn.commit()
    conn.close()

def get_pending_requests():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, order_id, action FROM pending_actions WHERE status = 'pending'")
    rows = cursor.fetchall()
    conn.close()
    return rows

def approve_request(request_id):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT order_id FROM pending_actions WHERE id = ?", (request_id,))
    res = cursor.fetchone()
    if res:
        order_id = res[0]
        cursor.execute("UPDATE orders SET status = 'Cancelled' WHERE id = ?", (order_id,))
        cursor.execute("UPDATE pending_actions SET status = 'approved' WHERE id = ?", (request_id,))
    conn.commit()
    conn.close()

def update_status(request_id):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT order_id FROM pending_actions WHERE id = ?", (request_id,))
    res = cursor.fetchone()
    if res:
        order_id = res[0]
        cursor.execute("UPDATE orders SET status = 'Pending' WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()

def get_new_notifications():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, order_id, status FROM pending_actions WHERE status IN ('approved', 'refused') AND notified = 0")
    rows = cursor.fetchall()
    for row in rows:
        cursor.execute("UPDATE pending_actions SET notified = 1 WHERE id = ?", (row[0],))
    conn.commit()
    conn.close()
    return rows

def refuse_request(request_id):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE pending_actions SET status = 'refused' WHERE id = ?", (request_id,))
    conn.commit()
    conn.close()