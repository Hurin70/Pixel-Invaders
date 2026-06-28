import asyncio
import pygame
import Juego

async def main():
    # Inicializa el motor de juego dentro del entorno web
    pygame.init()
    
    # Llama a la función principal de tu juego de manera asíncrona
    await Juego.main()

# Punto de entrada obligatorio para el emulador web de pygbag
asyncio.run(main())
