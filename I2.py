import urllib.parse
import requests

route_url = "https://graphhopper.com/api/1/route?"
key = "e35861dd-b8d6-4808-bf37-1f835a44cf05"  #api key

def geocoding(location, key):
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})

    try:
        replydata = requests.get(url)
        replydata.raise_for_status()  #Verificar si funciona
        json_data = replydata.json()

        if 'hits' in json_data and len(json_data['hits']) > 0:
            lat = json_data["hits"][0]["point"]["lat"]
            lng = json_data["hits"][0]["point"]["lng"]
            return 200, lat, lng
        else:
            print(f"No se encontraron resultados para {location}.")
            return 404, None, None
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud HTTP: {e}")
        return replydata.status_code if 'replydata' in locals() else 500, None, None

def calcular_distancia_duracion_indicaciones(origen, destino, key, vehiculo):
    #codificar origen y destino
    orig_status, orig_lat, orig_lng = geocoding(origen, key)
    dest_status, dest_lat, dest_lng = geocoding(destino, key)

    if orig_status != 200 or dest_status != 200:
        print("Error en la geocodificación. No se puede calcular la distancia y duración.")
        return None, None, None

    #elegir transporte en español 
    vehiculo_dict = {"auto": "car", "bicicleta": "bike", "caminar": "foot"}
    vehiculo_api = vehiculo_dict.get(vehiculo, "car")

    #ruta entre origen y destino
    route_params = {
        "point": [f"{orig_lat},{orig_lng}", f"{dest_lat},{dest_lng}"],
        "vehicle": vehiculo_api,  # Modo de transporte
        "key": key,
        "instructions": "true",  #Incluir instrucciones
        "locale": "es"  #Instrucciones en español
    }

    try:
        route_response = requests.get(route_url, params=route_params)
        route_response.raise_for_status()
        route_data = route_response.json()

        if 'paths' not in route_data or len(route_data['paths']) == 0:
            print("No se encontró una ruta válida entre los puntos.")
            return None, None, None

        #distancia y duración de la ruta
        distance_meters = route_data['paths'][0]['distance']
        duration_seconds = route_data['paths'][0]['time'] / 1000  #milisegundos a segundos
        instrucciones = route_data['paths'][0]['instructions']  #Instrucciones de la ruta

        distance_km = distance_meters / 1000  #Convertir a kilómetros
        distance_miles = distance_km * 0.621371  #Convertir a millas
        duration_hms = convertir_duracion(duration_seconds)

        return distance_km, distance_miles, duration_hms, instrucciones
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud HTTP para la ruta: {e}")
        return None, None, None

def convertir_duracion(segundos):
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segundos = int(segundos % 60)
    return f"{horas:02}:{minutos:02}:{segundos:02}"

def generar_narrativa(origen, destino, distancia_km, distancia_miles, duracion, instrucciones):
    narrativa = (f"El viaje desde {origen} hasta {destino} cubre una distancia de aproximadamente "
                 f"{distancia_km:.2f} kilómetros ({distancia_miles:.2f} millas). "
                 f"La duración estimada del viaje es de {duracion} (horas:minutos:segundos). "
                 "Aquí están las indicaciones detalladas:\n")
    for instruccion in instrucciones:
        distancia_instruccion = instruccion['distance'] / 1000  #Convertir a kilómetros
        narrativa += f"{instruccion['text']} durante {distancia_instruccion:.2f} kilómetros.\n"
    return narrativa

def calcular_consumo_combustible(kilometros_recorridos, litros_por_100km=10):
    consumo_combustible = (kilometros_recorridos / 100) * litros_por_100km
    return consumo_combustible

def generar_narrativa_consumo(consumo_combustible):
    return f"Consumo de combustible estimado para el viaje: {consumo_combustible:.2f} litros."

#Bucle para solicitar origen y destino o hasta que el usuario escriba "s"
while True:
    origen = input("Ingrese la Ciudad de Origen (o escriba 's' para salir): ")
    if origen.lower() == "s":
        break
    destino = input("Ingrese la Ciudad de Destino (o escriba 's' para salir): ")
    if destino.lower() == "s":
        break

    vehiculo = input("Ingrese el medio de transporte (auto, bicicleta, caminar): ").lower()

    #Calcular distancia, duración y obtener indicaciones entre origen y destino proporcionados por el usuario
    distancia_km, distancia_miles, duracion, instrucciones = calcular_distancia_duracion_indicaciones(origen, destino, key, vehiculo)

    if distancia_km is not None and duracion is not None and instrucciones is not None:
        narrativa = generar_narrativa(origen, destino, distancia_km, distancia_miles, duracion, instrucciones)
        print(narrativa)

        #Calcular y mostrar el consumo de combustible
        if vehiculo == 'auto':
            consumo_combustible = calcular_consumo_combustible(distancia_km)
            narrativa_consumo = generar_narrativa_consumo(consumo_combustible)
            print(narrativa_consumo)