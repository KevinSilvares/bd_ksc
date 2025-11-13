{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "c60268ba-9ab7-481e-ba4f-3e27bc0342ce",
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
   "execution_count": 3,
   "id": "47b6fa0e-5bf7-4417-9c6b-f5cbf51437bd",
   "metadata": {},
   "outputs": [],
   "source": [
    "import redis\n",
    "\n",
    "r = redis.Redis(\n",
    "    host = \"redis\",\n",
    "    port = 6379,\n",
    "    db = 0,\n",
    "    decode_responses = True\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "id": "c056202e-14bf-4ebb-9dab-6e3ca22155c0",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "-> Matadero Madrid (poi_019)\n",
      "-> Catedral de la Almudena (poi_012)\n",
      "-> Palacio Real (poi_004)\n",
      "-> Templo de Debod (poi_010)\n",
      "-> Plaza de Cascorro (El Rastro) (poi_018)\n",
      "-> Mercado de San Miguel (poi_011)\n",
      "-> Plaza Mayor (poi_005)\n",
      "-> Puerta del Sol (poi_001)\n",
      "-> Museo Reina Sofía (poi_006)\n",
      "-> CaixaForum Madrid (poi_017)\n",
      "-> Museo del Prado (poi_002)\n",
      "-> Museo Thyssen-Bornemisza (poi_007)\n",
      "-> Gran Vía (Plaza Callao) (poi_009)\n",
      "-> Plaza de España (poi_016)\n",
      "-> Plaza de Cibeles (poi_014)\n",
      "-> Estadio Santiago Bernabéu (poi_008)\n",
      "-> Estación de Atocha (poi_013)\n",
      "-> Parque del Retiro (poi_003)\n",
      "-> Puerta de Alcalá (poi_015)\n",
      "-> Estadio Cívitas Metropolitano (poi_020)\n"
     ]
    }
   ],
   "source": [
    "nearest_pois = r.geosearch(\n",
    "    \"poi:locations\", \n",
    "    longitude = user_location[\"lon\"], \n",
    "    latitude = user_location[\"lat\"],\n",
    "    radius = 2000,\n",
    "    unit = \"km\"\n",
    ")\n",
    "\n",
    "for poi in nearest_pois:\n",
    "    print(f\"-> {r.hget('poi:info', poi)} ({poi})\")"
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
