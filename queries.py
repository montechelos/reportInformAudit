import pymysql
from pymysql import OperationalError, Error as MySQLError
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

def connect(db_name):
    """Conexión a la base de datos."""
    try:
        # Intento establecer una conexión a la base de datos utilizando las credenciales almacenadas en las variables de entorno
        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),        # Host de la base de datos
            user=os.getenv('DB_USER'),        # Usuario de la base de datos
            password=os.getenv('DB_PASSWORD'), # Contraseña de la base de datos
            database=db_name,                  # Nombre de la base de datos a la que me conecto
            cursorclass=pymysql.cursors.DictCursor  # Utilizo un cursor que devuelve los resultados como diccionarios
        )
        return connection
    except pymysql.err.OperationalError as e:
        # Si hay un error de conexión, lanzo una excepción con un mensaje específico
        raise Exception(f"Error en la conexión a la base de datos: {e}")

class Queries:
    # Defino una clase llamada Queries para manejar las consultas a la base de datos
    def get_db_consult(self, data, batch_size=1000):
        try:
            # Extraigo las fechas y el nombre de la base de datos de los datos proporcionados
            fecha_inicio, fecha_fin, base_datos = data
            # Realizo la conexión a la base de datos
            conexion = connect(base_datos)

            # Configuro la conexión para que haga autocommit
            conexion.autocommit = True
            # Creo un cursor para ejecutar las consultas
            cursor = conexion.cursor(pymysql.cursors.DictCursor)

            # Defino la consulta SQL para obtener las promesas en el rango de fechas especificado
            query = """
                SELECT p.id, p.tipo_promesa, p.monto, p.fecha, p.estado, 
                       c.id AS cliente_id, c.nombre AS nombre_cliente, 
                       c.email AS email_cliente, c.cedula
                FROM promises p
                JOIN clientes c ON p.cliente_id = c.id
                WHERE p.fecha BETWEEN %s AND %s
            """
            # Ejecuto la consulta pasando las fechas como parámetros
            cursor.execute(query, (fecha_inicio, fecha_fin))

            while True:
                # Utilizo fetchmany para obtener un lote de resultados
                ventas = cursor.fetchmany(size=batch_size)
                if not ventas:
                    break  # Salgo del bucle si no hay más resultados
                yield ventas  # Devuelvo los resultados como un generador

            # Cierro el cursor y la conexión a la base de datos
            cursor.close()
            conexion.close()

        except OperationalError as e:
            # Manejo errores de conexión a la base de datos
            raise Exception(f"Error al conectarse a la base de datos: {e}")
        except MySQLError as e:
            # Manejo errores específicos de MySQL
            raise Exception(f"Error de MySQL: {e}")
        except Exception as e:
            # Capturo cualquier otro tipo de error inesperado
            raise Exception(f"Error inesperado: {e}")
