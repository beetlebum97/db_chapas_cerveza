import sys
import mysql.connector
import pyodbc

def conectar_a_base_de_datos(motor,servidor,usuario,contraseña):
    if motor.lower() == 'mysql':
        cnx = mysql.connector.connect(user=usuario, password=contraseña,
                                      host=servidor,autocommit=True)
        cursor = cnx.cursor()
        print()
        print("Conectado a MySQL")
        print()
        
# 0. CREAR Y USAR LA BASE DE DATOS
        cursor.execute('CREATE DATABASE CHAPAS_CERVEZA')
        cursor.execute('USE CHAPAS_CERVEZA')
        
# 1. TABLA FABRICANTES_CHAPA
        CREAR_FABRICANTES = """
            CREATE TABLE Fabricantes_Chapa(
            ID int PRIMARY KEY,
            Nombre varchar(255) UNIQUE,
            Empresa varchar(255) NULL,
            País varchar(255) NULL,
            URL varchar(255) NULL,
            Imagen varchar(255)
            ); """
        cursor.execute(CREAR_FABRICANTES)
        
        INSERTAR_FABRICANTES = """
            LOAD DATA INFILE '/var/lib/mysql-files/fabricantes.csv'
            INTO TABLE Fabricantes_Chapa
            FIELDS TERMINATED BY ';'
            LINES TERMINATED BY '\n'
            IGNORE 1 LINES
            (ID,Nombre,@Empresa,@País,@URL,Imagen)
            SET Empresa = NULLIF(@Empresa,''),
            País = NULLIF(@País,''),
            URL = NULLIF(@URL,'')
            ; """
        cursor.execute(INSERTAR_FABRICANTES)
        
# 2. TABLA PRODUCTORES_CERVEZA
        CREAR_PRODUCTORES = """
            CREATE TABLE Productores_Cerveza(
            ID int PRIMARY KEY,
            Nombre varchar(255) UNIQUE,
            País varchar(255) NULL,
            Región varchar(255) NULL,
            Ciudad varchar (255) NULL,
            Fundación int NULL,
            URL varchar(255) NULL,
            `Empresa matriz` varchar(255) NULL
            ); """
        cursor.execute(CREAR_PRODUCTORES)
        
        INSERTAR_PRODUCTORES = """
            LOAD DATA INFILE '/var/lib/mysql-files/productores.csv'
            INTO TABLE Productores_Cerveza
            FIELDS TERMINATED BY ';'
            LINES TERMINATED BY '\n'
            IGNORE 1 LINES
            (ID,Nombre,@País,@Región,@Ciudad,@Fundación,@URL,@`Empresa matriz`)
            SET País = NULLIF(@País,''),
            Región = NULLIF(@Región,''),
            Ciudad = NULLIF(@Ciudad,''),
            Fundación = NULLIF(@Fundación,''),
            URL = NULLIF(@URL,''),
            `Empresa matriz` = NULLIF(@`Empresa matriz`,'')
            ; """
        cursor.execute(INSERTAR_PRODUCTORES)
        
# 3. TABLA CERVEZAS
        CREAR_CERVEZAS = """
            CREATE TABLE Cervezas(
            ID int PRIMARY KEY,
            Nombre varchar(255) UNIQUE,
            Tipo varchar(255) NOT NULL,
            Estilo varchar(255) NOT NULL,
            Grado decimal (4,2) NOT NULL,
            IBU int NULL,
            Lanzamiento int NULL,
            Estado varchar (255) CHECK (Estado IN('Activa','Retirada')),
            País varchar(255) NOT NULL,
            URL varchar(255) NULL,
            Productor varchar(255),

            FOREIGN KEY (Productor) REFERENCES Productores_Cerveza (Nombre) ON UPDATE CASCADE ON DELETE CASCADE
            ); """
        cursor.execute(CREAR_CERVEZAS)
        
        INSERTAR_CERVEZAS = """
            LOAD DATA INFILE '/var/lib/mysql-files/cervezas.csv'
            INTO TABLE Cervezas
            FIELDS TERMINATED BY ';'
            LINES TERMINATED BY '\n'
            IGNORE 1 LINES
            (ID,Nombre,Tipo,Estilo,Grado,@IBU,@Lanzamiento,Estado,País,@URL,@Productor)
            SET IBU = NULLIF(@IBU,''),
            Lanzamiento = NULLIF(@Lanzamiento,''),
            URL = NULLIF(@URL,''),
            Productor = TRIM(TRAILING '\r' FROM @Productor)
            ; """
        cursor.execute(INSERTAR_CERVEZAS)
        
