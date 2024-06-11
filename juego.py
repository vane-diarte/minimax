import tkinter as tk
from tkinter import messagebox
import random

class JuegoGatoRaton:
    def __init__(self, raiz, tamaño=10):
        self.tamaño = tamaño
        self.raiz = raiz
        self.tablero = [[0] * tamaño for _ in range(tamaño)]
        self.gato_pos = (0, 0)
        self.raton_pos = (tamaño - 1, tamaño - 1)
        self.pos_inicial_gato = self.gato_pos
        self.obstaculos = self.generar_obstaculos()
        self.turno_raton = True
        self.canvas = tk.Canvas(raiz, width=400, height=400)
        self.canvas.pack()        
        self.historial = HistorialMovimientos()
        self.historial.agregar_movimiento(self.gato_pos, self.raton_pos)        
        self.dibujar_tablero()
        self.canvas.bind("<Button-1>", self.seleccionar_celda)
        self.delay = 500  # Retraso en milisegundos entre movimientos
        
        self.ultimo_movimiento_gato = []
        self.ultimo_movimiento_raton = []

    def generar_obstaculos(self):
        obstaculos = set() # conjunto que permite guardar valores sin que se repitan
        while len(obstaculos) < (self.tamaño * self.tamaño) // 5:
            x = random.randint(0, self.tamaño - 1)
            y = random.randint(0, self.tamaño - 1)
            if (x, y) != self.gato_pos and (x, y) != self.raton_pos and (x, y) not in self.posiciones_iniciales():
                #si x e y son diferentes a la posicion del gato y del raton y tambien de las posibles posiciones inicialles se agregan los obstaculos
                obstaculos.add((x, y))
        return obstaculos
    
    # metodo para que los obstaculos no se agreguen en las direcciones posibles de movimiento inicial
    def posiciones_iniciales(self):
        posiciones = set()
        
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Direcciones posibles: arriba, abajo, izquierda, derecha
        for dx, dy in direcciones:
            nuevo_x_gato = self.gato_pos[0] + dx
            nuevo_y_gato = self.gato_pos[1] + dy
            
             # Verificar si la nueva posición está dentro del tablero
            if 0 <= nuevo_x_gato < self.tamaño and 0 <= nuevo_y_gato < self.tamaño:
                posiciones.add((nuevo_x_gato, nuevo_y_gato))
                
            # Posiciones posibles para el ratón
            nuevo_x_raton = self.raton_pos[0] + dx
            nuevo_y_raton = self.raton_pos[1] + dy            
            
            # Verificar si la nueva posición está dentro del tablero
            # que no sea menor que cero y al mismo tiempo que sea menor que el tamanho del tablero
            if 0 <= nuevo_x_raton < self.tamaño and 0 <= nuevo_y_raton < self.tamaño:
                posiciones.add((nuevo_x_raton, nuevo_y_raton)) #se agrega los valores a la nueva posicion del gato y del raton
                
        return posiciones
    
    
 
    def dibujar_tablero(self):
        self.canvas.delete("all") #elimina todos los elementos dibujados previamente en el lienzo
        tamaño_celda = 400 // self.tamaño #se divide la cantidad de pixeles del lienzo por el numero de celdas
        for i in range(self.tamaño): #itera sobre las filas del tablero
            for j in range(self.tamaño): #itera sobre las columnas del tablero
                x1, y1 = i * tamaño_celda, j * tamaño_celda #calcula el tamanho de la celda i= fila j= columna
                x2, y2 = x1 + tamaño_celda, y1 + tamaño_celda
                color = "white" #color de la celda 
                if (i, j) in self.obstaculos: #si las coordenadas de la iteracion coinciden con las del obstaculo se pinta en negro
                    color = "pink"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
        self.actualizar_posiciones()

    def actualizar_posiciones(self):
        tamaño_celda = 400 // self.tamaño
        gato_x, gato_y = self.gato_pos #obtiene las coordenadas actuales del gato
        raton_x, raton_y = self.raton_pos #obtiene las coordenadas actuales del raton
        
        self.canvas.create_oval(gato_x * tamaño_celda, gato_y * tamaño_celda, #especifican la esquina superior izquierda del óvalo
                                (gato_x + 1) * tamaño_celda, #especifican la esquina inferior derecha
                                (gato_y + 1) * tamaño_celda,
                                fill="gold") #relleno
        
        self.canvas.create_oval(raton_x * tamaño_celda, raton_y * tamaño_celda,
                                (raton_x + 1) * tamaño_celda, 
                                (raton_y + 1) * tamaño_celda,
                                fill="purple") #relleno

    def seleccionar_celda(self, evento):
        tamaño_celda = 400 // self.tamaño
        x, y = evento.x // tamaño_celda, evento.y // tamaño_celda
        
        if self.turno_raton and (x, y) in self.movimientos_posibles(self.raton_pos):
            #si es el turno del raton y si los movimientos son posibles desde su posicion actual
            self.raton_pos = (x, y) #Actualiza la posición del ratón a la celda en la que se hizo clic
            self.historial.agregar_movimiento(self.gato_pos, self.raton_pos) #registra el movimiento
            
            self.dibujar_tablero() #vuelve a dibujar el tablero despues de actualizar 
            if self.raton_pos == self.pos_inicial_gato:
                self.mostrar_mensaje_ganaste()
            else:
                self.turno_raton = False
                self.raiz.after(self.delay, self.mover_gato) #el gato se mueve llamando al metodo mover_gato despues de un retraso
                
                

    """ ----------------------- metodo para mover al gato -------------------------- """
    def mover_gato(self):
        _, mejor_movimiento = self.minimax(self.tablero, self.gato_pos, self.raton_pos, 8, True, float('-inf'), float('inf'))
        
        # Verificar si el movimiento se repite
        if mejor_movimiento in self.ultimo_movimiento_gato:
            for mov in self.movimientos_posibles(self.gato_pos):
                #si el mejor movimiento se repite, se busca otro movimiento posible que no sea igual al anterior
                if mov != mejor_movimiento:
                    mejor_movimiento = mov
                    break
        
        self.ultimo_movimiento_gato.append(mejor_movimiento)
        if len(self.ultimo_movimiento_gato) > 2:
            self.ultimo_movimiento_gato.pop(0)

        self.gato_pos = mejor_movimiento
        self.historial.agregar_movimiento(self.gato_pos, self.raton_pos)
        self.dibujar_tablero()
        if self.gato_pos == self.raton_pos:
            self.mostrar_mensaje_perdido()
        else:
            self.turno_raton = True
            self.raiz.after(self.delay, self.mover_raton)

    
    
    """ ----------------------- metodo para mover al raton -------------------------- """
    
    def mover_raton(self):
        _, mejor_movimiento = self.minimax(self.tablero, self.gato_pos, self.raton_pos, 5, False, float('-inf'), float('inf'))
        
        # Verificar si el movimiento se repite
        if mejor_movimiento in self.ultimo_movimiento_raton:
            for mov in self.movimientos_posibles(self.raton_pos):
            #si el mejor movimiento se repite, se busca otro movimiento posible que no sea igual al anterior
                if mov != mejor_movimiento:
                    mejor_movimiento = mov
                    break

        self.ultimo_movimiento_raton.append(mejor_movimiento)  
        #Agrega el mejor movimiento actual a la lista de los últimos movimientos del ratón.
        if len(self.ultimo_movimiento_raton) > 2:
            self.ultimo_movimiento_raton.pop(0)

        self.raton_pos = mejor_movimiento #actualiza la posicion del raton con el mejor movimiento
        self.historial.agregar_movimiento(self.gato_pos, self.raton_pos) #Registra el movimiento del ratón en el historial de movimientos.
        self.dibujar_tablero()
        
        if self.raton_pos == self.pos_inicial_gato:
            self.mostrar_mensaje_ganaste()
        elif self.gato_pos == self.raton_pos:
            self.mostrar_mensaje_perdido()
        else:
            self.turno_raton = False #cambia el turno al gato

            self.raiz.after(self.delay, self.mover_gato) 
    def mostrar_mensaje_perdido(self):
        messagebox.showinfo("Juego Terminado", "El gato atrapo al reton.")
        self.raiz.quit()

    def mostrar_mensaje_ganaste(self):
        messagebox.showinfo("Juego Terminado", "El raton se escapo.")
        self.raiz.quit()
        
        
        
    """ ----------------------- FUNCION DE EVALUACION / DISTANCIA MANHATAN -------------------------- """    

    def evaluar_estado(self, gato_pos, raton_pos):
        if gato_pos == raton_pos:
            return float('inf')
        distancia = abs(gato_pos[0] - raton_pos[0]) + abs(gato_pos[1] - raton_pos[1])
        return -distancia 
    
    


    """ ----------------------- MINIMAX -------------------------- """
    
    def minimax(self, tablero, gato_pos, raton_pos, profundidad, max_jugador, alpha, beta):
        if gato_pos == raton_pos or profundidad == 0: #si el gato esta en la misma casilla que el raton y la profundidad llego a cero
            return self.evaluar_estado(gato_pos, raton_pos), gato_pos 
            #devuelve el resultado de la funcion evaluar estado y la posicion actual del gato
        
        if max_jugador:
            max_eval = float('-inf') #valor extremo para max
            mejor_movimiento = gato_pos
            for mov in self.movimientos_posibles(gato_pos): #itera sobre todos los movimientos posibles del gato
                eval, _ = self.minimax(tablero, mov, raton_pos, profundidad - 1, False, alpha, beta) #llama recursivamente a la función minimax
                if eval > max_eval:
                    max_eval = eval #actualiza la variable si el numero es mayor a max_eval
                    mejor_movimiento = mov #elige el mejor movimiento en base a la evaluacion
                alpha = max(alpha, eval) #actualiza el valor de alfa 
                if beta <= alpha: #verifica si alfa es mayor o igual a beta para hacer la poda
                    break
            return max_eval, mejor_movimiento
        
        else:
            min_eval = float('inf') #valor extremo para min
            mejor_movimiento = raton_pos
            for mov in self.movimientos_posibles(raton_pos): #itera sobre todos los movimientos posibles del raton
                eval, _ = self.minimax(tablero, gato_pos, mov, profundidad - 1, True, alpha, beta) 
                #llama recursivamente a la función minimax y resta uno a la profundidad cada vez que se llama
                if eval < min_eval:
                    min_eval = eval #actualiza la variable si el numero es menor a min_eval
                    mejor_movimiento = mov #elige el mejor movimiento en base a la evaluacion
                beta = min(beta, eval)
                if beta <= alpha: #si alfa es mayor o igual que beta se poda el arbol (deja de evaluar nodos restantes)
                    break
            return min_eval, mejor_movimiento
        
        
        
    """ ----------------------- Movimientos permitidos para cada jugador -------------------------- """
    
    def movimientos_posibles(self, pos):
        x, y = pos
        posibles = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nuevo_x, nuevo_y = x + dx, y + dy
            if 0 <= nuevo_x < len(self.tablero) and 0 <= nuevo_y < len(self.tablero) and (nuevo_x, nuevo_y) not in self.obstaculos:
                posibles.append((nuevo_x, nuevo_y))
        return posibles
    
    
    
#lista doblemente enlazada para recorrer la lista hacia adelante y hacia atras

class Nodo:
    def __init__(self, gato_pos, raton_pos):
        self.gato_pos = gato_pos
        self.raton_pos = raton_pos
        self.siguiente = None
        self.anterior = None
        

#Metodo para agregar movimientos
class HistorialMovimientos:
    def __init__(self):
        self.cabeza = None
        self.cola = None

    def agregar_movimiento(self, gato_pos, raton_pos):
        nuevo_nodo = Nodo(gato_pos, raton_pos)
        if self.cola:
            self.cola.siguiente = nuevo_nodo
            nuevo_nodo.anterior = self.cola
            self.cola = nuevo_nodo
        else:
            self.cabeza = self.cola = nuevo_nodo

    def deshacer_movimiento(self):
        if self.cola and self.cola.anterior:
            self.cola = self.cola.anterior
            self.cola.siguiente = None
        elif self.cola:
            self.cabeza = self.cola = None

if __name__ == "__main__":
    raiz = tk.Tk()
    juego = JuegoGatoRaton(raiz)
    raiz.mainloop()
