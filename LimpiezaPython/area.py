import csv
import random
from datetime import datetime
import pandas as pd

def limpiar_tildes(texto):
    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'
    }
    for acento, letra in reemplazos.items():
        texto = texto.replace(acento, letra)
    return texto

def intentar_convertir_fecha(campo):
    if isinstance(campo, datetime):
        return campo.strftime('%Y-%m-%d')
    elif isinstance(campo, float):
        campo = str(int(campo))
    formatos = [
        '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%Y-%m-%d', '%Y/%m/%d',
        '%d/%m/%y', '%d-%m-%y', '%m-%d-%Y', '%m-%d-%y', '%Y-%m-%d %H:%M:%S'
    ]
    for formato in formatos:
        try:
            fecha = datetime.strptime(campo, formato)
            if fecha.year < 100:
                fecha = fecha.replace(year=fecha.year + 2000)
            return fecha.strftime('%Y-%m-%d')
        except ValueError:
            pass
    return campo

def crear_coordenadas(latitud, longitud):
    try:
        lat = float(latitud)
        lon = float(longitud)
        return [lon, lat]  # Formato [longitud, latitud] requerido por MongoDB como un string
    except ValueError:
        return None  # Si la latitud o longitud no son válidas, retorna None

def obtener_cod_postal(lector_csv):
    cod_pstal = {}
    for fila in lector_csv:
        codigo = fila.get('COD_POSTAL')
        barrio = limpiar_tildes(fila.get('BARRIO', '').strip())
        if codigo and barrio and barrio not in cod_pstal.keys() and int(float(codigo))!=0:
            cod_pstal[barrio.upper()] = codigo
         
    return cod_pstal

def obtener_distritos(lector_csv):
    distritos = {}
    for fila in lector_csv:
        codigo = fila.get('COD_DISTRITO')
        distrito = limpiar_tildes(fila.get('DISTRITO', '').strip())
        if codigo and distrito and codigo not in distritos.keys():
            distritos[codigo] = distrito.upper()

    return distritos


def obtener_fecha_mas_antigua(df, id, fecha):
    fechas =df[df['AreaRecreativaID'] == int(id)][fecha].tolist()
    fechas_validas = []

    for fecha in fechas:
        if fecha!='' and fecha!='fecha_incorrecta':
            try:
                # Verificar si la fecha ya es un objeto datetime
                if isinstance(fecha, datetime):
                    fecha_dt = fecha
                else:
                    # Convertir la fecha a un objeto datetime
                    fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')
                fechas_validas.append(fecha_dt)
            except:
                # Si la fecha no está en el formato correcto, la ignoramos
                continue
    # Verificamos si hay fechas válidas y devolvemos la más antigua si la hay
    if len(fechas_validas) > 0:
        return min(fechas_validas)
    else:
        return ''

def contar_valores_repetidos(archivo_csv, columna):
    # Leer el archivo CSV
    df = pd.read_csv(archivo_csv)
    
    # Contar las ocurrencias de cada valor en la columna especificada
    conteo = df[columna].value_counts()
    
    # Filtrar los valores que se repiten
    repetidos = conteo[conteo > 1]
    
    # Imprimir los valores repetidos y el número de veces que se repiten
    print(f'Valores repetidos en la columna {columna}:')
    for valor, cuenta in repetidos.items():
        print(f'{valor}: {cuenta} veces')


def juegos_por_tipo(id, juegos_df):
    juegos = juegos_df[juegos_df['AreaRecreativaID'] == int(id)]['tipo_juego'].tolist()
    juegos_por_tipo = {'deportivas':0, 'mayores':0, 'infantiles':0}
    for juego in juegos:
        if juego in juegos_por_tipo:
            juegos_por_tipo[juego] += 1
        else:
            print(f"Tipo de juego desconocido: {juego}")
    
    return juegos_por_tipo

def obtener_estado_global(id, juegos_df, incidente_df, encuestas_df):
    # Calcular el estado global del área: puntuacion_calidad *10 - (nº juegos en mantenimiento * nº incidentes de seguridad)
    puntuacion_calidad = encuestas_df[encuestas_df['AreaRecreativaID'] == int(id)]['PUNTUACION_CALIDAD'].tolist()
    juegos_mantenimiento = juegos_df[(juegos_df['AreaRecreativaID'] == int(id)) & (juegos_df['ESTADO'] == 'EN MANTENIMIENTO')].shape[0]
    incidentes = incidente_df[incidente_df['AreaRecreativaID'] == int(id)].shape[0]
    
    if len(puntuacion_calidad) > 0:
        puntuacion_calidad = sum(puntuacion_calidad) / len(puntuacion_calidad)
    else:
        puntuacion_calidad = 0
    
    return puntuacion_calidad * 10 - (juegos_mantenimiento  + incidentes) 

