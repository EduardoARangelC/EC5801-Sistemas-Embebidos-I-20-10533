import sys
import logging
import queue
import threading
import time
from typing import Callable, Any, Dict, Optional, Tuple

# Clase logger de la tarea anterior (Tarea 3)
class Gestor_Log:
    @staticmethod
    def configurar_canal(__nombre__: str) -> logging.Logger:
        logger = logging.getLogger(__nombre__)
        logger.setLevel(logging.DEBUG)

        if not logger.handlers:
            consola_handler = logging.StreamHandler(stream=sys.stdout)
            consola_handler.setLevel(logging.DEBUG)

            formato = logging.Formatter(
                fmt='(%(levelname)s) [%(asctime)s] -> %(message)s',
                datefmt='%H:%M:%S'
            )
            consola_handler.setFormatter(formato)
            logger.addHandler(consola_handler)
            
        return logger
# Logger global para funciones externas
log_global = Gestor_Log.configurar_canal("App")

# Gestor de Mensajería
class Messages_Manager:
    def __init__(self):
        self._queues: Dict[str, queue.Queue] = {}
        self._callbacks: Dict[str, Callable[[Any], None]] = {}
        
        # Mutex para proteger el acceso a las estructuras de datos compartidas
        self._lock = threading.Lock()
        
        # Sistema de logging interno del gestor
        self.logger = Gestor_Log.configurar_canal("Messages_Manager")
    
    # Función de creación de colas
    def create(self, name: str, maxsize: int = 0, callback: Optional[Callable[[Any], None]] = None) -> None: 
        with self._lock: 
            # Verificación de que la cola no exista previamente
            if name in self._queues:    
                self.logger.warning(f"La cola '{name}' ya existe")
                return
            # Creación de la cola con el tamaño máximo especificado
            self._queues[name] = queue.Queue(maxsize=maxsize)
            if callback is not None:
                self._callbacks[name] = callback
            
            self.logger.info(f"Cola '{name}' creada con exito")

    # Eliminación de colas
    def delete(self, name: str) -> None:
        with self._lock: 
            if name not in self._queues:
                self.logger.error(f"Error al eliminar: la cola '{name}' no existe")
                return
            # Para eliminar la cola primero la vaciamos
            target_queue = self._queues[name]
            with target_queue.mutex:
                target_queue.queue.clear()

            del self._queues[name]
            if name in self._callbacks:
                del self._callbacks[name]

            self.logger.info(f"Cola '{name}' eliminada del sistema")

    # Enviar datos de las colas
    def send(self, name: str, data: Any) -> None:
        # Obtenemos la referencia a la cola
        with self._lock:
            target_queue = self._queues.get(name)
        
        if target_queue is None:
            self.logger.error(f"No se puede enviar: la cola '{name}' no existe")
            return

        try:
            self.logger.info(f"Intentando enviar datos a '{name}'")
            target_queue.put(data, block=True)
            self.logger.info(f"Datos depositados con éxito en la cola '{name}'")
        except Exception as e:
            self.logger.error(f"Error al enviar datos a '{name}': {e}")
    
    # Extrae datos de las colas
    def receive(self, name: str) -> Optional[Tuple[str, Any]]:
        with self._lock:
            target_queue = self._queues.get(name)

        if target_queue is None:
            self.logger.error(f"No se puede recibir: la cola '{name}' no existe")
            return None

        try:
            data = target_queue.get(block=False)
            self.logger.info(f"Dato extraído exitosamente de la cola '{name}'")
            return (name, data)
        except queue.Empty:
            return None
        
    # Iteración de Polling para revisar las colas activas
    def poll(self) -> None:

        with self._lock:
            active_queue_names = list(self._queues.keys())

        for name in active_queue_names:
            # Revisamos cada cola para ver si hay datos disponibles
            res = self.receive(name)
            if res is not None:
                q_name, data = res
                with self._lock:
                    register = self._callbacks.get(q_name)
                
                if register:
                    try:
                        register(data)
                    except Exception as e:
                        self.logger.error(f"Error al ejecutar el callback de '{q_name}': {e}")
                
                with self._lock:
                    if q_name in self._queues:
                        self._queues[q_name].task_done()

# Demostración de uso
if __name__ == "__main__":
    
    # Callbacks de ejemplo
    def register_critico(datos: Any):
        log_global.info(f"[PROCESADOR CRÍTICO] Alerta del sistema procesada: {datos}")

    def register_events(datos: Any):
        log_global.info(f"[PROCESADOR EVENTOS] Evento registrado: {datos}")
   
    # Iniciamos el gestor de mensajes
    manager = Messages_Manager()

    # Creamos dos colas con diferentes propósitos
    manager.create("Alertas", maxsize=2, callback=register_critico)
    manager.create("Eventos", maxsize=10, callback=register_events)

    # Evento de parada para el hilo productor
    shutdown_event = threading.Event()

    # Hilo Productor externo que simula la generación de alertas y eventos
    def productor_externo(event: threading.Event):
        log_global.info("[Hilo Secundario] Ejecutando bucle")
        while not event.is_set():
            manager.send("Alertas", "VOLTAJE_ALTO_BATERIA")
            manager.send("Eventos", {"temperatura": 35})
            time.sleep(2)

    # Pasamos el evento a través de los argumentos del hilo
    t_prod = threading.Thread(
        target=productor_externo, 
        kwargs={'event': shutdown_event}, 
        name="Productor_Externo"
    )
    t_prod.start()

    log_global.info("Iniciando ciclo principal")
    # El bucle principal lee durante un tiempo simulado
    for i in range(5):
        log_global.info(f"[Loop Principal] Muestreo #{i+1}")
        manager.poll()
        time.sleep(0.5)

    # El hilo principal apaga los hilos secundarios
    log_global.warning("Apagando los hilos...")
    shutdown_event.set()

    # Espera a la culminación del hilo secundario
    t_prod.join()
    
    manager.delete("Alertas")
    manager.delete("Eventos")
    log_global.info("Programa finalizado de manera limpia")