import time

import pygame

import devices.draft.LandNSM5

pygame.init()
dev = devices.draft.LandNSM5.LandNSM5()
dev.goVariableFastToAbsolutePosition(3, 'x', 0)
dev.goVariableFastToAbsolutePosition(3, 'y', 0)
def main():
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Joystick Testing / XBOX360 Controller")

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((255, 255, 255))

    joysticks = []
    clock = pygame.time.Clock()
    keepPlaying = True

    # for al the connected joysticks
    for i in range(0, pygame.joystick.get_count()):
        # create an Joystick object in our list
        joysticks.append(pygame.joystick.Joystick(i))
        # initialize them all (-1 means loop forever)
        joysticks[-1].init()
        # print a statement telling what the name of the controller is
        print "Detected joystick '", joysticks[-1].get_name(), "'"
    while keepPlaying:
        clock.tick(60)

        time.sleep(0.1)
        a = 5 * (pygame.mouse.get_pos()[0] - 320)
        b = 5 * (pygame.mouse.get_pos()[1] - 240)
        print
        dev.goVariableFastToAbsolutePosition(3, 'x', -a)
        #dev.goVariableSlowToAbsolutePosition(3, 'y', b)

        #pos = dev.getPosition(3,'x')
        #print (pos)

            #elif event.type == pygame.MOUSEMOTION:
            #    time.sleep(3)
            #    a = 5 * (pygame.mouse.get_pos()[0] - 320)
            #    b = 5 * (pygame.mouse.get_pos()[1] - 240)
            #    print -a, b
                # b = a
            #    dev.goVariableFastToAbsolutePosition(3, 'x', -a)
            #    dev.goVariableFastToAbsolutePosition(3, 'y', b)






            #elif event.type == pygame.JOYAXISMOTION:
            #    print "Joystick '", joysticks[event.joy].get_name(), "' axis", event.axis, "motion."
            #elif event.type == pygame.JOYBUTTONDOWN:
            #    print "Joystick '", joysticks[event.joy].get_name(), "' button", event.button, "down."
            #    if event.button == 0:
            #        background.fill((255, 0, 0))
            #    elif event.button == 1:
            #        background.fill((0, 0, 255))
            #elif event.type == pygame.JOYBUTTONUP:
            #    print "Joystick '", joysticks[event.joy].get_name(), "' button", event.button, "up."
            #    if event.button == 0:
            #        background.fill((255, 255, 255))
            #    elif event.button == 1:
            #        background.fill((255, 255, 255))
            #elif event.type == pygame.JOYHATMOTION:
            #    print "Joystick '", joysticks[event.joy].get_name(), "' hat", event.hat, " moved."

        screen.blit(background, (0, 0))
        pygame.display.flip()


main()
pygame.quit()
