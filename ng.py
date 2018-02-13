import pygame
import random
import time
from pygame.locals import QUIT, KEYDOWN
from pygame import gfxdraw
import os



''' NOTES:

    TO DO:

        SHORT TERM (now):

            reformat display so that they're right next to each other

            make it so their borders are always the same size

            make normal distribution that continuously
            generates floats

            build histogram from that


        MEDIUM TERM (later):

            I want GUI display of network that:
                a 2d histogram of how data is being added on 1 plot
                    colors are used to represent the number of
                    samples in a given bin with a color legend on
                    the side 

                a 2d plot of the neural gas
                    starts with 2 nodes like in the research paper
                    the network itself could be a dictionary
                    where each key is a node
                    each node's value is another dictionary
                    where we have:
                        coordinates
                        list of nodes connected to
                        error from original position (i think?)

                a bunch of data on the side displaying:
                    number of data points added
                    number of nodes in the neural gas

                buttons so user can:
                    start data addition
                    pause data addition
                    reset data to zero

                I need to find a way to rebuild a histogram
                from the neural gass network to then compare
                to the actual histogram of the original data


        LONG TERM (eventually):

            maybe make different data distributions than normal distribution
            do something like what they do in videos

            make gifs and pretty readme

            maybe make a video explaining neural gas how it works
            and talk about comparing it to histogram
            and talk about tuning hyper parameters


    SOURCES:

        pygame:
        https://www.pygame.org/docs/

        A Growing Neural Gas Learns Topologies - Original Research Paper
        https://papers.nips.cc/paper/893-a-growing-neural-gas-network-learns-topologies.pdf

        '''


class PyGameView(object):

    def __init__(self, model, size):

        self.model = model
        self.screen = pygame.display.set_mode((size[0], size[1]))
        self.surface = pygame.Surface((size[0], size[1]))
        
    def draw_simulation(self):

        # fill background
        self.surface.fill(pygame.Color('black'))

        #pygame.draw.circle(self.surface, pygame.Color('green'), (50,50), 10)
        #pygame.draw.line(self.surface,   (255,255,255), (10, 20), (30, 40), 4) # (start_x, start_y), (end_x, end_y), width
        #pygame.draw.rect(self.surface,   pygame.Color('red'), [100, 100, 40, 100])

        # draw histogram of actual data
        self.draw_2d_histogram([
            [0,1,0],
            [1,3,1],
            [0,1,0]
            ])

        # draw neural gas network
        self.draw_2d_graph({
            (10,10):[(30,30), (10,20)],
            (30,30):[(10,10)],
            (10,20):[(10,10)]
            })

        # update display
        pygame.display.update()

    def draw_2d_graph(self, neural_gas):

        sp = (150, 50)
        w, h = 100, 100

        # draw border graph resides in
        pygame.draw.rect(self.surface,
            pygame.Color('white'),
            (sp[0], sp[1], w, h), 1)
            
        # draw graph
        edges = []
        for v, es in neural_gas.items():

            # draw vertex v
            pygame.draw.circle(self.surface,
                pygame.Color('white'),
                (sp[0]+v[0], sp[1]+v[1]),
                3)

            # draw edge e in edges es connected to vertex v 
            for e in es:
                if not (e, v) in edges:
                    edges.append((e, v))
                    pygame.draw.line(self.surface,
                        pygame.Color('white'),
                        (sp[0]+v[0], sp[1]+v[1]), 
                        (sp[0]+e[0], sp[1]+e[1]),
                        2)
    def draw_2d_histogram(self, hist):

        sp = (50, 50) # sp = start point
        mx = max(map(max, hist))
        mn = min(map(min, hist))
        s = 10 # s = bin_pixel_width

        # draw border of histogram
        pygame.draw.rect(self.surface, pygame.Color('white'),
            (sp[0], sp[1], s*len(hist), s*len(hist[0])), 3)

        # draw bins of histogram
        for i in range(len(hist)):
            for j in range(len(hist)):
                pygame.draw.rect(self.surface,
                    self.bin_color(hist[i][j], mx, mn),
                    [sp[0] + i*s, sp[1] + j*s, s, s])
    def bin_color(self, value, mx, mn):

        # interpolate
        x = float(value - mn) / (mx - mn)
        return (255*x,255*x,255*x)

    def draw_text_in_simulation(self, text, x, y, size, color = (100, 100, 100)):
        """ 
        Helper to draw text onto screen.

        Args:
            text (string): text to display
            x (int): horizontal position
            y (int): vertical position
            size (int): font size
            color (3-tuple int): color of text.  Can use pygame colors.
            defualt = (100, 100, 100)
        """
        basicfont = pygame.font.SysFont(None, size)
        text_render = basicfont.render(
            text, True, color)
        self.surface.blit(text_render, (x, y))

class Model(object):
    """
    Represents the state of all entities in the environment and drawing
    parameters
    """

    def __init__(self, width, height):
        """
        initialize model, environment, and default keyboard controller states

        Args:
            width (int): width of window in pixels
            height (int): height of window in pixels
        """
        #window parameters / drawing
        self.height = height
        self.width = width
        self.show = True # show current model
        self.show_controls = False # controls toggle



        ############## NEURAL GAS LOGIC STARTS HERE ##################



        ##############################################################

    def update(self, controller):
        pass

class PyGameKeyboardController(object):
    """
    Keyboard controller that responds to keyboard input
    """


    def __init__(self):
        """
        Creates keyboard controller

        Args:
            model (object): contains attributes of the environment
        """
        #self.model = model
        self.paused = False


    def handle_event(self, event):
        """ 
        Look for left and right keypresses to modify the x position of the paddle 

        Args:
            event (pygame class): type of event
        """
        if event.type != KEYDOWN:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    print('mouse wheel scroll up')
                elif event.button == 5:
                    print('mouse wheel scroll down')
                elif event.button == 1:
                    print('mouse left click')
                elif event.button == 3:
                    print('mouse right click')
                else:
                    print('event.button = %d' % event.button)
            return True
        elif event.key == pygame.K_SPACE:
            self.paused = not self.paused
        elif event.key == pygame.K_d:
            pass
        elif event.key == pygame.K_k:
            pass
        elif event.key == pygame.K_s:
            pass

        #elif event.key == pygame.K_PERIOD:
        #    model.sleep_time = max(model.sleep_time-0.005, 0.0)
        #elif event.key == pygame.K_COMMA:
        #    model.sleep_time += 0.005
        elif event.key == pygame.K_h:
            model.show_controls = not model.show_controls
        elif event.key == pygame.K_l:
            pass
        elif event.key == pygame.K_r:
            pass
        return True



if __name__ == '__main__':

    pygame.init()

    SCREEN_SIZE = (750, 500)
    model = Model(SCREEN_SIZE[0], SCREEN_SIZE[1])
    view = PyGameView(model, SCREEN_SIZE)
    controller = PyGameKeyboardController()
    running = True

    start_time = time.time()
    period = 1
    iterations = 0

    while running:

        iterations += 1
        if time.time() - start_time > period:
            start_time += period
            # print('%s fps' % iterations)
            iterations = 0

        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            else:
                # handle event can end pygame loop
                if not controller.handle_event(event):
                    running = False

        if not controller.paused:
            model.update(controller)
        
        if model.show:
            view.draw_simulation()
            view.screen.blit(view.surface, (0,0))
            pygame.display.update()
            #time.sleep(model.sleep_time)


