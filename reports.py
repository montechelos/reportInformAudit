from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font
from datetime import datetime
import os
from collections import defaultdict

class ReportG:
    def generate_report_excel(self, data, generar_report, first_batch):
        # Extraigo las fechas y el nombre de la base de datos de los datos proporcionados
        fecha_inicio, fecha_fin, base_datos = data

        # Creo un nuevo libro de trabajo de Excel
        wb = Workbook()
        wb.remove(wb.active)  # Elimino la hoja predeterminada que se crea al iniciar

        # Uso defaultdict para almacenar las ventas agrupadas por fecha
        ventas_por_fecha = defaultdict(list)

        # Procesar el primer bloque de datos
        for venta in first_batch:
            # Formateo la fecha en el formato deseado
            fecha = venta['fecha'].strftime('%Y-%m-%d')
            # Agrego la venta a la lista correspondiente a su fecha
            ventas_por_fecha[fecha].append([
                venta['id'],                     # ID de la venta
                fecha,                           # Fecha de la venta
                venta['monto'],                  # Monto de la venta
                venta['tipo_promesa'],           # Tipo de promesa
                venta['estado'],                 # Estado de la venta
                venta['cliente_id'],             # ID del cliente
                venta.get('nombre_cliente', ''), # Nombre del cliente (opcional)
                venta.get('email_cliente', ''),  # Email del cliente (opcional)
                venta.get('cedula', '')          # Cédula del cliente (opcional)
            ])

        # Procesar los bloques restantes de datos del generador
        for todas_ventas in generar_report:
            for venta in todas_ventas:
                fecha = venta['fecha'].strftime('%Y-%m-%d')
                ventas_por_fecha[fecha].append([
                    venta['id'],
                    fecha,
                    venta['monto'],
                    venta['tipo_promesa'],
                    venta['estado'],
                    venta['cliente_id'],
                    venta.get('nombre_cliente', ''),
                    venta.get('email_cliente', ''),
                    venta.get('cedula', '')
                ])

        # Aseguro que la carpeta 'reportes' exista
        os.makedirs('reportes', exist_ok=True)

        # Creo una hoja por cada fecha única con ventas
        total_registros = 0  # Inicializo un contador de registros
        for fecha, ventas in ventas_por_fecha.items():
            ws = wb.create_sheet(title=fecha)  # Creo una nueva hoja para cada fecha
            # Establezco los encabezados de las columnas
            headers = ['ID VENTA', 'FECHA', 'MONTO', 'TIPO DE PROMESA', 'ESTADO', 'ID CLIENTE', 'NOMBRE CLIENTE', 'EMAIL CLIENTE', 'CEDULA']
            ws.append(headers)
            
            # Aplico estilos a los encabezados
            for col in range(1, len(headers) + 1):
                cell = ws.cell(row=1, column=col)  # Accedo a la celda del encabezado
                cell.fill = PatternFill(start_color='000000', end_color='000000', fill_type='solid')  # Fondo negro
                cell.font = Font(color='FFFFFF', bold=True)  # Texto blanco y en negrita

            # Agrego todas las ventas para esa fecha en la hoja
            for venta in ventas:
                ws.append(venta)  # Agrego la venta a la hoja
                total_registros += 1  # Incremento el contador por cada venta

        # Guardar el archivo Excel con un nombre que incluye la fecha y la base de datos
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # Formateo la fecha y hora actual
        nombre_excel = f"reporte_ventas_{base_datos}_{timestamp}.xlsx"  # Defino el nombre del archivo
        ruta = os.path.join('reportes', nombre_excel)  # Especifico la ruta donde guardar el archivo
        wb.save(ruta)  # Guardo el archivo

        return nombre_excel, total_registros  # Retorno el nombre del archivo y el conteo de registros
