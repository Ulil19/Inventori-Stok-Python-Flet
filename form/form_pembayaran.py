from flet import *
import mysql.connector
import datetime

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


# Fungsi untuk mengambil data pembayaran dari database
def ambil_data_pembayaran():
    query = """
    SELECT pb.pembayaran_id, p.nama_pemasok, pb.tanggal_pembayaran, 
           pb.jumlah_pembayaran, pb.metode_pembayaran, pb.keterangan
    FROM pembayaran pb
    JOIN pemasok p ON pb.pemasok_id = p.pemasok_id
    ORDER BY pb.pembayaran_id DESC
    """
    cursor.execute(query)
    return cursor.fetchall()


# Fungsi untuk mengambil data pemasok untuk dropdown
def ambil_data_pemasok():
    query = "SELECT pemasok_id, nama_pemasok FROM pemasok"
    cursor.execute(query)
    return cursor.fetchall()


def form_pembayaran(page: Page):
    data_pembayaran = ambil_data_pembayaran()
    daftar_pemasok = ambil_data_pemasok()

    baris_data_per_hal = 5
    hal_sekarang = 0

    # Inputan fields untuk pembayaran
    inputan_pencarian = TextField(label="Pencarian", width=300, autofocus=True)
    inputan_id_pembayaran = TextField(visible=False, width=300)
    inputan_pemasok_id = Dropdown(
        label="Pilih Pemasok",
        options=[
            dropdown.Option(str(pemasok[0]), pemasok[1]) for pemasok in daftar_pemasok
        ],
        width=300,
    )
    # debug
    print("Daftar opsi dropdown pemasok:")
    for pemasok in daftar_pemasok:
        print(f"ID: {pemasok[0]}, Nama: {pemasok[1]}")

    inputan_tanggal_pembayaran = TextField(
        label="Tanggal Pembayaran",
        width=300,
        hint_text="masukkan tanggal pembayaran",
        expand=True,
        read_only=True,
    )

    def change_date(e):
        if (
            inputan_tanggal_pembayaran_picker.value
        ):  # Pastikan ada nilai dari DatePicker
            try:
                tgl_baru = inputan_tanggal_pembayaran_picker.value
                inputan_tanggal_pembayaran.value = tgl_baru.strftime("%Y-%m-%d")
            except Exception as ex:
                inputan_tanggal_pembayaran.value = f"Error: {str(ex)}"
        else:
            inputan_tanggal_pembayaran.value = "Tanggal tidak dipilih!"
        inputan_tanggal_pembayaran.update()

    def date_picker_dismissed(e):
        if inputan_tanggal_pembayaran_picker.value:
            inputan_tanggal_pembayaran.value = (
                inputan_tanggal_pembayaran_picker.value.strftime("%Y-%m-%d")
            )
        else:
            inputan_tanggal_pembayaran.value = "Tanggal tidak dipilih!"
        inputan_tanggal_pembayaran.update()

    inputan_tanggal_pembayaran_picker = DatePicker(
        on_change=change_date,
        on_dismiss=date_picker_dismissed,
        first_date=datetime.datetime(1945, 1, 1),
        last_date=datetime.datetime(2050, 10, 1),
    )

    inputan_jumlah_pembayaran = TextField(label="Jumlah Pembayaran", width=300)
    inputan_metode_pembayaran = Dropdown(
        label="Metode Pembayaran",
        options=[
            dropdown.Option("Transfer"),
            dropdown.Option("Tunai"),
            dropdown.Option("Cek"),
        ],
        width=300,
    )

    inputan_keterangan = TextField(label="Keterangan", width=300)

    snack_bar_berhasil = SnackBar(Text("Operasi berhasil"), bgcolor="green")
    snack_bar_gagal = SnackBar(Text("Operasi gagal"), bgcolor="red")

    def format_rupiah(value):
        return f"Rp. {int(value):,}".replace(",", ".")

    # Fungsi untuk membersihkan form
    def bersihkan_form_entri(e=None):
        inputan_id_pembayaran.value = ""
        inputan_pemasok_id.value = ""
        inputan_tanggal_pembayaran.value = ""
        inputan_jumlah_pembayaran.value = ""
        inputan_metode_pembayaran.value = ""
        inputan_keterangan.value = ""

        inputan_id_pembayaran.update()
        inputan_pemasok_id.update()
        inputan_tanggal_pembayaran.update()
        inputan_jumlah_pembayaran.update()
        inputan_metode_pembayaran.update()
        inputan_keterangan.update()

    # Fungsi untuk mengisi data pembayaran masuk ke dalam form entri (edit data)
    def detail_data_pembayaran(e):
        # print("Data yang diterima dari tombol edit:", e.control.data)
        inputan_id_pembayaran.value = e.control.data[0]
        # Cari pemasok_id berdasarkan nama pemasok
        nama_pemasok = e.control.data[1]
        pemasok_id = None
        for pemasok in daftar_pemasok:
            if pemasok[1] == nama_pemasok:  # Cocokkan nama pemasok
                pemasok_id = str(pemasok[0])  # Ambil pemasok_id
                break

        inputan_pemasok_id.value = pemasok_id
        # print("Pemasok ID yang diatur:", inputan_pemasok_id.value)
        inputan_tanggal_pembayaran.value = e.control.data[2]
        inputan_jumlah_pembayaran.value = str(e.control.data[3])
        inputan_metode_pembayaran.value = e.control.data[4]
        inputan_keterangan.value = e.control.data[5]

        inputan_id_pembayaran.update()
        inputan_pemasok_id.update()
        inputan_tanggal_pembayaran.update()
        inputan_jumlah_pembayaran.update()
        inputan_metode_pembayaran.update()
        inputan_keterangan.update()

    # fungsi untuk menyimpan data pembayaran
    def simpan_data_pembayaran(e=None):
        try:
            if inputan_id_pembayaran.value:  # Update data
                query = """
                UPDATE pembayaran 
                SET pemasok_id = %s, tanggal_pembayaran = %s, jumlah_pembayaran = %s, 
                    metode_pembayaran = %s, keterangan = %s
                WHERE pembayaran_id = %s
                """
                values = (
                    inputan_pemasok_id.value,
                    inputan_tanggal_pembayaran.value,
                    inputan_jumlah_pembayaran.value,
                    inputan_metode_pembayaran.value,
                    inputan_keterangan.value,
                    inputan_id_pembayaran.value,
                )
            else:  # Insert data baru
                query = """
                INSERT INTO pembayaran (pemasok_id, tanggal_pembayaran, jumlah_pembayaran, 
                                        metode_pembayaran, keterangan) 
                VALUES (%s, %s, %s, %s, %s)
                """
                values = (
                    inputan_pemasok_id.value,
                    inputan_tanggal_pembayaran.value,
                    inputan_jumlah_pembayaran.value,
                    inputan_metode_pembayaran.value,
                    inputan_keterangan.value,
                )
            cursor.execute(query, values)
            koneksi_db.commit()
            print(cursor.rowcount, "Data disimpan!")

            data_pembayaran = ambil_data_pembayaran()
            nonlocal filtered_data_pembayaran
            filtered_data_pembayaran = data_pembayaran

            update_baris_data_pembayaran()

            snack_bar_berhasil.open = True
            snack_bar_berhasil.update()
            bersihkan_form_entri()
        except Exception as e:
            print(e)
            print("Ada yang error!")

    # Fungsi untuk menghapus data pembayaran
    def hapus_data_pembayaran(e):
        try:
            sql = "DELETE FROM pembayaran WHERE pembayaran_id = %s"
            val = (e.control.data,)
            cursor.execute(sql, val)
            koneksi_db.commit()
            print(cursor.rowcount, "Data dihapus!")

            data_pembayaran = ambil_data_pembayaran()
            nonlocal filtered_data_pembayaran
            filtered_data_pembayaran = data_pembayaran

            update_baris_data_pembayaran()

            snack_bar_berhasil.open = True
            snack_bar_berhasil.update()
            bersihkan_form_entri()
        except Exception as e:
            print(e)
            print("Ada yang error!")

    # variabel untuk menyimpan data pembayaran yang difilter
    filtered_data_pembayaran = data_pembayaran

    # fungsi untuk memfilter data pembayaran berdasarkan pencarian
    def filter_pembayaran(e):
        data_pembayaran = ambil_data_pembayaran()

        query_pencarian = inputan_pencarian.value
        nonlocal filtered_data_pembayaran
        filtered_data_pembayaran = [
            pembayaran_kolom
            for pembayaran_kolom in data_pembayaran
            if query_pencarian in pembayaran_kolom[2]
        ]
        update_baris_data_pembayaran()

    # Menghubungkan fungsi filter dengan perubahan nilai di pencarian
    inputan_pencarian.on_change = filter_pembayaran

    # Fungsi untuk membuat DataRow berdasarkan data pembayaran
    def update_baris_data_pembayaran():
        nonlocal filtered_data_pembayaran
        index_mulai = hal_sekarang * baris_data_per_hal
        index_selesai = index_mulai + baris_data_per_hal
        hal_data = filtered_data_pembayaran[index_mulai:index_selesai]
        baris_data_pembayaran = [
            DataRow(
                cells=[
                    DataCell(Text(str(index_mulai + i + 1))),
                    DataCell(Text(pembayaran_kolom[1])),
                    DataCell(Text(pembayaran_kolom[2])),
                    DataCell(Text(format_rupiah(pembayaran_kolom[3]))),
                    DataCell(Text(pembayaran_kolom[4])),
                    DataCell(Text(pembayaran_kolom[5])),
                    DataCell(
                        Row(
                            [
                                IconButton(
                                    "edit",
                                    icon_color="grey",
                                    data=pembayaran_kolom,  # Pastikan data lengkap
                                    on_click=detail_data_pembayaran,
                                ),
                                IconButton(
                                    "delete",
                                    icon_color="red",
                                    data=pembayaran_kolom[0],  # Pastikan data lengkap
                                    on_click=hapus_data_pembayaran,
                                ),
                            ]
                        )
                    ),
                ]
            )
            for i, pembayaran_kolom in enumerate(hal_data)
        ]

        tabel_data_pembayaran.rows = baris_data_pembayaran
        tabel_data_pembayaran.update()

    baris_data_pembayaran = [
        DataRow(
            cells=[
                DataCell(Text(str(i + 1))),
                DataCell(Text(pembayaran_kolom[1])),
                DataCell(Text(pembayaran_kolom[2])),
                DataCell(Text(format_rupiah(pembayaran_kolom[3]))),
                DataCell(Text(pembayaran_kolom[4])),
                DataCell(Text(pembayaran_kolom[5])),
                DataCell(
                    Row(
                        [
                            IconButton(
                                "edit",
                                icon_color="grey",
                                data=pembayaran_kolom,  # Pastikan data lengkap
                                on_click=detail_data_pembayaran,
                            ),
                            IconButton(
                                "delete",
                                icon_color="red",
                                data=pembayaran_kolom[0],  # Pastikan data lengkap
                                on_click=hapus_data_pembayaran,
                            ),
                        ]
                    )
                ),
            ]
        )
        for i, pembayaran_kolom in enumerate(
            filtered_data_pembayaran[:baris_data_per_hal]
        )
    ]
    tabel_data_pembayaran = DataTable(
        columns=[
            DataColumn(Text("No")),
            DataColumn(Text("Nama Pemasok")),
            DataColumn(Text("Tanggal Pembayaran")),
            DataColumn(Text("Jumlah Pembayaran")),
            DataColumn(Text("Metode Pembayaran")),
            DataColumn(Text("Keterangan")),
            DataColumn(Text("Aksi")),
        ],
        rows=baris_data_pembayaran,
        width="auto",
    )

    # Kontrol untuk tombol navigasi pagination
    def pergi_hal_sebelumnya(e):
        nonlocal hal_sekarang
        if hal_sekarang > 0:
            hal_sekarang -= 1
            update_baris_data_pembayaran()

    def pergi_hal_selanjutnya(e):
        nonlocal hal_sekarang
        if (hal_sekarang + 1) * baris_data_per_hal < len(filtered_data_pembayaran):
            hal_sekarang += 1
            update_baris_data_pembayaran()

    # Tombol navigasi pagination
    btn_sebelumnya = ElevatedButton("Sebelumnya", on_click=pergi_hal_sebelumnya)
    btn_selanjutnya = ElevatedButton("Selanjutnya", on_click=pergi_hal_selanjutnya)

    # membuat bagian kiri dengan form
    form_kiri = Container(
        Column(
            controls=[
                Text("Data Pembayaran", size=14, weight="bold"),
                inputan_id_pembayaran,
                Text("Nama Pemasok"),
                inputan_pemasok_id,
                Text("Tanggal Pembayaran"),
                Row(
                    [
                        inputan_tanggal_pembayaran,
                        inputan_tanggal_pembayaran_picker,
                        IconButton(
                            icon=icons.CALENDAR_MONTH,
                            icon_color="blue",
                            on_click=lambda _: inputan_tanggal_pembayaran_picker.pick_date(),
                        ),
                    ],
                ),
                Text("Jumlah Pembayaran"),
                inputan_jumlah_pembayaran,
                Text("Metode Pembayaran"),
                inputan_metode_pembayaran,
                Text("Keterangan"),
                inputan_keterangan,
                Row(
                    controls=[
                        ElevatedButton("Simpan", on_click=simpan_data_pembayaran),
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

    # membuat bagian kanan dengan search fields dan tabel
    form_kanan = Container(
        Column(
            controls=[
                Text("Data Pembayaran", size=14, weight="bold"),
                Row(controls=[inputan_pencarian]),
                Row(controls=[tabel_data_pembayaran], scroll="auto"),
                Row(
                    controls=[
                        btn_sebelumnya,
                        btn_selanjutnya,
                    ],
                ),
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
                            name=icons.PAYMENT_ROUNDED,
                            size=50,
                            color=colors.BLUE_400,
                        ),
                        Text("Pembayaran", size=30, weight="bold"),
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
