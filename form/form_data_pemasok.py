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


# Fungsi untuk mengambil data pemasok dari database MySQL
def ambil_data_pemasok():
    # Query untuk mengambil data pemasok
    query = "SELECT * FROM pemasok ORDER BY pemasok_id DESC"
    cursor.execute(query)

    # Mengambil semua baris data
    data_pemasok = cursor.fetchall()

    return data_pemasok


# Halaman kelola pemasok
def form_kelola_pemasok(page: Page):
    # Mengambil data pemasok dari database MySQL
    data_pemasok = ambil_data_pemasok()

    # Variabel untuk paginasi
    baris_data_per_hal = 5  # Jumlah baris per halaman
    hal_sekarang = 0  # Mulai dari halaman pertama

    # Membuat inputan untuk form entri
    inputan_pencarian = TextField(
        label="Cari by Nama Pemasok", width=300, autofocus=True
    )  # Pencarian berdasarkan nama pemasok
    inputan_id_pemasok = TextField(
        visible=False, width=300
    )  # Field ID yang disembunyikan
    inputan_nama_pemasok = TextField(label="Nama Pemasok", width=300)
    inputan_alamat = TextField(label="Alamat", width=300)
    inputan_no_telepon = TextField(label="No. Telepon", width=300)
    snack_bar_berhasil = SnackBar(Text("Operasi berhasil"), bgcolor="green")
    snack_bar_gagal = SnackBar(Text("Operasi gagal"), bgcolor="red")

    # Fungsi untuk membersihkan form entri
    def bersihkan_form_entri(e=None):
        inputan_id_pemasok.value = ""
        inputan_nama_pemasok.value = ""
        inputan_alamat.value = ""
        inputan_no_telepon.value = ""

        inputan_id_pemasok.update()
        inputan_nama_pemasok.update()
        inputan_alamat.update()
        inputan_no_telepon.update()

    # Fungsi untuk mengisi data pemasok ke dalam form entri (edit data)
    def detail_data_pemasok(e):
        inputan_id_pemasok.value = e.control.data[0]
        inputan_nama_pemasok.value = e.control.data[1]
        inputan_alamat.value = e.control.data[2]
        inputan_no_telepon.value = e.control.data[3]

        inputan_id_pemasok.update()
        inputan_nama_pemasok.update()
        inputan_alamat.update()
        inputan_no_telepon.update()

    # Fungsi untuk menyimpan data pemasok ke database
    def simpan_data_pemasok(e):
        try:
            if inputan_id_pemasok.value == "":
                sql = "INSERT INTO pemasok (nama_pemasok, alamat, no_telepon) VALUES(%s, %s, %s)"
                val = (
                    inputan_nama_pemasok.value,
                    inputan_alamat.value,
                    inputan_no_telepon.value,
                )
            else:
                sql = "UPDATE pemasok SET nama_pemasok = %s, alamat = %s, no_telepon = %s WHERE pemasok_id = %s"
                val = (
                    inputan_nama_pemasok.value,
                    inputan_alamat.value,
                    inputan_no_telepon.value,
                    inputan_id_pemasok.value,
                )

            cursor.execute(sql, val)
            koneksi_db.commit()
            print(cursor.rowcount, "Data disimpan!")

            data_pemasok = (
                ambil_data_pemasok()
            )  # Mengambil kembali data pemasok yang terbaru dari database
            nonlocal filtered_data_pemasok
            filtered_data_pemasok = (
                data_pemasok  # Set data yang difilter menjadi data terbaru
            )

            update_baris_data_pemasok()
            bersihkan_form_entri()

            snack_bar_berhasil.open = True
            snack_bar_berhasil.update()

        except Exception as e:
            print(e)
            print("Ada yang error!")

    # Fungsi untuk menghapus data pemasok
    def hapus_data_pemasok(e):
        try:
            sql = "DELETE FROM pemasok WHERE pemasok_id = %s"
            val = (e.control.data,)
            cursor.execute(sql, val)
            koneksi_db.commit()
            print(cursor.rowcount, "Data dihapus!")

            data_pemasok = (
                ambil_data_pemasok()
            )  # Mengambil kembali data pemasok yang terbaru dari database
            nonlocal filtered_data_pemasok
            filtered_data_pemasok = (
                data_pemasok  # Set data yang difilter menjadi data terbaru
            )

            update_baris_data_pemasok()

            snack_bar_berhasil.open = True
            snack_bar_berhasil.update()
            bersihkan_form_entri()

        except Exception as e:
            print(e)
            print("Ada yang error!")

    # Variabel untuk menyimpan data pemasok yang telah difilter
    filtered_data_pemasok = data_pemasok

    # Fungsi untuk memfilter data pemasok berdasarkan input di search field
    def filter_pemasok(e):
        data_pemasok = (
            ambil_data_pemasok()
        )  # Mengambil kembali data pemasok yang terbaru dari database
        query_pencarian = (
            inputan_pencarian.value.lower()
        )  # Mendapatkan kata pencarian dalam huruf kecil
        nonlocal filtered_data_pemasok
        # Memfilter data pemasok berdasarkan nama pemasok (tidak peka huruf besar/kecil)
        filtered_data_pemasok = [
            pemasok_kolom
            for pemasok_kolom in data_pemasok
            if query_pencarian in pemasok_kolom[1].lower()
        ]
        update_baris_data_pemasok()

    # Menghubungkan fungsi filter dengan perubahan nilai di search field
    inputan_pencarian.on_change = filter_pemasok

    # Fungsi untuk membuat DataRow berdasarkan data pemasok yang sudah difilter
    def update_baris_data_pemasok():
        nonlocal baris_data_pemasok
        index_mulai = hal_sekarang * baris_data_per_hal
        index_selesai = index_mulai + baris_data_per_hal
        hal_data = filtered_data_pemasok[index_mulai:index_selesai]

        baris_data_pemasok = [
            DataRow(
                cells=[
                    DataCell(
                        Text(str(index_mulai + i + 1))
                    ),  # Nomor urut otomatis (indeks mulai dari 1)
                    DataCell(Text(pemasok_kolom[1])),  # Nama pemasok
                    DataCell(Text(pemasok_kolom[2])),  # Alamat pemasok
                    DataCell(Text(pemasok_kolom[3])),  # No Telepon
                    DataCell(
                        Row(
                            [
                                IconButton(
                                    "create",
                                    icon_color="grey",
                                    data=pemasok_kolom,
                                    on_click=detail_data_pemasok,
                                ),
                                IconButton(
                                    "delete",
                                    icon_color="red",
                                    data=pemasok_kolom[0],
                                    on_click=hapus_data_pemasok,
                                ),
                            ]
                        )
                    ),
                ]
            )
            for i, pemasok_kolom in enumerate(hal_data)
        ]

        tabel_data_pemasok.rows = baris_data_pemasok
        tabel_data_pemasok.update()

    baris_data_pemasok = [
        DataRow(
            cells=[
                DataCell(Text(str(i + 1))),
                DataCell(Text(pemasok_kolom[1])),
                DataCell(Text(pemasok_kolom[2])),
                DataCell(Text(pemasok_kolom[3])),
                DataCell(
                    Row(
                        [
                            IconButton(
                                "create",
                                icon_color="grey",
                                data=pemasok_kolom,
                                on_click=detail_data_pemasok,
                            ),
                            IconButton(
                                "delete",
                                icon_color="red",
                                data=pemasok_kolom[0],
                                on_click=hapus_data_pemasok,
                            ),
                        ]
                    )
                ),
            ]
        )
        for i, pemasok_kolom in enumerate(filtered_data_pemasok[:baris_data_per_hal])
    ]

    tabel_data_pemasok = DataTable(
        columns=[
            DataColumn(Text("No.")),
            DataColumn(Text("Nama Pemasok")),
            DataColumn(Text("Alamat")),
            DataColumn(Text("No. Telepon")),
            DataColumn(Text("Opsi")),
        ],
        rows=baris_data_pemasok,
        width="auto",
    )

    # Kontrol untuk tombol navigasi pagination
    def pergi_hal_sebelumnya(e):
        nonlocal hal_sekarang
        if hal_sekarang > 0:
            hal_sekarang -= 1
            update_baris_data_pemasok()

    def pergi_hal_selanjutnya(e):
        nonlocal hal_sekarang
        if (hal_sekarang + 1) * baris_data_per_hal < len(filtered_data_pemasok):
            hal_sekarang += 1
            update_baris_data_pemasok()

    btn_sebelumnya = ElevatedButton("Sebelumnya", on_click=pergi_hal_sebelumnya)
    btn_selanjutnya = ElevatedButton("Berikutnya", on_click=pergi_hal_selanjutnya)

    # Membuat bagian kiri dengan form
    form_kiri = Container(
        Column(
            controls=[
                Text("Form Entri", size=14, weight=FontWeight.BOLD),
                inputan_id_pemasok,
                Text("Masukkan Nama Pemasok :"),
                inputan_nama_pemasok,
                Text("Masukkan Alamat :"),
                inputan_alamat,
                Text("Masukkan No Telepon :"),
                inputan_no_telepon,
                Row(
                    controls=[
                        ElevatedButton("Simpan", on_click=simpan_data_pemasok),
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
                Text("Tabel Data Pemasok", size=14, weight=FontWeight.BOLD),
                inputan_pencarian,
                tabel_data_pemasok,
                Row([btn_sebelumnya, btn_selanjutnya]),
            ],
            width="auto",
        ),
        border_radius=20,
        border=border.all(color=colors.GREY_900, width=0.5),
        padding=20,
    )

    # Menambahkan baris ke halaman
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
                        Text("Kelola Pemasok", size=30, weight="bold"),
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
