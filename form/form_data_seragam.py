from flet import *
import mysql.connector

# Setup koneksi ke database MySQL
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


# Fungsi untuk mengambil data seragam dari database MySQL
def ambil_data_seragam():
    query = "SELECT * FROM seragam ORDER BY seragam_id DESC"
    cursor.execute(query)
    data_seragam = cursor.fetchall()
    return data_seragam


def form_kelola_seragam(page: Page):
    data_seragam = ambil_data_seragam()

    baris_data_per_hal = 5
    hal_sekarang = 0

    inputan_pencarian = TextField(
        label="Cari by Nama Seragam", width=300, autofocus=True
    )
    inputan_id_seragam = TextField(visible=False, width=300)
    inputan_nama_seragam = TextField(label="Nama Seragam", width=300)
    inputan_jenis = TextField(label="Jenis", width=300)
    inputan_ukuran = TextField(label="Ukuran", width=300)
    inputan_tipe = TextField(label="Tipe", width=300)
    inputan_harga = TextField(label="Harga", width=300)
    inputan_stok = TextField(label="Stok", width=300)

    snack_bar_berhasil = SnackBar(Text("Operasi berhasil"), bgcolor="green")
    snack_bar_gagal = SnackBar(Text("Operasi gagal"), bgcolor="red")

    def format_rupiah(value):
        return f"Rp. {int(value):,}".replace(",", ".")

    def bersihkan_form_entri(e=None):
        inputan_id_seragam.value = ""
        inputan_nama_seragam.value = ""
        inputan_jenis.value = ""
        inputan_ukuran.value = ""
        inputan_tipe.value = ""
        inputan_harga.value = ""
        inputan_stok.value = ""
        inputan_id_seragam.update()
        inputan_nama_seragam.update()
        inputan_jenis.update()
        inputan_ukuran.update()
        inputan_tipe.update()
        inputan_harga.update()
        inputan_stok.update()

    # Fungsi untuk mengisi data seragam ke dalam form entri (edit data)
    def detail_data_seragam(e):
        inputan_id_seragam.value = e.control.data[0]  # Menyimpan ID seragam ke form
        inputan_nama_seragam.value = e.control.data[1]  # Nama seragam
        inputan_jenis.value = e.control.data[2]  # Jenis seragam
        inputan_ukuran.value = e.control.data[3]  # Ukuran seragam
        inputan_tipe.value = e.control.data[4]  # Tipe seragam
        inputan_harga.value = str(e.control.data[5])  # Harga seragam
        inputan_stok.value = str(e.control.data[6])  # Stok seragam

        inputan_id_seragam.update()
        inputan_nama_seragam.update()
        inputan_jenis.update()
        inputan_ukuran.update()
        inputan_tipe.update()
        inputan_harga.update()
        inputan_stok.update()

    def simpan_data_seragam(e):
        try:
            if inputan_id_seragam.value == "":
                sql = "INSERT INTO seragam (nama_seragam, jenis, ukuran, tipe, harga, stok) VALUES(%s, %s, %s, %s, %s, %s)"
                val = (
                    inputan_nama_seragam.value,
                    inputan_jenis.value,
                    inputan_ukuran.value,
                    inputan_tipe.value,
                    inputan_harga.value,
                    inputan_stok.value,
                )
            else:
                sql = "UPDATE seragam SET nama_seragam = %s, jenis = %s, ukuran = %s, tipe = %s, harga = %s, stok = %s WHERE seragam_id = %s"
                val = (
                    inputan_nama_seragam.value,
                    inputan_jenis.value,
                    inputan_ukuran.value,
                    inputan_tipe.value,
                    inputan_harga.value,
                    inputan_stok.value,
                    inputan_id_seragam.value,
                )

            cursor.execute(sql, val)
            koneksi_db.commit()

            data_seragam = ambil_data_seragam()
            nonlocal filtered_data_seragam
            filtered_data_seragam = data_seragam  # Update data terbaru
            update_baris_data_seragam()

            snack_bar_berhasil.open = True
            snack_bar_berhasil.update()
            bersihkan_form_entri()

        except Exception as e:
            print("Error:", e)

    def hapus_data_seragam(e):
        try:
            sql = "DELETE FROM seragam WHERE seragam_id = %s"
            val = (e.control.data,)
            cursor.execute(sql, val)
            koneksi_db.commit()

            data_seragam = ambil_data_seragam()
            nonlocal filtered_data_seragam
            filtered_data_seragam = data_seragam
            update_baris_data_seragam()

            snack_bar_berhasil.open = True
            snack_bar_berhasil.update()
            bersihkan_form_entri()

        except Exception as e:
            print("Error:", e)

    filtered_data_seragam = data_seragam

    def filter_seragam(e):
        data_seragam = ambil_data_seragam()
        query_pencarian = inputan_pencarian.value.lower()
        nonlocal filtered_data_seragam
        filtered_data_seragam = [
            seragam_kolom
            for seragam_kolom in data_seragam
            if query_pencarian in seragam_kolom[1].lower()
        ]
        update_baris_data_seragam()

    inputan_pencarian.on_change = filter_seragam

    def update_baris_data_seragam():
        nonlocal baris_data_seragam
        index_mulai = hal_sekarang * baris_data_per_hal
        index_selesai = index_mulai + baris_data_per_hal
        hal_data = filtered_data_seragam[index_mulai:index_selesai]

        baris_data_seragam = [
            DataRow(
                cells=[
                    DataCell(Text(str(index_mulai + i + 1))),
                    DataCell(Text(seragam_kolom[1])),
                    DataCell(Text(seragam_kolom[2])),
                    DataCell(Text(seragam_kolom[3])),
                    DataCell(Text(seragam_kolom[4])),
                    DataCell(Text(format_rupiah(seragam_kolom[5]))),
                    DataCell(Text(str(seragam_kolom[6]))),
                    DataCell(
                        Row(
                            [
                                IconButton(
                                    "create",
                                    icon_color="grey",
                                    data=seragam_kolom,
                                    on_click=detail_data_seragam,
                                ),
                                IconButton(
                                    "delete",
                                    icon_color="red",
                                    data=seragam_kolom[0],
                                    on_click=hapus_data_seragam,
                                ),
                            ]
                        )
                    ),
                ]
            )
            for i, seragam_kolom in enumerate(hal_data)
        ]

        tabel_data_seragam.rows = baris_data_seragam
        tabel_data_seragam.update()

    baris_data_seragam = [
        DataRow(
            cells=[
                DataCell(Text(str(i + 1))),
                DataCell(Text(seragam_kolom[1])),
                DataCell(Text(seragam_kolom[2])),
                DataCell(Text(seragam_kolom[3])),
                DataCell(Text(seragam_kolom[4])),
                DataCell(Text(format_rupiah(seragam_kolom[5]))),
                DataCell(Text(str(seragam_kolom[6]))),
                DataCell(
                    Row(
                        [
                            IconButton(
                                "create",
                                icon_color="grey",
                                data=seragam_kolom,
                                on_click=detail_data_seragam,
                            ),
                            IconButton(
                                "delete",
                                icon_color="red",
                                data=seragam_kolom[0],
                                on_click=hapus_data_seragam,
                            ),
                        ]
                    )
                ),
            ]
        )
        for i, seragam_kolom in enumerate(filtered_data_seragam[:baris_data_per_hal])
    ]

    tabel_data_seragam = DataTable(
        columns=[
            DataColumn(Text("No.")),
            DataColumn(Text("Nama Seragam")),
            DataColumn(Text("Jenis")),
            DataColumn(Text("Ukuran")),
            DataColumn(Text("Tipe")),
            DataColumn(Text("Harga")),
            DataColumn(Text("Stok")),
            DataColumn(Text("Opsi")),
        ],
        rows=baris_data_seragam,
        width="800",
    )

    def pergi_hal_sebelumnya(e):
        nonlocal hal_sekarang
        if hal_sekarang > 0:
            hal_sekarang -= 1
            update_baris_data_seragam()

    def pergi_hal_selanjutnya(e):
        nonlocal hal_sekarang
        if (hal_sekarang + 1) * baris_data_per_hal < len(filtered_data_seragam):
            hal_sekarang += 1
            update_baris_data_seragam()

    btn_sebelumnya = ElevatedButton("Sebelumnya", on_click=pergi_hal_sebelumnya)
    btn_selanjutnya = ElevatedButton("Berikutnya", on_click=pergi_hal_selanjutnya)

    # Membuat bagian kiri dengan form
    form_kiri = Container(
        Column(
            controls=[
                Text("Form Entri", size=14, weight=FontWeight.BOLD),
                inputan_id_seragam,
                Text("Masukkan Nama Seragam :"),
                inputan_nama_seragam,
                Text("Masukkan Jenis :"),
                inputan_jenis,
                Text("Masukkan Ukuran :"),
                inputan_ukuran,
                Text("Masukkan Tipe :"),
                inputan_tipe,
                Text("Masukkan Harga :"),
                inputan_harga,
                Text("Masukkan Stok :"),
                inputan_stok,
                Row(
                    controls=[
                        ElevatedButton("Simpan", on_click=simpan_data_seragam),
                        ElevatedButton("Batal", on_click=bersihkan_form_entri),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    spacing=20,
                ),
            ],
            width=300,
        ),
        border_radius=20,
        border=border.all(color=colors.GREY_900, width=0.5),
        padding=20,
    )

    # Membuat bagian kanan dengan search field dan table
    form_kanan = Container(
        Column(
            controls=[
                Text("Tabel Data Seragam", size=14, weight=FontWeight.BOLD),
                Row(
                    controls=[inputan_pencarian],
                ),
                Row(controls=[tabel_data_seragam], scroll="auto"),
                Row([btn_sebelumnya, btn_selanjutnya]),
            ],
            alignment=MainAxisAlignment.START,
            scroll="auto",
        ),
        width="800",
        border_radius=20,
        border=border.all(color=colors.GREY_900, width=0.5),
        padding=20,
    )

    return Container(
        content=Column(
            controls=[
                Row(
                    [
                        Icon(
                            name=icons.TABLE_CHART_ROUNDED,
                            size=50,
                            color=colors.BLUE_400,
                        ),
                        Text("Kelola Seragam", size=30, weight="bold"),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                ),
                Row(
                    controls=[form_kiri, form_kanan],
                    alignment=MainAxisAlignment.START,
                    vertical_alignment=CrossAxisAlignment.START,
                ),
                snack_bar_berhasil,
                snack_bar_gagal,
            ]
        ),
        margin=10,
    )
