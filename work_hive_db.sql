DROP TABLE IF EXISTS lamaran;
DROP TABLE IF EXISTS lowongan;

CREATE TABLE lowongan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_perusahaan VARCHAR(100),
    posisi VARCHAR(100),
    gambar VARCHAR(255) DEFAULT 'lowongan_kerja.jpg'
);

CREATE TABLE lamaran (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_lengkap VARCHAR(100),
    jurusan VARCHAR(100),
    sekolah VARCHAR(100),
    jenis_kelamin VARCHAR(20),
    perusahaan VARCHAR(100),
    status VARCHAR(50) DEFAULT 'Pending'
);

INSERT INTO lowongan (nama_perusahaan, posisi) VALUES 
('Alfamart', 'Kasir'),
('Indomaret', 'Pramuniaga'),
('Superindo', 'Gudang'),
('Lawson', 'Crew Store'),
('Danone', 'Admin'),
('KFC', 'Waiters');