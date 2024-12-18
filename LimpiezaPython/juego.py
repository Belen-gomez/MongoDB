import csv
import random
from datetime import datetime
import csv
import pandas as pd
from scipy.spatial import cKDTree

def limpiar_tildes(texto):
    if isinstance(texto, str):
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

def contar_valores_nulos_por_columna(lector_csv):
    conteo_nulos = {campo: 0 for campo in lector_csv.fieldnames}
    
    for fila in lector_csv:
        for campo in conteo_nulos.keys():
            if fila[campo] == '' or fila[campo] is None:
                conteo_nulos[campo] += 1
    
    return conteo_nulos

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

def obtener_fecha_mantenimiento(id):
    mantenimiento_df = pd.read_csv(archivo_mantenimiento)
    
    fecha = mantenimiento_df[mantenimiento_df['JuegoID'] == int(id)]['FECHA_INTERVENCION'].tolist()
    if len(fecha) > 0:
        return max(fecha), len(fecha)
    else:     
        return "Ausente", 0

def obtener_fecha_area(areaID):
    area_df = pd.read_csv(archivo_areas)
    
    fecha = area_df[area_df['ID'] == areaID]['FECHA_INSTALACION'].tolist()
    if len(fecha) == 1:
        return min(fecha)
    else:
        if(len(fecha) > 1):
            print("Juego con id que si tiene fecha", areaID)
        return ''
    
def obtner_accesibilidad(areaID):
    encuenta_df = pd.read_csv(archivo_encuestas)
    
    accesibilidad = encuenta_df[encuenta_df['AreaRecreativaID'] == areaID]['PUNTUACION_ACCESIBILIDAD'].tolist()
    if len(accesibilidad) > 0:
        return sum(accesibilidad) / len(accesibilidad)
    else:
        return ''

def obtener_area_mas_cercana(juegos_coords, areas_df):
    # Convertir las coordenadas a arrays numpy
   
    areas_coords = areas_df[['LATITUD', 'LONGITUD']].to_numpy()

    # Crear un KDTree para las áreas
    tree = cKDTree(areas_coords)

    # Encontrar el índice del área más cercana para cada juego
    distancias, indices = tree.query(juegos_coords)

    # Asignar el área más cercana a cada juego
    area_id = areas_df.iloc[indices]['ID']

    return area_id

def limpiar_csv(archivo_entrada, archivo_salida):
    area_df = pd.read_csv(archivo_areas)

    with open(archivo_entrada, 'r', encoding='utf-8') as f_entrada, open(archivo_salida, 'r+', encoding='utf-8', newline='') as f_salida:
        lector_csv = csv.DictReader(f_entrada)
        campos = lector_csv.fieldnames+ ['indicadorExposicion'] + ['ultimaFechaMantenimiento'] + ['desgasteAcumulado'] + ['AreaRecreativaID']
        escritor_csv = csv.DictWriter(f_salida, fieldnames=campos)
        escritor_csv.writeheader()

        for fila in lector_csv:
            # quitar tildes
            fila = {k: limpiar_tildes(v) for k, v in fila.items()}

            # Obtener las coordenadas del juego
            juego_coords = [float(fila['LATITUD']), float(fila['LONGITUD'])]

            # Obtener el área más cercana para el juego
            fila['AreaRecreativaID'] = obtener_area_mas_cercana(juego_coords, area_df)
            
            fila['ultimaFechaMantenimiento'], n_matenimientos = obtener_fecha_mantenimiento(fila['ID'])
            if fila['FECHA_INSTALACION'] == '' or fila['FECHA_INSTALACION'] == "fecha_incorrecta":
                fila['FECHA_INSTALACION'] = obtener_fecha_area(fila['AreaRecreativaID'])
            
            fila['FECHA_INSTALACION'] = intentar_convertir_fecha(fila.get('FECHA_INSTALACION', ''))
                        
            accesible = obtner_accesibilidad(fila['AreaRecreativaID'])
            if accesible == '':
                fila['ACCESIBLE'] = "Desconocido"
            elif accesible > 3:
                fila['ACCESIBLE'] = True
            else:
                fila['ACCESIBLE'] = False
            
            indicador = random.randint(1,3)
            if indicador == 1:
                fila['indicadorExposicion'] = 'bajo'
            elif indicador == 2:
                fila['indicadorExposicion'] = 'medio'
            else:
                fila['indicadorExposicion'] = 'alto'

            fila['desgasteAcumulado'] = random.randint(1,15) * indicador*100 - (n_matenimientos*100)
            
            if fila['MODELO'] == '':
                fila['MODELO'] = fila['DESC_CLASIFICACION']
            
            fila['ID'] = str(fila['ID'])
            
            escritor_csv.writerow(fila)
       
    df = pd.read_csv(archivo_salida)
    df = df.drop(columns=columnas_a_eliminar, errors='ignore')
    df.to_csv(archivo_salida, index=False)

    df = pd.read_csv(archivo_salida)
    valores_nulos = df.isnull().sum()
    print('Valores nulos por columna:',  valores_nulos)
    eliminar_duplicados(archivo_salida, 'ID')

    contar_valores_repetidos(archivo_salida, 'ID')



archivo_entrada = 'JuegosSucio.csv' 
archivo_salida = 'JuegosLimpio.csv' 
archivo_mantenimiento = 'MantenimientoLimpio.csv'
archivo_areas = 'AreaLimpioConCoordenadas.csv'
area_df = pd.read_csv(archivo_areas)
archivo_encuestas = 'EncuestaLimpio.csv'
columnas_a_eliminar = ['NDP','CODIGO_INTERNO','DESC_CLASIFICACION', 'COORD_GIS_X', 'COORD_GIS_Y', 'SISTEMA_COORD', 'CONTRATO_COD', 'BARRIO', 'COD_BARRIO', 'DISTRITO', 'COD_DISTRITO', 'LATITUD', 'LONGITUD', 'TIPO_VIA', 'NOM_VIA', 'NUM_VIA', 'COD_POSTAL','DIRECCION_AUX']
limpiar_csv(archivo_entrada, archivo_salida)
