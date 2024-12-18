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


def obtener_valores_unicos_tipo(archivo_csv):
    # Leer el archivo CSV
    df = pd.read_csv(archivo_csv)
    
    # Obtener los valores únicos de la columna ID
    valores_unicos = df['ID'].unique()
    
    return valores_unicos

def limpiar_csv(archivo_entrada, archivo_salida):

    with open(archivo_entrada, 'r', encoding='utf-8') as f_entrada, open(archivo_salida, 'w', encoding='utf-8', newline='') as f_salida:
        lector_csv = csv.DictReader(f_entrada)
        campos = lector_csv.fieldnames
        escritor_csv = csv.DictWriter(f_salida, fieldnames=campos)
        escritor_csv.writeheader()

        for fila in lector_csv:
            #quitar tildes
            fila = {k: limpiar_tildes(v) for k, v in fila.items()}
            
            fila['FECHA'] = intentar_convertir_fecha(fila.get('FECHA', ''))

            escritor_csv.writerow(fila)
              
    df = pd.read_csv(archivo_salida)
    
    valores_nulos = df.isnull().sum()
    print('Valores nulos por columna:',  valores_nulos)

    contar_valores_repetidos(archivo_salida, 'ID')

archivo_entrada = 'EncuestasSatisfaccionSucio.csv'
archivo_salida = 'EncuestaLimpio.csv'
limpiar_csv(archivo_entrada, archivo_salida)
