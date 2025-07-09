# database_helper.py

import sqlite3
import datetime

# Veritabanını ve tabloyu oluşturan fonksiyon
def init_db():
    conn = sqlite3.connect('veritabani.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uyarilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            moderator_id INTEGER NOT NULL,
            sebep TEXT NOT NULL,
            zaman_damgasi TIMESTAMP NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("Veritabanı başarıyla başlatıldı ve 'uyarilar' tablosu hazır.")

# Veritabanına yeni bir uyarı ekleyen fonksiyon
def add_warning(user_id: int, moderator_id: int, reason: str):
    conn = sqlite3.connect('veritabani.db')
    cursor = conn.cursor()
    # SQL INSERT komutu ile verileri tabloya ekliyoruz.
    # Güvenlik için verileri bu şekilde '?' ile eklemek en doğrusudur (SQL Injection önlemi).
    cursor.execute(
        "INSERT INTO uyarilar (user_id, moderator_id, sebep, zaman_damgasi) VALUES (?, ?, ?, ?)",
        (user_id, moderator_id, reason, datetime.datetime.now())
    )
    conn.commit()
    conn.close()

# Belirli bir kullanıcının tüm uyarılarını çeken fonksiyon
def get_warnings(user_id: int):
    conn = sqlite3.connect('veritabani.db')
    cursor = conn.cursor()
    # SQL SELECT komutu ile belirli bir kullanıcıya ait tüm uyarıları çekiyoruz.
    cursor.execute("SELECT moderator_id, sebep, zaman_damgasi FROM uyarilar WHERE user_id = ?", (user_id,))
    # fetchall() ile tüm sonuçları bir liste olarak alıyoruz.
    warnings = cursor.fetchall()
    conn.close()
    return warnings