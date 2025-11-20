# PR0203 - Estructuras de datos avanzadas


```python
import redis
import datetime

leaderboard_key = "leaderboard"
log_base_key = "unique:players:"

initial_score = 0

r = redis.Redis(
    host = "redis",
    port = 6379,
    db = 0,
    decode_responses = True
)

print(r.ping())
```

    True


### Gestión de jugadores.


```python
def add_player(id, name, country, score = initial_score):
    r.hset(f"player:{id}", mapping={
        "name": name,
        "country": country,
        "games_played": 1,
        "score": score,
    })

    r.zadd(leaderboard_key, {id: score})
```


```python
def update_score(id, points):
    id_player = f"player:{id}"
    
    r.hset(id_player, mapping={
        "score": points,
    })
    games_played = int(r.hget(id_player, "games_played"))
    r.hset(id_player, mapping={
        "games_played": games_played + 1
    })

    r.zadd(leaderboard_key, {id: points})
```


```python
def player_info(id):
    print(r.hgetall(f"player:{id}"))
```


```python
def show_top_player(n):
    info = (r.zrevrange(leaderboard_key, 0, n -1, withscores=True))
    print("Top Jugadores")
    for id, score in info:
        player_name = r.hget(f"player:{id}", "name")
        print(f"{player_name}: {score}")
```

### Registro de actividad diaria (HyperLogLog) 


```python
def register_login(player_id):
    date = datetime.date.today().isoformat()
    r.pfadd(f"{log_base_key}{date}", player_id)
```


```python
def count_unique_logins(date):
    print(r.pfcount(f"{log_base_key}{date}"))
```


```python
def weekly_report(dates):
    r.pfmerge(f"{log_base_key}week", f"{log_base_key}{dates[0]}", f"{log_base_key}{dates[1]}")
    print(r.pfcount(f"{log_base_key}week"))
```

### Reseteo sistema


```python
def reset_system():
    players_ids = (r.zrange(leaderboard_key, 0, -1))

    for id in players_ids:
        player_keys = r.hkeys(f"player:{id}")
        r.hdel(f"player:{id}", *player_keys)
        r.zrem(leaderboard_key, id)
```
