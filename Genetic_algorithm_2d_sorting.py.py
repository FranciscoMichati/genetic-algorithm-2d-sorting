# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 17:40:26 2022

@author: Francisco
"""

# Celda 1
# Instalar libreria Pygame

# Importar librerias
import numpy as np
import pygame
import math
import random
from matplotlib import pyplot as plt


# Variables
lifespan = 1250
mutation_rate = 0.005

# Celda 2
# Clase Vector


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # __add__ me dice que pasa cuando calleo Vector1+Vector2
    def __add__(self, otro):
        x = self.x + otro.x
        y = self.y + otro.y
        return Vector(x, y)

    def __mul__(self, numero):
        return Vector(self.x * numero, self.y * numero)

    # __str__ me dice que pasa cuando ejecuto print(Vector)
    def __str__(self):
        return "(" + str(self.x) + " " + str(self.y) + ")"

    def normalizar(self):
        norma = np.sqrt(self.x**2 + self.y**2)
        return Vector(self.x / norma, self.y / norma)

    @staticmethod
    def crear_vector_random():
        return Vector(
            np.random.uniform(
                0,
                2.0) - 1,
            np.random.uniform(
                0,
                2.0) - 1)


# Clase ADN
class ADN:
    def __init__(self, gen=[]):
        if len(gen) != 0:
            self.genes = gen
        else:
            self.genes = []
            for i in range(lifespan):
                vec = Vector.crear_vector_random()
                vec.normalizar()
                # Multiplico por .1 para disminuir el modulo
                self.genes.append(vec * .1)
    # Funcion que me calcula, dado 2 ADNs, un nuevo ADN hijo con la mitad de
    # cada uno

    def crossover(self, otro):
        aux = []
        mid = len(self.genes) / 2
        for i in range(len(self.genes)):
            if i > mid:
                aux.append(self.genes[i])
            else:
                aux.append(otro.genes[i])
        nuevo_adn = ADN(aux)
        return nuevo_adn


# Celda 5
# Clase Bola: métodos
class Bola:
    def __init__(self, color, tamaño, lifespan, adn=None, elite=False):
      # Posicion, velocidad y aceleraciones iniciales:
        self.posicion = Vector(200, 300)
        self.velocidad = Vector(0, 0)
        self.aceleracion = Vector(0, 0)
        # adn
        if adn is None:
            self.adn = ADN()
        else:
            self.adn = adn
        # Contador de frames y tiempo maximo de vida
        self.contador = 0
        self.lifespan = lifespan
        # Flags para ver si la bola colisionó contra un obstaculo, el objetivo
        # o una pared, respectivamente
        self.vivo = True
        self.win = False
        self.colision_pared = False
        # Tamaño de las bolas
        self.tamaño = tamaño
        # Crea el rectangulo para las colisiones
        self.rectangulo = pygame.Rect(
            self.posicion.x, self.posicion.y, self.tamaño, self.tamaño)
        self.color = color
        # Elite flag, por defecto es False
        self.elite = elite
        # Contador de tiempo
        self.timer = []

    # Metodos

    def apply_force(self, fuerza):
        self.aceleracion = self.aceleracion + fuerza

    def update(self):
        self.apply_force(self.adn.genes[self.contador])
        self.contador = self.contador + 1
        if self.vivo and self.win == False and self.colision_pared == False:
            self.velocidad = self.velocidad + self.aceleracion
            self.posicion = self.posicion + self.velocidad
            self.aceleracion = Vector(0, 0)
            self.rectangulo = pygame.Rect(
                self.posicion.x, self.posicion.y, self.tamaño, self.tamaño)

    def show(self):
        pygame.draw.circle(screen, self.color,
                           (self.posicion.x, self.posicion.y), self.tamaño)

    def fitness(self, Objetivo):
        fitness_rate = 1.0
        # Penaliza el fitness si choca contra un obstaculo
        if not self.vivo:
            fitness_rate = .2  # 1: modifica

        # Penaliza el fitness si choca contra una pared
        if self.colision_pared:
            fitness_rate = .2  # 1:  modifica

        # Opcional, contribuye al fitness si colisiona con el objetivo
        # if self.win==True:
            # fitness_rate=1 #No modifica

        # Penalizacion por el tiempo que tarda: Si no se llega al objetivo, se penaliza con la inversa del tiempo de vida.
        # Si se llega al objetivo, se penaliza con la inversa del tiempo que tarda en llegar.
        # Esto resulta en que si dos bolas llegan al objetivo, la que llega
        # antes ve penalizado su fitness score en menor medida.
        if len(self.timer) > 0:
            time_penalty = 1 / self.timer[0]
        else:
            time_penalty = 1 / self.lifespan
        distance = np.sqrt((self.posicion.x - Objetivo.posicion.x)
                           ** 2 + (self.posicion.y - Objetivo.posicion.y)**2)
        d = 1.0 / (distance**2)
        return d * fitness_rate * time_penalty

    def paredes(self):
        if self.posicion.x >= ancho - self.tamaño / \
                2 or self.posicion.x <= 0 + self. tamaño / 2:
            self.colision_pared = True
        if self.posicion.y >= alto - self.tamaño / \
                2 or self.posicion.y <= self.tamaño / 2:
            self.colision_pared = True

    def mutar(self, mutation_rate):
        if not self.elite:
            for i in range(self.lifespan):
                valor_random = np.random.rand()
                if valor_random < mutation_rate:
                    self.adn.genes[i] = Vector.crear_vector_random()


# Clase Obstaculo
class Obstaculo:
    def __init__(self, x, y, ancho, alto, color):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.color = color
        self.rectangulo = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        self.posicion = Vector(self.x, self.y)

    def show(self):
        pygame.draw.rect(screen, self.color,
                         (self.x, self.y, self.ancho, self.alto))

    def obstacle_ball_collision(self, Bola):
        if pygame.Rect.colliderect(Bola.rectangulo, self.rectangulo):
            Bola.vivo = False


# Clase Objetivo
class Objetivo:
    def __init__(self, x, y, ancho, alto, color):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.color = color
        self.rectangulo = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        self.posicion = Vector(self.x, self.y)

    def show(self):
        pygame.draw.rect(screen, self.color,
                         (self.x, self.y, self.ancho, self.alto))

    def objetivo_ball_collision(self, Bola):
        if pygame.Rect.colliderect(Bola.rectangulo, self.rectangulo):
            Bola.win = True
            Bola.timer.append(Bola.contador)


# colores RGB
black = (0, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
red = (255, 0, 0)
pink = (255, 192, 203)
white = (255, 255, 255)
orange = (255, 128, 0)
violet = (153, 51, 255)

# Valores para la interfaz de pygame
ancho, alto = 1400, 1000  # tamaño del display
pygame.init()  # inicialización
screen = pygame.display.set_mode((ancho, alto))
clock = pygame.time.Clock()
pygame.font.init()  # modulo para renderizar y cargar textos

# Inicio de arrays a utilizar
poblacion = []
poblacion_size = 250  # cantidad de individuos
# valor inicial del array que contiene los valores de fitness para cada
# individuo
fitness_list = np.zeros(poblacion_size) + 0.000000000000001
avg_fitness_vector = []
generation_count_vector = []


def setup():
    screen.fill(black)
    for i in range(poblacion_size):
        poblacion.append(Bola(red, 10, lifespan))


# funcion selection
def selection(objetivo, poblacion):
    screen.fill(black)
    lista_de_padres = []
    nueva_poblacion = []

    # Calculo del fitness para cada bola
    for i, member in enumerate(poblacion):
        fitness_list[i] = member.fitness(objetivo)

    # Elitismo: selección del individuo con mayor fitness
    max_fitness = max(fitness_list)
    aux_max_fitness_index = np.where(fitness_list == max_fitness)
    max_fitness_index = int(aux_max_fitness_index[0][0])
    poblacion[max_fitness_index].elite = True

    # Normalizacion del fitness

    fitness_list_normalizado = (fitness_list / max_fitness) * 100
    avg_fitness = np.mean(fitness_list_normalizado)
    avg_fitness_not_normalized = np.mean(fitness_list)

    # Ruleta de seleccion
    for i in range(len(fitness_list_normalizado)):
        j = int(fitness_list_normalizado[i])
        for k in range(j):
            lista_de_padres.append(poblacion[i])

    # Asegura la supervivencia del elite
    elite_adn = poblacion[max_fitness_index].adn
    nueva_poblacion.append(Bola(violet, 11, lifespan, elite_adn, elite=True))

    for i in range(len(poblacion) - 1):
      # Elije al azar 2 padres
        padre_A = random.choice(lista_de_padres)
        padre_B = random.choice(lista_de_padres)
      # Toma sus adns
        padre_A_adn = padre_A.adn
        padre_B_adn = padre_B.adn
      # genera un adn nuevo con información de ambos adns padres
        hijo_adn = padre_A_adn.crossover(padre_B_adn)
      # crea una nueva población
        nueva_poblacion.append(Bola(red, 10, lifespan, hijo_adn))
    pobl = nueva_poblacion

    # Posible mutacion de la nueva poblacion
    for hijo in nueva_poblacion:
        hijo.mutar(mutation_rate)

    # regresa la nueva poblacion y el average fitness score no normalizado de
    # la poblacion anterior
    return pobl, avg_fitness_not_normalized


# función draw: main loop

def draw(poblacion):
  # Flag que indica si se debe cerrar el display de pygame
    cerrar_display = True
  # arrays vacios
    aux = []
    flag_vec = []
  # Arrays que contienen los obstaculos (por ahora lo dejo vacío) y el objetivo
    wall_vec = [
        Obstaculo(
            850, 150, 20, 550, green), Obstaculo(
            850, 700, 400, 20, green), Obstaculo(
                650, 400, 20, 450, green), Obstaculo(
                    500, 0, 20, 400, green)]
    # wall_vec=[Obstaculo(850,150,20,550,green), Obstaculo(850,700,400,20,green)]
    objetivo = Objetivo(1150, 300, 30, 30, (255, 255, 255))
  # Flag para volver a empezar una generación
    reset_flag = False
  # Fuente para el texto
    myfont = pygame.font.SysFont("monospace", 25)
  # Contador de generaciones
    generacion_count = 0

    # main loop
    while cerrar_display:
      # el siguiente loop es para cerar el display manualmente
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cerrar_display = False
                pygame.quit()

        screen.fill(black)  # llena la pantalla de color negro

        # Mostar los obstaculos
        for wall in wall_vec:
            wall.show()
        objetivo.show()
        # Flag para ver si todos los individuos están "muertos", si todos
        # llegaron al objetivo o si chocaron. Esta información se guarda en el
        # booleano reset_flag.
        for member in poblacion:
            if member.vivo == False or member.win or member.colision_pared:
                flag_vec.append(True)
            else:
                flag_vec.append(False)
        if all(flag_vec):  # flag_vec almacena la informacion de toda la poblacion, si se llena con valores "True" entonces cambia el valor de reset_flag
            reset_flag = True
        # Crea una nueva generacion cuando termina el lifespan o si ningún
        # individuo se mueve
        for member in poblacion:
            if member.contador == lifespan or reset_flag:
                reset_flag = False  # reestablece el valor de reset_flag

                # Contador de generaciones para el ploteo
                generation_count_vector.append(generacion_count)
                generacion_count = generacion_count + 1
                flag_vec.clear()
                aux = selection(objetivo, poblacion)[0]

                # Guarda el average fitness de la generacion para el ploteo
                avg_fitness_vector.append(selection(objetivo, poblacion)[1])

                poblacion = aux
                # ploteo del average fitness score de la poblacion (no
                # normalizado) en cada generación. Comentado para que no se
                # llene de imágenes el Colab.
                plt.plot(generation_count_vector, avg_fitness_vector)
                plt.xlabel('Generation')
                plt.ylabel('Average fitness')
                plt.show()
            break
        # El siguiente for itera sobre toda la poblacion y chequea colisiones
        # con el objetivo y los obstaculos
        for member in poblacion:
            for wall in wall_vec:
                wall.obstacle_ball_collision(member)
            objetivo.objetivo_ball_collision(member)
            member.paredes()
            member.update()
            member.show()
        flag_vec.clear()
        # Escribe en el display información sobre la generación y el lifespan
        # actual
        label = myfont.render(str('generation') + str(' ') +
                              str(generacion_count), 1, pink)
        screen.blit(label, (0, 10))
        label2 = myfont.render(str('lifespan') + str(' ') +
                               str(poblacion[0].contador), 1, pink)
        screen.blit(label2, (0, 40))
        clock.tick(500)
        pygame.display.flip()


# Inicializa la primera generación
setup()
# Ejecuta la función draw
draw(poblacion)

# Cierra Pygame al finalizar
pygame.quit()