# 4. TABLA CHAPAS
        CREAR_CHAPAS = """
            CREATE TABLE Chapas(
            ID int PRIMARY KEY,
            Cerveza varchar(255),
            Año int NOT NULL,
            Color varchar(255) NOT NULL,
            Fabricante varchar(255),
            Obturador varchar(255) NULL,
            Inscripción varchar(255) NULL,
            Estado varchar (255) CHECK (Estado IN('Perfecto','Bueno','Regular','Malo')),
            Repetida varchar (255) CHECK (Repetida IN('SI','NO')),
            Formato varchar (255) CHECK (Formato IN('20cl','25cl','33cl','50cl')),
            Registro datetime DEFAULT CURRENT_TIMESTAMP,
            Imagen varchar(255),

            FOREIGN KEY (Cerveza) REFERENCES Cervezas (Nombre) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (Fabricante) REFERENCES Fabricantes_Chapa (Nombre) ON UPDATE CASCADE ON DELETE CASCADE
            ); """
        cursor.execute(CREAR_CHAPAS)
        
        INSERTAR_CHAPAS = """
            LOAD DATA INFILE '/var/lib/mysql-files/chapas.csv'
            INTO TABLE Chapas
            FIELDS TERMINATED BY ';'
            LINES TERMINATED BY '\n'
            IGNORE 1 LINES
            (ID,Cerveza,Año,Color,Fabricante,@Obturador,@Inscripción,Estado,Repetida,@Formato,@Registro,Imagen)
            SET Obturador = NULLIF(@Obturador,''),
            Inscripción = NULLIF(@Inscripción,''),
            Formato = NULLIF(@Formato,''),
            Registro = COALESCE(NULLIF(@Registro,''), CURRENT_TIMESTAMP)
            ; """
        cursor.execute(INSERTAR_CHAPAS)
        
# 5. TABLA CATAS
        CREAR_CATAS = """
            CREATE TABLE Catas(
            ID int PRIMARY KEY,
            Cerveza varchar (255),
            `Nota de Cata` varchar (255) NOT NULL,
            Sabor varchar (255) CHECK (Sabor IN('Excelente','Bueno','Aceptable','Regular','Malo')),
            Puntos int NOT NULL,
            Fecha date,

            FOREIGN KEY (Cerveza) REFERENCES Cervezas (Nombre) ON UPDATE CASCADE ON DELETE CASCADE
            ); """
        cursor.execute(CREAR_CATAS)
        
        INSERTAR_CATAS = """
            LOAD DATA INFILE '/var/lib/mysql-files/catas.csv'
            INTO TABLE Catas
            FIELDS TERMINATED BY ';'
            LINES TERMINATED BY '\n'
            IGNORE 1 LINES
            (ID,Cerveza,`Nota de Cata`,Sabor,Puntos,@Fecha)
            SET Fecha = NULLIF(TRIM(TRAILING '\r' FROM @Fecha),'')
            ; """
        cursor.execute(INSERTAR_CATAS)
        
# 6. REGISTROS TOTALES
        REGISTROS = """
            SELECT A.Nombre AS Fabricantes_Chapa, B.Nombre AS Productores_Cerveza, C.Nombre AS Cervezas, D.ID AS Chapas, E.Cerveza AS Catas
            FROM (SELECT COUNT(FC.Nombre) AS Nombre FROM Fabricantes_Chapa FC) A
            CROSS JOIN (SELECT COUNT(PC.Nombre) AS Nombre FROM Productores_Cerveza PC) B
            CROSS JOIN (SELECT COUNT(C.Nombre) AS Nombre FROM Cervezas C) C
            CROSS JOIN (SELECT COUNT(CH.ID) AS ID FROM Chapas CH) D
            CROSS JOIN (SELECT COUNT(CT.Cerveza) AS Cerveza FROM Catas CT) E
            ; """
        cursor.execute(REGISTROS)
        
        columnas = [columna[0] for columna in cursor.description]
        resultados = cursor.fetchall()
        
        for fila in resultados:
            for nombre_columna, valor in zip(columnas, fila):
                print(f"{nombre_columna}: {valor}")
        
        #print(columnas)
        #for fila in resultado:
            #print(fila)
        
