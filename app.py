#--------------------------------------------------------------------
# Instalar con pip install Flask
from flask_cors import CORS
from flask import Flask, request, jsonify

# Instalar con pip install mysql-connector-python
import mysql.connector

# Si es necesario, pip install Werkzeug
from werkzeug.utils import secure_filename

# No es necesario instalar, es parte del sistema standard de Python
import os
import time
#--------------------------------------------------------------------

app = Flask(__name__)
CORS(app)  # Esto habilitará CORS para todas las rutas

class Registro:
    #----------------------------------------------------------------
    # Constructor de la clase
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(


            host=host,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()
        # Intentamos seleccionar la base de datos
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, la creamos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err
            
    
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS alumnos (
            codigo INT AUTO_INCREMENT PRIMARY KEY,
            apellido VARCHAR(40) NOT NULL,
            nombre VARCHAR (40) NOT NULL,
            dni INT (8) NOT NULL
            clase INT NOT NULL,
            nivel VARCHAR (1) NOT NULL,
            imagen_url VARCHAR(40))''' )
        self.conn.commit()
        
        # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

    def listar_alumnos(self):
        self.cursor.execute("SELECT * FROM alumnos")
        alumnos = self.cursor.fetchall()
        return alumnos
    
    def consultar_alumnos(self, codigo):
        # Consultamos un alumno a partir de su código
        self.cursor.execute(f"SELECT * FROM productos WHERE codigo = {codigo}")
        return self.cursor.fetchone()

    def mostrar_alumno(self, codigo):
        # Mostramos los datos de un alumno a partir de su código
        alumno = self.consultar_alumno(codigo)
        if alumno:
            
            print(f"Código: {alumno['codigo']}")
            print(f"Apellido: {alumno['apellido']}")
            print(f"Nombre: {alumno['nombre']}")
            print(f"Dni:{alumno[ 'dni' ]}")
            print(f"Clase: {alumno['clase']}")
            print(f"Nivel: {alumno['nivel']}")
            print(f"Imagen: {alumno['imagen_url']}")
            
        else:
            print("Alumno no encontrado")

    # Agregar un alumno 
    def agregar_alumno(self, apellido, nombre, clase, nivel, imagen_url):
        sql = "INSERT INTO alumnos (apellido, nombre,dni, clase, nivel, imagen_url) VALUES (%s, %s, %s, %s, %s, %s)"
        valores = (apellido, nombre,dni, clase, nivel, imagen_url)
        self.cursor.execute(sql, valores)
        self.conn.commit
        return self.cursor.lastrowid

    def modificar_alumno(self, codigo, nuevo_codigo, nuevo_apellido, nuevo_nombre,nuevo_dni, nueva_clase, nuevo_nivel, nueva_imagen_url):
        sql = "UPDATE alumnos SET apellido = %s, nombre = %s, clase = %s, nivel = %s, imagen_url = %s WHERE codigo = %s"
        valores = (nuevo_codigo, nuevo_apellido, nuevo_nombre, nuevo_dni, nueva_clase, nuevo_nivel, nueva_imagen_url)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def eliminar_producto(self, codigo):
        # Eliminamos un producto de la tabla a partir de su código
        self.cursor.execute(f"DELETE FROM alumnos WHERE codigo = {codigo}")
        self.conn.commit()
        return self.cursor.rowcount > 0

#--------------------------------------------------------------------
# Cuerpo del programa
#--------------------------------------------------------------------
# Crear una instancia de la clase Registro
registro = Registro(host='querrien47.mysql.pythonanywhere-services.com', user='querrien47', password='CaC24170', database='querrien47$miapp')

# Carpeta para guardar las imagenes
# ruta_destino = './imagenes/'
ruta_destino = '/home/querrien47/mysite/static/imagenes/'

@app.route("/alumnos", methods=["GET"])
def listar_alumnos():
    alumnos = registro.listar_alumnos()
    return jsonify(alumnos)

@app.route("/alumnos/<int:codigo>", methods=["GET"])
def mostrar_alumnos(codigo):
    alumno = registro.consultar_alumno(codigo)
    if alumno:
        return jsonify(alumno)
    else:
        return "Alumno no encontrado", 

@app.route("/alumnos", methods=["POST"])
def agregar_alumno():
    #Recojo los datos del form
    apellido = request.form['apellido']
    nombre = request.form['nombre']
    dni = request.form['dni']
    clase = request.form['clase']
    nivel = request.form['nivel']
    nombre_imagen = request.files['imagen']  
    

    # Genero el nombre de la imagen
    nombre_imagen = secure_filename(nombre_imagen.filename)
    nombre_base, extension = os.path.splitext(nombre_imagen) 
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" 

    nuevo_codigo = registro.agregar_alumno (apellido, nombre, dni, clase, nivel, nombre_imagen )
    if nuevo_codigo:    
        nombre_imagen.save(os.path.join(ruta_destino, nombre_imagen))
        return jsonify({"mensaje": "Alumno agregado correctamente.", "codigo": nuevo_codigo, "imagen": nombre_imagen})
    else:
        return jsonify({"mensaje": "Error al agregar el alumno."})

@app.route("/alumnos/<int:codigo>", methods=["PUT"])
def modificar_alumno(codigo):
    #Se recuperan los nuevos datos del formulario
    nuevo_apellido = request.form.get("apellido")
    nuevo_nombre = request.form.get("nombre")
    nuevo dni = request.form.get("dni")
    nueva_clase = request.form.get("clase")
    nuevo_nivel = request.form.get("nivel")
    nueva_imagen = request.files.get('imagen')
    
    # Verifica si se proporcionó una nueva imagen
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        # Procesamiento de la imagen
        nombre_imagen = secure_filename(imagen.filename) 
        nombre_base, extension = os.path.splitext(nombre_imagen) 
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" 

        # Guardar la imagen en el servidor
        imagen.save(os.path.join(ruta_destino, nombre_imagen))
        
        # Busco el producto guardado
        alumno = registro.consultar_alumno(codigo)
        if alumno: # Si existe el producto...
            imagen_vieja = alumno["imagen_url"]
            # Armo la ruta a la imagen
            ruta_imagen = os.path.join(ruta_destino, imagen_vieja)

            # Y si existe la borro.
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)
    else:     
       alumno = registro.consultar_alumno(codigo)
    if alumno:
            nombre_imagen = alumno["imagen_url"]

   # Se llama al método modificar_alumno pasando el codigo del alumno y los nuevos datos.
    if registro.modificar_alumno(codigo, nuevo_apellido, nuevo_nombre,nuevo_dni, nueva_clase, nuevo_nivel, nueva_imagen):
        return jsonify({"mensaje": "Alumno modificado"}), 
    else:
        return jsonify({"mensaje": "Alumno no encontrado"}), 

@app.route("/alumnos/<int:codigo>", methods=["DELETE"])
def eliminar_alumnos(codigo):
    # Primero, obtiene la información del alumno para encontrar la imagen
    alumno = registro.consultar_alumno(codigo)
    if alumno:
        # Eliminar la imagen asociada si existe
        ruta_imagen = os.path.join(ruta_destino, alumno['imagen_url'])
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

        # Luego, elimina el alumno del registro
        if registro.eliminar_alumno(codigo):
            return jsonify({"mensaje": "Alumno dado de baja"}),
        else:
            return jsonify({"mensaje": "Error, algo salio mal"}),
    else:
        return jsonify({"mensaje": "Alumno no encontrado"}), 

if __name__ == "__main__":
    app.run(debug=True)from flask import Flask, request, jsonify

# Instalar con pip install flask-cors
from flask_cors import CORS

# Instalar con pip install mysql-connector-python
import mysql.connector

# Si es necesario, pip install Werkzeug
from werkzeug.utils import secure_filename

# No es necesario instalar, es parte del sistema standard de Python
import os
import time
#--------------------------------------------------------------------

app = Flask(__name__)
CORS(app)  # Esto habilitará CORS para todas las rutas

class Catalogo:
    #----------------------------------------------------------------
    # Constructor de la clase
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()
        # Intentamos seleccionar la base de datos
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, la creamos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
            codigo INT AUTO_INCREMENT PRIMARY KEY,
            descripcion VARCHAR(255) NOT NULL,
            cantidad INT NOT NULL,
            precio DECIMAL(10, 2) NOT NULL,
            imagen_url VARCHAR(255),
            proveedor INT(4))''')
        self.conn.commit()
        
        # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

    def listar_productos(self):
        self.cursor.execute("SELECT * FROM productos")
        productos = self.cursor.fetchall()
        return productos
    
    def consultar_producto(self, codigo):
        # Consultamos un producto a partir de su código
        self.cursor.execute(f"SELECT * FROM productos WHERE codigo = {codigo}")
        return self.cursor.fetchone()

    def mostrar_producto(self, codigo):
        # Mostramos los datos de un producto a partir de su código
        producto = self.consultar_producto(codigo)
        if producto:
            print("-" * 40)
            print(f"Código.....: {producto['codigo']}")
            print(f"Descripción: {producto['descripcion']}")
            print(f"Cantidad...: {producto['cantidad']}")
            print(f"Precio.....: {producto['precio']}")
            print(f"Imagen.....: {producto['imagen_url']}")
            print(f"Proveedor..: {producto['proveedor']}")
            print("-" * 40)
        else:
            print("Producto no encontrado.")

    def agregar_producto(self, descripcion, cantidad, precio, imagen, proveedor):
        sql = "INSERT INTO productos (descripcion, cantidad, precio, imagen_url, proveedor) VALUES (%s, %s, %s, %s, %s)"
        valores = (descripcion, cantidad, precio, imagen, proveedor)

        self.cursor.execute(sql,valores)
        self.conn.commit()
        return self.cursor.lastrowid

    def modificar_producto(self, codigo, nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_imagen, nuevo_proveedor):
        sql = "UPDATE productos SET descripcion = %s, cantidad = %s, precio = %s, imagen_url = %s, proveedor = %s WHERE codigo = %s"
        valores = (nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_imagen, nuevo_proveedor, codigo)

        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def eliminar_producto(self, codigo):
        # Eliminamos un producto de la tabla a partir de su código
        self.cursor.execute(f"DELETE FROM productos WHERE codigo = {codigo}")
        self.conn.commit()
        return self.cursor.rowcount > 0

