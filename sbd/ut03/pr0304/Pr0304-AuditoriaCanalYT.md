# PR0304 - Auditoría y evolución de un canal de YouTube

### Importaciones y configuración base


```python
import requests
import pandas as pd
import math

API_KEY = "AIzaSyDSicSU_3Qrn8mmI3aRqTJW3KsUDmrmJDo"
CHANNEL_ID = "UCZcvCpFcLxOKGbMocVgLjEA" 
BASE_URL = 'https://www.googleapis.com/youtube/v3'
```

## Obtención vídeos (Channels: list)


```python
def get_uploads_playlist_id(channel_id):
    """Paso 1: Obtener el ID de la lista de reproducción 'Uploads' del canal"""
    url = f"{BASE_URL}/channels?part=contentDetails&id={channel_id}&key={API_KEY}"
    response = requests.get(url).json()
    
    try:
        # TODO: Extrae el id del playlist (está en la clave uploads)
        # ...
        print(response)
        
        #return playlist_id
    except KeyError:
        print("Error al obtener la playlist. Revisa el ID del canal y tu API Key.")
        return None
```


```python
get_uploads_playlist_id(CHANNEL_ID)
```

    {'kind': 'youtube#channelListResponse', 'etag': 'wZVzfwRVOdsLVmeUpSAPjQz6azc', 'pageInfo': {'totalResults': 1, 'resultsPerPage': 5}, 'items': [{'kind': 'youtube#channel', 'etag': 'MMVuyO3_OLpLDxTakdLqzK55phc', 'id': 'UCZcvCpFcLxOKGbMocVgLjEA', 'contentDetails': {'relatedPlaylists': {'likes': '', 'uploads': 'UUZcvCpFcLxOKGbMocVgLjEA'}}}]}


## Obtención lista de vídeos (PlaylistItems: list)


```python
def get_all_video_ids(playlist_id):
    """Paso 2: Obtener todos los IDs de los videos de la playlist"""
    video_ids = []
    next_page_token = None
    
    print("Extrayendo IDs de videos...")
    
    while True:
        url = f"{BASE_URL}/playlistItems?part=contentDetails&maxResults=50&playlistId={playlist_id}&key={API_KEY}"
        
        # TODO: Si existe un next_page_token, añádelo a la URL (&pageToken=...)
        # ...
        
        response = requests.get(url).json()
        
        for item in response.get('items', []):
            video_ids.append(item['contentDetails']['videoId'])
            
        # TODO: Lógica de paginación. 
        # Busca 'nextPageToken' en la respuesta. Si existe, actualiza la variable. Si no, rompe el bucle.
        # ...
        break # BORRAR ESTE BREAK CUANDO IMPLEMENTES LA PAGINACIÓN
        
    print(f"Total de videos encontrados: {len(video_ids)}")
    return video_ids
```

## Obtención de datos de cada vídeo (Videos: list)


```python
def get_video_details(video_ids):
    """Paso 3: Obtener estadísticas de los videos en lotes de 50"""
    all_video_data = []
    
    # TODO: Agrupa la lista video_ids en sub-listas de máximo 50 elementos.
    # ...
    
    # Este bucle simula el procesamiento por lotes (debes adaptarlo a tus sub-listas)
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        
        ids_string = ','.join(chunk)
        url = f"{BASE_URL}/videos?part=snippet,statistics,contentDetails&id={ids_string}&key={API_KEY}"
        
        response = requests.get(url).json()
        
        # TODO: de cada vídeo, extraer: id, title, publishedAt, ViewCount, likeCount, CommentCount, duration
        # Guardar los datos en un diccionario y anexarlo a all_video_data
        # ...
            
    return all_video_data
```

### Formato duración


```python
def parse_duration(iso_duration):
    """Paso 4: Transformar la duración ISO 8601 (ej: PT1H2M10S) a segundos totales"""
    # TODO: Convierte la duración de ISO8601 a segundos
    # ...

    return iso_duration 
```

## Main


```python
if __name__ == "__main__":
    print("Iniciando pipeline de ingesta...")
    
    uploads_id = get_uploads_playlist_id(CHANNEL_ID)
    
    if uploads_id:
        lista_ids = get_all_video_ids(uploads_id)
        datos_completos = get_video_details(lista_ids)
        
        df = pd.DataFrame(datos_completos)
        
        # Limpieza básica
        df['fecha_publicacion'] = pd.to_datetime(df['fecha_publicacion'])
        
        print("\nMuestra de los datos extraídos:")
        print(df.head())
        
        # 5. Guardar en un formato analítico
        # TODO: Utiliza el método de Pandas adecuado para guardar el DataFrame en formato Parquet.
        # Nombra el archivo como 'dataset_canal_youtube.parquet'.
        # ...
        
        print("\nPipeline finalizado. Revisa tus archivos locales.")
```

    Iniciando pipeline de ingesta...



    ---------------------------------------------------------------------------

    NameError                                 Traceback (most recent call last)

    Cell In[11], line 4
          1 if __name__ == "__main__":
          2     print("Iniciando pipeline de ingesta...")
    ----> 4     uploads_id = get_uploads_playlist_id(CHANNEL_ID)
          6     if uploads_id:
          7         lista_ids = get_all_video_ids(uploads_id)


    Cell In[4], line 10, in get_uploads_playlist_id(channel_id)
          4 response = requests.get(url).json()
          6 try:
          7     # TODO: Extrae el id del playlist (está en la clave uploads)
          8     # ...
    ---> 10     return playlist_id
         11 except KeyError:
         12     print("Error al obtener la playlist. Revisa el ID del canal y tu API Key.")


    NameError: name 'playlist_id' is not defined

