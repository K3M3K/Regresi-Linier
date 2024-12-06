import os
from flask import Flask, render_template, request, jsonify
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import mysql.connector  # Mengimport konektor MySQL

# Gunakan backend non-GUI untuk Matplotlib
matplotlib.use('Agg')

# Path absolut untuk static dan templates
STATIC_FOLDER = r'C:\Users\Administrator\Documents\TUGAS BESAR METODE NUMERIK\project\static'
TEMPLATES_FOLDER = r'C:\Users\Administrator\Documents\TUGAS BESAR METODE NUMERIK\templates'

# Inisialisasi Flask
app = Flask(__name__, static_folder=STATIC_FOLDER, template_folder=TEMPLATES_FOLDER)

# Koneksi ke database MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",        # Username default XAMPP
        password="",        # Kosong jika belum diatur
        database="metnum"   # Nama database Anda
    )

# Fungsi regresi linier
def regresi_linier(x, y):
    x = x.reshape(-1, 1)
    y = y.reshape(-1, 1)
    
    # Model regresi
    model = LinearRegression()
    model.fit(x, y)
    y_pred = model.predict(x)
    
    # Parameter regresi
    b1 = model.coef_[0][0]
    b0 = model.intercept_[0]
    
    # Error metrics
    r2 = r2_score(y, y_pred)
    mse = mean_squared_error(y, y_pred)
    rmse = np.sqrt(mse)
    
    # Statistik deskriptif
    stats = {
        "x_mean": np.mean(x),
        "y_mean": np.mean(y),
        "x_median": np.median(x),
        "y_median": np.median(y),
        "x_std": np.std(x),
        "y_std": np.std(y),
    }
    
    return b0, b1, r2, mse, rmse, y_pred.flatten(), stats


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Ambil data dari form
        x_values = request.form['x_values']
        y_values = request.form['y_values']

        # Parsing ke array
        x = np.array([float(val) for val in x_values.split(',')])
        y = np.array([float(val) for val in y_values.split(',')])

        if len(x) != len(y):
            return jsonify({'error': 'Jumlah nilai x dan y harus sama'}), 400

        # Hitung regresi linier
        b0, b1, r2, mse, rmse, y_pred, stats = regresi_linier(x, y)

        # Cek folder static
        if not os.path.exists(STATIC_FOLDER):
            os.makedirs(STATIC_FOLDER)

        # Plot hasil regresi
        regresi_plot_path = os.path.join(STATIC_FOLDER, 'regresi_plot.png')
        plt.figure()
        plt.scatter(x, y, color='blue', label='Data Aktual')
        plt.plot(x, y_pred, color='red', label=f'Garis Regresi: y = {b0:.4f} + {b1:.4f}x')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Hasil Regresi Linier')
        plt.legend()
        plt.grid()
        plt.savefig(regresi_plot_path)
        plt.close()

        # Plot residuals
        residuals = y - y_pred
        residuals_plot_path = os.path.join(STATIC_FOLDER, 'residuals_plot.png')
        plt.figure()
        plt.scatter(x, residuals, color='purple', label='Residuals')
        plt.axhline(y=0, color='red', linestyle='--', label='y = 0')
        plt.xlabel('x')
        plt.ylabel('Residuals')
        plt.title('Grafik Residuals')
        plt.legend()
        plt.grid()
        plt.savefig(residuals_plot_path)
        plt.close()

        # Simpan hasil ke database (opsional)
        save_results_to_db(b0, b1, r2, mse, rmse)

        # Kirim hasil ke HTML
        return render_template(
            'index.html',
            b0=round(b0, 4),
            b1=round(b1, 4),
            r2=round(r2, 4),
            mse=round(mse, 4),
            rmse=round(rmse, 4),
            stats=stats,
            regresi_plot_url='/static/regresi_plot.png',
            residuals_plot_url='/static/residuals_plot.png'
        )
    except ValueError:
        return jsonify({'error': 'Input tidak valid. Pastikan nilai dipisahkan dengan koma'}), 400


# Fungsi untuk menyimpan hasil ke database
def save_results_to_db(b0, b1, r2, mse, rmse):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO hasil_regresi (b0, b1, r2, mse, rmse) VALUES (%s, %s, %s, %s, %s)",
            (b0, b1, r2, mse, rmse)
        )
        db.commit()
        cursor.close()
        db.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")


if __name__ == '__main__':
    app.run(debug=True)
