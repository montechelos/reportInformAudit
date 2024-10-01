# Importamos dependencias y librerías
from flask import Flask, request, jsonify, send_file
from datetime import datetime
from queries import Queries
from reports import ReportG
import os
from datetime import datetime
import pandas as pd
from flask import jsonify, request, send_from_directory, url_for

# Instanciamos Flask para saber si lo estamos ejecutando de primera mano
app = Flask(__name__)

# Función para mostrar mensaje
def mensaje():
    print("Hola, este endpoint consiste en consultar a una base de datos en especifico, para poder descargar un reporte en excel con la ayuda de la libreria openpyxl")
    return 'Hola, este endpoint consiste en consultar a una base de datos en especifico, para poder descargar un reporte en excel con la ayuda de la libreria openpyxl'
# Ruta para validar las fechas y registrar el pago
@app.route("/consultaVentas", methods=["POST"])
def validarDb():
    data = request.get_json()

    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    base_datos = data.get('bdName')

    # Crear una lista para almacenar los datos recibidos
    arrdata = []

    # Almacenar datos en el arreglo
    arrdata.append(fecha_inicio)  # fecha_inicio está en la posición 0
    arrdata.append(fecha_fin)  # fecha_fin está en la posición 1
    arrdata.append(base_datos)  # base_datos está en la posición 2

    # Validamos que las fechas y demás parámetros sean válidos
    if not all(arrdata):
        return jsonify({"status": "error", "message": "Datos incompletos", "datos_enviados": arrdata}), 400

    # Convertir fechas a formato datetime para validar
    try:
        arrdata[0] = datetime.strptime(arrdata[0], "%Y-%m-%d")  
        arrdata[1] = datetime.strptime(arrdata[1], "%Y-%m-%d")    
    except ValueError:
        return jsonify({"status": "error", "message": "Formato de fecha incorrecto. Debe ser YYYY-MM-DD", "datos_enviados": arrdata}), 400

    # Validar que la fecha de inicio sea menor que la fecha de fin
    if arrdata[0] >= arrdata[1]:
        return jsonify({"status": "error", "message": "La fecha de inicio debe ser menor a la fecha de fin"}), 400

    # Conectarse a la base de datos y realizar la consulta
    try:
        queries_ins = Queries()
        generar_report = queries_ins.get_db_consult(arrdata)
        
        # Obtener el primer batch (bloque) para verificar que no venga vacios
        first_batch = next(generar_report, None)
        
        if not first_batch:
            return jsonify({"status": "error", "message": "No se encontraron ventas en el rango indicado de fechas"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

    # Generar el archivo Excel 
    try:
        report_g = ReportG()
        nombre_excel = report_g.generate_report_excel(arrdata, generar_report, first_batch)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
    # Generar la URL de descarga
    download_url = url_for('download_file', filename=nombre_excel, _external=True)
    return jsonify({"status": "success", "message": "Reporte generado con éxito", "url_descarga": download_url}), 200
    
@app.route('/reportes/<filename>', methods=['GET'])
def download_file(filename):
    """Ruta para descargar el archivo generado."""
    return send_from_directory('reportes', filename)  # Ajusta la ruta de acuerdo a tu estructura
    
# Manejo de errores de página no encontrada
@app.errorhandler(404)
def not_found(error):
    return jsonify({"status": "error", "message": "Página no encontrada", "mensaje": mensaje()}), 404

if __name__ == "__main__":
    mensaje()
    app.run(debug=True)
    
