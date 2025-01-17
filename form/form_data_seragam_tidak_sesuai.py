from flet import *
import mysql.connector
import datetime

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


# Fungsi untuk mengambil data seragam_masuk dari database
def ambil_data_seragam_masuk():
    query = """
    SELECT sm.masuk_id, s.nama_seragam, p.nama_pemasok, sm.tanggal_masuk, 
           sm.jumlah_masuk, sm.jumlah_tidak_sesuai, sm.jumlah_valid
    FROM seragam_masuk sm
    JOIN seragam s ON sm.seragam_id = s.seragam_id
    JOIN pemasok p ON sm.pemasok_id = p.pemasok_id
    ORDER BY sm.masuk_id DESC
    """
    cursor.execute(query)
    data_seragam_masuk = cursor.fetchall()
    return data_seragam_masuk


# Fungsi untuk mengambil daftar seragam untuk pilihan
def ambil_data_seragam():
    query = "SELECT seragam_id, nama_seragam FROM seragam"
    cursor.execute(query)
    return cursor.fetchall()


# Fungsi untuk mengambil daftar pemasok untuk pilihan
def ambil_data_pemasok():
    query = "SELECT pemasok_id, nama_pemasok FROM pemasok"
    cursor.execute(query)
    return cursor.fetchall()


# Fungsi untuk mengambil data seragam_tidak_sesuai
def ambil_data_seragam_tidak_sesuai():
    query = """
    SELECT st.tidak_sesuai_id, sm.masuk_id, s.nama_seragam, p.nama_pemasok, st.jumlah_tidak_sesuai, st.keterangan, st.status
    FROM seragam_tidak_sesuai st
    JOIN seragam_masuk sm ON st.masuk_id = sm.masuk_id
    JOIN seragam s ON sm.seragam_id = s.seragam_id
    JOIN pemasok p ON sm.pemasok_id = p.pemasok_id
    ORDER BY st.tidak_sesuai_id DESC
    """
    cursor.execute(query)
    data_seragam_tidak_sesuai = cursor.fetchall()
    return data_seragam_tidak_sesuai


