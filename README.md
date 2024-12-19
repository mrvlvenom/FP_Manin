# Implementasi Program Deteksi ARP Spoofing Sederhana Berbasis Teknik Analisis Lalu Lintas Jaringan Secara Real-Time dalam Manajemen Insiden Respons
Final Project Mata Kuliah Manajemen Insiden Semester 5 Tahun 2024

## Anggota Kelompok :

| Nama Lengkap              | NRP        |
| --------------------      | ---------- |
| M. Januar Eko Wicaksono   | 5027221006 |
| Rahmad Aji Wicaksono      | 5027221034 |
| Ilhan Ahmad Syafa         | 5027221040 |

## Daftar isi

- [Preparation](#preparation)
- [Identification](#identification)
- [Containment](#containment)
- [Eradication](#Eradication)
- [Recovery](#recovery)
- [Lesson Learned](#lesson-learned)
- [Documentation](#doucmentation)

## Preparation
### *Setup* dan Instalasi GNS3
Ikuti langkah-langkah pada [Modul Jarkom - GNS3](https://github.com/lab-kcks/Modul-Jarkom/tree/master/Modul-GNS3)

### Buat Topologi Simulasi Jaringan
![image](https://github.com/mrvlvenom/FP_Manin/blob/main/img/Topologi.png)

### *Setup* *Router* dan *Server*
- Paradis (Router)
```auto eth0
iface eth0 inet dhcp

auto eth1
iface eth1 inet static
  address 192.232.1.1
  netmask 255.255.255.0

auto eth2
iface eth2 inet static
  address 192.232.2.1
  netmask 255.255.255.0

up iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE -s 192.232.0.0/16
```

- Armin (Web Server Terget)
```
auto eth0
iface eth0 inet static
  address 192.232.1.2
  netmask 255.255.255.0
  gateway 192.232.1.1

up echo nameserver 192.168.122.1 > /etc/resolv.conf
```

- Eren (Web Server)
```
auto eth0
iface eth0 inet static
  address 192.232.1.3
  netmask 255.255.255.0
  gateway 192.232.1.1

up echo nameserver 192.168.122.1 > /etc/resolv.conf
```

- Mikasa (Client Penyerang)
```
auto eth0
iface eth0 inet static
  address 192.232.1.4
  netmask 255.255.255.0
  gateway 192.232.1.1

up echo nameserver 192.168.122.1 > /etc/resolv.conf
```

- Zeke (Client Penyerang)
```
auto eth0
iface eth0 inet static
  address 192.232.1.5
  netmask 255.255.255.0
  gateway 192.232.1.1

up echo nameserver 192.168.122.1 > /etc/resolv.conf
```

Pastikan setiap *server* sudah terhubung dengan internet. Kita bisa mengeceknya dengan melakukan ping ke google, apabila terdapat respons maka *server* telah terhubung dengan internet.
![image](https://github.com/mrvlvenom/FP_Manin/blob/main/img/ping1.png)

### *Setup* Program pada *Web Server*
Lakukan instalasi berikut pada setiap *server*:
- Install Python: `sudo apt install python3 python3-pip python3-venv -y`
- Install pip: `sudo apt install python3-pip -y`
- Install scapy: `pip3 install scapy`

Kemudian buatlah suatu *file* python yang berisi program [berikut](https://github.com/mrvlvenom/FP_Manin/blob/main/arp-spooof-detector.py)

### *Setup* Pada *Client Penyerang*
Lakukan instalasi berikut pada device penyerang:
- Install dsniff: `sudo apt install dsniff`

## Identification
Skrip deteksi memantau lalu lintas jaringan secara real-time untuk mengidentifikasi anomali ARP Spoofing, seperti perubahan alamat MAC yang tidak sesuai. Ketika anomali terdeteksi, insiden dicatat secara detail, termasuk alamat IP, MAC Address, waktu kejadian.

### Setup Armin (Web Server)
Kemudian buatlah suatu *file* python pada Armin (Web Server Target) yang berisi program [berikut](https://github.com/mrvlvenom/FP_Manin/blob/main/arp-spooof-detector.py)

Kemudian jalankan command berikut:
`python3 [nama_program_python]`

Kemudian mendapatkan output sebagai berikut:
![image](https://github.com/mrvlvenom/FP_Manin/blob/main/img/4.png)

### Setup Mikasa dan Zeke (Client Penyerang)
Kemudian jalankan command berikut:
`arpspoof -i [interface] -t [IP target] -r [IP host/router]`

Dan Hasilnya seperti berikut:
![image](https://github.com/mrvlvenom/FP_Manin/blob/main/img/5.png)

### Hasil Pemantauan oleh Web Server
Pantau *server* yang menjadi target penyerangan, apabila muncul *alert* seperti gambar di bawah ini maka program detektor berjalan dengan baik. 
![image](https://github.com/mrvlvenom/FP_Manin/blob/main/img/6.png)

## Containment
Setelah serangan ARP Spoofing teridentifikasi, langkah containment diimplementasikan. Skrip secara otomatis memblokir alamat IP penyerang pada router Erangel untuk mencegah penyebaran serangan lebih lanjut ke perangkat lain dalam jaringan.

Kemudian jalankan command berikut:
`iptables -L -v`

kemudian menghasilkan sebagai berikut:
![image](https://github.com/mrvlvenom/FP_Manin/blob/main/img/7.png)

Setelah itu penyerang tidak bisa mengirimkan packet ke Web Server (Armin), seperti hasil dibawah ini:
![image](https://github.com/mrvlvenom/FP_Manin/blob/main/img/8.png)

Di lain sisi, client yang tidak menyerang bisa mengirimkan packet ke Web Server (Armin):
![image](https://github.com/mrvlvenom/FP_Manin/blob/main/img/9.png)

## Eradication
Setelah containment dilakukan, langkah eradication dilakukan dengan membersihkan jaringan dari paket ARP berbahaya. Skrip memastikan tidak ada cache ARP yang terinfeksi pada perangkat, menggunakan alat seperti perintah “ARP Flush” untuk membersihkan cache pada setiap node.
Kemudian jalankan command berikut:
`iptables -F`

untuk membersihkan penyerang yang sudah terdeteksi oleh web server. Kemudian bisa mengirimkan packet dengan normal:
![image](https://github.com/mrvlvenom/FP_Manin/blob/main/img/10.png)

## Recovery
Setelah jaringan dinyatakan aman, konfigurasi ulang dilakukan untuk memastikan jaringan kembali berfungsi normal. Perangkat yang sebelumnya terkena dampak serangan diperiksa dan dipastikan bebas dari jejak serangan.

## Lesson-Learned
Data dan log dari insiden ARP Spoofing dianalisis untuk mengidentifikasi kelemahan sistem yang memungkinkan serangan terjadi. Wawasan ini digunakan untuk memperkuat konfigurasi jaringan, mengembangkan kebijakan keamanan, dan meningkatkan kemampuan deteksi di masa depan

Dari program python tadi, hasil dari programnya akan dimasukkan ke dalam log.txt, seperti pada gambar:
![image](https://github.com/mrvlvenom/FP_Manin/blob/main/img/11.png)

## Documentation
Setiap langkah dalam respons insiden didokumentasikan dengan detail, mencakup identifikasi serangan, langkah-langkah mitigasi, serta rekomendasi untuk mencegah insiden serupa di masa mendatang. Dokumentasi ini menjadi pedoman bagi tim keamanan jaringan untuk penanganan insiden di masa yang akan datang. 
