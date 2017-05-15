for event in pygame.event.get():
    if event.type == pygame.QUIT:
        print "Received event 'Quit', exiting."
        keepPlaying = False
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        print "Escape key pressed, exiting."
        keepPlaying = False
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_w:
            print "Moving,", event.key
            # dev.switchOffAxis(1,'x')
            dev.goVariableSlowToAbsolutePosition(1, 'x', 2000)
    elif event.type == pygame.KEYUP:
        if event.key == pygame.K_w:
            print "Keyup,", event.key
            # dev.Stop(1,'x')
            # elif event.type == pygame.MOUSEMOTION:
            #   print "Mouse movement detected."

    elif event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            dev.switchOnAxis(1, 'x')
            a = 5 * (pygame.mouse.get_pos()[0] - 320)
            b = 5 * (pygame.mouse.get_pos()[1] - 240)
            print -a, b
            # b = a
            # dev.goVariableFastToAbsolutePosition(3, 'x', -a)
            # dev.goVariableFastToAbsolutePosition(3, 'y', b)
        elif event.button == 3:
            dev.switchOnAxis(1, 'y')
            print ("Axe 'y' switched on")
