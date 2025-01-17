from flet import *
import mysql.connector
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os
import webbrowser
import datetime


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


# Fungsi untuk mengambil data seragam masuk dari database MySQL
def ambil_data_seragam_masuk():
    query = """
    SELECT 
        sm.masuk_id, sm.tanggal_masuk, sm.jumlah_masuk, sm.jumlah_tidak_sesuai, sm.jumlah_valid, 
        s.nama_seragam, s.jenis, s.ukuran, s.harga, s.stok,
        p.nama_pemasok
    FROM 
        seragam_masuk sm
    JOIN 
        seragam s ON sm.seragam_id = s.seragam_id
    JOIN 
        pemasok p ON sm.pemasok_id = p.pemasok_id
    ORDER BY sm.masuk_id DESC
    """
    cursor.execute(query)
    return cursor.fetchall()


def wrap_text(text, max_width, canvas_obj, font="Helvetica", font_size=9):
    """Fungsi untuk membungkus teks agar sesuai dengan lebar kolom"""
    canvas_obj.setFont(font, font_size)
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        if canvas_obj.stringWidth(current_line + " " + word) <= max_width:
            current_line = (current_line + " " + word).strip()
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    return lines


def buat_pdf_pratinjau(data_seragam):
    pdf_file = "laporan_seragam.pdf"
    c = canvas.Canvas(pdf_file, pagesize=A4)
    width, height = A4

    logo_laporan = "logo_report.png"  # Ganti dengan path ikon Anda
    if os.path.exists(logo_laporan):
        c.drawImage(
            logo_laporan,
            30,
            height - 60,
            width=40,
            height=40,
            preserveAspectRatio=True,
            mask="auto",
        )

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(80, height - 30, "Laporan Seragam Masuk")
    c.setFont("Helvetica", 10)
    c.drawString(30, height - 70, "Mobile Application Development - UAS 2024")
    c.line(30, height - 75, width - 30, height - 75)

    # Header Kolom
    c.setFont("Helvetica-Bold", 10)
    y = height - 90
    column_positions = [30, 70, 150, 250, 320, 370, 420, 480]  # Sesuaikan posisi kolom
    headers = [
        "No.",
        "Tanggal",
        "Seragam",
        "Jenis",
        "Ukuran",
        "Jumlah",
        "Valid",
        "Pemasok",
    ]
    column_widths = [
        40,
        70,
        100,
        80,
        50,
        40,
        30,
        140,
    ]  # Kurangi lebar kolom

    for i, header in enumerate(headers):
        c.drawString(column_positions[i], y, header)

    c.line(30, y - 5, width - 30, y - 5)
    y -= 20

    # Isi Data
    c.setFont("Helvetica", 9)
    row_height = 15
    for i, row in enumerate(data_seragam, start=1):
        if y < 50:  # Jika ruang tidak cukup, buat halaman baru
            c.showPage()
            y = height - 50
            c.setFont("Helvetica-Bold", 10)
            for j, header in enumerate(headers):
                c.drawString(column_positions[j], y, header)
            c.line(30, y - 5, width - 30, y - 5)
            y -= 20

        # Isi Baris
        c.setFont("Helvetica", 9)
        c.drawString(column_positions[0], y, str(i))
        c.drawString(column_positions[1], y, row["tanggal_masuk"].strftime("%Y-%m-%d"))
        c.drawString(column_positions[2], y, row["nama_seragam"])
        c.drawString(column_positions[3], y, row["jenis"])
        c.drawString(column_positions[4], y, row["ukuran"])
        c.drawString(column_positions[5], y, str(row["jumlah_masuk"]))
        c.drawString(column_positions[6], y, str(row["jumlah_valid"]))

        # Pembungkus teks untuk kolom pemasok
        pemasok_text = row["nama_pemasok"]
        pemasok_lines = wrap_text(pemasok_text, column_widths[7], c)

        for line in pemasok_lines:
            c.drawString(column_positions[7], y, line)
            y -= 10  # Sesuaikan jarak antara baris tambahan

        y -= row_height - 10  # Kurangi tinggi baris tambahan untuk baris biasa

    tanda_tangan_y = 50
    c.setFont("Helvetica", 10)
    tanggal_hari_ini = datetime.date.today().strftime("%d %B %Y")
    c.drawString(width - 180, tanda_tangan_y + 80, f"Kudus, {tanggal_hari_ini}")
    c.drawString(width - 180, tanda_tangan_y + 60, "Mengetahui,")
    c.drawString(width - 180, tanda_tangan_y + 45, "Manajer Gudang")
    c.drawString(
        width - 180, tanda_tangan_y - 30, "(....................................)"
    )

    c.save()
    return pdf_file


