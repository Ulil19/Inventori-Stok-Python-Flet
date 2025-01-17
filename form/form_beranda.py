from flet import *
import mysql.connector

# Koneksi ke database MySQL
koneksi_db = mysql.connector.connect(
    host="localhost", user="root", password="", database="uas_mad"
)
cursor = koneksi_db.cursor()


def renew_koneksi_db():
    try:
        global koneksi_db, cursor
        if "koneksi_db" in globals() and koneksi_db.is_connected():
            cursor.close()
            koneksi_db.close()
            print("Koneksi database lama ditutup.")

        koneksi_db = mysql.connector.connect(
            host="localhost", user="root", password="", database="uas_mad"
        )
        cursor = koneksi_db.cursor(dictionary=True)
        print("Koneksi database berhasil diperbarui!")
    except mysql.connector.Error as err:
        print(f"Terjadi kesalahan koneksi database: {err}")


# Fungsi untuk mendapatkan jumlah data dari tabel seragam
def hitung_seragam():
    cursor.execute("SELECT COUNT(*) FROM seragam")
    result = cursor.fetchone()
    return result[0]


# Fungsi untuk mendapatkan jumlah data dari tabel pemasok
def hitung_pemasok():
    cursor.execute("SELECT COUNT(*) FROM pemasok")
    result = cursor.fetchone()
    return result[0]


# Fungsi untuk mendapatkan jumlah data dari tabel seragam_masuk
def hitung_seragam_masuk():
    cursor.execute("SELECT COUNT(*) FROM seragam_masuk")
    result = cursor.fetchone()
    return result[0]


# Halaman Beranda
def form_beranda(page: Page):
    # Mengambil jumlah data dari tabel seragam
    seragam_count = hitung_seragam()

    # Mengambil jumlah data dari tabel pemasok
    pemasok_count = hitung_pemasok()

    # Mengambil jumlah data dari tabel seragam_masuk
    seragam_masuk_count = hitung_seragam_masuk()

    return Container(
        content=Column(
            [
                Row(
                    [
                        Icon(name=icons.HOME_ROUNDED, size=50, color=colors.BLUE_400),
                        Text("Beranda", size=30, weight="bold"),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                ),
                Row(
                    [
                        Card(
                            content=Container(
                                content=Column(
                                    [
                                        Icon(
                                            name=icons.INFO_ROUNDED,
                                            size=30,
                                            color=colors.GREY_900,
                                        ),
                                        Text(
                                            f"{seragam_count} seragam",
                                            size=35,
                                            weight="bold",
                                        ),
                                        Text("Seragam", size=12),
                                    ]
                                ),
                                padding=10,
                                bgcolor=colors.RED_100,
                                width=250,
                                height=150,
                                border_radius=15,
                                border=border.all(color=colors.GREY_900, width=0.5),
                            ),
                            elevation=3,
                        ),
                        Card(
                            content=Container(
                                content=Column(
                                    [
                                        Icon(
                                            name=icons.INFO_ROUNDED,
                                            size=30,
                                            color=colors.GREY_900,
                                        ),
                                        Text(
                                            f"{pemasok_count} pemasok",
                                            size=35,
                                            weight="bold",
                                        ),
                                        Text("Pemasok", size=12),
                                    ]
                                ),
                                padding=10,
                                bgcolor=colors.GREEN_100,
                                width=250,
                                height=150,
                                border_radius=15,
                                border=border.all(color=colors.GREY_900, width=0.5),
                            ),
                            elevation=3,
                        ),
                        Card(
                            content=Container(
                                content=Column(
                                    [
                                        Icon(
                                            name=icons.INFO_ROUNDED,
                                            size=30,
                                            color=colors.GREY_900,
                                        ),
                                        Text(
                                            f"{seragam_masuk_count} masuk",
                                            size=35,
                                            weight="bold",
                                        ),
                                        Text("Seragam Masuk", size=12),
                                    ]
                                ),
                                padding=10,
                                bgcolor=colors.BLUE_100,
                                width=250,
                                height=150,
                                border_radius=15,
                                border=border.all(color=colors.GREY_900, width=0.5),
                            ),
                            elevation=3,
                        ),
                    ],
                    alignment=MainAxisAlignment.START,
                ),
                Row([], alignment=MainAxisAlignment.CENTER),  # Baris ketiga
                Row(
                    [
                        Icon(name=icons.COPYRIGHT_ROUNDED, size=14),
                        Text("Mobile Application Development", size=14, weight="bold"),
                        Text(" - ", size=14, weight="bold"),
                        Text("Ulil Fathon", size=14),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                ),
            ]
        ),
        margin=10,
    )
