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

                if we can completely disconnect the stddev2
                and the distance then da = 0 wont be a problem

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
        
        self.s = 4 # s = the number of pixels a bin of the histogram is wide and tall

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

                    # delta angle
                    if m['relative'] == 'left':
                        pygame.draw.arc(self.surface, col,
                            [vx-amp, vy-amp, 2*amp, 2*amp],
                            m['a'] + np.pi/2, m['a'] + np.pi/2 + m['da'])
                    else:
                        pygame.draw.arc(self.surface, col,
                            [vx-amp, vy-amp, 2*amp, 2*amp],
                            m['a'] + np.pi/2 - m['da'], m['a'] + np.pi/2)

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

        if model.selected_vertex:
            rr = 2.0
            col = pygame.Color('blue')
            for i in range(360):
                a = np.pi * i / 180
                x = model.selected_vertex.pos[0] + rr*np.cos(a)
                y = model.selected_vertex.pos[1] + rr*np.sin(a)
                xx = math.trunc((w * (x - model.min_x) / (model.max_x - model.min_x)) + sp[0])
                yy = math.trunc((h * (y - model.min_y) / (model.max_y - model.min_y)) + sp[1])
                pygame.draw.circle(self.surface, col, (xx,yy), 1)

                sigma = model.variable_std_dev2(model.selected_vertex, (x,y))
                x  = model.selected_vertex.pos[0] + sigma*np.cos(a)
                y  = model.selected_vertex.pos[1] + sigma*np.sin(a)
                xx = math.trunc((w * (x - model.min_x) / (model.max_x - model.min_x)) + sp[0])
                yy = math.trunc((h * (y - model.min_y) / (model.max_y - model.min_y)) + sp[1])
                pygame.draw.circle(self.surface, col, (xx,yy), 1)


        # draw point of interest
        px = math.trunc((w * (model.pt_of_interest[0] - model.min_x) / (model.max_x - model.min_x)) + sp[0])
        py = math.trunc((h * (model.pt_of_interest[1] - model.min_y) / (model.max_y - model.min_y)) + sp[1])
        pygame.draw.circle(self.surface,
                pygame.Color('green'), (px, py), r)


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
                col = self.bin_color(hist[j][i], mx, mn)
                pygame.draw.rect(self.surface, col, [sp[0] + i*s, sp[1] + j*s, s, s])
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
        self.g.add_vertex((1,1))
        self.g.add_vertex((1,3))
        self.g.add_vertex((1,5))
        self.g.add_vertex((3,1))
        # self.g.add_vertex((3,3))
        # self.g.add_vertex((3,5))
        # self.g.add_vertex((4,1))
        # self.g.add_vertex((4,5))
        # self.g.add_vertex((4,3))

        self.pt_of_interest = (4,4)

        # create 2d histogram h of graph g with b^2 bins
        self.b = 80 # b = number of bins on each axis
        self.h = [[0 for x in range(self.b)] for y in range(self.b)]
        
        self.construct_histogram()

    def construct_histogram(self):

        bin_width  = ((float(self.max_x) - self.min_x) / self.b)
        bin_height = ((float(self.max_y) - self.min_y) / self.b)
        half_bin_width  = bin_width / 2.0  # half a bin width on x axis
        half_bin_height = bin_height / 2.0 # half a bin width on y axis

        # get dist_kNN for each point
        k = 22
        vk = {}
        for v in self.g.vertices:
            kNNs, net_dist = self.kNN_stuff(v.pos, k)
            vk[v] = {'kNNs':kNNs, 'net_distance':net_dist}

        # find minimum and maximum
        max_dist, min_dist = -999999999999.9, 9999999999.9
        for vert, knn_stuff in vk.iteritems():
            if max_dist < knn_stuff['net_distance']:
                max_dist = knn_stuff['net_distance']    
            if min_dist > knn_stuff['net_distance']:
                max_dist = knn_stuff['net_distance']

        # for each histogram point
        # determine its kNNs and dist_kNN
        h = [[0 for x in range(self.b)] for y in range(self.b)]
        for i in range(self.b):
            for j in range(self.b):
                bin_x = i * bin_width
                bin_y = j * bin_height
                x = bin_x + half_bin_width
                y = bin_y + half_bin_height
                kNNs, net_dist = self.kNN_stuff((x,y), k)
                h[j][i] = {'kNNs':kNNs, 'net_distance':net_dist}
                self.h[j][i] = net_dist

        # normalize it with the min and max dist_kNN


        # divide it by the normalized value of the points dist_kNN

        # for i in range(self.b):
        #     for j in range(self.b):
        #         bin_x = i * bin_width
        #         bin_y = j * bin_height
        #         x = bin_x + half_bin_width
        #         y = bin_y + half_bin_height
        #         for v in self.g.vertices:
        #             self.h[j][i] += 1.0/(dist(v, (x, y))**0.25)
        #         # self.h[j][i] = 1.0 / self.h[j][i]
    def kNN_stuff(self, v0, k):
        kNNs = []
        for v in self.g.vertices:
            if v.pos != v0:
                d = dist(v, v0)
                i = self.index_of_new(kNNs, d)
                kNNs.insert(i, {'v':v, 'd':d})
        kNNs = kNNs[:k]
        net_dist = 0.0
        for v in kNNs:
            net_dist += v['d']
        return kNNs, net_dist
    def index_of_new(self, list, value):
        # finds index in list to keep list sorted
        if len(list) == 0:
            return 0
        else:
            for i in range(len(list)):
                if value < list[i]['d']:
                    return i
            return len(list)


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
            self.variable_std_dev2(self.selected_vertex, self.pt_of_interest)

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

    SCREEN_SIZE = (850, 500)
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

