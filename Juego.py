# -*- coding: utf-8 -*-
import pygame
import random
import os
import json
import time
import math
import sys
import subprocess
import asyncio # Necesario para la web

from FondoAnimado import FondoAnimado
from Personaje import Nave
from Enemigo import Enemigo
from NaveAmarilla import NaveAmarilla
from NaveRoja import NaveRoja
from NaveVerde import NaveVerde
from NaveNaranja import NaveNaranja
from Bala import Bala
from BalaEnemiga import BalaEnemiga
from Jefe import Jefe
from Modificadores import Escudo, DisparoTriple
from Explosion import Explosion
from SpriteManager import SpriteManager
from ManejadorMusica import ManejadorMusica

# Definición de variables globales (sin inicializar con pygame todavía)
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(BASE_PATH, "img")
FUENTES_PATH = os.path.join(BASE_PATH, "FUENTES")
ANCHO_BASE = 700
ALTO_BASE = 800
ANCHO = ANCHO_BASE
ALTO = ALTO_BASE
FPS = 60
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)

# Variables que se inicializarán en main()
manejador_musica = None
VENTANA = None
surface_juego = None
sprite_nave = None
sprite_nave_original = None
sprite_enemigo = None
sprite_jefe = None
sprite_bala = None
sprite_bala_enemiga = None
sprite_explosion = None
sprite_nave_verde = None
sprite_nave_roja = None
sprite_nave_amarilla = None
sprite_nave_naranja = None
icono_escudo = None
icono_triple = None
burbuja_escudo_img = None
FUENTE = None
FUENTE_HUD = None
fondo_animado = None
fondo_inicio_img = None
sprite_manager = None
reloj = None

# Variables de estado del juego
vida = 5
puntos = 0
enemigos_abatidos = 0
enemigos_por_jefe = 100
jefes_derrotados = 0
enemigos_abatidos_ocultos = 0
tiempo_entre_enemigos = 500
tiempo_entre_balas = 100
ultima_bala = 0
tiempo_ultimo_jefe = 0
enemigos = []
balas = []
balas_enemigas = []
jefe = None
nave = None
mundo = 1
fondo_color = NEGRO
musica_muted = False
vida_base_jefe = 10
escudo = None
disparo_triple = None
mensaje_modificador = None
mensaje_modificador_color = (255, 255, 0)
mensaje_modificador_tiempo = 0
MAX_PROB = 10000
prob_nave_roja = 1000
prob_nave_verde = 1000
prob_nave_amarilla = 1000
prob_nave_naranja = 500
tiempo_disparo_nave_especial = 1200
modificadores_activos = []
contador_escudo = 0
contador_disparo_triple = 0
tiempo_inicio_nivel = 0
duracion_nivel = 30
max_enemigos_en_pantalla = 6
FACTOR_ESCALA = 1.0
ANCHO_NAVE_BASE = 75
ALTO_NAVE_BASE = 75
primera_partida = True
explosiones = []

# --- FUNCIONES ---

def reproducir_musica(ruta, loop=True):
    try:
        if os.path.exists(ruta):
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.set_volume(0.7)
            pygame.mixer.music.play(-1 if loop else 0)
            return True
        else:
            return False
    except:
        return False
    
