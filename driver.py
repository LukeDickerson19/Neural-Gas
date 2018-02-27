import pygame
import random
import time
import math
from pygame.locals import QUIT, KEYDOWN
from pygame import gfxdraw
import os, sys
import numpy as np
from neural_gas import *


''' NOTES:

    TO DO:

        implement new way to do neural gas histogram
            see histogram_creator_test TO DO

        need to experiment with neural gas hyper parameters

        once you have a deeper understanding of it
        make a new video with new hyper parameter output for 2d normal dist.
        make a video or image of I topology
            1 with standard hyper parameters
            1 with modified ones
                the current hyper parameters make a pretty
                good neural gas when the number of data points reaches about 600

                the hyper-parameters of the neural gas seem to basically create a
                trade off of accuracy of data representation with speed and memory
                usage

        make neural gas histogram

            if the std of the gas histogram was 
            based off the neighbors as it wraps arounds
            the mean in 2d maybe it could represent it really well

            how are we going to make the
            probability density function?
                create 2d fourier series
                    normal distribution as base function
                    mean is the location of each unit
                    std_dev is based on:
                        total number of Units
                        total number of data points 
                        
                        ... if you could model this in mathematica
                        where you could plot the 2d normal distributions
                        both individually where they overlap and cumutively
                        where they sum to form the actual distribution
                        and you could pause the data stream and 
                        modify what the std_dev is, to represent the data
                        as accurately as possible .. see if that value holds
                        its accuracy when the data stream is unpaused ...
                        is there a way to then do this mathematically
                        ... for now i could create this fourier serires thing,
                        and just make std_dev a constant, (or a fn. of the 
                            num of units and num of data points)
                        and then see hwo the mean squared error of the histogram
                        fluctuates over time as data is input

                        ... wtf this doesnt use the edges at all!

                maybe we could increase the probability for areas enclosed
                by edges


    SOURCES:

        pygame
        https://www.pygame.org/docs/

        A Growing Neural Gas Learns Topologies - Original Research Paper
        https://papers.nips.cc/paper/893-a-growing-neural-gas-network-learns-topologies.pdf

        C++ implementation of growing neural gas:
        https://github.com/BelBES/libGNG/blob/master/GNG.cpp
            helped clear up how to calculate error

        '''

