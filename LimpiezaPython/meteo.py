import pandas as pd
from datetime import datetime

def obtener_codigo_postal(punto_muestreo):
    df_CODIGO = pd.read_csv('estaciones_meteo_CodigoPostal.csv', sep=';', header=0)
    codigo_postal = df_CODIGO[df_CODIGO['CÓDIGO'] == int(punto_muestreo)]['Codigo Postal'].tolist()
    if len(codigo_postal) > 0:
        return codigo_postal[0]
    else:
        return None
# Leer el archivo CSV original
df = pd.read_csv('meteo24.csv', sep=';', header=0)

# Crear una lista para almacenar las nuevas filas
new_rows = []
id = 0
# Iterar sobre cada fila del archivo original
for index, row in df.iterrows():
    punto_muestreo = row['PUNTO_MUESTREO'].strip()[:8] 
    fecha_base = row[5:7].astype(str).str.cat(sep='-')
    
    # Iterar sobre cada día del mes
    for day in range(1, 32):
        valor = row[f'D{day:02d}']
        valid = row[f'V{day:02d}']
        
        if valid.strip() == 'V':
            fecha = f"{fecha_base}-{day:02d}"
            fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d')
            magnitud = row['MAGNITUD']
            if magnitud == 81:
                if valor!= '' and valor>1.5:
                    viento = True
                else:
                    viento = False
                temperatura = None
                precipitaciones = None
            elif magnitud == 83:
                viento = None
                temperatura = valor
                precipitaciones = None
            elif magnitud == 89:
                viento = None
                temperatura = None
                precipitaciones = valor
            codigo_postal = obtener_codigo_postal(punto_muestreo)
            id +=1
            new_rows.append([ id, punto_muestreo, fecha, temperatura, viento, precipitaciones, codigo_postal])
        

# Crear un nuevo DataFrame con las nuevas filas
new_df = pd.DataFrame(new_rows, columns=['ID', 'Punto_Muestreo', 'Fecha', 'Temperatura', 'Viento', 'Precipitaciones', 'CODIGO_POSTAL'])

# Agrupar por Punto_Muestro y Fecha, y combinar las magnitudes en una sola fila
grouped_df = new_df.groupby(['Punto_Muestreo', 'Fecha']).agg({
    'Temperatura': 'first',
    'Viento': 'first',
    'Precipitaciones': 'first',
    'ID': 'first',
    'CODIGO_POSTAL': 'first'
}).reset_index()
num_nulos_id = grouped_df['CODIGO_POSTAL'].isnull().sum()
print(f'Número de valores nulos en la columna ID: {num_nulos_id}')

grouped_df.to_csv('meteo24Limpio.csv', index=False, sep=',')