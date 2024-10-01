import mysql.connector
from mysql.connector import OperationalError, Error as MySQLError
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
}

def connectdb(base_datos):
    try:
        config['database'] = base_datos
        conexion = mysql.connector.connect(**config)
        return conexion
    except OperationalError as e:
        raise Exception(f"Error al conectarse a la base de datos: {e}")
    except MySQLError as e:
        raise Exception(f"Error en la consulta: {e}")
    except Exception as e:
        raise Exception(f"Error inesperado: {e}")

class Queries:
    # Funcion para hacer la consulta 
    def get_db_consult(self, data, batch_size=1000):
        try:
            fecha_inicio, fecha_fin, base_datos = data
            conexion = connectdb(base_datos)

            conexion.autocommit = True
            cursor = conexion.cursor(dictionary=True)

            query = """SELECT id, fecha_inicio, fecha_fin, total, id_cliente    
                       FROM promisess 
                       WHERE fecha_inicio BETWEEN %s AND %s 
                       ORDER BY fecha_inicio"""
            cursor.execute(query, (fecha_inicio, fecha_fin))

            while True:
                ventas = cursor.fetchmany(size=batch_size)
                if not ventas:
                    break
                yield ventas #generador

            cursor.close()
            conexion.close()

        except OperationalError as e:
            raise Exception(f"Error al conectarse a la base de datos: {e}")
        except MySQLError as e:
            raise Exception(f"Error de MySQL: {e}")
        except Exception as e:
            raise Exception(f"Error inesperado: {e}")

    