# Fungsi untuk mengelola form seragam tidak sesuai
def form_kelola_seragam_tidak_sesuai(page: Page):
    data_seragam_tidak_sesuai = ambil_data_seragam_tidak_sesuai()
    data_seragam_masuk = ambil_data_seragam_masuk()

    baris_data_per_hal = 5
    hal_sekarang = 0

    # Input fields untuk seragam tidak sesuai
    inputan_pencarian = TextField(label="Pencarian", width=300, autofocus=True)
    inputan_id_tidak_sesuai = TextField(visible=False, width=300)
    inputan_masuk_id = Dropdown(
        label="Pilih Seragam Masuk",
        options=[
            dropdown.Option(str(masuk[0]), f"{masuk[1]} - {masuk[2]}")
            for masuk in data_seragam_masuk
        ],
        width=300,
    )
    inputan_jumlah_tidak_sesuai = TextField(
        label="Jumlah Tidak Sesuai", width=300, value="0"
    )
    inputan_keterangan = TextField(label="Keterangan", width=300, max_length=255)
    inputan_status = Dropdown(
        label="Status",
        options=[dropdown.Option("Dikembalikan"), dropdown.Option("Diterima")],
        width=300,
    )

    snack_bar_berhasil = SnackBar(Text("Operasi berhasil"), bgcolor="green")
    snack_bar_gagal = SnackBar(Text("Operasi gagal"), bgcolor="red")

    # Fungsi untuk membersihkan form entri seragam tidak sesuai
    def bersihkan_form_entri(e=None):
        inputan_id_tidak_sesuai.value = ""
        inputan_masuk_id.value = ""
        inputan_jumlah_tidak_sesuai.value = "0"
        inputan_keterangan.value = ""
        inputan_status.value = "Dikembalikan"

        inputan_id_tidak_sesuai.update()
        inputan_masuk_id.update()
        inputan_jumlah_tidak_sesuai.update()
        inputan_keterangan.update()
        inputan_status.update()

    # fungsi untuk mengisi data seragam tidak sesuai ke form (edit data
    def detail_data_seragam_tidak_sesuai(e):
        inputan_id_tidak_sesuai.value = e.control.data[0]
        inputan_masuk_id.value = e.control.data[1]
        inputan_jumlah_tidak_sesuai.value = str(e.control.data[4])
        inputan_keterangan.value = e.control.data[5]
        inputan_status.value = e.control.data[6]

        inputan_id_tidak_sesuai.update()
        inputan_masuk_id.update()
        inputan_jumlah_tidak_sesuai.update()
        inputan_keterangan.update()
        inputan_status.update()

    # Fungsi untuk menyimpan data seragam tidak sesuai
    def simpan_data_seragam_tidak_sesuai(e=None):
        try:
            if inputan_id_tidak_sesuai.value:
                query = """
                UPDATE seragam_tidak_sesuai 
                SET masuk_id = %s, jumlah_tidak_sesuai = %s, keterangan = %s, status = %s
                WHERE tidak_sesuai_id = %s
                """
                values = (
                    inputan_masuk_id.value,
                    int(inputan_jumlah_tidak_sesuai.value),
                    inputan_keterangan.value,
                    inputan_status.value,
                    inputan_id_tidak_sesuai.value,
                )
            else:
                # Insert data baru
                query = """
                INSERT INTO seragam_tidak_sesuai (masuk_id, jumlah_tidak_sesuai, keterangan, status) 
                VALUES (%s, %s, %s, %s)
                """
                values = (
                    inputan_masuk_id.value,
                    int(inputan_jumlah_tidak_sesuai.value),
                    inputan_keterangan.value,
                    inputan_status.value,
                )
            cursor.execute(query, values)
            koneksi_db.commit()
            print(cursor.rowcount, "Data disimpan!")

            data_seragam_tidak_sesuai = ambil_data_seragam_tidak_sesuai()
            nonlocal filtered_data_seragam_tidak_sesuai
            filtered_data_seragam_tidak_sesuai = data_seragam_tidak_sesuai
            update_baris_data_seragam_tidak_sesuai()

            snack_bar_berhasil.open = True
            snack_bar_berhasil.update()
            bersihkan_form_entri()

        except Exception as e:
            print(e)
            print("Ada yang error!")

    # Fungsi untuk menghapus data seragam tidak sesuai
    def hapus_data_seragam_tidak_sesuai(e):
        try:
            sql = "DELETE FROM seragam_tidak_sesuai WHERE tidak_sesuai_id = %s"
            val = (e.control.data,)
            cursor.execute(sql, val)
            koneksi_db.commit()

            data_seragam_tidak_sesuai = ambil_data_seragam_tidak_sesuai()
            nonlocal filtered_data_seragam_tidak_sesuai
            filtered_data_seragam_tidak_sesuai = data_seragam_tidak_sesuai
            update_baris_data_seragam_tidak_sesuai()

            snack_bar_berhasil.open = True
            snack_bar_berhasil.update()
            bersihkan_form_entri()

        except Exception as e:
            print(e)
            print("Ada yang error!")

    filtered_data_seragam_tidak_sesuai = ambil_data_seragam_tidak_sesuai()

    def filter_seragam_tidak_sesuai(e):
        data_seragam_tidak_sesuai = ambil_data_seragam_tidak_sesuai()
        query_pencarian = inputan_pencarian.value.lower()
        nonlocal filtered_data_seragam_tidak_sesuai
        filtered_data_seragam_tidak_sesuai = [
            seragam_tidak_sesuai_kolom
            for seragam_tidak_sesuai_kolom in data_seragam_tidak_sesuai
            if query_pencarian in seragam_tidak_sesuai_kolom[3].lower()
        ]
        update_baris_data_seragam_tidak_sesuai()

    inputan_pencarian.on_change = filter_seragam_tidak_sesuai

    def update_baris_data_seragam_tidak_sesuai():
        nonlocal baris_data_seragam_tidak_sesuai
        index_mulai = hal_sekarang * baris_data_per_hal
        index_selesai = index_mulai + baris_data_per_hal
        hal_data = filtered_data_seragam_tidak_sesuai[index_mulai:index_selesai]

        baris_data_seragam_tidak_sesuai = [
            DataRow(
                cells=[
                    DataCell(Text(str(index_mulai + i + 1))),  # Nomor Urut
                    DataCell(Text(seragam_tidak_sesuai_kolom[2])),
                    DataCell(Text(seragam_tidak_sesuai_kolom[4])),
                    DataCell(Text(seragam_tidak_sesuai_kolom[5])),
                    DataCell(Text(seragam_tidak_sesuai_kolom[6])),
                    DataCell(
                        Row(
                            [
                                IconButton(
                                    "create",
                                    icon_color="grey",
                                    data=seragam_tidak_sesuai_kolom,
                                    on_click=detail_data_seragam_tidak_sesuai,
                                ),
                                IconButton(
                                    "delete",
                                    icon_color="red",
                                    data=seragam_tidak_sesuai_kolom[0],
                                    on_click=hapus_data_seragam_tidak_sesuai,
                                ),
                            ]
                        )
                    ),
                ]
            )
            for i, seragam_tidak_sesuai_kolom in enumerate(hal_data)
        ]

        table_seragam_tidak_sesuai.rows = baris_data_seragam_tidak_sesuai
        table_seragam_tidak_sesuai.update()

    baris_data_seragam_tidak_sesuai = [
        DataRow(
            cells=[
                DataCell(Text(str(i + 1))),
                DataCell(
                    Text(
                        seragam_tidak_sesuai_kolom[2]
                        + " - "
                        + seragam_tidak_sesuai_kolom[3]
                    )
                ),
                DataCell(Text(seragam_tidak_sesuai_kolom[4])),
                DataCell(Text(seragam_tidak_sesuai_kolom[5])),
                DataCell(Text(seragam_tidak_sesuai_kolom[6])),
                DataCell(
                    Row(
                        [
                            IconButton(
                                "create",
                                icon_color="grey",
                                data=seragam_tidak_sesuai_kolom,
                                on_click=detail_data_seragam_tidak_sesuai,
                            ),
                            IconButton(
                                "delete",
                                icon_color="red",
                                data=seragam_tidak_sesuai_kolom[0],
                                on_click=hapus_data_seragam_tidak_sesuai,
                            ),
                        ]
                    )
                ),
            ]
        )
        for i, seragam_tidak_sesuai_kolom in enumerate(
            filtered_data_seragam_tidak_sesuai
        )
    ]

    table_seragam_tidak_sesuai = DataTable(
        columns=[
            DataColumn(label=Text("No")),
            DataColumn(label=Text("Nama Seragam")),
            DataColumn(label=Text("Jumlah Tidak Sesuai")),
            DataColumn(label=Text("Keterangan")),
            DataColumn(label=Text("Status")),
            DataColumn(label=Text("Aksi")),
        ],
        rows=baris_data_seragam_tidak_sesuai,
        width="auto",
    )

    def pergi_hal_sebelumnya(e):
        nonlocal hal_sekarang
        if hal_sekarang > 0:
            hal_sekarang -= 1
            update_baris_data_seragam_tidak_sesuai()

    def pergi_hal_selanjutnya(e):
        nonlocal hal_sekarang
        if (hal_sekarang + 1) * baris_data_per_hal < len(
            filtered_data_seragam_tidak_sesuai
        ):
            hal_sekarang += 1
            update_baris_data_seragam_tidak_sesuai()

    btn_sebelumnya = ElevatedButton("Sebelumnya", on_click=pergi_hal_sebelumnya)
    btn_selanjutnya = ElevatedButton("Berikutnya", on_click=pergi_hal_selanjutnya)

    # membuat bagian kiri form
    form_kiri = Container(
        Column(
            controls=[
                Text("Data Seragam Tidak Sesuai", size=14, weight=FontWeight.BOLD),
                inputan_id_tidak_sesuai,
                Text("nama seragam"),
                inputan_masuk_id,
                Text("jumlah tidak sesuai"),
                inputan_jumlah_tidak_sesuai,
                Text("keterangan"),
                inputan_keterangan,
                Text("status"),
                inputan_status,
                Row(
                    controls=[
                        ElevatedButton(
                            "Simpan", on_click=simpan_data_seragam_tidak_sesuai
                        ),
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

    form_kanan = Container(
        Column(
            controls=[
                Text("Data Seragam Tidak Sesuai", size=14, weight=FontWeight.BOLD),
                Row(
                    controls=[
                        inputan_pencarian,
                    ]
                ),
                Row(controls=[table_seragam_tidak_sesuai], scroll="auto"),
                Row([btn_sebelumnya, btn_selanjutnya]),
            ],
            alignment=MainAxisAlignment.START,
            scroll="auto",
        ),
        width=800,
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
                        Text("Data Seragam Tidak Sesuai", size=30, weight="bold"),
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
