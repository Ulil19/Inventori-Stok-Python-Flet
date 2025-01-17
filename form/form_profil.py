from flet import *
from koneksi import create_connection
from session_manager import get_session
import mysql.connector

# Koneksi ke database
koneksi_db = create_connection()
if koneksi_db is None:
    print("Koneksi gagal")
else:
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


snack_bar_berhasil = SnackBar(Text("Operasi berhasil"), bgcolor="green")
snack_bar_gagal = SnackBar(Text("Operasi gagal"), bgcolor="red")


# Mengambil data profil pengguna berdasarkan username
def ambil_user_data(username):
    cursor.execute(
        "SELECT username, password FROM user WHERE username = %s", (username,)
    )
    data_akun_user = cursor.fetchone()
    return data_akun_user  # Mengembalikan tuple (username, password)


# Memperbarui data profil pengguna ke database
def update_user_data(username, password_baru):
    # Query untuk memperbarui data pengguna
    query = "UPDATE user SET password = %s WHERE username = %s"
    cursor.execute(query, (password_baru, username))
    koneksi_db.commit()  # Menyimpan perubahan ke database


# Formulir Profil dengan mengambil data dari database berdasarkan session username
def form_profil(page: Page):
    # Mendapatkan session pengguna
    user = get_session()  # Mendapatkan informasi session yang aktif
    username = user["username"]  # Mengambil username dari session

    # Mengambil data profil dari database
    user_data = ambil_user_data(username)

    if user_data:
        username_db, password_db = user_data
    else:
        username_db, password_db = "", ""  # Jika tidak ada data pengguna

    # Set nilai untuk inputan_password dengan data dari database
    inputan_username = TextField(label="Username", value=username_db, read_only=True)
    inputan_password = TextField(label="Password", value=password_db, password=True)

    # Fungsi untuk menangani penyimpanan profil
    def simpan_profil(e):
        # Mendapatkan nilai dari TextField
        password_baru = inputan_password.value

        # Memperbarui data pengguna di database
        update_user_data(username, password_baru)

        # Memberikan konfirmasi kepada pengguna
        print("Profil disimpan")
        snack_bar_berhasil

    return Container(  # Membungkus seluruh Column dalam sebuah Container
        content=Column(
            [
                # Judul dengan ikon pengguna
                Row(
                    [
                        Icon(name=icons.PERSON, size=50, color=colors.BLUE_400),
                        Text("Profil Pengguna", size=30, weight="bold"),
                    ]
                ),
                # Formulir untuk informasi profil pengguna
                Container(  # Membungkus seluruh Column dalam sebuah Container
                    content=Column(
                        [
                            # Memusatkan Ikon dengan Row
                            Row(
                                [
                                    Icon(
                                        name=icons.PERSON_PIN_CIRCLE_ROUNDED,
                                        size=125,
                                        color=colors.GREY_500,
                                    )
                                ],
                                width=350,
                                alignment=MainAxisAlignment.CENTER,
                            ),  # Memusatkan ikon dalam Row
                            Text("Username"),
                            inputan_username,
                            Text("Password"),
                            inputan_password,
                            ElevatedButton("Simpan Profil", on_click=simpan_profil),
                        ],
                        spacing=10,
                    ),
                    # Menambahkan border pada Container yang membungkus seluruh Column
                    border_radius=20,
                    border=border.all(
                        color=colors.GREY_900, width=0.5
                    ),  # Border hitam di sekeliling seluruh Column
                    padding=20,  # Memberikan padding di dalam container
                ),
            ],
            alignment=MainAxisAlignment.CENTER,
        ),
        width=350,
        margin=10,  # Memberikan jarak di luar container
    )
