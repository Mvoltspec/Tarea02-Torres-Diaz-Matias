import requests
import subprocess
import sys
import getopt

# Función: consulta el fabricante de una dirección MAC usando una API externa
def consultar_mac(direccion_mac):
    # Construimos la URL con la dirección MAC que queremos consultar
    url = f"https://api.maclookup.app/v2/macs/{direccion_mac}"
    try:
        # Realizamos la solicitud HTTP GET a la API
        respuesta = requests.get(url)

        # Verificamos si la solicitud fue exitosa
        if respuesta.status_code == 200:
            datos = respuesta.json()  # Convertir a JSON para manipular los datos
            if 'company' in datos:  # Verificamos si se encontró la información de la compañía
                print(f"Dirección MAC: {direccion_mac}")
                print(f"Fabricante: {datos['company']}")
                # Mostramos el tiempo que tomó la respuesta
                print(f"Tiempo de respuesta: {respuesta.elapsed.total_seconds() * 1000:.2f} ms")
            else:
                print(f"Dirección MAC: {direccion_mac}")
                print("Fabricante: No encontrado en la base de datos.")
        else:
            # Si el código de estado no es 200, significa que algo salió mal en la API
            print(f"Error al consultar la API. Código de estado: {respuesta.status_code}")
    except requests.RequestException as error:
        # En caso de que haya un error durante la solicitud
        print(f"Error en la solicitud: {error}")

# Función: Muestra tabla ARP y consulta los fabricantes de las MACs encontradas
def mostrar_arp():
    try:
        # Ejecutamos el comando 'arp -a'para obtener la tabla ARP de la red local
        resultado = subprocess.check_output("arp -a", shell=True, text=True)

        # Dividimos el resultado en líneas para procesar más fácilmente
        lineas = resultado.splitlines()

        # Recorremos línea por línea el resultado de la tabla ARP
        for linea in lineas:
            partes = linea.split()  # Divide cada linea para usarlo como separador

            # Nos aseguramos de que la línea tenga más de un elemento antes de procesarla
            if len(partes) > 1:
                ip = partes[0]  # Primera parte es la dirección IP
                mac = partes[1]  # Segunda parte es la dirección MAC

                # Evitamos direcciones MAC especiales que no son de interés
                if mac not in ["ff-ff-ff-ff-ff-ff", "00-00-00-00-00-00", "incompl"]:
                    print(f"Consultando fabricante para la MAC: {mac}")
                    consultar_mac(mac)  # Consultamos el fabricante de esta dirección MAC

    except subprocess.CalledProcessError as error:
        # Si el comando 'arp -a' falla, mostramos un mensaje de error
        print(f"Error al obtener la tabla ARP: {error}")

# Función: muestra un mensaje como ayuda para el usuario
def mostrar_ayuda():
    print("Uso: python OUILookup.py --mac <direccion_mac> | --arp | [--help]")
    print("--mac: Consulta el fabricante de una dirección MAC. ejemplo: aa:bb:cc:00:00:00 (Agregar una mac dentro del código para que funcione)")
    print("--arp: Muestra los fabricantes de los dispositivos en la tabla ARP")
    print("--help: Muestra este mensaje de ayuda")

# Función principal: maneja los argumentos proporcionados por el usuario
def main(argv):
    try:
        # Obtenemos los argumentos y opciones que el usuario ingresa en la línea de comandos
        opts, args = getopt.getopt(argv, "hm:a", ["help", "mac=", "arp"])
    except getopt.GetoptError:
        # Si hay un error en los argumentos, mostramos la ayuda y salimos del programa
        mostrar_ayuda()
        sys.exit(2)

    # Inicializamos las variables
    direccion_mac = None  # Esta variable guardará la dirección MAC si se proporciona
    mostrar_arp_flag = False  # Bandera que indica si debemos mostrar la tabla ARP

    # Recorremos las opciones que el usuario ingresó
    for opt, arg in opts:
        if opt in ("-h", "--help"):  # Si el usuario pide ayuda
            mostrar_ayuda()
            sys.exit()
        elif opt in ("-m", "--mac"):  # Si el usuario ingresó una dirección MAC
            direccion_mac = arg
        elif opt in ("-a", "--arp"):  # Si el usuario pidió mostrar la tabla ARP
            mostrar_arp_flag = True

    # Tomamos acciones según los argumentos proporcionados
    if direccion_mac:  # Si se proporciona una dirección MAC, consultamos su fabricante
        consultar_mac(direccion_mac)
    elif mostrar_arp_flag:  # Si se solicita la tabla ARP, la mostramos
        mostrar_arp()
    else:
        # Si no se proporciona ni una dirección MAC ni la opción ARP, mostramos la ayuda
        mostrar_ayuda()

# Ejecutamos el programa si se llama directamente desde la terminal
if __name__ == "__main__":
    main(sys.argv[1:])
