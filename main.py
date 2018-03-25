import time
import pygame
import mpu
from Vec2d import Vec2d
import unicornhathd as unicorn


#set up Unicorn Hat
unicorn.brightness(1.0)

width = 16
height = 16
center = (8, 8)
pygame.init()
screen = pygame.display.set_mode((width, height))
done = False

def getXY(vector):
    return (int(vector.x), int(vector.y))

gravityInput = mpu.mpu()

clock = pygame.time.Clock()

gravity = Vec2d(0,0)
circleXY = Vec2d(center)
circleVelocity = Vec2d(0,0)


while not done:
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    unicorn.off()
                    done = True
    #print("gravityInput.GetXY(.033) = " + str(gravityInput.GetXY(.033)))
    
    #clear the screen
    background_colour = (0,0,0)
    screen.fill(background_colour)
    #draw old circle position
    #print("circleXY = " + str(int(circleXY.x)) + ", "  + str(int(circleXY.y)))
    pygame.draw.circle(screen, (255,0,0), getXY(circleXY), 0)
    #get current gravity
    gravityX, gravityY = gravityInput.GetXY(.05)
    gravity = Vec2d(int(gravityX),int(gravityY))
    #update circle velocity by adding gravity to it
    circleVelocity = gravity.normalized()
    #update to new circle position
    circleXY = circleXY + circleVelocity
    #check for "bouncing off wall"
    if(circleXY.x < 0):
        circleXY.x = 0
    if(circleXY.x > width):
        circleXY.x = width
    if(circleXY.y < 0):
        circleXY.y = 0
    if(circleXY.y > height):
        circleXY.y = height
    #draw new circle position
    pygame.draw.circle(screen, (255,255,255), getXY(circleXY), 0)
    pygame.display.flip()
    displaySurface = pygame.display.get_surface()
    unicorn.clear()
    for x in range(0, width):
        for y in range(0, height):
            #print("displaySurface[" + str(x) + ", " + str(y) + "] = " + str(displaySurface.get_at((x, y))))
            pixelColor = displaySurface.get_at((x, y))
            #print("pixel[" + str(x) + ", " + str(y) + "] = " + str(pixelColor.r) + "," + str(pixelColor.g) + "," + str(pixelColor.b))
            unicorn.set_pixel(x, y, pixelColor.r, pixelColor.g, pixelColor.b)
    unicorn.show()
    clock.tick(20)
