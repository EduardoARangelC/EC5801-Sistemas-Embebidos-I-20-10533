import logging
import sys

# Clase para configurar el sistema de logging
class Gestor_Log:
    
    @staticmethod
    def configurar_canal(__nombre__: str) -> logging.Logger:
        # Creamos el logger
        logger = logging.getLogger(__nombre__)
        logger.setLevel(logging.DEBUG)

        # Configurar la salida a consola
        consola_handler = logging.StreamHandler(stream=sys.stdout)
        consola_handler.setLevel(logging.DEBUG)

        # (Nivel) [Hora] -> Mensaje
        formato = logging.Formatter(
            fmt='(%(levelname)s) [%(asctime)s] -> %(message)s',
            datefmt='%H:%M:%S'
        )
        consola_handler.setFormatter(formato)
        
        # Agregamos el handler al logger
        logger.addHandler(consola_handler)
        return logger

# Bloque de prueba
if __name__ == "__main__":
    # Configuración del logger
    log = Gestor_Log.configurar_canal(__name__)

    # DEBUG
    registro_id = 2010533
    log.debug(f"Verificando dirección de memoria del registro. ID: {registro_id}")

    # INFO
    log.info("Bucle principal de ejecución iniciado correctamente")

    # WARNING
    log.warning("Fluctuación detectada en la tasa de refresco de datos")

    # ERROR
    log.error("Fallo matemático en el procesamiento de señales")

    # CRITICAL
    log.critical("Detención del script. Estado del sistema CRITICO")