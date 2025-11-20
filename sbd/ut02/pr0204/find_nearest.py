{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "8e76035c-d49a-486e-a180-4937c46e2276",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Localización del usuario predefinida (Pueta del Sol)\n",
    "user_location = {\n",
    "    \"lat\": 40.41677,\n",
    "    \"lon\": -3.70379,\n",
    "}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "605e228f-7418-42cb-b546-27cb26e0af62",
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
   "execution_count": 23,
   "id": "f745b08e-1436-486d-ab84-21ee65f36500",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "El POI más cercano es Puerta del Sol, que está a 0.0004 km.\n"
     ]
    }
   ],
   "source": [
    "nearest_poi = r.geosearch(\n",
    "    \"poi:locations\", \n",
    "    longitude = user_location[\"lon\"], \n",
    "    latitude = user_location[\"lat\"],\n",
    "    radius = 2000,\n",
    "    unit = \"km\",\n",
    "    count = 1,\n",
    "    withdist = True\n",
    ")\n",
    "\n",
    "print(f\"El POI más cercano es {r.hget('poi:info', nearest_poi[0][0])}, que está a {nearest_poi[0][1]} km.\")"
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