# Halaman kelola laporan
def form_kelola_laporan(page: Page):
    renew_koneksi_db()

    def preview_data(e=None):
        data_seragam = ambil_data_seragam_masuk()
        rows = []
        for i, row in enumerate(data_seragam, start=1):
            rows.append(
                DataRow(
                    cells=[
                        DataCell(Text(str(i))),
                        DataCell(Text(row["tanggal_masuk"].strftime("%Y-%m-%d"))),
                        DataCell(Text(row["nama_seragam"])),
                        DataCell(Text(row["jenis"])),
                        DataCell(Text(row["ukuran"])),
                        DataCell(Text(str(row["jumlah_masuk"]))),
                        DataCell(Text(str(row["jumlah_valid"]))),
                        DataCell(Text(row["nama_pemasok"])),
                    ]
                )
            )
        preview_table.rows = rows
        page.update()

    def bersihkan_preview(e=None):
        preview_table.rows = []
        page.update()

    def pratinjau_pdf(e=None):
        data_seragam = ambil_data_seragam_masuk()
        pdf_file = buat_pdf_pratinjau(data_seragam)
        webbrowser.open("file://" + os.path.abspath(pdf_file))

    form_kiri = Container(
        content=Column(
            controls=[
                ElevatedButton(
                    "Preview Data Seragam Masuk",
                    icon=icons.PREVIEW,
                    on_click=preview_data,
                ),
                ElevatedButton(
                    "Bersihkan Preview", icon=icons.CLEAR, on_click=bersihkan_preview
                ),
                ElevatedButton("Cetak PDF", icon=icons.PRINT, on_click=pratinjau_pdf),
            ],
            alignment=MainAxisAlignment.START,
        ),
        width=300,
        border_radius=20,
        border=border.all(color=colors.GREY_900, width=0.5),
        padding=20,
    )

    preview_table = DataTable(
        columns=[
            DataColumn(label=Text("No.")),
            DataColumn(label=Text("Tanggal")),
            DataColumn(label=Text("Seragam")),
            DataColumn(label=Text("Jenis")),
            DataColumn(label=Text("Ukuran")),
            DataColumn(label=Text("Jumlah")),
            DataColumn(label=Text("Valid")),
            DataColumn(label=Text("Pemasok")),
        ],
        rows=[],
    )

    form_kanan = Container(
        content=Column(
            controls=[
                Text("Preview Cetak Data", size=20, weight="bold"),
                Row(
                    controls=[preview_table],
                    scroll="auto",
                ),
            ],
            alignment=MainAxisAlignment.START,
            scroll="auto",
        ),
        width=700,
        border_radius=20,
        border=border.all(color=colors.GREY_900, width=0.5),
        padding=20,
    )

    return Container(
        content=Column(
            controls=[
                Row(
                    controls=[
                        Icon(
                            name=icons.DATA_EXPLORATION_ROUNDED,
                            size=50,
                            color=colors.BLUE_400,
                        ),
                        Text("Kelola Laporan", size=30, weight="bold"),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                ),
                Row(
                    controls=[form_kiri, form_kanan],
                    alignment=MainAxisAlignment.START,
                    vertical_alignment=CrossAxisAlignment.START,
                ),
            ]
        ),
        margin=10,
    )
