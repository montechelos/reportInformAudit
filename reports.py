from openpyxl import Workbook
import os
from datetime import datetime
from openpyxl.styles import Font, PatternFill
import pandas as pd

class ReportG:

    def generate_report_excel(self, data, generar_report, first_batch):
        fecha_inicio, fecha_fin, base_datos = data

        # Crear el libro de trabajo
        wb = Workbook()
        wb.remove(wb.active)  # Eliminar la hoja predeterminada 

        # Diccionario para almacenar ventas por fecha
        ventas_por_fecha = {}

        # Procesar el primer bloque
        for venta in first_batch:
            fecha = venta['fecha_inicio'].strftime('%Y-%m-%d')
            if fecha not in ventas_por_fecha:
                ventas_por_fecha[fecha] = []
            ventas_por_fecha[fecha].append([
                venta['id'],
                venta['fecha_inicio'].strftime('%Y-%m-%d'),
                venta['fecha_fin'].strftime('%Y-%m-%d'),
                venta['total'],
                venta['id_cliente']
            ])

        # Procesar los siguientes bloques del generador
        for todas_ventas in generar_report:
            for venta in todas_ventas:
                fecha = venta['fecha_inicio'].strftime('%Y-%m-%d')
                if fecha not in ventas_por_fecha:
                    ventas_por_fecha[fecha] = []
                ventas_por_fecha[fecha].append([
                    venta['id'],
                    venta['fecha_inicio'].strftime('%Y-%m-%d'),
                    venta['fecha_fin'].strftime('%Y-%m-%d'),
                    venta['total'],
                    venta['id_cliente']
                ])

        # Crear una hoja por cada fecha única con ventas
        for fecha, ventas in ventas_por_fecha.items():
            ws = wb.create_sheet(title=fecha)
            for cell in ws["1:1"]:
                        cell.fill = PatternFill(start_color="000000", end_color="000000", fill_type="solid")  # Color de fondo
                        cell.font = Font(color="FFFFFF")  # Color de texto
            ws.append(['ID VENTA', 'FECHA INICIO', 'FECHA FIN', 'TOTAL', 'ID CLIENTE'])
            for venta in ventas:  # Agregar todas las ventas para esa fecha
                ws.append(venta)

        # Guardar el archivo Excel
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        nombre_excel = f"reporte_ventas_{base_datos}_{fecha_inicio.strftime('%Y-%m-%d')}_al_{fecha_fin.strftime('%Y-%m-%d')}.xlsx"
        ruta = os.path.join('reportes', nombre_excel)  # Ajusta esta ruta a tu estructura de carpetas
        wb.save(ruta)

        return nombre_excel  # Retornamos el nombre del archivo
