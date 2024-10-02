from flask import Flask, request, jsonify, send_from_directory, url_for
from datetime import datetime
from queries import Queries
from reports import ReportG
import os
from dotenv import load_dotenv

load_dotenv()  # Cargar variables de entorno desde .env

app = Flask(__name__)

def mensaje():
    print("✅✅REPORTE PROMESAS✅✅")
    return 'Hola, este endpoint consiste en consultar a una base de datos específica, para poder descargar un reporte en excel con la ayuda de la librería openpyxl'

@app.route("/consultaVentas", methods=["POST"])
def validarDb():
    data = request.get_json()

    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    base_datos = data.get('bdName')

    arrdata = [fecha_inicio, fecha_fin, base_datos]

    if not all(arrdata):
        return jsonify({"status": "error", "message": "Datos incompletos", "datos_enviados": arrdata}), 400

    try:
        arrdata[0] = datetime.strptime(arrdata[0], "%Y-%m-%d")  
        arrdata[1] = datetime.strptime(arrdata[1], "%Y-%m-%d")    
    except ValueError:
        return jsonify({"status": "error", "message": "Formato de fecha incorrecto. Debe ser YYYY-MM-DD", "datos_enviados": arrdata}), 400

    if arrdata[0] >= arrdata[1]:
        return jsonify({"status": "error", "message": "La fecha de inicio debe ser menor a la fecha de fin"}), 400

    try:
        queries_ins = Queries()
        generar_report = queries_ins.get_db_consult(arrdata)
        first_batch = next(generar_report, None)
        
        if not first_batch:
            return jsonify({"status": "error", "message": "No se encontraron ventas en el rango indicado de fechas"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

    try:
        report_g = ReportG()
        nombre_excel = report_g.generate_report_excel(arrdata, generar_report, first_batch)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
    download_url = url_for('download_file', filename=nombre_excel, _external=True)
    return jsonify({"status": "success", "message": "Reporte generado con éxito", "url_descarga": download_url}), 200
    
@app.route('/reportes/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory('reportes', filename)

@app.errorhandler(404)
def not_found(error):
    return jsonify({"status": "error", "message": "Página no encontrada", "mensaje": mensaje()}), 404

if __name__ == "__main__":
    mensaje()
    app.run(debug=True)