def limpiar_csv(archivo_entrada, archivo_salida, archivo_juegos):
    juegos_df = pd.read_csv(archivo_juegos)
    encuestas_df = pd.read_csv('EncuestaLimpio.csv')
    incidente_df = pd.read_csv('IncidentesSeguridadLimpio.csv')

    with open(archivo_entrada, 'r', encoding='utf-8') as f_entrada, open(archivo_salida, 'r+', encoding='utf-8', newline='') as f_salida:
        lector_csv = csv.DictReader(f_entrada)
        campos = lector_csv.fieldnames + ['coordenadasGPS'] + ['capacidadMax'] + ['cantidadJuegosPorTipo'] + ['estadoGlobalArea']
        escritor_csv = csv.DictWriter(f_salida, fieldnames=campos)
        escritor_csv.writeheader()

        # Obtener distritos y sus códigos
        distritos= obtener_distritos(lector_csv)

        # Reiniciar el lector para escribir el archivo de salida
        f_entrada.seek(0)
        lector_csv = csv.DictReader(f_entrada)   

        cod_postal = obtener_cod_postal(lector_csv)

        # Reiniciar el lector para escribir el archivo de salida
        f_entrada.seek(0)
        lector_csv = csv.DictReader(f_entrada) 

        for fila in lector_csv:
            #quitar tildes
            fila = {k: limpiar_tildes(v) for k, v in fila.items()}

            if fila['FECHA_INSTALACION'] =='' or fila['FECHA_INSTALACION'].lower() == 'fecha_incorrecta':
                fila['FECHA_INSTALACION'] = obtener_fecha_mas_antigua(juegos_df, fila['ID'], 'FECHA_INSTALACION')
            if fila['FECHA_INSTALACION'] == '':
                fila['FECHA_INSTALACION'] = obtener_fecha_mas_antigua(encuestas_df, fila['ID'], 'FECHA')
            if fila['FECHA_INSTALACION'] == '':
                fila['FECHA_INSTALACION'] = obtener_fecha_mas_antigua(incidente_df, fila['ID'], 'FECHA_REPORTE')
            fila['FECHA_INSTALACION'] = intentar_convertir_fecha(fila.get('FECHA_INSTALACION', ''))

            #crear coordenadas
            fila['coordenadasGPS'] = crear_coordenadas(fila.get('LATITUD', ''), fila.get('LONGITUD', ''))

            # Convertir el valor de la columna BARRIO a mayúsculas
            if 'BARRIO' in fila:
                fila['BARRIO'] = fila['BARRIO'].upper()

             # Convertir el valor de la columna DISTRITO a mayúsculas
            if fila['DISTRITO']  != '' :
                fila['DISTRITO'] = fila['DISTRITO'].upper()
            else:
                fila['DISTRITO'] = distritos[fila['COD_DISTRITO']]
            
            if fila['COD_POSTAL'] == '' or int(float(fila['COD_POSTAL'])) == 0:
                fila['COD_POSTAL'] = int(float(cod_postal[fila['BARRIO']]))
            else:
                fila['COD_POSTAL'] = int(float(fila['COD_POSTAL']))
                
            fila['capacidadMax'] = int(fila['TOTAL_ELEM']) + random.randint(1, 10)
            
            juegos_diccionario = juegos_por_tipo(fila['ID'], juegos_df)
            
            fila['cantidadJuegosPorTipo'] = juegos_diccionario

            # Calcular el estado global del área: puntuacion_calidad *10 - (nº juegos en mantenimiento + nº incidentes de seguridad)
            estado_global = obtener_estado_global(fila['ID'], juegos_df, incidente_df, encuestas_df)
            if estado_global < 0:
                fila['estadoGlobalArea'] = 'INSUFICIENTE'
            elif 0 < estado_global < 25:
                fila['estadoGlobalArea'] = 'SUFICIENTE'
            else:
                fila['estadoGlobalArea'] = 'BUENO'
            escritor_csv.writerow(fila)

    df = pd.read_csv(archivo_salida)
    df = df.drop(columns=columnas_a_eliminar, errors='ignore')
    df.to_csv(archivo_salida, index=False)

    valores_nulos = df.isnull().sum()
    num_ceros_codigo_postal = (df['COD_POSTAL'] == 0).sum()

    print(f'Número de valores que son 0 en la columna CODIGO_POSTAL: {num_ceros_codigo_postal}')
    print('Valores nulos por columna:',  valores_nulos)


    contar_valores_repetidos(archivo_salida, 'ID')

archivo_entrada = 'AreasSucio.csv' 
archivo_salida = 'AreaLimpio.csv' 
archivo_juegos = 'JuegosLimpio.csv'
columnas_a_eliminar = ['COD_DISTRITO','COORD_GIS_X', 'COORD_GIS_Y', 'SISTEMA_COORD',  'CONTRATO_COD', 'tipo', 'COD_BARRIO', 'DESC_CLASIFICACION', 'TOTAL_ELEM', 'TIPO_VIA', 'NOM_VIA', 'NUM_VIA', 'DIRECCION_AUX', 'NDP', 'CODIGO_INTERNO' ] 
limpiar_csv(archivo_entrada, archivo_salida, archivo_juegos)
