import time
import numpy as np
import sounddevice as sd
from pynput.mouse import Button, Controller

# --- CONFIGURACIÓN ---
SAMPLE_RATE = 44100
BLOCK_SIZE = 512

# UMBRAL DE SENSIBILIDAD: Ajústalo según tu micrófono y qué tan fuerte sea el golpe.
UMBRAL = 0.05

# Cooldown (en segundos) para evitar múltiples clics por un solo golpe con eco o rebote.
COOLDOWN = 0.05 
ultimo_clic = 0

mouse = Controller()

def audio_callback(indata, frames, time_info, status):
    global ultimo_clic
    if status:
        return
    
    # Calcular la amplitud (RMS / norma del bloque de audio)
    volumen = np.linalg.norm(indata) / np.sqrt(len(indata))
    
    # Si supera el umbral, hacemos clic
    if volumen > UMBRAL:
        tiempo_actual = time.time()
        if (tiempo_actual - ultimo_clic) > COOLDOWN:
            mouse.click(Button.left, 1)
            print(f"¡Golpe detectado! Volumen: {volumen:.4f} -> Clic ejecutado")
            ultimo_clic = tiempo_actual

def seleccionar_dispositivo():
    print("--- Dispositivos de audio de entrada disponibles ---")
    dispositivos = sd.query_devices()
    
    # Filtrar solo los dispositivos que tienen canales de entrada (input_channels > 0)
    entradas = []
    for i, dev in enumerate(dispositivos):
        if dev['max_input_channels'] > 0:
            entradas.append((i, dev['name']))
            print(f"[{i}] {dev['name']} (Canales: {dev['max_input_channels']})")
            
    if not entradas:
        print("¡No se encontraron dispositivos de entrada de audio!")
        exit(1)
        
    while True:
        try:
            seleccion = int(input("\nIngresa el número del dispositivo que deseas usar: "))
            # Validar que el ID exista y sea un dispositivo de entrada válido
            if any(id_dev == seleccion for id_dev, _ in entradas):
                return seleccion
            else:
                print("Número no válido o corresponde a un dispositivo sin entrada. Inténtalo de nuevo.")
        except ValueError:
            print("Por favor, ingresa un número válido.")

def main():
    print("--- Detector de Golpes con Selector de Micrófono ---")
    
    # Mostrar selector y obtener el ID elegido
    device_id = seleccionar_dispositivo()
    
    print(f"\nIniciando escucha en el dispositivo ID {device_id}...")
    print(f"Umbral actual: {UMBRAL} | Presiona Ctrl + C en la terminal para detener.\n")
    
    # Abrir el flujo de audio especificando el dispositivo elegido
    try:
        with sd.InputStream(device=device_id,
                            callback=audio_callback,
                            channels=1,
                            samplerate=SAMPLE_RATE,
                            blocksize=BLOCK_SIZE):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nScript detenido por el usuario.")

if __name__ == "__main__":
    main()