#--------------------------------------------------------------------
# Cuerpo del programa
#--------------------------------------------------------------------
# Crear una instancia de la clase Catalogo
catalogo = Catalogo(host='juanpablocodo.mysql.pythonanywhere-services.com', user='juanpablocodo', password='root-123456', database='juanpablocodo$miapp')

# Carpeta para guardar las imagenes
# ruta_destino = './static/imagenes/'
ruta_destino = '/home/juanpablocodo/mysite/static/imagenes/'

@app.route("/productos", methods=["GET"])
def listar_productos():
    productos = catalogo.listar_productos()
    return jsonify(productos)

@app.route("/productos/<int:codigo>", methods=["GET"])
def mostrar_producto(codigo):
    producto = catalogo.consultar_producto(codigo)
    if producto:
        return jsonify(producto)
    else:
        return "Producto no encontrado", 404

@app.route("/productos", methods=["POST"])
def agregar_producto():
    #Recojo los datos del form
    descripcion = request.form['descripcion']
    cantidad = request.form['cantidad']
    precio = request.form['precio']
    imagen = request.files['imagen']
    proveedor = request.form['proveedor']  
    nombre_imagen = ""

    # Genero el nombre de la imagen
    nombre_imagen = secure_filename(imagen.filename) 
    nombre_base, extension = os.path.splitext(nombre_imagen) 
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" 

    nuevo_codigo = catalogo.agregar_producto(descripcion, cantidad, precio, nombre_imagen, proveedor)
    if nuevo_codigo:    
        imagen.save(os.path.join(ruta_destino, nombre_imagen))
        return jsonify({"mensaje": "Producto agregado correctamente.", "codigo": nuevo_codigo, "imagen": nombre_imagen}), 201
    else:
        return jsonify({"mensaje": "Error al agregar el producto."}), 500

