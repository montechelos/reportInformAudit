from flask import Flask, request, jsonify, send_from_directory, url_for
from datetime import datetime
from queries import Queries
from reports import ReportG
import os
from dotenv import load_dotenv

load_dotenv()  # Cargar las variables de entorno desde el archivo .env (como credenciales de base de datos, rutas, etc.)

app = Flask(__name__)  # Inicializar la aplicación Flask

@app.route('/')
def saludo():
    """Función que devuelve un saludo cuando accedes a la raíz de la aplicación."""
    return "✅✅REPORTE PROMESAS✅✅"

@app.route("/consulta_promesas", methods=["POST"])
def validarDb():
    """
    Endpoint que valida la información enviada, realiza una consulta a la base de datos y genera un reporte.
    """
    # Obtener los datos enviados en el cuerpo de la solicitud en formato JSON
    data = request.get_json()

    # Extraer las fechas y el nombre de la base de datos del JSON
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    base_datos = data.get('bdName')

    # Lista con los datos a utilizar para la consulta y reporte
    arrdata = [fecha_inicio, fecha_fin, base_datos]
    
    # Validaciones de los campos
    if not fecha_inicio:
        return {"status": "error", "message": "La fecha de inicio es requerida."}, 400
    if not fecha_fin:
        return {"status": "error", "message": "La fecha de fin es requerida."}, 400
    if not base_datos:
        return {"status": "error", "message": "El nombre de la base de datos es requerido."}, 400
    
    # Convierte las fechas de cadena a objeto de fecha, manejando posibles errores de formato
    try:
        fecha_ini_date = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_date = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    except ValueError:
        return {"status": "error", "message": "Formato de fecha incorrecto. Debe ser YYYY-MM-DD."}, 400

    # Validar que la fecha de inicio no sea posterior a la fecha de fin
    if fecha_ini_date > fecha_fin_date:
        return {"status": "error", "message": "La fecha de inicio debe ser anterior a la fecha de fin."}, 400

    # Verificar que las fechas no sean mayores a la fecha actual
    today = datetime.now().date()
    if fecha_ini_date > today or fecha_fin_date > today:
        return {"status": "error", "message": "Las fechas no pueden ser mayores a la fecha actual."}, 400

    # Realiza la consulta a la base de datos utilizando Queries
    try:
        queries_ins = Queries()  # Instancia de la clase Queries
        generar_report = queries_ins.get_db_consult(arrdata)  # Llamar a la función que obtiene la consulta en la base de datos
        first_batch = next(generar_report, None)  # Obtener el primer lote de registros
        
        if not first_batch:
            # Si no hay registros, retornar un mensaje de error
            return jsonify({"status": "error", "message": "No se encontraron Promesas en el rango indicado de fechas"}), 400

    except Exception as e:
        # En caso de error en la consulta, retornar el mensaje del error
        return jsonify({"status": "error", "message": str(e)}), 400

    # Genera el reporte en Excel
    try:
        report_g = ReportG()  # Instancia de la clase ReportG
        # Generar el reporte en Excel y obtener el nombre del archivo y el total de registros
        nombre_excel, total_registros = report_g.generate_report_excel(arrdata, generar_report, first_batch)
    except Exception as e:
        # Si ocurre algún error en la generación del reporte, retornar el mensaje del error
        return jsonify({"status": "error", "message": str(e)}), 500
    
    # Crear la URL de descarga para el reporte generado
    download_url = url_for('download_file', filename=nombre_excel, _external=True)  # Correcto: solo el nombre del archivo
    # Retornar una respuesta exitosa con la URL para descargar el archivo y el total de registros
    return jsonify({"status": "success", "message": "Reporte generado con éxito", "url_descarga": download_url, "total_registros": total_registros}), 200

@app.route('/reportes/<filename>', methods=['GET'])
def download_file(filename):
    """
    Endpoint para descargar un archivo específico desde la carpeta 'reportes'.
    """
    return send_from_directory('reportes', filename)

@app.errorhandler(404)
def not_found(error):
    """
    Manejador de error 404, cuando una página no es encontrada.
    """
    return jsonify({"status": "error", "message": "Página no encontrada", "mensaje": saludo()}), 404

if __name__ == "__main__":
    # Ejecutar la aplicación Flask en modo debug
    app.run(debug=True)