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

def eliminar_duplicados(archivo_csv, columna):
    # Leer el archivo CSV
    df = pd.read_csv(archivo_csv)
    
    # Eliminar duplicados
    df_sin_duplicados = df.drop_duplicates(subset=[columna], keep='first')
    
    # Guardar el archivo CSV resultante
    df_sin_duplicados.to_csv(archivo_csv, index=False)
    print(f'Duplicados eliminados en la columna {columna}.')

def intentar_convertir_fecha(campo):
    formatos = [
        '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%Y-%m-%d', '%Y/%m/%d',
        '%d/%m/%y', '%d-%m-%y', '%m-%d-%Y', '%m-%d-%y'
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

def obtener_timepo_resolucion(mantenimiento_df, fecha, id, estado):
    lista_id = []
    if ',' not in id:
        lista_id.append(id[2:-2])
    else:
        cadena_limpia = id.strip("[]").replace("'", "")
        # Dividir la cadena por comas para obtener los ids
        lista_id = [elemento.strip() for elemento in cadena_limpia.split(",")]

    fechas_intervencion = []
    for intervencion in lista_id:
        fechas_int =mantenimiento_df[mantenimiento_df['ID'] == intervencion]['FECHA_INTERVENCION'].tolist()
        if(len(fechas_int) ==0):
            print("No se ha encontrado en el otro csv " , lista_id)
        else:
            fechas_intervencion.append(fechas_int[0])
    
    ultima_fecha = max(fechas_intervencion)    
    # Convertir las fechas a objetos datetime
    fecha = datetime.strptime(fecha, '%Y-%m-%d')
    ultima_fecha = datetime.strptime(ultima_fecha, '%Y-%m-%d')
    if fecha > ultima_fecha:
        diferencia_dias = -1
    else:
        diferencia_dias = (ultima_fecha- fecha).days
    return diferencia_dias

def obtener_valores_unicos_tipo(archivo_csv):
    # Leer el archivo CSV
    df = pd.read_csv(archivo_csv)
    
    # Obtener los valores únicos de la columna TIPO_INCIDENCIA
    valores_unicos = df['TIPO_INCIDENCIA'].unique()
    
    return valores_unicos

def obtener_nivel_escalamiento(usuario_id):
    usuario_id = usuario_id.split(',')
    if len(usuario_id) ==1:
        return 'POCO URGENTE'
    elif len(usuario_id) ==2:
        return 'URGENTE'
    else:
        return 'MUY URGENTE'

def obtener_juego_id(id, mantenimiento_df):
    lista_id = []
    if ',' not in id:
        lista_id.append(id[2:-2])
    else:
        cadena_limpia = id.strip("[]").replace("'", "")
        # Dividir la cadena por comas para obtener los elementos individuales
        lista_id = [elemento.strip() for elemento in cadena_limpia.split(",")]

    mantenimientos = []
    for mantenimiento in lista_id:
        juegos_id =mantenimiento_df[mantenimiento_df['ID'] == mantenimiento]['JuegoID'].tolist()
        if(len(juegos_id) ==0):
            print("No se ha encontrado en el otro csv " , lista_id)
        else:
            mantenimientos.append(juegos_id[0])

    if len(mantenimientos) > 0 and all(x == mantenimientos[0] for x in mantenimientos):
        return mantenimientos[0]
    else:
        print("Los valores en mantenimientos no son todos iguales:", mantenimientos)
        return 0

def limpiar_csv(archivo_entrada, archivo_salida):
    mantenimiento_df = pd.read_csv(mantenimiento)
    with open(archivo_entrada, 'r', encoding='utf-8') as f_entrada, open(archivo_salida, 'w', encoding='utf-8', newline='') as f_salida:
        lector_csv = csv.DictReader(f_entrada)
        campos = lector_csv.fieldnames + ['tiempoResolucion'] + ['JuegoID'] + ['nivelEscalamiento']
        escritor_csv = csv.DictWriter(f_salida, fieldnames=campos)
        escritor_csv.writeheader()

        for fila in lector_csv:
            #quitar tildes
            fila = {k: limpiar_tildes(v) for k, v in fila.items()}

            # convertir la fecha
            fila['FECHA_REPORTE'] = intentar_convertir_fecha(fila.get('FECHA_REPORTE', ''))
            if fila['ESTADO'] == "Cerrada":
                fila['tiempoResolucion'] = obtener_timepo_resolucion(mantenimiento_df, fila['FECHA_REPORTE'], fila['MantenimientoID'], fila['ESTADO'])
            else:
                fila['tiempoResolucion'] = -1
            fila['nivelEscalamiento'] = obtener_nivel_escalamiento(fila['UsuarioID'])
            fila['JuegoID'] = obtener_juego_id(fila['MantenimientoID'], mantenimiento_df)
            escritor_csv.writerow(fila)

    df = pd.read_csv(archivo_salida)
    valores_nulos = df.isnull().sum()
    print('Valores nulos por columna:',  valores_nulos)

    # Eliminar duplicados basados en la columna ID
    eliminar_duplicados(archivo_salida, 'ID')

    contar_valores_repetidos(archivo_salida, 'ID')

archivo_entrada = 'IncidenciasUsuariosSucio.csv'  
archivo_salida = 'IncidenciasUsuariosLimpio_v1.csv'  
mantenimiento = 'MantenimientoLimpio.csv'
limpiar_csv(archivo_entrada, archivo_salida)
