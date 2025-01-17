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


def form_kelola_seragam_masuk(page: Page):
    data_seragam_masuk = ambil_data_seragam_masuk()
    daftar_seragam = ambil_data_seragam()
    daftar_pemasok = ambil_data_pemasok()

    baris_data_per_hal = 5
    hal_sekarang = 0

    # Input fields
    inputan_pencarian = TextField(
        label="Cari by Nama Seragam", width=300, autofocus=True
    )
    inputan_id_masuk = TextField(visible=False, width=300)
    inputan_seragam_id = Dropdown(
        label="Pilih Seragam",
        options=[
            dropdown.Option(str(seragam[0]), seragam[1]) for seragam in daftar_seragam
        ],
        width=300,
    )
    inputan_pemasok_id = Dropdown(
        label="Pilih Pemasok",
        options=[
            dropdown.Option(str(pemasok[0]), pemasok[1]) for pemasok in daftar_pemasok
        ],
        width=300,
    )

    inputan_tanggal_masuk = TextField(
        label="Tanggal Masuk",
        width=300,
        hint_text="masukkan tanggal mulai masuk",
        expand=True,
        read_only=True,
    )

    def change_date(e):
        if inputan_tanggal_masuk_picker.value:  # Pastikan ada nilai dari DatePicker
            try:
                tgl_baru = inputan_tanggal_masuk_picker.value
                inputan_tanggal_masuk.value = tgl_baru.strftime("%Y-%m-%d")
            except Exception as ex:
                inputan_tanggal_masuk.value = f"Error: {str(ex)}"
        else:
            inputan_tanggal_masuk.value = "Tanggal tidak dipilih!"
        inputan_tanggal_masuk.update()

    def date_picker_dismissed(e):
        if inputan_tanggal_masuk_picker.value:
            inputan_tanggal_masuk.value = inputan_tanggal_masuk_picker.value.strftime(
                "%Y-%m-%d"
            )
        else:
            inputan_tanggal_masuk.value = "Tanggal tidak dipilih!"
        inputan_tanggal_masuk.update()

    inputan_tanggal_masuk_picker = DatePicker(
        on_change=change_date,
        on_dismiss=date_picker_dismissed,
        first_date=datetime.datetime(1945, 1, 1),
        last_date=datetime.datetime(2050, 10, 1),
    )

    inputan_jumlah_masuk = TextField(label="Jumlah Masuk", width=300)
    inputan_jumlah_tidak_sesuai = TextField(
        label="Jumlah Tidak Sesuai", width=300, value="0"
    )
    snack_bar_berhasil = SnackBar(Text("Operasi berhasil"), bgcolor="green")
    snack_bar_gagal = SnackBar(Text("Operasi gagal"), bgcolor="red")

    # Fungsi untuk membersihkan form entri
    def bersihkan_form_entri(e=None):
        inputan_id_masuk.value = ""
        inputan_seragam_id.value = ""
        inputan_pemasok_id.value = ""
        inputan_tanggal_masuk.value = ""
        inputan_jumlah_masuk.value = ""
        inputan_jumlah_tidak_sesuai.value = "0"

        inputan_id_masuk.update()
        inputan_seragam_id.update()
        inputan_pemasok_id.update()
        inputan_tanggal_masuk.update()
        inputan_jumlah_masuk.update()
        inputan_jumlah_tidak_sesuai.update()

    # Fungsi untuk mengisi data seragam masuk ke dalam form entri (edit data)
    def detail_data_seragam_masuk(e):
        # Set nilai ID
        inputan_id_masuk.value = e.control.data[0]

        # Cari dan set nilai dropdown seragam
        seragam_text = e.control.data[1]
        inputan_seragam_id.value = None  # Default jika tidak ditemukan
        for option in inputan_seragam_id.options:
            if option.text == seragam_text:
                inputan_seragam_id.value = option.key
                break
        # print("Seragam ID setelah set:", inputan_seragam_id.value)

        # Cari dan set nilai dropdown pemasok
        pemasok_text = e.control.data[2]
        inputan_pemasok_id.value = None  # Default jika tidak ditemukan
        for option in inputan_pemasok_id.options:
            if option.text == pemasok_text:
                inputan_pemasok_id.value = option.key
                break
        # print("Pemasok ID setelah set:", inputan_pemasok_id.value)

        # Set nilai lainnya
        inputan_tanggal_masuk.value = e.control.data[3]
        inputan_jumlah_masuk.value = str(e.control.data[4])
        inputan_jumlah_tidak_sesuai.value = str(e.control.data[5])

        # Update UI
        inputan_id_masuk.update()
        inputan_seragam_id.update()
        inputan_pemasok_id.update()
        inputan_tanggal_masuk.update()
        inputan_jumlah_masuk.update()
        inputan_jumlah_tidak_sesuai.update()

    # Fungsi untuk menyimpan data seragam masuk
    def simpan_data_seragam_masuk(e=None):
        try:
            if inputan_id_masuk.value:
                query = """
                UPDATE seragam_masuk 
                SET seragam_id = %s, pemasok_id = %s, tanggal_masuk = %s, jumlah_masuk = %s, jumlah_tidak_sesuai = %s
                WHERE masuk_id = %s
                """
                values = (
                    inputan_seragam_id.value,
                    inputan_pemasok_id.value,
                    inputan_tanggal_masuk.value,
                    int(inputan_jumlah_masuk.value),
                    int(inputan_jumlah_tidak_sesuai.value),
                    inputan_id_masuk.value,
                )

            else:
                # Insert data baru
                query = """
                INSERT INTO seragam_masuk (seragam_id, pemasok_id, tanggal_masuk, jumlah_masuk, jumlah_tidak_sesuai) 
                VALUES (%s, %s, %s, %s, %s)
                """
                values = (
                    inputan_seragam_id.value,
                    inputan_pemasok_id.value,
                    inputan_tanggal_masuk.value,
                    int(inputan_jumlah_masuk.value),
                    int(inputan_jumlah_tidak_sesuai.value),
                )
            cursor.execute(query, values)
            koneksi_db.commit()
            print(cursor.rowcount, "Data disimpan!")

            data_seragam_masuk = ambil_data_seragam_masuk()
            nonlocal filtered_data_seragam_masuk
            filtered_data_seragam_masuk = data_seragam_masuk

            update_baris_data_seragam_masuk()

            snack_bar_berhasil.open = True
            snack_bar_berhasil.update()
            bersihkan_form_entri()

        except Exception as e:
            print(e)
            print("Ada yang error!")

    # Fungsi untuk menghapus data seragam masuk
    def hapus_data_seragam_masuk(e):
        try:
            sql = "DELETE FROM seragam_masuk WHERE masuk_id = %s"
            val = (e.control.data,)
            cursor.execute(sql, val)
            koneksi_db.commit()
            print(cursor.rowcount, "Data dihapus!")

            data_seragam_masuk = ambil_data_seragam_masuk()

            nonlocal filtered_data_seragam_masuk
            filtered_data_seragam_masuk = data_seragam_masuk

            update_baris_data_seragam_masuk()

            snack_bar_berhasil.open = True
            snack_bar_berhasil.update()
            bersihkan_form_entri()

        except Exception as e:
            print(e)
            print("Ada yang error!")

    # Variabel untuk menyimpan data pemasok yang telah difilter
    filtered_data_seragam_masuk = data_seragam_masuk

    # Fungsi untuk memfilter data pemasok berdasarkan input di search field
    def filter_seragam_masuk(e):
        data_seragam_masuk = ambil_data_seragam_masuk()

        query_pencarian = (
            inputan_pencarian.value
        )  # Mendapatkan kata pencarian dalam huruf kecil
        nonlocal filtered_data_seragam_masuk
        filtered_data_seragam_masuk = [
            seragam_masuk_kolom
            for seragam_masuk_kolom in data_seragam_masuk
            if query_pencarian in seragam_masuk_kolom[2]
        ]
        update_baris_data_seragam_masuk()

    # Menghubungkan fungsi filter dengan perubahan nilai di search field
    inputan_pencarian.on_change = filter_seragam_masuk

    # Fungsi untuk membuat DataRow berdasarkan data seragam masuk
    def update_baris_data_seragam_masuk():
        # print("Data seragam masuk yang difilter:", filtered_data_seragam_masuk)
        nonlocal filtered_data_seragam_masuk
        index_mulai = hal_sekarang * baris_data_per_hal
        index_selesai = index_mulai + baris_data_per_hal
        hal_data = filtered_data_seragam_masuk[index_mulai:index_selesai]
        baris_data_seragam_masuk = [
            DataRow(
                cells=[
                    DataCell(Text(str(index_mulai + i + 1))),  # Nomor Urut
                    DataCell(Text(seragam_masuk_kolom[1])),  # Nama Seragam
                    DataCell(Text(seragam_masuk_kolom[2])),  # Nama Pemasok
                    DataCell(Text(seragam_masuk_kolom[3])),  # Tanggal Masuk
                    DataCell(Text(seragam_masuk_kolom[4])),  # Jumlah Masuk
                    DataCell(Text(seragam_masuk_kolom[5])),  # Jumlah Tidak Sesuai
                    DataCell(Text(seragam_masuk_kolom[6])),  # Jumlah Valid
                    DataCell(
                        Row(
                            [
                                IconButton(
                                    "edit",
                                    icon_color="grey",
                                    data=seragam_masuk_kolom,  # Pastikan data lengkap
                                    on_click=detail_data_seragam_masuk,
                                ),
                                IconButton(
                                    "delete",
                                    icon_color="red",
                                    data=seragam_masuk_kolom[0],
                                    on_click=hapus_data_seragam_masuk,
                                ),
                            ]
                        )
                    ),
                ]
            )
            for i, seragam_masuk_kolom in enumerate(hal_data)
        ]

        tabel_data_seragam_masuk.rows = baris_data_seragam_masuk
        tabel_data_seragam_masuk.update()

    baris_data_seragam_masuk = [
        DataRow(
            cells=[
                DataCell(Text(str(i + 1))),  # Menampilkan nomor urut otomatis
                DataCell(Text(seragam_masuk_kolom[1])),  # Menampilkan Nama Seragam
                DataCell(Text(seragam_masuk_kolom[2])),  # Menampilkan Nama Pemasok
                DataCell(Text(seragam_masuk_kolom[3])),  # Menampilkan Tanggal Masuk
                DataCell(Text(seragam_masuk_kolom[4])),  # Menampilkan Jumlah Masuk
                DataCell(
                    Text(seragam_masuk_kolom[5])
                ),  # Menampilkan Jumlah Tidak Sesuai
                DataCell(Text(seragam_masuk_kolom[6])),  # Menampilkan jumlah valid
                DataCell(
                    Row(
                        [
                            IconButton(
                                "edit",
                                icon_color="grey",
                                data=seragam_masuk_kolom,
                                on_click=detail_data_seragam_masuk,
                            ),
                            IconButton(
                                "delete",
                                icon_color="red",
                                data=seragam_masuk_kolom[0],
                                on_click=hapus_data_seragam_masuk,
                            ),
                        ]
                    )
                ),
            ]
        )
        for i, seragam_masuk_kolom in enumerate(
            filtered_data_seragam_masuk[:baris_data_per_hal]
        )
    ]
    tabel_data_seragam_masuk = DataTable(
        columns=[
            DataColumn(Text("No.")),
            DataColumn(Text("Nama Seragam")),
            DataColumn(Text("Nama Pemasok")),
            DataColumn(Text("Tanggal Masuk")),
            DataColumn(Text("Jumlah Masuk")),
            DataColumn(Text("Jumlah Tidak Sesuai")),
            DataColumn(Text("Jumlah Valid")),
            DataColumn(Text("Aksi")),
        ],
        rows=baris_data_seragam_masuk,
        width="auto",
    )

    # Kontrol untuk tombol navigasi pagination
    def pergi_hal_sebelumnya(e):
        nonlocal hal_sekarang
        if hal_sekarang > 0:
            hal_sekarang -= 1
            update_baris_data_seragam_masuk()

    def pergi_hal_selanjutnya(e):
        nonlocal hal_sekarang
        if (hal_sekarang + 1) * baris_data_per_hal < len(filtered_data_seragam_masuk):
            hal_sekarang += 1
            update_baris_data_seragam_masuk()

    # Tombol navigasi pagination
    btn_sebelumnya = ElevatedButton("Sebelumnya", on_click=pergi_hal_sebelumnya)
    btn_selanjutnya = ElevatedButton("Selanjutnya", on_click=pergi_hal_selanjutnya)

    # membuat bagian kiri dengan form
    form_kiri = Container(
        Column(
            controls=[
                Text("Form Seragam Masuk", size=14, weight="bold"),
                inputan_id_masuk,
                Text("Nama Seragam :"),
                inputan_seragam_id,
                Text("Nama Pemasok :"),
                inputan_pemasok_id,
                Text("Tanggal Masuk :"),
                Row(
                    [
                        inputan_tanggal_masuk,
                        inputan_tanggal_masuk_picker,
                        IconButton(
                            icon=icons.CALENDAR_MONTH,
                            icon_color="black",
                            on_click=lambda _: inputan_tanggal_masuk_picker.pick_date(),
                        ),
                    ],
                ),
                Text("Jumlah Masuk :"),
                inputan_jumlah_masuk,
                Text("Jumlah Tidak Sesuai :"),
                inputan_jumlah_tidak_sesuai,
                Row(
                    controls=[
                        ElevatedButton("Simpan", on_click=simpan_data_seragam_masuk),
                        ElevatedButton("Bersihkan", on_click=bersihkan_form_entri),
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
                Text("Tabel Seragam Masuk", size=14, weight="bold"),
                Row(controls=[inputan_pencarian]),
                Row(controls=[tabel_data_seragam_masuk], scroll="auto"),
                Row(
                    [
                        btn_sebelumnya,
                        btn_selanjutnya,
                    ]
                ),
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
                        Text("Data Seragam Masuk", size=30, weight="bold"),
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
            ],
        ),
        margin=10,
    )
