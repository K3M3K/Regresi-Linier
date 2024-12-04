from flask import Flask, render_template, request, jsonify
import numpy as np
import mysql.connector
import matplotlib
import matplotlib.pyplot as plt
import os

# Menggunakan backend non-GUI untuk Matplotlib
matplotlib.use('Agg')

# Tentukan folder static
app = Flask(__name__, static_folder='C:/Users/Administrator/Documents/TUGAS BESAR METODE NUMERIK/project/static')

# Koneksi ke database MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",        # Username default XAMPP
    password="",        # Kosong jika belum diatur
    database="metnum"
)

# Fungsi untuk menghitung regresi linier
def regresi_linier(x, y):
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    b1 = sum((x - x_mean) * (y - y_mean)) / sum((x - x_mean)**2)
    b0 = y_mean - b1 * x_mean
    y_pred = b0 + b1 * x
    r2 = 1 - sum((y - y_pred)**2) / sum((y - y_mean)**2)
    return b0, b1, r2, y_pred

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    # Mengambil data dari form
    x_values = request.form['x_values']
    y_values = request.form['y_values']

    # Memisahkan nilai x dan y yang dipisahkan dengan koma
    try:
        x = np.array([float(val) for val in x_values.split(',')], dtype=float)
        y = np.array([float(val) for val in y_values.split(',')], dtype=float)

        if len(x) != len(y):
            return jsonify({'error': 'Jumlah nilai x dan y harus sama'}), 400

        # Hitung regresi linier
        b0, b1, r2, y_pred = regresi_linier(x, y)

        # Pastikan folder 'static' ada
        static_folder = 'C:/Users/Administrator/Documents/TUGAS BESAR METODE NUMERIK/project/static'
        if not os.path.exists(static_folder):
            os.makedirs(static_folder)

        # Plot hasil regresi
        plt.figure()
        plt.scatter(x, y, color='blue', label='Data Aktual')  # Titik data
        plt.plot(x, y_pred, color='red', label=f'Garis Regresi: y = {b0:.4f} + {b1:.4f}x')  # Garis regresi
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Hasil Regresi Linier')
        plt.legend()
        plt.grid()

        # Menyimpan plot ke file di folder static
        plot_path = os.path.join(static_folder, 'regresi_plot.png')
        plt.savefig(plot_path)
        plt.close()

        # Mengembalikan hasil regresi dan plot ke client
        return render_template('index.html', 
                               b0=b0, b1=b1, r2=r2, 
                               plot_url=f'/static/regresi_plot.png')
    except ValueError:
        return jsonify({'error': 'Pastikan input angka dipisahkan dengan koma'}), 400

if __name__ == '__main__':
    app.run(debug=True)