# 7. CERRAR CONEXIÓN
        cursor.close()
        cnx.close()
        
    elif motor.lower() == 'sql-server':
        cnx = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                             'SERVER=' + servidor + ';'
                             'UID=' + usuario + ';'
                             'PWD=' + contraseña, 
                              autocommit=True)
                              
        cursor = cnx.cursor()
        print()
        print("Conectado a SQL Server")
        print()
        
# 0. CREAR Y USAR LA BASE DE DATOS
        cursor.execute('CREATE DATABASE CHAPAS_CERVEZA')
        cursor.execute('USE CHAPAS_CERVEZA')
        
# 1. TABLA FABRICANTES_CHAPA
        CREAR_FABRICANTES = """ 
            CREATE TABLE Fabricantes_Chapa(
            ID int PRIMARY KEY,
            Nombre nvarchar(255) UNIQUE,
            Empresa nvarchar(255) NULL,
            País nvarchar(255) NULL,
            [URL] nvarchar(255) NULL,
            Imagen nvarchar(255) NULL
            ) """
        cursor.execute(CREAR_FABRICANTES)

        INSERTAR_FABRICANTES = """
            BULK INSERT Fabricantes_Chapa
            FROM 'D:\\db_chapas_cerveza_dev\\data\\fabricantes.csv'
            WITH (
            FORMAT = 'CSV',
            FIELDTERMINATOR = ';',
            ROWTERMINATOR = '\n',
            FIRSTROW = 2,
            CODEPAGE='65001'
            ) """
        cursor.execute(INSERTAR_FABRICANTES)
        
# 2. TABLA PRODUCTORES_CERVEZA
        CREAR_PRODUCTORES = """
            CREATE TABLE Productores_Cerveza(
            ID int PRIMARY KEY,
            Nombre nvarchar(255) UNIQUE,
            País nvarchar(255) NULL,
            Región nvarchar(255) NULL,
            Ciudad nvarchar(255) NULL,
            Fundación int NULL,
            [URL] nvarchar(255) NULL,
            [Empresa matriz] nvarchar(255) NULL
            ) """
        cursor.execute(CREAR_PRODUCTORES)
        
        INSERTAR_PRODUCTORES = """
            BULK INSERT Productores_Cerveza
            FROM 'D:\\db_chapas_cerveza_dev\\data\\productores.csv'
            WITH (
            FORMAT = 'CSV',
            FIELDTERMINATOR = ';',
            ROWTERMINATOR = '\n',
            FIRSTROW = 2,
            CODEPAGE='65001'
            ) """
        cursor.execute(INSERTAR_PRODUCTORES)

# 3. TABLA CERVEZAS
        CREAR_CERVEZAS = """
            CREATE TABLE Cervezas(
            ID int PRIMARY KEY,
            Nombre nvarchar(255) UNIQUE,
            Tipo nvarchar(255) NULL,
            Estilo nvarchar(255) NULL,
            Grado decimal(4,2) NULL,
            IBU int NULL,
            Lanzamiento int NULL,
            Estado nvarchar(255) CHECK (Estado IN('Activa','Retirada')),
            País nvarchar(255) NULL,
            [URL] nvarchar(255) NULL,
            Productor nvarchar(255),

            FOREIGN KEY (Productor) REFERENCES Productores_Cerveza (Nombre) ON UPDATE CASCADE ON DELETE CASCADE
            ) """
        cursor.execute(CREAR_CERVEZAS)
        
        INSERTAR_CERVEZAS = """
            BULK INSERT Cervezas
            FROM 'D:\\db_chapas_cerveza_dev\\data\\cervezas.csv' 
            WITH (
            FORMAT = 'CSV',
            FIELDTERMINATOR = ';',
            ROWTERMINATOR = '\n',
            FIRSTROW = 2,
            CODEPAGE='65001'
            ) """
        cursor.execute(INSERTAR_CERVEZAS)
        
