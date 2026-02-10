from flask import Flask, render_template, request, redirect, session
import mysql.connector
from datetime import date

app = Flask(__name__)
app.secret_key = "klinik123"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="klinik_rawat_inap"
)

# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM user WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()

        if user:
            session["role"] = user["role"]
            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "role" not in session:
        return redirect("/")
    return render_template("dashboard.html", role=session["role"])


# ================= PASIEN =================
@app.route("/pasien", methods=["GET", "POST"])
def pasien():
    if "role" not in session:
        return redirect("/")

    if request.method == "POST":
        nik = request.form["nik"]
        nama = request.form["nama"]
        jk = request.form["jk"]
        alamat = request.form["alamat"]

        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO pasien (nik, nama, no_rekmed, jk, alamat, tgl_daftar)
            VALUES (%s,%s,%s,%s,%s,CURDATE())
            """,
            (nik, nama, "RM"+nik[-3:], jk, alamat)
        )
        db.commit()

    return render_template("pasien.html")


# ================= REKAM MEDIS =================
@app.route("/rekam_medis", methods=["GET", "POST"])
def rekam_medis():
    if "role" not in session:
        return redirect("/")

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pasien")
    pasien = cursor.fetchall()

    cursor.execute("SELECT * FROM dokter")
    dokter = cursor.fetchall()

    if request.method == "POST":
        nik = request.form["nik"]
        keluhan = request.form["keluhan"]
        diagnosis = request.form["diagnosis"]
        id_dokter = request.form["id_dokter"]

        cursor.execute("""
            INSERT INTO detail_rekmed (nik, keluhan, diagnosis, id_dokter)
            VALUES (%s,%s,%s,%s)
        """, (nik, keluhan, diagnosis, id_dokter))
        db.commit()

    return render_template("rekam_medis.html", pasien=pasien, dokter=dokter)


# ================= TRANSAKSI =================


@app.route('/transaksi', methods=['GET', 'POST'])
def transaksi():
    if "role" not in session:
        return redirect("/")

    cursor = db.cursor(dictionary=True)

    # ambil pasien
    cursor.execute("SELECT nik FROM pasien")
    pasien = cursor.fetchall()

    # ambil obat
    cursor.execute("SELECT id_obat, nama, harga FROM obat")
    obat = cursor.fetchall()

    if request.method == 'POST':
        nik = request.form['nik']
        id_obat = request.form['id_obat']
        jumlah = int(request.form['jumlah'])

        # ambil data obat
        cursor.execute(
            "SELECT nama, harga FROM obat WHERE id_obat=%s",
            (id_obat,)
        )
        data_obat = cursor.fetchone()

        nama = data_obat['nama']
        harga = data_obat['harga']
        total = harga * jumlah

        cursor.execute("""
            INSERT INTO transaksi 
            (nik, id_obat, nama, jumlah, total, tanggal)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (nik, id_obat, nama_obat, jumlah, total, date.today()))

        db.commit()
        return redirect('/transaksi')

    return render_template(
        'transaksi.html',
        pasien=pasien,
        obat=obat
    )


@app.route('/riwayat_transaksi')
def riwayat_transaksi():
    if "role" not in session:
        return redirect("/")

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            t.id_transaksi,
            t.nik,
            o.nama_obat,
            o.harga,
            t.jumlah,
            t.total,
            t.tanggal
        FROM transaksi t
        JOIN obat o ON t.id_obat = o.id_obat
        ORDER BY t.tanggal DESC
    """)

    riwayat = cursor.fetchall()

    return render_template(
        'riwayat_transaksi.html',
        riwayat=riwayat
    )

app.run(debug=True)