@app.route("/productos/<int:codigo>", methods=["PUT"])
def modificar_producto(codigo):
    #Se recuperan los nuevos datos del formulario
    nueva_descripcion = request.form.get("descripcion")
    nueva_cantidad = request.form.get("cantidad")
    nuevo_precio = request.form.get("precio")
    nuevo_proveedor = request.form.get("proveedor")
    
    # Verifica si se proporcionó una nueva imagen
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        # Procesamiento de la imagen
        nombre_imagen = secure_filename(imagen.filename) 
        nombre_base, extension = os.path.splitext(nombre_imagen) 
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" 

        # Guardar la imagen en el servidor
        imagen.save(os.path.join(ruta_destino, nombre_imagen))
        
        # Busco el producto guardado
        producto = catalogo.consultar_producto(codigo)
        if producto: # Si existe el producto...
            imagen_vieja = producto["imagen_url"]
            # Armo la ruta a la imagen
            ruta_imagen = os.path.join(ruta_destino, imagen_vieja)

            # Y si existe la borro.
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)
    else:     
        producto = catalogo.consultar_producto(codigo)
        if producto:
            nombre_imagen = producto["imagen_url"]

   # Se llama al método modificar_producto pasando el codigo del producto y los nuevos datos.
    if catalogo.modificar_producto(codigo, nueva_descripcion, nueva_cantidad, nuevo_precio, nombre_imagen, nuevo_proveedor):
        return jsonify({"mensaje": "Producto modificado"}), 200
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 403

@app.route("/productos/<int:codigo>", methods=["DELETE"])
def eliminar_producto(codigo):
    # Primero, obtiene la información del producto para encontrar la imagen
    producto = catalogo.consultar_producto(codigo)
    if producto:
        # Eliminar la imagen asociada si existe
        ruta_imagen = os.path.join(ruta_destino, producto['imagen_url'])
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

        # Luego, elimina el producto del catálogo
        if catalogo.eliminar_producto(codigo):
            return jsonify({"mensaje": "Producto eliminado"}), 200
        else:
            return jsonify({"mensaje": "Error al eliminar el producto"}), 500
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 404


if __name__ == "__main__":
    app.run(debug=True)