class PyGameView(object):

    def __init__(self, model, size):

        self.model = model
        self.screen = pygame.display.set_mode((size[0], size[1]))
        self.surface = pygame.Surface((size[0], size[1]))

        self.s = 10 # s = the number of pixels a bin of the histogram is wide and tall

        # draw non changing images
        self.draw_text_in_simulation(
            str('Eb = %f' % model.neural_gas.Eb),
            150, 50 + 2*model.b * self.s + 50, 20, pygame.Color('white'))
        self.draw_text_in_simulation(
            str('En = %f' % model.neural_gas.En),
            150, 50 + 2*model.b * self.s + 70, 20, pygame.Color('white'))
        self.draw_text_in_simulation(
            str('alpha = %f' % model.neural_gas.alpha),
            150, 50 + 2*model.b * self.s + 90, 20, pygame.Color('white'))
        self.draw_text_in_simulation(
            str('a_max = %d' % model.neural_gas.a_max),
            150, 50 + 2*model.b * self.s + 110, 20, pygame.Color('white'))
        self.draw_text_in_simulation(
            str('lambda = %d' % model.neural_gas.lmbda),
            150, 50 + 2*model.b * self.s + 130, 20, pygame.Color('white'))
        self.draw_text_in_simulation(
            str('d = %f' % model.neural_gas.d),
            150, 50 + 2*model.b * self.s + 150, 20, pygame.Color('white'))

    def draw_simulation(self):

        # fill background
        # self.surface.fill(pygame.Color('black'))
        # clear parts that are changing
        pygame.draw.rect(self.surface, pygame.Color('black'),
            [149, 29, 2 * model.b * self.s + 25, 2 * model.b * self.s + 65])

        #pygame.draw.circle(self.surface, pygame.Color('green'), (50,50), 10)
        #pygame.draw.line(self.surface,   (255,255,255), (10, 20), (30, 40), 4) # (start_x, start_y), (end_x, end_y), width
        #pygame.draw.rect(self.surface,   pygame.Color('red'), [100, 100, 40, 100])

        # draw actual data
        self.draw_2d_graph(model.raw_data, (150, 50), r=2)

        # draw histogram of actual data
        self.draw_2d_histogram(model.raw_histogram, (150 + model.b * self.s + 25, 50))

        # draw neural gas network
        self.draw_2d_graph(model.neural_gas, (150, 50 + model.b * self.s + 25))

        # draw histogram of neural gas
        self.draw_2d_histogram(model.gas_histogram, (150 + model.b * self.s + 25, 50 + model.b * self.s + 25))

        # provide data:
        #    Number of data points (in top left plot)
        self.draw_text_in_simulation(
            str('Number of Data Points = %d' % model.num_data_points),
            150, 30, 20, pygame.Color('white'))
        #    Number of Units (Nodes in bottom left plot)
        self.draw_text_in_simulation(
            str('Number of Units = %d' % len(model.neural_gas.vertices)),
            150, 50 + 2*model.b * self.s + 30, 20, pygame.Color('white'))

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
        for v in graph.vertices:

            # interpolate v to screen
            vx = math.trunc((w * (v.pos[0] - model.min_x) / (model.max_x - model.min_x)) + sp[0])
            vy = math.trunc((h * (v.pos[1] - model.min_y) / (model.max_y - model.min_y)) + sp[1])
            
            # draw vertex v
            pygame.draw.circle(self.surface,
                pygame.Color('white'),
                (vx, vy), r)

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

        #window parameters / drawing
        self.height = height
        self.width = width
        self.show = True # show current model
        self.show_controls = False # controls toggle

        self.num_data_points = 0

        # raw data has a 2d normal distribution
        self.raw_data = Graph()
        
        self.max_x, self.min_x = 10, 0
        self.mu_x, self.std_x = (self.max_x - self.min_x) / 2, ((self.max_x - self.min_x) / 2 ) / 3 

        self.max_y, self.min_y = 10, 0
        self.mu_y, self.std_y = (self.max_y - self.min_y) / 2, ((self.max_y - self.min_y) / 2 ) / 3 

        self.R = (self.min_x, self.min_y, self.max_x, self.max_y) # region of 2d space
        self.topology = [self.R] # entire space
        # self.topology = [
        #     (2, 2, 7, 3),
        #     (4, 3, 5, 7),
        #     (2, 7, 7, 8)
        # ] # I-beam shaped topology
        self.distribution = 'normal'

        self.b = 20 # b = the number of bins the histogram is wide and tall
        self.raw_histogram = [[0 for x in range(self.b)] for y in range(self.b)]


        self.neural_gas = NeuralGas(self)

        self.gas_histogram = [[0 for x in range(self.b)] for y in range(self.b)]
        self.gas_std_dev = 0.75

        # mean squared error histogram
        self.mse_histogram = [[0 for x in range(self.b)] for y in range(self.b)]


    def update(self, controller):
        
        # create new data point in 2d normal distribution
        new_data_point = random2dPoint(
            self.distribution, self.topology, self.R,
            self.mu_x, self.std_x, self.mu_y, self.std_y)

        # add it to list of data
        self.raw_data.add_vertex(new_data_point)
        self.num_data_points += 1

        # add it to raw data histogram
        self.update_raw_histogram(new_data_point)
        
        # update the neural gas
        self.neural_gas.update(new_data_point)

        # update neural gas histogram
        self.update_gas_histogram()

        # update mean squared error histogram
        # self.update_mse()

    def update_raw_histogram(self, new_data_point):
        bx = math.trunc(self.b * (new_data_point[0] - self.min_x) / (self.max_x - self.min_x))
        if bx == self.b: bx -= 1
        by = math.trunc(self.b * (new_data_point[1] - self.min_y) / (self.max_y - self.min_y))
        if by == self.b: by -= 1
        self.raw_histogram[by][bx] += 1

    def update_gas_histogram(self):

        # reset
        self.gas_histogram = [[0 for x in range(self.b)] for y in range(self.b)]

        self.variable_std_dev_fourier_hist()

    def basic_fourier_hist(self):
        
        # sum fourier series
        bin_width  = ((float(self.max_x) - self.min_x) / self.b)
        bin_height = ((float(self.max_y) - self.min_y) / self.b)
        half_bin_width  = bin_width / 2.0  # half a bin width on x axis
        half_bin_height = bin_height / 2.0 # half a bin width on y axis
        for u in self.neural_gas.vertices:
            for i in range(self.b):
                for j in range(self.b):
                    bin_x = i * bin_width
                    bin_y = j * bin_height
                    self.gas_histogram[j][i] += normpdf(dist(u, (bin_x+half_bin_width,bin_y+half_bin_height)), 0, self.gas_std_dev)

    def variable_std_dev_fourier_hist(self):

        bin_width  = ((float(self.max_x) - self.min_x) / self.b)
        bin_height = ((float(self.max_y) - self.min_y) / self.b)
        half_bin_width  = bin_width / 2.0
        half_bin_height = bin_height / 2.0
        verts = {}
        for u1 in self.neural_gas.vertices:
            verts[u1] = {'neighbors':[]}
            for u2 in self.neural_gas.vertices:
                if u1 != u2:
                    verts[u1]['neighbors'].append(u2)

        # for v, n in verts.items():
        #     pass

    def scaled_histogram(self, hist):

        scaled_hist = [[0.0 for x in range(self.b)] for y in range(self.b)]

        mx = max(map(max, hist))
        mn = min(map(min, hist))
        if mx == 0: return scaled_hist

        for i in range(self.b):
            for j in range(self.b):
                scaled_hist[j][i] = (hist[j][i] - mn) / (mx - mn)

        return scaled_hist

    def update_mse(self):

        scaled_gas_hist = self.scaled_histogram(self.gas_histogram)
        scaled_raw_hist = self.scaled_histogram(self.raw_histogram)

        for i in range(self.b):
            for j in range(self.b):
                self.mse_histogram[j][i] = \
                (scaled_gas_hist[j][i] - scaled_raw_hist[j][i])**2


class PyGameKeyboardController(object):

    def __init__(self):
        """
        Creates keyboard controller

        Args:
            model (object): contains attributes of the environment
        """
        #self.model = model
        self.paused = True

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

    SCREEN_SIZE = (850, 650)
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

        if model.num_data_points > 10000:
            print 'pausing because there are 10000 data points. Continuing will take up a lot of memory ...'
            controller.paused = True

        if model.show:
            view.draw_simulation()
            view.screen.blit(view.surface, (0,0))
            pygame.display.update()
            # time.sleep(1.1)


