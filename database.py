import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        self.host = 'localhost'
        self.user = 'root'
        self.password = ''  # Sesuaikan dengan password MySQL Anda
        self.database = 'db_money_track'
        self.connection = None
        self.connect()
        if self.connection and self.connection.is_connected():
            self.create_tables()

    def connect(self):
        """Membuat koneksi ke database MySQL"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                auth_plugin='mysql_native_password'
            )
            if self.connection.is_connected():
                print("✅ Berhasil terhubung ke MySQL database")
                return True
        except Error as e:
            print(f"❌ Error connecting to database: {e}")
            return self.create_database()
        return False

    def create_database(self):
        """Membuat database jika belum ada"""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                auth_plugin='mysql_native_password'
            )
            
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                print("✅ Database created successfully")
                
                cursor.execute(f"USE {self.database}")
                self.create_tables_with_connection(connection)
                
                cursor.close()
                connection.close()
                
                # Reconnect to the new database
                return self.connect_to_existing_database()
                
        except Error as e:
            print(f"❌ Error creating database: {e}")
            return False

    def connect_to_existing_database(self):
        """Connect ke database yang sudah ada"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                auth_plugin='mysql_native_password'
            )
            return self.connection.is_connected()
        except Error as e:
            print(f"❌ Error connecting to existing database: {e}")
            return False

    def create_tables_with_connection(self, connection):
        """Membuat tabel dengan koneksi yang diberikan"""
        try:
            cursor = connection.cursor()
            
            create_transactions_table = """
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                amount DECIMAL(15, 2) NOT NULL,
                type ENUM('income', 'expense') NOT NULL,
                category VARCHAR(100) NOT NULL,
                transaction_date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_transactions_table)
            connection.commit()
            print("✅ Tables created successfully")
            cursor.close()
        except Error as e:
            print(f"❌ Error creating tables: {e}")

    def create_tables(self):
        """Membuat tabel jika belum ada"""
        if not self.connection or not self.connection.is_connected():
            print("❌ No database connection available")
            return
            
        try:
            cursor = self.connection.cursor()
            
            create_transactions_table = """
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                amount DECIMAL(15, 2) NOT NULL,
                type ENUM('income', 'expense') NOT NULL,
                category VARCHAR(100) NOT NULL,
                transaction_date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_transactions_table)
            self.connection.commit()
            print("✅ Tables created successfully")
            cursor.close()
        except Error as e:
            print(f"❌ Error creating tables: {e}")

    # QUERY 1: Menambahkan transaksi baru
    def add_transaction(self, title, amount, type_, category, transaction_date, notes=""):
        """Menambahkan transaksi baru ke database"""
        if not self.connection or not self.connection.is_connected():
            return {"status": "error", "message": "Database connection not available"}
            
        try:
            cursor = self.connection.cursor()
            insert_query = """
            INSERT INTO transactions (title, amount, type, category, transaction_date, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (title, amount, type_, category, transaction_date, notes))
            self.connection.commit()
            cursor.close()
            return {"status": "success", "message": "Transaksi berhasil ditambahkan"}
        except Error as e:
            return {"status": "error", "message": f"Gagal menambahkan transaksi: {e}"}

    # QUERY 2: Mengambil semua transaksi
    def get_all_transactions(self):
        """Mengambil semua transaksi dari database"""
        if not self.connection or not self.connection.is_connected():
            return {"status": "error", "message": "Database connection not available", "data": []}
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            select_query = """
            SELECT * FROM transactions 
            ORDER BY transaction_date DESC, created_at DESC
            """
            cursor.execute(select_query)
            transactions = cursor.fetchall()
            
            # Convert decimal to float for JSON serialization
            for transaction in transactions:
                transaction['amount'] = float(transaction['amount'])
                transaction['transaction_date'] = transaction['transaction_date'].isoformat()
                transaction['created_at'] = transaction['created_at'].isoformat()
            
            cursor.close()
            return {"status": "success", "data": transactions}
        except Error as e:
            return {"status": "error", "message": f"Gagal mengambil data: {e}", "data": []}

    def delete_transaction(self, transaction_id):
        """Menghapus transaksi"""
        if not self.connection or not self.connection.is_connected():
            return {"status": "error", "message": "Database connection not available"}
            
        try:
            cursor = self.connection.cursor()
            delete_query = "DELETE FROM transactions WHERE id = %s"
            cursor.execute(delete_query, (transaction_id,))
            self.connection.commit()
            cursor.close()
            return {"status": "success", "message": "Transaksi berhasil dihapus"}
        except Error as e:
            return {"status": "error", "message": f"Gagal menghapus transaksi: {e}"}

    def get_financial_summary(self):
        """Mendapatkan ringkasan keuangan sederhana"""
        if not self.connection or not self.connection.is_connected():
            return {"status": "error", "message": "Database connection not available"}
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Total income
            cursor.execute("SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE type = 'income'")
            total_income = float(cursor.fetchone()['total'])
            
            # Total expense
            cursor.execute("SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE type = 'expense'")
            total_expense = float(cursor.fetchone()['total'])
            
            # Balance
            balance = total_income - total_expense
            
            cursor.close()
            
            return {
                "status": "success", 
                "data": {
                    "total_income": total_income,
                    "total_expense": total_expense,
                    "balance": balance
                }
            }
        except Error as e:
            return {"status": "error", "message": f"Gagal mengambil ringkasan: {e}"}

    def close_connection(self):
        """Menutup koneksi database"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ Koneksi database ditutup")