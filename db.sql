CREATE TABLE seragam (
    seragam_id INT AUTO_INCREMENT PRIMARY KEY,
    nama_seragam VARCHAR(100) NOT NULL,
    jenis VARCHAR(50),
    ukuran VARCHAR(10),
    tipe VARCHAR(50),
    harga DECIMAL(10, 2),
    stok INT DEFAULT 0
);

CREATE TABLE pemasok (
    pemasok_id INT AUTO_INCREMENT PRIMARY KEY,
    nama_pemasok VARCHAR(100) NOT NULL,
    alamat VARCHAR(255),
    no_telepon VARCHAR(20)
);

CREATE TABLE seragam_masuk (
    masuk_id INT AUTO_INCREMENT PRIMARY KEY,
    seragam_id INT NOT NULL,
    pemasok_id INT NOT NULL,
    tanggal_masuk DATE NOT NULL,
    jumlah_masuk INT NOT NULL,
    jumlah_tidak_sesuai INT DEFAULT 0,
    jumlah_valid INT GENERATED ALWAYS AS (jumlah_masuk - jumlah_tidak_sesuai) STORED,
    FOREIGN KEY (seragam_id) REFERENCES seragam(seragam_id),
    FOREIGN KEY (pemasok_id) REFERENCES pemasok(pemasok_id)
);
CREATE TABLE seragam_tidak_sesuai (
    tidak_sesuai_id INT AUTO_INCREMENT PRIMARY KEY,
    masuk_id INT NOT NULL,
    jumlah_tidak_sesuai INT NOT NULL,
    keterangan VARCHAR(255),
    status ENUM('Dikembalikan', 'Diterima') NOT NULL,
    FOREIGN KEY (masuk_id) REFERENCES seragam_masuk(masuk_id)
);
CREATE TABLE pembayaran (
    pembayaran_id INT AUTO_INCREMENT PRIMARY KEY,
    pemasok_id INT NOT NULL,
    tanggal_pembayaran DATE NOT NULL,
    jumlah_pembayaran DECIMAL(10, 2) NOT NULL,
    metode_pembayaran ENUM('Transfer', 'Tunai', 'Cek') NOT NULL,
    keterangan VARCHAR(255),
    FOREIGN KEY (pemasok_id) REFERENCES pemasok(pemasok_id)
);

CREATE TABLE user (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    hak_akses VARCHAR(20) NOT NULL
);

INSERT INTO user (username, password, hak_akses) 
VALUES 
    ('admin', '123', 'Admin');

-- Data untuk tabel seragam
INSERT INTO seragam (nama_seragam, jenis, ukuran, tipe, harga, stok)
VALUES 
    ('Seragam SMA', 'Kemeja Osis', "L", "Pria", 500000, 10),
    ('Seragam SMA', 'Kemeja Pramuka', "L", "Wanita", 500000, 10);


-- Data untuk tabel pemasok
INSERT INTO pemasok (nama_pemasok, alamat, no_telepon)
VALUES 
    ('PT Pemasok Seragam', 'Jl. Mawar No. 10', '081234567890'),
    ('CV Seragam Indonesia', 'Jl. Melati No. 5', '082345678901');

-- Data untuk tabel seragam_masuk
INSERT INTO seragam_masuk (seragam_id, pemasok_id, tanggal_masuk, jumlah_masuk, jumlah_tidak_sesuai)
VALUES 
    (1, 1, '2025-01-01', 20, 2),
    (2, 2, '2025-01-02', 15, 1);

-- Data untuk tabel seragam_tidak_sesuai
INSERT INTO seragam_tidak_sesuai (masuk_id, jumlah_tidak_sesuai, keterangan, status)
VALUES 
    (1, 2, 'Ukuran tidak sesuai', 'Dikembalikan'),
    (2, 1, 'Jahitan rusak', 'Dikembalikan');

-- Data untuk tabel pembayaran
INSERT INTO pembayaran (pemasok_id, tanggal_pembayaran, jumlah_pembayaran, metode_pembayaran, keterangan)
VALUES 
    (1, '2025-01-05', 1500000, 'Transfer', 'Pembayaran termin 1'),
    (2, '2025-01-06', 2000000, 'Tunai', 'Pembayaran lunas');

