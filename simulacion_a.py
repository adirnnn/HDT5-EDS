import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

# Semilla aleatoria para reproducibilidad
RANDOM_SEED = 42

# Velocidad del CPU (instrucciones por unidad de tiempo)
CPU_SPEED = 1  

# Tamaño de la memoria RAM
MEMORY_SIZE = 100  

# Intervalo para la distribución exponencial de la llegada de procesos
INTERVAL = 10  

# Número de instrucciones a ejecutar por ciclo de CPU
NUM_INSTRUCTIONS = 3  

class Process:
    def __init__(self, env, process_id, cpu, memory):
        self.env = env
        self.process_id = process_id
        self.cpu = cpu
        self.memory = memory
        self.waiting_time = 0
        self.total_time = 0
        self.instructions_remaining = random.randint(1, 10)
        self.action = env.process(self.run())

    def run(self):
        # Requerimiento de memoria para el proceso
        memory_required = random.randint(1, 10)
        
        # Obtiene la memoria necesaria
        with self.memory.get(memory_required) as req:
            yield req
            
            # Simula el tiempo que toma asignar memoria
            yield self.env.timeout(1)  
            
            # Marca el tiempo de inicio
            start_time = self.env.now
            
            # Ejecución del proceso
            while self.instructions_remaining > 0:
                with self.cpu.request() as req:
                    yield req
                    # Simula la ejecución de instrucciones en el CPU
                    for _ in range(min(self.instructions_remaining, NUM_INSTRUCTIONS)):
                        yield self.env.timeout(1 / CPU_SPEED)
                    self.instructions_remaining -= NUM_INSTRUCTIONS
                    if self.instructions_remaining <= 0:
                        # Calcula el tiempo total de ejecución
                        self.total_time = self.env.now - start_time
                        break
                    else:
                        # Simula la probabilidad de espera
                        waiting_chance = random.randint(1, 21)
                        if waiting_chance == 1:
                            self.action = self.env.process(self.wait())
                        elif waiting_chance == 2:
                            self.ready()  # Llamada corregida
                        else:
                            self.stay_ready()
                            
        # Devuelve la memoria utilizada
        self.memory.put(memory_required)

    def wait(self): # Simula el tiempo de espera para operaciones de I/O.
        start_time = self.env.now
        yield self.env.timeout(1)  
        self.waiting_time += self.env.now - start_time
        self.ready()

    def ready(self): # Prepara el proceso para su ejecución.
        self.action = self.env.process(self.run())

    def stay_ready(self): # Mantiene proceso listo
        pass

def setup(env, num_processes, cpu, memory):
    # Configura los procesos iniciales.
    processes = []
    for i in range(num_processes):
        process = Process(env, i, cpu, memory)
        processes.append(process)
        yield process
        yield env.timeout(random.expovariate(1.0 / INTERVAL))

def run_simulation(num_processes):
    # Ejecuta la simulación.
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    cpu = simpy.Resource(env, capacity=1)
    memory = simpy.Container(env, init=MEMORY_SIZE, capacity=MEMORY_SIZE)
    processes = list(setup(env, num_processes, cpu, memory))
    env.run()

    total_times = [process.total_time for process in processes if hasattr(process, 'total_time')]
    waiting_times = [process.waiting_time for process in processes if hasattr(process, 'waiting_time')]
    return np.mean(total_times), np.std(total_times), np.mean(waiting_times), np.std(waiting_times)

# Lista de cantidades de procesos a simular
num_processes_list = [25, 50, 100, 150, 200]

# Listas para almacenar tiempos promedio y desviaciones estándar
average_total_times = []
std_total_times = []
average_waiting_times = []
std_waiting_times = []

# Itera la lista de cantidades de procesos
for num_processes in num_processes_list:
    total_times = []
    waiting_times = []
    
    # Ejecuta la simulación 5 veces para cada cantidad de procesos
    for _ in range(5):  
        processes = run_simulation(num_processes)
        total_times.append(processes[0])
        waiting_times.append(processes[2])
        
    # Calcula tiempo promedio y desviaciones estándar
    average_total_times.append(np.mean(total_times))
    std_total_times.append(np.std(total_times))
    average_waiting_times.append(np.mean(waiting_times))
    std_waiting_times.append(np.std(waiting_times))

# Grafica los resultados usando matplotlib
plt.figure(figsize=(10, 6))
plt.errorbar(num_processes_list, average_total_times, yerr=std_total_times, fmt='o-', label='Tiempo Promedio en CPU')
plt.errorbar(num_processes_list, average_waiting_times, yerr=std_waiting_times, fmt='o-', label='Tiempo Promedio de Espera')
plt.xlabel('Número de Procesos')
plt.ylabel('Tiempo Promedio')
plt.title('Tiempo Promedio en CPU y Tiempo Promedio de Espera vs. Número de Procesos')
plt.legend()
plt.grid(True)
plt.show()