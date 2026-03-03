# PR0304 - Auditoría y evolución de un canal de YouTube

### Importaciones y configuración base


```python
!pip install isodate
```

    Collecting isodate
      Downloading isodate-0.7.2-py3-none-any.whl.metadata (11 kB)
    Downloading isodate-0.7.2-py3-none-any.whl (22 kB)
    Installing collected packages: isodate
    Successfully installed isodate-0.7.2



```python
import requests
import pandas as pd
import math
import isodate

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
        playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        return playlist_id
    except KeyError:
        print("Error al obtener la playlist. Revisa el ID del canal y tu API Key.")
        return None
```

## Obtención lista de vídeos (PlaylistItems: list)


```python
def get_all_video_ids(playlist_id):
    """Paso 2: Obtener todos los IDs de los videos de la playlist"""
    video_ids = []
    next_page_token = None
    
    print("Extrayendo IDs de videos...")
    
    while True:
        if not next_page_token:
            url = f"{BASE_URL}/playlistItems?part=contentDetails&maxResults=50&playlistId={playlist_id}&key={API_KEY}"
        else:
            url = f"{BASE_URL}/playlistItems?part=contentDetails&maxResults=50&playlistId={playlist_id}&key={API_KEY}&pageToken={next_page_token}"
            
        response = requests.get(url).json()
            
        for item in response.get('items', []):
            video_ids.append(item['contentDetails']['videoId'])

        #print(response)
        # TODO: Lógica de paginación. 
        # Busca 'nextPageToken' en la respuesta. Si existe, actualiza la variable. Si no, rompe el bucle.
        try:
            next_page_token = response["nextPageToken"]
        except KeyError:
            break
        
    print(f"Total de videos encontrados: {len(video_ids)}")
    return video_ids
```

### Formato duración


```python
def parse_duration(iso_duration):
    """Paso 4: Transformar la duración ISO 8601 (ej: PT1H2M10S) a segundos totales"""
    return isodate.parse_duration(iso_duration).total_seconds()
```

## Obtención de datos de cada vídeo (Videos: list)


```python
def get_video_details(video_ids):
    """Paso 3: Obtener estadísticas de los videos en lotes de 50"""
    all_video_data = []
    
    # TODO: Agrupa la lista video_ids en sub-listas de máximo 50 elementos.
    
    # Este bucle simula el procesamiento por lotes (debes adaptarlo a tus sub-listas)
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]

        ids_string = ','.join(chunk)
        
        url = f"{BASE_URL}/videos?part=snippet,statistics,contentDetails&id={ids_string}&key={API_KEY}"
        
        response = requests.get(url).json()
        # TODO: de cada vídeo, extraer: id, title, publishedAt, ViewCount, likeCount, CommentCount, duration
        # Guardar los datos en un diccionario y anexarlo a all_video_data
        for item in response["items"]:
            all_video_data.append({
                "id" : item["id"],
                "publishedAt" : item["snippet"]["publishedAt"],
                "view_count" : item["statistics"]["viewCount"],
                "like_count" : item["statistics"]["likeCount"],
                "comment_count" : item["statistics"]["commentCount"],
                "duration" : parse_duration(item["contentDetails"]["duration"]),
            })
        
    return all_video_data
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
        df['publishedAt'] = pd.to_datetime(df['publishedAt'])
        
        print("\nMuestra de los datos extraídos:")
        print(df.head())
        
        # 5. Guardar en un formato analítico
        # TODO: Utiliza el método de Pandas adecuado para guardar el DataFrame en formato Parquet.
        # Nombra el archivo como 'dataset_canal_youtube.parquet'.
        df.to_parquet("dataset_canal_youtube.parquet")
        
        print("\nPipeline finalizado. Revisa tus archivos locales.")
```

    Iniciando pipeline de ingesta...
    Extrayendo IDs de videos...
    Total de videos encontrados: 96
    
    Muestra de los datos extraídos:
                id               publishedAt view_count like_count comment_count  \
    0  bDRVjoVn0Fg 2026-01-08 15:01:11+00:00     495301      40214          1032   
    1  cWm6rExjaAw 2025-11-27 16:01:05+00:00     440793      28703          1017   
    2  mWfW4Rnltew 2025-11-06 15:01:33+00:00     233157      20648           966   
    3  HDjhze0znNI 2025-09-16 15:00:33+00:00    1806043      58793          1503   
    4  FFeJwnUzbzU 2025-09-10 15:03:08+00:00     163579      14166           687   
    
       duration  
    0     704.0  
    1     841.0  
    2     718.0  
    3     758.0  
    4      70.0  
    
    Pipeline finalizado. Revisa tus archivos locales.

