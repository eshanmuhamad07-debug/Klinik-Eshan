from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="db_rawatinap"
)


@app.route('/')
def index():
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT transaksi.id_transaksi,
               pasien.nama,
               transaksi.total_biaya,
               transaksi.status_pembayaran,
               transaksi.tanggal
        FROM transaksi
        JOIN pasien ON transaksi.id_pasien = pasien.id_pasien
    """)
    data = cursor.fetchall()
    cursor.close()
    return render_template('form.html', data=data)



@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pasien")
    pasien = cursor.fetchall()

    if request.method == 'POST':
        id_pasien = request.form['id_pasien']
        total = request.form['total']
        status = request.form['status']
        tanggal = request.form['tanggal']

        sql = """
            INSERT INTO transaksi
            (id_pasien, total_biaya, status_pembayaran, tanggal)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (id_pasien, total, status, tanggal))
        db.commit()
        cursor.close()
        return redirect(url_for('index'))

    cursor.close()
    return render_template('tambah.html', pasien=pasien)



@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM transaksi WHERE id_transaksi=%s", (id,))
    data = cursor.fetchone()

    cursor.execute("SELECT * FROM pasien")
    pasien = cursor.fetchall()

    if request.method == 'POST':
        id_pasien = request.form['id_pasien']
        total = request.form['total']
        status = request.form['status']
        tanggal = request.form['tanggal']

        sql = """
            UPDATE transaksi SET
            id_pasien=%s,
            total_biaya=%s,
            status_pembayaran=%s,
            tanggal=%s
            WHERE id_transaksi=%s
        """
        cursor.execute(sql, (id_pasien, total, status, tanggal, id))
        db.commit()
        cursor.close()
        return redirect(url_for('index'))

    cursor.close()
    return render_template('edit.html', data=data, pasien=pasien)



@app.route('/hapus/<int:id>')
def hapus(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM transaksi WHERE id_transaksi=%s", (id,))
    db.commit()
    cursor.close()
    return redirect(url_for('index'))




@app.route('/pasien')
def pasien():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pasien")
    data_pasien = cursor.fetchall()
    cursor.close()
    return render_template('pasien.html', pasien=data_pasien)



if __name__ == '__main__':
    app.run(debug=True)
