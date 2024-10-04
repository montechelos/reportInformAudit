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

        # Uso defaultdict para almacenar las promessas agrupadas por fecha
        promesas_por_fecha = defaultdict(list)

        # Procesar el primer bloque de datos
        for promesa in first_batch:
            # Formateo la fecha en el formato deseado
            fecha = promesa['fecha'].strftime('%Y-%m-%d')
            # Agrego la promesaa la lista correspondiente a su fecha
            promesas_por_fecha[fecha].append([
                promesa['id'],                     # ID de la promesa
                fecha,                           # Fecha de la promesaa
                promesa['monto'],                  # Monto de la promesa
                promesa['tipo_promesa'],           # Tipo de promesa
                promesa['estado'],                 # Estado de la promesa
                promesa.get('cedula', ''),        # Cédula del cliente 
                promesa.get('nombre_cliente', ''), # Nombre del cliente 
                promesa.get('email_cliente', '')  # Email del cliente 
                
            ])

        # Procesar los bloques restantes de datos del generador
        for todas_promesas in generar_report:
            for promesa in todas_promesas:
                fecha = promesa['fecha'].strftime('%Y-%m-%d')
                promesas_por_fecha[fecha].append([
                   promesa['id'],
                    fecha,
                    promesa['monto'],
                    promesa['tipo_promesa'],
                    promesa['estado'],
                    promesa.get('cedula', ''),
                    promesa.get('nombre_cliente', ''),
                    promesa.get('email_cliente', '')
                    
                ])

        # Aseguro que la carpeta 'reportes' exista
        os.makedirs('reportes', exist_ok=True)

        # Creo una hoja por cada fecha única con promesa
        total_registros = 0  # Inicializo un contador de registros
        for fecha, promesas in promesas_por_fecha.items():
            ws = wb.create_sheet(title=fecha)  # Creo una nueva hoja para cada fecha
            # Establezco los encabezados de las columnas
            headers = ['ID PROMESA', 'FECHA', 'MONTO', 'TIPO DE PROMESA', 'ESTADO',  'CEDULA','NOMBRE CLIENTE', 'EMAIL CLIENTE']
            ws.append(headers)
            
            # Aplico estilos a los encabezados
            for col in range(1, len(headers) + 1):
                cell = ws.cell(row=1, column=col)  # Accedo a la celda del encabezado
                cell.fill = PatternFill(start_color='000000', end_color='000000', fill_type='solid')  # Fondo negro
                cell.font = Font(color='FFFFFF', bold=True)  # Texto blanco y en negrita

            # Agrego todas las promesas para esa fecha en la hoja
            for promesa in promesas:
                ws.append(promesa)  # Agrego la promesa a la hoja
                total_registros += 1  # Incremento el contador por cada promesa

        # Guardar el archivo Excel con un nombre que incluye la fecha y la base de datos
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # Formateo la fecha y hora actual
        nombre_excel = f"reporte_promesas_{base_datos}_{timestamp}.xlsx"  # Defino el nombre del archivo
        ruta = os.path.join('reportes', nombre_excel)  # Especifico la ruta donde guardar el archivo
        wb.save(ruta)  # Guardo el archivo

        return nombre_excel, total_registros  # Retorno el nombre del archivo y el conteo de registros
