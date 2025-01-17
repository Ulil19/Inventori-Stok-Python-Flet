import mysql.connector
from flet import *
from session_manager import *
import time

# Setup koneksi ke database MySQL
koneksi_db = mysql.connector.connect(
    host="localhost", user="root", password="", database="uas_mad"
)
cursor = koneksi_db.cursor()

# Input field dan form_login
inputan_username = TextField(
    autofocus=True,
    width=335,
    height=40,
    hint_text="Masukkan username",
    border="underline",
    color="black",
    prefix_icon=icons.PERSON_ROUNDED,
)
inputan_password = TextField(
    width=335,
    height=40,
    hint_text="Masukkan password",
    border="underline",
    color="black",
    prefix_icon=icons.LOCK,
    password=True,
)

snack_bar_berhasil = SnackBar(Text("Operasi berhasil"), bgcolor="green")
snack_bar_gagal = SnackBar(Text("Operasi gagal"), bgcolor="red")

form_login = Container(
    Row(
        [
            Container(
                Column(
                    controls=[
                        snack_bar_berhasil,
                        snack_bar_gagal,
                        Container(
                            Icon(
                                name=icons.LOGIN_ROUNDED, size=50, color=colors.GREY_900
                            ),
                            width=360,
                        ),
                        Text(
                            "Halaman Login",
                            width=360,
                            size=30,
                            weight="w900",
                            text_align="center",
                        ),
                        Container(inputan_username, padding=padding.only(20, 10)),
                        Container(inputan_password, padding=padding.only(20, 10)),
                        Container(
                            ElevatedButton(
                                content=Text("M a s u k", color="white", weight="w500"),
                                width=335,
                                height=50,
                                bgcolor="black",
                                on_click=lambda e: proses_login(
                                    e.page
                                ),  # Pass halaman ke handler
                            ),
                            padding=padding.only(25, 10),
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_EVENLY,
                ),
                gradient=LinearGradient([colors.GREY_100, colors.GREY_200]),
                width=380,
                height=460,
                border_radius=20,
                border=border.all(color=colors.GREY_900, width=0.5),
            ),
        ],
        alignment=MainAxisAlignment.SPACE_EVENLY,
    ),
    padding=10,
)


# Fungsi login untuk mengautentikasi pengguna
def auntentifikasi_user(username, password):
    cursor = koneksi_db.cursor(dictionary=True)
    query = "SELECT * FROM user WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    if user:
        return user  # Mengembalikan detail pengguna jika ditemukan
    else:
        return None


# Fungsi untuk menangani login dan menyimpan sesi
def proses_login(page: Page):
    username = inputan_username.value
    password = inputan_password.value

    # Periksa apakah username dan password sudah diisi
    if not username or not password:
        snack_bar_gagal.open = True
        snack_bar_gagal.content = Text("Username atau password tidak boleh kosong.")
        snack_bar_gagal.update()
        print("Username atau password tidak boleh kosong.")
        return

    # Autentikasi pengguna
    user = auntentifikasi_user(username, password)

    if user:
        snack_bar_berhasil.open = True
        snack_bar_berhasil.update()
        print("Login berhasil!")
        # Simpan sesi pengguna menggunakan session_manager
        set_session(user)
        time.sleep(2.75)  # Delay selama
        page.clean()  # Bersihkan halaman

        # Impor tertunda untuk menghindari impor sirkular
        from hal_pengguna import main_hal_pengguna

        page.clean()  # Bersihkan halaman
        main_hal_pengguna(page)  # Muat halaman dasbor
    else:
        snack_bar_gagal.open = True
        snack_bar_gagal.update()
        print("Username atau password salah.")


# Fungsi untuk memeriksa apakah pengguna sudah login
def periksa_session():
    if "user" in session:
        user = get_session()
        print(f"Sesi aktif: {user['username']}")
        return True
    else:
        print("Tidak ada sesi aktif.")
        return False


# Pengaturan halaman utama
def main(page: Page):
    page.title = "Aplikasi Pengelolaan Stok Seragam - Halaman Login"
    page.window_width = 1280
    page.theme_mode = ThemeMode.LIGHT
    page.window_height = 720
    page.padding = 0
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    # page.scroll = ScrollMode.ADAPTIVE

    # Jika pengguna sudah login, tampilkan halaman dasbor
    if periksa_session():
        # Jika sesi aktif, tampilkan halaman dasbor
        page.clean()  # Bersihkan halaman saat ini
        from hal_pengguna import main_hal_pengguna

        main_hal_pengguna(page)  # Tampilkan halaman dasbor
    else:
        # Jika belum login, tampilkan form login
        page.add(form_login)


# Jalankan aplikasi
app(target=main)