def mostrar_overlay_pausa():
    fuente_pausa = pygame.font.Font(os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf"), 60)
    overlay = pygame.Surface((ANCHO_BASE, ALTO_BASE), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    texto = fuente_pausa.render("PAUSE", True, BLANCO)
    overlay.blit(texto, (ANCHO_BASE // 2 - texto.get_width() // 2, ALTO_BASE // 2 - texto.get_height() // 2))
    surface_juego.blit(overlay, (0, 0))
    blit_centrado_letterbox()

def actualizar_ventana_y_escala(nuevo_ancho, nuevo_alto):
    global ANCHO, ALTO, VENTANA, FACTOR_ESCALA, sprite_nave, FUENTE, FUENTE_HUD
    global icono_escudo, icono_triple, burbuja_escudo_img
    ANCHO = nuevo_ancho
    ALTO = nuevo_alto
    VENTANA = pygame.display.set_mode([ANCHO, ALTO], pygame.RESIZABLE)
    FACTOR_ESCALA = min(ANCHO / ANCHO_BASE, ALTO / ALTO_BASE)
    nuevo_ancho_nave = max(1, int(ANCHO_NAVE_BASE * FACTOR_ESCALA))
    nuevo_alto_nave = max(1, int(ALTO_NAVE_BASE * FACTOR_ESCALA))
    if nave:
        nave.redimensionar(FACTOR_ESCALA, sprite_nave_original)
    fondo_animado.ancho = ANCHO
    fondo_animado.alto = ALTO
    for enemigo in enemigos:
        if hasattr(enemigo, 'sprite_original'):
            enemigo.redimensionar(FACTOR_ESCALA, sprite_enemigo)
        else:
            enemigo.redimensionar(FACTOR_ESCALA)
    for bala in balas:
        if hasattr(bala, 'sprite_original'):
            bala.redimensionar(FACTOR_ESCALA, sprite_bala)
        else:
            bala.redimensionar(FACTOR_ESCALA)
    for bala_enemiga in balas_enemigas:
        if hasattr(bala_enemiga, 'sprite_original'):
            bala_enemiga.redimensionar(FACTOR_ESCALA, sprite_bala_enemiga)
        else:
            bala_enemiga.redimensionar(FACTOR_ESCALA)
    if jefe:
        if hasattr(jefe, 'sprite_original'):
            jefe.redimensionar(FACTOR_ESCALA, sprite_jefe)
        else:
            jefe.redimensionar(FACTOR_ESCALA)
        if hasattr(jefe, 'escudo') and jefe.escudo:
            jefe.escudo.redimensionar(FACTOR_ESCALA, burbuja_escudo_img)
    for enemigo in enemigos:
        if hasattr(enemigo, 'redimensionar'):
            if hasattr(enemigo, 'sprite_original'):
                if isinstance(enemigo, NaveRoja):
                    enemigo.redimensionar(FACTOR_ESCALA, sprite_nave_roja)
                elif isinstance(enemigo, NaveVerde):
                    enemigo.redimensionar(FACTOR_ESCALA, sprite_nave_verde)
                elif isinstance(enemigo, NaveAmarilla):
                    enemigo.redimensionar(FACTOR_ESCALA, sprite_nave_amarilla)
                elif isinstance(enemigo, NaveNaranja):
                    enemigo.redimensionar(FACTOR_ESCALA, sprite_nave_naranja)
            else:
                enemigo.redimensionar(FACTOR_ESCALA)
    for explosion in explosiones:
        if hasattr(explosion, 'sprite_original'):
            explosion.redimensionar(FACTOR_ESCALA, sprite_explosion)
        else:
            explosion.redimensionar(FACTOR_ESCALA)
    for mod in modificadores_activos:
        if hasattr(mod, 'redimensionar'):
            if isinstance(mod, Escudo):
                mod.redimensionar(FACTOR_ESCALA, burbuja_escudo_img)
            else:
                mod.redimensionar(FACTOR_ESCALA)
    icono_escudo = pygame.transform.smoothscale(pygame.image.load(os.path.join(IMG_PATH, "icono_escudo.png")).convert_alpha(), (int(32 * FACTOR_ESCALA), int(32 * FACTOR_ESCALA)))
    icono_triple = pygame.transform.smoothscale(pygame.image.load(os.path.join(IMG_PATH, "icono_triple.png")).convert_alpha(), (int(32 * FACTOR_ESCALA), int(32 * FACTOR_ESCALA)))
    burbuja_escudo_img = pygame.transform.smoothscale(pygame.image.load(os.path.join(IMG_PATH, "burbuja_escudo.png")).convert_alpha(), (int(nuevo_ancho_nave * 1.3), int(nuevo_alto_nave * 1.3)))
    FUENTE = pygame.font.Font(os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf"), max(int(40 * FACTOR_ESCALA), 12))
    FUENTE_HUD = pygame.font.Font(os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf"), max(int(20 * FACTOR_ESCALA), 10))

def fuente_ajustada(texto, fuente_path, ancho_max, alto_max=None, tamaño_inicial=60):
    tamaño = tamaño_inicial
    while tamaño > 10:
        fuente = pygame.font.Font(fuente_path, tamaño)
        superficie = fuente.render(texto, True, (255,255,255))
        if superficie.get_width() <= ancho_max and (alto_max is None or superficie.get_height() <= alto_max):
            return fuente
        tamaño -= 2
    return pygame.font.Font(fuente_path, 10)

def reiniciar_juego():
    global nave, modificadores_activos, vida, puntos, enemigos_abatidos, enemigos_por_jefe, jefes_derrotados
    global enemigos_abatidos_ocultos, tiempo_entre_enemigos, tiempo_entre_balas
    global ultima_bala, tiempo_ultimo_jefe, enemigos, balas, balas_enemigas
    global jefe, mundo, fondo_color, explosiones, contador_escudo, contador_disparo_triple
    global tiempo_inicio_nivel, duracion_nivel
    
    nave = Nave(ANCHO // 2 - 25, ALTO - 60)
    nave.sprite = sprite_nave
    modificadores_activos = []
    Enemigo.velocidad = 5
    Jefe.velocidad = 5
    Jefe.tiempo_entre_disparos = 1000 
    vida = 5
    puntos = 0
    enemigos_abatidos = 0
    enemigos_por_jefe = 100
    jefes_derrotados = 0
    enemigos_abatidos_ocultos = 0
    tiempo_entre_enemigos = 500
    tiempo_entre_balas = 100
    ultima_bala = 0
    tiempo_ultimo_jefe = pygame.time.get_ticks()
    enemigos = []
    balas = []
    balas_enemigas = []
    jefe = None
    mundo = 1
    fondo_color = NEGRO
    explosiones = []
    fondo_animado.seleccionar_fondo(mundo)

def dibujar_fondo_inicio(ventana, fondo_img, ancho, alto, opacidad=255, oscurecer=80):
    fondo_escalado = pygame.transform.smoothscale(fondo_img, (ancho, alto))
    ventana.blit(fondo_escalado, (0, 0))
    oscurecedor = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    oscurecedor.fill((0, 0, 0, oscurecer))
    ventana.blit(oscurecedor, (0, 0))

def render_texto_dorado(texto, fuente, ancho, alto, destello_x):
    texto_img = fuente.render(texto, True, (255, 255, 255))
    degradado = pygame.Surface(texto_img.get_size()).convert_alpha()
    for y in range(texto_img.get_height()):
        color = (255, int(180 + 75 * y / texto_img.get_height()), int(40 + 100 * y / texto_img.get_height()))
        pygame.draw.line(degradado, color, (0, y), (texto_img.get_width(), y))
    texto_dorado = texto_img.copy()
    texto_dorado.blit(degradado, (0, 0), special_flags=pygame.BLEND_MULT)
    destello = pygame.Surface((40, texto_img.get_height()), pygame.SRCALPHA)
    pygame.draw.rect(destello, (255, 255, 255, 120), (0, 0, 40, texto_img.get_height()))
    texto_dorado.blit(destello, (destello_x % texto_img.get_width(), 0), special_flags=pygame.BLEND_ADD)
    return texto_dorado

def mostrar_pantalla_inicio():
    global primera_partida
    font_title = pygame.font.Font(os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf"), int(60 * FACTOR_ESCALA))
    font_instructions = pygame.font.Font(os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf"), int(14 * FACTOR_ESCALA))
    destello_x = 0
    esperando = True
    offset_y = int(ALTO * 0.2)
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    esperando = False
                    pygame.mixer.music.stop()
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
        dibujar_fondo_inicio(surface_juego, fondo_inicio_img, ANCHO_BASE, ALTO_BASE, 128)
        titulo_pixel = render_texto_dorado("PIXEL", font_title, ANCHO_BASE, ALTO_BASE, destello_x)
        titulo_invaders = render_texto_dorado("INVADERS", font_title, ANCHO_BASE, ALTO_BASE, destello_x + int(80 * FACTOR_ESCALA))
        y_titulo = int(ALTO_BASE // 6 + offset_y)
        surface_juego.blit(titulo_pixel, (ANCHO_BASE // 2 - titulo_pixel.get_width() // 2, y_titulo))
        surface_juego.blit(titulo_invaders, (ANCHO_BASE // 2 - titulo_invaders.get_width() // 2, y_titulo + titulo_pixel.get_height() + int(10 * FACTOR_ESCALA)))
        instrucciones = ["Controles:", "W, A, S, D para mover la nave", "ESPACIO para disparar", "ESC para salir", "P pausa M mute", ""]
        for i, linea in enumerate(instrucciones):
            texto = font_instructions.render(linea, True, BLANCO)
            surface_juego.blit(texto, (ANCHO_BASE // 2 - texto.get_width() // 2, int(ALTO_BASE // 3 + offset_y + i * 30 * FACTOR_ESCALA)))
        alpha = int(128 + 127 * (1 + math.sin(pygame.time.get_ticks() / 500)) / 2)
        font_intro = pygame.font.Font(os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf"), max(int(18 * FACTOR_ESCALA), 12))
        texto_intro = font_intro.render("Presiona ENTER para comenzar", True, BLANCO)
        texto_intro.set_alpha(alpha)
        superficie_intro = pygame.Surface(texto_intro.get_size(), pygame.SRCALPHA)
        superficie_intro.blit(texto_intro, (0, 0))
        y_intro = int(ALTO_BASE // 2 + offset_y + len(instrucciones) * 35 * FACTOR_ESCALA + 30 * FACTOR_ESCALA)
        if y_intro + texto_intro.get_height() > ALTO_BASE:
            y_intro = ALTO_BASE - texto_intro.get_height() - int(20 * FACTOR_ESCALA)
        surface_juego.blit(superficie_intro, (ANCHO_BASE // 2 - texto_intro.get_width() // 2, y_intro))
        blit_centrado_letterbox()
        destello_x += int(8 * FACTOR_ESCALA)
        # Sustituir reloj.tick por una pausa asíncrona
        # reloj.tick(60) 
        
def blit_centrado_letterbox():
    ventana_real = pygame.display.get_surface()
    ancho_ventana, alto_ventana = ventana_real.get_size()
    escala = min(ancho_ventana / ANCHO_BASE, alto_ventana / ALTO_BASE)
    ancho_escalado = int(ANCHO_BASE * escala)
    alto_escalado = int(ALTO_BASE * escala)
    x_offset = (ancho_ventana - ancho_escalado) // 2
    y_offset = (alto_ventana - alto_escalado) // 2
    ventana_real.fill((0, 0, 0))
    surface_escalada = pygame.transform.smoothscale(surface_juego, (ancho_escalado, alto_escalado))
    ventana_real.blit(surface_escalada, (x_offset, y_offset))
    pygame.display.update()

# --- AQUÍ EMPIEZA LA LÓGICA ASÍNCRONA ---

async def main():
    global manejador_musica, VENTANA, surface_juego, sprite_nave, sprite_nave_original
    global sprite_enemigo, sprite_jefe, sprite_bala, sprite_bala_enemiga, sprite_explosion
    global sprite_nave_verde, sprite_nave_roja, sprite_nave_amarilla, sprite_nave_naranja
    global icono_escudo, icono_triple, burbuja_escudo_img, FUENTE, FUENTE_HUD, fondo_animado
    global fondo_inicio_img, sprite_manager, reloj, nave, mundo, jefes_derrotados, enemigos_abatidos_ocultos
    global tiempo_inicio_nivel, duracion_nivel, jugando, tiempo_pasado, juego_en_progreso
    global en_pausa, musica_muted, vida, enemigos, balas, balas_enemigas, jefe, explosiones, fondo_color

    pygame.init()
    pygame.mixer.init()
    
    # Inicialización de objetos que dependen de pygame
    manejador_musica = ManejadorMusica(BASE_PATH)
    pygame.display.set_caption("Pixel Invaders")
    VENTANA = pygame.display.set_mode([ANCHO, ALTO], pygame.RESIZABLE)
    surface_juego = pygame.Surface((ANCHO_BASE, ALTO_BASE))
    reloj = pygame.time.Clock()
    fondo_animado = FondoAnimado(ANCHO, ALTO, BASE_PATH)
    sprite_manager = SpriteManager()
    
    # Carga de recursos (imágenes)
    # (El resto de la lógica de carga va aquí dentro)
    try:
        FUENTE = pygame.font.Font(os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf"), 40)
        FUENTE_HUD = pygame.font.Font(os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf"), 20)
    except:
        FUENTE = pygame.font.SysFont("Consolas", 40)
        FUENTE_HUD = pygame.font.SysFont("Consolas", 20)

    # Carga de sprites (SVG)
    svg_nave = open(os.path.join(IMG_PATH, 'nave-sprite.svg'), 'r').read()
    sprite_nave = sprite_manager.cargar_svg('nave', svg_nave)
    sprite_nave_original = sprite_nave
    # ... (el resto de sprites cargados igual que antes)
    sprite_enemigo = sprite_manager.cargar_svg('enemigo', open(os.path.join(IMG_PATH, 'enemigo-sprite.svg'), 'r').read())
    sprite_jefe = sprite_manager.cargar_svg('jefe', open(os.path.join(IMG_PATH, 'jefe-sprite.svg'), 'r').read())
    sprite_bala = sprite_manager.cargar_svg('bala', open(os.path.join(IMG_PATH, 'bala-sprite.svg'), 'r').read())
    sprite_bala_enemiga = sprite_manager.cargar_svg('bala_enemiga', open(os.path.join(IMG_PATH, 'bala-enemiga-sprite.svg'), 'r').read())
    sprite_explosion = sprite_manager.cargar_svg('explosion', open(os.path.join(IMG_PATH, 'efectos-explosiones.svg'), 'r').read())
    sprite_nave_verde = sprite_manager.cargar_svg('nave_verde', open(os.path.join(IMG_PATH, 'naveVerde-sprite.svg'), 'r').read())
    sprite_nave_roja = sprite_manager.cargar_svg('nave_roja', open(os.path.join(IMG_PATH, 'naveRoja-sprite.svg'), 'r').read())
    sprite_nave_amarilla = sprite_manager.cargar_svg('nave_amarilla', open(os.path.join(IMG_PATH, 'naveAmarilla-sprite.svg'), 'r').read())
    sprite_nave_naranja = sprite_manager.cargar_svg('nave_naranja', open(os.path.join(IMG_PATH, 'naveNaranja-sprite.svg'), 'r').read())

    fondo_inicio_img = pygame.image.load(os.path.join(BASE_PATH, "main", "fondo inicio.png")).convert()
    
    # Bucle principal del juego
    while True:
        manejador_musica.reproducir(os.path.join(BASE_PATH, "songs", "main.ogg"))
        reiniciar_juego()
        jefe = None
        jefes_derrotados = 0
        enemigos_abatidos_ocultos = 0
        tiempo_inicio_nivel = pygame.time.get_ticks()
        duracion_nivel = 30
        actualizar_ventana_y_escala(ANCHO, ALTO)
        
        mostrar_pantalla_inicio()
        manejador_musica.reproducir_para_mundo(1)

        jugando = True
        tiempo_pasado = 0
        juego_en_progreso = True
        en_pausa = False
        
        while juego_en_progreso and vida > 0:
            tiempo_pasado += reloj.tick(FPS)
            # (El resto de la lógica del bucle sigue igual, pero al final del bucle:)
            
            # --- ESPERAR PARA LA WEB ---
            await asyncio.sleep(0) 
