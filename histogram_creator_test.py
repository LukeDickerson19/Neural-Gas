import pygame
import random
import time
from pygame.locals import QUIT, KEYDOWN
from pygame import gfxdraw
import os
from neural_gas import *
from operator import itemgetter

''' NOTES:

    TO DO:

        need to depict the std dev sum around 1 node on graph plot
        from data aquired in m dictionary

            determine how distance and angle are going to
            influence the std dev2
                cant be infinity for 0 angle
                both were inversely proportional though

            

        might want to plot the individual gaussians on a 2d plot as well

        might want to make it so you can pick up and move points

            shouldn't be to hard with most of setup already done
            see evolutionary neural network for mouse pos tracking
            if neccessary

    SOURCES:

    OTHER:

        '''


class PyGameView(object):

    def __init__(self, model, size):

        self.model = model
        self.screen = pygame.display.set_mode((size[0], size[1]))
        self.surface = pygame.Surface((size[0], size[1]))
        
        self.s = 8 # s = the number of pixels a bin of the histogram is wide and tall

    def draw_simulation(self):

        # fill background
        self.surface.fill(pygame.Color('black'))

        # draw actual data
        self.draw_2d_graph(model.g, (150, 50), r=2)

        # draw histogram of actual data
        self.draw_2d_histogram(model.h, (150 + model.b * self.s + 25, 50))

        # update display
        pygame.display.update()

    # sp = starting point of graph
    # r = radius of vertices, default value of 3
    def draw_2d_graph(self, graph, sp, r=3):

        w, h = model.b * self.s, model.b * self.s

        # draw border graph resides in
        pygame.draw.rect(self.surface,
            pygame.Color('white'),
            (sp[0], sp[1], w, h), 1)

        # draw graph

        if model.selecting_vertex:
            model.selected_vertex = model.g.vertices[0]

        for v in graph.vertices:

            # interpolate v to screen
            vx = math.trunc((w * (v.pos[0] - model.min_x) / (model.max_x - model.min_x)) + sp[0])
            vy = math.trunc((h * (v.pos[1] - model.min_y) / (model.max_y - model.min_y)) + sp[1])

            # determine selected vertex
            if model.selecting_vertex:
                svx = math.trunc((w * (model.selected_vertex.pos[0] - model.min_x) / (model.max_x - model.min_x)) + sp[0])
                svy = math.trunc((h * (model.selected_vertex.pos[1] - model.min_y) / (model.max_y - model.min_y)) + sp[1])
                if math.sqrt((vx - model.mouse_pos[0])**2 + (vy - model.mouse_pos[1])**2) < \
                    math.sqrt((svx - model.mouse_pos[0])**2 + (svy - model.mouse_pos[1])**2):
                    model.selected_vertex = v
            
            if v == model.selected_vertex:
                col = pygame.Color('red')
            else:
                col = pygame.Color('white')

            # draw angles of selected vertex
            if not model.selecting_vertex and v == model.selected_vertex:
                amp = 20
                for m in model.m:
                    amp += 5 
                    # # delta angle ahead
                    # pygame.draw.arc(self.surface, col,
                    #     [vx-amp, vy-amp, 2*amp, 2*amp],
                    #     m['a'] + np.pi/2, m['a'] + np.pi/2 + m['da ahead'])

                    # # delta angle behind
                    # pygame.draw.arc(self.surface, col,
                    #     [vx-amp, vy-amp, 2*amp, 2*amp],
                    #     m['a'] + np.pi/2 - m['da behind'], m['a'] + np.pi/2)

            # draw vertex v
            pygame.draw.circle(self.surface,
                col, (vx, vy), r)

        model.selecting_vertex = False

        # draw edge e in edges es connected to vertex v 
        for e in graph.edges:
            v1x = math.trunc((w * (e.vertices[0].pos[0] - model.min_x) / (model.max_x - model.min_x)) + sp[0])
            v1y = math.trunc((h * (e.vertices[0].pos[1] - model.min_y) / (model.max_y - model.min_y)) + sp[1])
            v2x = math.trunc((w * (e.vertices[1].pos[0] - model.min_x) / (model.max_x - model.min_x)) + sp[0])
            v2y = math.trunc((h * (e.vertices[1].pos[1] - model.min_y) / (model.max_y - model.min_y)) + sp[1])
            pygame.draw.line(self.surface,
                pygame.Color('white'),
                (v1x, v1y), (v2x, v2y), 2)
    def draw_2d_histogram(self, hist, sp):

        mx = max(map(max, hist))
        mn = min(map(min, hist))
        s = self.s

        # draw border of histogram
        pygame.draw.rect(self.surface, pygame.Color('white'),
            (sp[0], sp[1], s*len(hist), s*len(hist[0])), 3)

        # draw bins of histogram
        for i in range(len(hist)):
            for j in range(len(hist)):
                pygame.draw.rect(self.surface,
                    self.bin_color(hist[j][i], mx, mn),
                    [sp[0] + i*s, sp[1] + j*s, s, s])
    def bin_color(self, value, mx, mn):

        # interpolate
        if mx != 0:
            x = float(value - mn) / (mx - mn)
            return (255*x,255*x,255*x)
        else:
            return (0,0,0)


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
        self.mouse_pos = (0,0) # (x,y) position of mouse
        self.selected_vertex = None
        self.selecting_vertex = False

        self.max_x, self.min_x = 10, 0
        # self.mu_x, self.std_x = (self.max_x - self.min_x) / 2, ((self.max_x - self.min_x) / 2 ) / 3 

        self.max_y, self.min_y = 10, 0
        # self.mu_y, self.std_y = (self.max_y - self.min_y) / 2, ((self.max_y - self.min_y) / 2 ) / 3 

        self.R = (self.min_x, self.min_y, self.max_x, self.max_y) # region of 2d space
        self.topology = [self.R] # entire space

        # create 2d graph g
        self.g = Graph()
        # self.g.add_vertex((1,1))
        # self.g.add_vertex((1,3))
        # self.g.add_vertex((1,5))
        self.g.add_vertex((3,1))
        self.g.add_vertex((3,3))
        self.g.add_vertex((3,5))
        self.g.add_vertex((5,1))
        self.g.add_vertex((5,5))
        self.g.add_vertex((5,3))

        # create 2d histogram h of graph g with b^2 bins
        self.b = 40 # b = number of bins on each axis
        self.h = [[0 for x in range(self.b)] for y in range(self.b)]
        self.construct_histogram()

    def construct_histogram(self):
        for v in self.g.vertices:
            self.update_histogram(v.pos)
    def update_histogram(self, new_data_point):
        bx = math.trunc(self.b * (new_data_point[0] - self.min_x) / (self.max_x - self.min_x))
        if bx == self.b: bx -= 1
        by = math.trunc(self.b * (new_data_point[1] - self.min_y) / (self.max_y - self.min_y))
        if by == self.b: by -= 1
        self.h[by][bx] += 1

    def variable_std_dev(self, v0):
        m = []
        for v in self.g.vertices:
            if v != v0:
                m.append(
                    {'a':np.arctan2(
                        v0.pos[0] - v.pos[0],
                        v0.pos[1] - v.pos[1]),
                    'd':dist(v0, v.pos),
                    'v':v.pos})

        m = sorted(m, key=itemgetter('a'))

        for i in range(len(m)):

            # first
            if i == 0:
                vect_behind = m[len(m)-1]['v']
                vect_ahead  = m[i+1]['v']

            # last
            elif i == len(m)-1:
                vect_behind = m[i-1]['v']
                vect_ahead  = m[0]['v']
            
            # middle
            else:
                vect_behind = m[i-1]['v']
                vect_ahead  = m[i+1]['v']
            
            # change in angle ahead and behind the current angle
            da_ahead  = abs(self.da2(v0.pos, m[i]['v'], vect_ahead))
            da_behind = abs(self.da2(v0.pos, vect_behind, m[i]['v']))

            m[i]['da ahead'] = da_ahead
            m[i]['da behind'] = da_behind
            # m[i]['std_dev_ahead']  = 1.0 / da_ahead
            # m[i]['std_dev_behind'] = 1.0 / da_behind
            # m[i]['amplitude'] = 1.0 / m[i]['d']

        self.m = m

    def da(self, a1, a2, direction): # delta angle from angle a1 to a2 either clockwise or counter clockwise direction
        da = a2 - a1
        while da < -np.pi: da += 2*np.pi
        while da > np.pi:  da -= 2*np.pi
        return da
        # if direction == 'counter-clockwise':

        # if a1 >= 0 and a2 >= 0:
    def da2(self, p0, p1, p2):
        
        v1 = (p1[0] - p0[0], p1[1] - p0[1])
        v2 = (p2[0] - p0[0], p2[1] - p0[1])

        # dot = x1*x2 + y1*y2      # dot product
        # det = x1*y2 - y1*x2      # determinant

        dot = v1[0]*v2[0] + v1[1]*v2[1]      # dot product
        det = v1[0]*v2[1] - v1[1]*v2[0]      # determinant
        if det <= 0:
            return np.arctan2(det, dot)
        return 2*np.pi - np.arctan2(det, dot)

    def update(self, controller):

        # update mouse position
        self.mouse_pos = pygame.mouse.get_pos()
        # if self.selected_vertex != None:
        #     print 'mouse_pos = %s\tselected vertex = (%f, %f)' \
        #     % (self.mouse_pos, self.selected_vertex.pos[0], self.selected_vertex.pos[1])
        # else:
        #     print 'mouse_pos = %s\tselected vertex = %s' \
        #     % (self.mouse_pos, self.selected_vertex)

        if self.selected_vertex:
            self.variable_std_dev(self.selected_vertex)

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
        self.model = model
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
                    # find point closest to mouse location
                    model.selecting_vertex = True

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

    SCREEN_SIZE = (850, 350)
    model = Model(SCREEN_SIZE[0], SCREEN_SIZE[1])
    view = PyGameView(model, SCREEN_SIZE)
    controller = PyGameKeyboardController()
    running = True

    start_time = time.time()
    # period = 1
    # iterations = 0

    while running:

        # iterations += 1
        # if time.time() - start_time > period:
        #     start_time += period
        #     print('%s fps' % iterations)
        #     iterations = 0

        
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

