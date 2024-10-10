import pymysql
import os
from dotenv import load_dotenv
from pymysql import MySQLError, OperationalError

# Cargar variables de entorno desde .env
load_dotenv()

def connect(db_name):
    """Conexión a la base de datos."""
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except OperationalError as e:
        print("Error operativo: ", e)
        raise Exception(f"Error al conectarse a la base de datos: {e}")
    except MySQLError as e:
        print("Error de MySQL: ", e)
        raise Exception(f"Error al conectarse a la base de datos: {e}")
    except Exception as e:
        print("Error inesperado: ", e)
        raise

class Querys:
    def get_db_consult(self, data, batch_size=1000):
        conexion = None
        cursor = None
        try:
            fecha_inicio, fecha_fin, base_datos = data
            conexion = connect(base_datos)

            # Crear un cursor para ejecutar las consultas
            cursor = conexion.cursor(pymysql.cursors.DictCursor)

            # Defino la consulta SQL para obtener las promesas en el rango de fechas especificado
            query = """
            SELECT DISTINCT 
    CL.identification AS ID,  
    CL.completed_name AS NOMBRE,
    PS.created_at AS FECHA_ACUERDO, 
    FORMAT(PS.amount_promise, 2, 'es_ES') AS VALOR_ACUERDO, -- Para no usar replace

    PS.id AS NUMERO_PROMESA,  
    PS.promise_state_id AS ESTADO_PROMESA,  
    COALESCE(FORMAT(QS.valor_cuota, 2, 'es_ES'), '0') AS VALOR_CUOTA, -- cambiar valor nulo a 0

    QS.quota_state_id AS ESTADO_CUOTA, 
    COUNT(QS2.numero_cuota) AS CUOTAS  
FROM 
    clients CL 
INNER JOIN 
    promises PS ON CL.id = PS.client_id  
LEFT JOIN 
    quota_promises QS ON PS.id = QS.promise_id 
LEFT JOIN 
    quota_promises QS2 ON PS.id = QS2.promise_id 
WHERE 
    PS.created_at  BETWEEN %s AND DATE_ADD(%s, INTERVAL 1 DAY)

GROUP BY 
    CL.ID;
    
            """
            
            # Ejecuto la consulta pasando las fechas como parámetros
            cursor.execute(query, (fecha_inicio, fecha_fin))

            while True:
                # Utilizo fetchmany para obtener un lote de resultados
                promesas = cursor.fetchmany(size=batch_size)
                if not promesas:
                    break  # Salgo del bucle si no hay más resultados
                yield promesas  # Devuelvo los resultados como un generador

        except OperationalError as e:
            raise Exception(f"Error al conectarse a la base de datos: {e}")
        except MySQLError as e:
            raise Exception(f"Error de MySQL: {e}")
        except Exception as e:
            raise Exception(f"Error inesperado: {e}")
        finally:
            # Cierro el cursor y la conexión a la base de datos
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()