# 4. TABLA CHAPAS
        CREAR_CHAPAS = """
            CREATE TABLE Chapas(
            ID int PRIMARY KEY,
            Cerveza nvarchar(255), 
            Año int NOT NULL,
            Color nvarchar(255) NOT NULL,
            Fabricante nvarchar(255),
            Obturador nvarchar(255) NULL,
            Inscripción nvarchar(255) NULL, 
            Estado nvarchar(255) CHECK (Estado IN('Perfecto','Bueno','Regular','Malo')),
            Repetida nvarchar(255) CHECK (Repetida IN('SI','NO')),
            Formato nvarchar(255) CHECK (Formato IN('20cl','25cl','33cl','50cl')),
            Registro datetime DEFAULT CURRENT_TIMESTAMP,
            Imagen nvarchar(255) NULL,

            FOREIGN KEY (Cerveza) REFERENCES Cervezas (Nombre) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (Fabricante) REFERENCES Fabricantes_Chapa (Nombre) ON UPDATE CASCADE ON DELETE CASCADE
            ) """
        cursor.execute(CREAR_CHAPAS)
        
        INSERTAR_CHAPAS = """
            BULK INSERT Chapas
            FROM 'D:\\db_chapas_cerveza_dev\\data\\chapas.csv'
            WITH (
            FORMAT = 'CSV',
            FIELDTERMINATOR = ';',
            ROWTERMINATOR = '\n',
            FIRSTROW = 2,
            CODEPAGE='65001'
            ) """
        cursor.execute(INSERTAR_CHAPAS)
        
# 5. TABLA CATAS
        CREAR_CATAS = """
            CREATE TABLE Catas(
            ID int PRIMARY KEY,
            Cerveza nvarchar(255),
            [Nota de Cata] nvarchar(255) NOT NULL,	
            Sabor nvarchar(255) CHECK (Sabor IN('Excelente','Bueno','Aceptable','Regular','Malo')),
            Puntos int NOT NULL,
            Fecha date DEFAULT '2019-01-15',

            FOREIGN KEY (Cerveza) REFERENCES Cervezas (Nombre) ON UPDATE CASCADE ON DELETE CASCADE
            ) """
        cursor.execute(CREAR_CATAS)
        
        INSERTAR_CATAS = """
            BULK INSERT Catas
            FROM 'D:\\db_chapas_cerveza_dev\\data\\catas.csv'
            WITH (
            FORMAT = 'CSV',
            FIELDTERMINATOR = ';',
            ROWTERMINATOR = '\n',
            FIRSTROW = 2,
            CODEPAGE='65001'
            ) """
        cursor.execute(INSERTAR_CATAS)
        
# 6. REGISTROS TOTALES
        REGISTROS = """
            SELECT A.Nombre AS Fabricantes_Chapa, B.Nombre AS Productores_Cerveza, C.Nombre AS Cervezas, D.ID AS Chapas, E.Cerveza AS Catas
            FROM (SELECT COUNT(FC.Nombre) AS Nombre FROM Fabricantes_Chapa FC) A
            CROSS JOIN (SELECT COUNT(PC.Nombre) AS Nombre FROM Productores_Cerveza PC) B
            CROSS JOIN (SELECT COUNT(C.Nombre) AS Nombre FROM Cervezas C) C
            CROSS JOIN (SELECT COUNT(CH.ID) AS ID FROM Chapas CH) D
            CROSS JOIN (SELECT COUNT(CT.Cerveza) AS Cerveza FROM Catas CT) E """
        cursor.execute(REGISTROS)
        
        columnas = [columna[0] for columna in cursor.description]
        resultados = cursor.fetchall()
        
        for fila in resultados:
            for nombre_columna, valor in zip(columnas, fila):
                print(f"{nombre_columna}: {valor}")
        
        #print(columnas)
        #for fila in resultado:
            #print(fila)
        
        
# 7. CERRAR CONEXIÓN
        cursor.close()
        cnx.close()
        
    else:
        print("Motor de base de datos no reconocido.")

# Argumentos script: 1º Motor BBDD, 2º Servidor, 3º Usuario, 4º Contraseña 
if len(sys.argv) > 4:
    conectar_a_base_de_datos(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
else:
    print("Por favor, proporciona motor, servidor, usuario y contraseña como argumentos.")








