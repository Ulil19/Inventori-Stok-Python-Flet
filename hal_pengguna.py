from flet import *

# Import fungsi halaman dari file lain
from form.form_beranda import form_beranda
from form.form_profil import form_profil
from form.form_data_seragam import form_kelola_seragam
from form.form_data_pemasok import form_kelola_pemasok
from form.form_data_seragam_masuk import form_kelola_seragam_masuk
from form.form_data_seragam_tidak_sesuai import form_kelola_seragam_tidak_sesuai
from form.form_pembayaran import form_pembayaran
from form.form_kelola_laporan import form_kelola_laporan

from session_manager import get_session, clear_session  # Mengimpor dari session_manager


def main_hal_pengguna(page: Page):
    # Mendapatkan sesi pengguna
    user = get_session()
    page.title = (
        f"Aplikasi Pengelolaan Data Seragam - Halaman Pengguna ({user['username']})"
    )
    page.window_width = "auto"

    # Inisialisasi indeks halaman yang dipilih
    selected_index = 0
    pages = [
        lambda: form_beranda(page),  # Halaman Beranda
        lambda: form_kelola_seragam(page),  # Halaman Data Seragam
        lambda: form_kelola_pemasok(page),  # Halaman Data Pemasok
        lambda: form_kelola_seragam_masuk(page),  # Halaman Data Seragam Masuk
        lambda: form_kelola_seragam_tidak_sesuai(
            page
        ),  # Halaman Data Seragam Tidak Sesuai
        lambda: form_pembayaran(page),  # Halaman Pembayaran
        lambda: form_kelola_laporan(page),  # Halaman Laporan
        lambda: form_profil(page),  # Halaman Profil
    ]

    # Fungsi untuk menangani perubahan navigasi
    def on_navigation_change(e):
        nonlocal selected_index
        selected_index = e.control.selected_index
        # Perbarui halaman yang ditampilkan
        content_area.controls.clear()
        content_area.controls.append(
            pages[selected_index]()
        )  # Panggil fungsi dalam daftar
        page.update()

    # Membuat NavigationRail untuk navigasi
    rail = NavigationRail(
        selected_index=selected_index,
        label_type=NavigationRailLabelType.ALL,
        destinations=[
            NavigationRailDestination(
                icon=icons.HOME, selected_icon=icons.HOME, label="Beranda"
            ),
            NavigationRailDestination(
                icon=icons.FOLDER, selected_icon=icons.FOLDER, label="Data Seragam"
            ),
            NavigationRailDestination(
                icon=icons.PEOPLE, selected_icon=icons.PEOPLE, label="Data Pemasok"
            ),
            NavigationRailDestination(
                icon=icons.INPUT, selected_icon=icons.INPUT, label="Data Seragam Masuk"
            ),
            NavigationRailDestination(
                icon=icons.REPORT, selected_icon=icons.REPORT, label="Data Tidak Sesuai"
            ),
            NavigationRailDestination(
                icon=icons.PAYMENTS, selected_icon=icons.PAYMENTS, label="Pembayaran"
            ),
            NavigationRailDestination(
                icon=icons.REPORT, selected_icon=icons.REPORT, label="Laporan"
            ),
            NavigationRailDestination(
                icon=icons.PERSON, selected_icon=icons.PERSON, label="Profil"
            ),
        ],
        height=500,
        on_change=on_navigation_change,
    )

    # Membuat area konten untuk menampung halaman
    content_area = Column()
    content_area.controls.append(pages[selected_index]())

    # Menambahkan NavigationRail dan area konten ke halaman utama
    page.add(
        Row(
            [
                Column(
                    [
                        rail,
                        Container(
                            ElevatedButton(
                                "Keluar",
                                color="white",
                                width=100,
                                bgcolor="black",
                                on_click=lambda e: handle_logout(page),
                            ),
                            alignment=alignment.center,
                            width=200,
                        ),
                    ],
                    alignment=alignment.center,
                    width=200,
                ),
                VerticalDivider(width=20),
                content_area,
            ],
            expand=True,
        ),
    )


# Fungsi untuk menangani proses logout
def handle_logout(page: Page):
    # Dialog konfirmasi
    def on_confirm(e):
        clear_session()  # Menghapus sesi pengguna
        page.window.close()  # Menutup jendela aplikasi saat ini
        # import subprocess
        # subprocess.Popen(["python", "hal_login.py"])  # Membuka halaman login menggunakan subprocess

    def on_cancel(e):
        page.dialog.open = False
        page.update()

    konfirmasi_dialog = AlertDialog(
        title=Row(
            [
                Icon(
                    icons.WARNING_ROUNDED, color=colors.RED, size=30
                ),  # Ikon peringatan
                Text(
                    "Konfirmasi Keluar", size=20, weight="bold", color=colors.BLACK
                ),  # Judul dengan teks
            ],
            spacing=10,  # Jarak antara ikon dan teks
            alignment="start",  # Menyusun ke kiri
        ),
        content=Text("Apakah Anda yakin ingin keluar?"),
        actions=[
            TextButton("Batal", on_click=on_cancel),
            TextButton("Keluar", on_click=on_confirm),
        ],
        actions_alignment="end",
    )

    # Membuka dialog konfirmasi
    page.dialog = konfirmasi_dialog
    konfirmasi_dialog.open = True
    page.update()


# Menjalankan aplikasi
# app(target=main_hal_pengguna)
