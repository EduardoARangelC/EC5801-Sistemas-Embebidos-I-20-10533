import sys
import logging
import threading
import time
from typing import Callable, Any, Dict, Optional

# Clase para configurar el sistema de logging del inciso 1
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


# Logger global para funciones externas
log_global = Gestor_Log.configurar_canal("App")

# Clase para gestionar hilos por semáforo
class Gestor_Hilos:
    def __init__(self, backlog: int):
        self.semaphore = threading.Semaphore(backlog)
        self.registry: Dict[str, Dict[str, Any]] = {}
        # Configuración del logger para esta clase
        self.logger = Gestor_Log.configurar_canal("Gestor_Hilos")
    
    # Función para alojar un hilo en el registro
    def Thread_Allocate(self, name: str, func: Callable, *args: Any, **kwargs: Any) -> None:
        if name in self.registry:
            self.logger.warning(f"El hilo '{name}' ya está registrado")
            return
        
        self.registry[name] = {
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'callback_start': None,
            'callback_end': None,
            'event': threading.Event(), 
            'thread': None
        }
        self.logger.info(f"Hilo '{name}' alojado correctamente")

    # Función para registrar callbacks de un hilO
    def Thread_Callback_Register(self, name: str, callback_start: Optional[Callable] = None, callback_end: Optional[Callable] = None) -> None:
        if name not in self.registry:
            self.logger.error(f"No se puede registrar callbacks: el hilo '{name}' no existe")
            return
        # Verificar si el hilo está en ejecución antes de modificar callbacks
        thread_info = self.registry[name]
        if thread_info['thread'] is not None and thread_info['thread'].is_alive():
            self.logger.error(f"No se pueden modificar callbacks. El hilo '{name}' ya está en ejecución")
            return

        if callback_start: 
            thread_info['callback_start'] = callback_start
        if callback_end:
            thread_info['callback_end'] = callback_end
            
        self.logger.info(f"Callbacks registrados exitosamente para '{name}'")
    
    # Función para ejecutar el hilo con semáforo y callbacks
    def worker(self, name: str) -> None:
        thread_info = self.registry[name]

        with self.semaphore:
            if thread_info['callback_start']:
                thread_info['callback_start']()

            kwargs = thread_info['kwargs'].copy()
            kwargs['stop_event'] = thread_info['event']
            
            try:
                thread_info['func'](*thread_info['args'], **kwargs)
            except Exception as e:
                self.logger.error(f"Excepción en la ejecución de '{name}': {e}")
            finally:
                if thread_info['callback_end']:
                    thread_info['callback_end']()

    # Función para iniciar un hilo
    def Thread_Start(self, name: str) -> None:
        if name not in self.registry:
            self.logger.error(f"No se puede iniciar: el hilo '{name}' no existe")
            return

        thread_info = self.registry[name]
        if thread_info['thread'] is not None and thread_info['thread'].is_alive():
            self.logger.warning(f"El hilo '{name}' ya se encuentra en ejecución")
            return

        thread_info['event'].clear()
        t = threading.Thread(target=self.worker, args=(name,), name=name)
        thread_info['thread'] = t
        t.start()

    # Función para detener un hilo
    def Thread_End(self, name: str) -> None:
        if name not in self.registry:
            self.logger.error(f"No se puede detener: el hilo '{name}' no existe")
            return
            
        self.logger.info(f"Señal de detención enviada al hilo '{name}'")
        self.registry[name]['event'].set()

    # Función para esperar a que un hilo termine
    def Thread_Join(self, name: str) -> None:
        if name not in self.registry:
            return
            
        thread = self.registry[name]['thread']
        if thread is not None and thread.is_alive():
            thread.join()
            self.logger.info(f"Finalización completada para '{name}'")

# Función de prueba
def Tarea(tarea_id: int, stop_event: threading.Event, repeticiones: int = 5):
    log_global.info(f"Iniciando tarea #{tarea_id}")
    # Simulamos un trabajo con iteraciones
    for i in range(repeticiones):
        if stop_event.is_set():
            log_global.warning(f"Tarea #{tarea_id} abortada antes de tiempo")
            return
            
        log_global.info(f"Tarea #{tarea_id} procesando iteración {i+1}/{repeticiones}...")
        time.sleep(1)
        
    log_global.info(f"Tarea #{tarea_id} completada exitosamente")

if __name__ == "__main__":
    # Configuración del gestor de hilos
    gestor = Gestor_Hilos(backlog=2)

    # Alojamos dos hilos con la función Tarea con diferentes parámetros
    gestor.Thread_Allocate("Hilo_A", Tarea, tarea_id=1, repeticiones=4)
    gestor.Thread_Allocate("Hilo_B", Tarea, tarea_id=2, repeticiones=8)

    log_global.info("Iniciando hilos...")
    # Iniciamos ambos hilos
    gestor.Thread_Start("Hilo_A")
    gestor.Thread_Start("Hilo_B")

    # Esperamos un poco antes de enviar la señal de detención al Hilo_B
    time.sleep(3)

    # Detenemos el Hilo_B antes de que complete su tarea
    gestor.Thread_End("Hilo_B")

    # Esperamos a que ambos hilos terminen
    gestor.Thread_Join("Hilo_A")
    gestor.Thread_Join("Hilo_B")

    log_global.info("Programa principal finalizado")
