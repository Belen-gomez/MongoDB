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

def limpiar_csv(archivo_entrada, archivo_salida):

    with open(archivo_entrada, 'r', encoding='utf-8') as f_entrada, open(archivo_salida, 'w', encoding='utf-8', newline='') as f_salida:
        lector_csv = csv.DictReader(f_entrada)
        campos = lector_csv.fieldnames
        escritor_csv = csv.DictWriter(f_salida, fieldnames=campos)
        escritor_csv.writeheader()

        for fila in lector_csv:
            #quitar tildes
            fila = {k: limpiar_tildes(v) for k, v in fila.items()}

            telefono = fila['TELEFONO'].replace(' ', '')  # Eliminar todos los espacios en blanco

            fila['TELEFONO'] = telefono

            escritor_csv.writerow(fila)

    df = pd.read_csv(archivo_salida)
    df = df.drop(columns=columnas_a_eliminar, errors='ignore')
    df.to_csv(archivo_salida, index=False)

    valores_nulos = df.isnull().sum()
    print('Valores nulos por columna:',  valores_nulos)

    # Eliminar duplicados basados en la columna NIF
    eliminar_duplicados(archivo_salida, 'NIF')

    contar_valores_repetidos(archivo_salida, 'NIF')

archivo_entrada = 'UsuariosSucio.csv'
archivo_salida = 'UsuariosLimpio.csv'
columnas_a_eliminar = ['Email'] 
limpiar_csv(archivo_entrada, archivo_salida)
