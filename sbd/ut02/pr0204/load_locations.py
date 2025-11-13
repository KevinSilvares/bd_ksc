{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "eff9a727-12af-4ea7-8057-706bb855f15c",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "True\n"
     ]
    }
   ],
   "source": [
    "# Conexión a la BD\n",
    "import redis, locations\n",
    "\n",
    "r = redis.Redis(\n",
    "    host = \"redis\",\n",
    "    port = 6379,\n",
    "    db = 0,\n",
    "    decode_responses = True\n",
    ")\n",
    "\n",
    "print(r.ping())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "d8aefd63-5c51-48ef-8a19-efa06ac1e9df",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Datos cargados\n"
     ]
    }
   ],
   "source": [
    "# Carga de datos\n",
    "data = locations.POIS\n",
    "\n",
    "for poi in data:\n",
    "    r.geoadd(\"poi:locations\", (poi[\"lon\"], poi[\"lat\"], poi[\"id\"]))\n",
    "    r.hset(\"poi:info\", poi[\"id\"], poi[\"name\"])\n",
    "\n",
    "print(\"Datos cargados\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
