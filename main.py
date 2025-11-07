import eel
from database import Database

eel.init('web')

db = Database()

@eel.expose
def add_transaction(title, amount, type_, category, transaction_date, notes=""):
    """Fungsi untuk menambahkan transaksi baru"""
    return db.add_transaction(title, amount, type_, category, transaction_date, notes)

@eel.expose
def get_all_transactions():
    """Fungsi untuk mengambil semua transaksi"""
    return db.get_all_transactions()

@eel.expose
def delete_transaction(transaction_id):
    """Fungsi untuk menghapus transaksi"""
    return db.delete_transaction(transaction_id)

@eel.expose
def get_financial_summary():
    """Fungsi untuk mendapatkan ringkasan keuangan"""
    return db.get_financial_summary()

eel.start('index.html', size=(1000, 700), port=3006)