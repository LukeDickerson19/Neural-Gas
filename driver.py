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

        SHORT TERM (now):

            make neural gas histogram
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

            make this work in python 3.5 too


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

    def draw_simulation(self):

        # fill background
        self.surface.fill(pygame.Color('black'))

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
    def draw_2d_graph_old(self, graph, sp, r=3):

        w, h = model.b * self.s, model.b * self.s

        # draw border graph resides in
        pygame.draw.rect(self.surface,
            pygame.Color('white'),
            (sp[0], sp[1], w, h), 1)
            
        # draw graph
        edges = []
        for v, es in graph.items():

            # interpolate v to screen
            vx = math.trunc((w * (v[0] - model.min_x) / (model.max_x - model.min_x)) + sp[0])
            vy = math.trunc((h * (v[1] - model.min_y) / (model.max_y - model.min_y)) + sp[1])
            
            # draw vertex v
            pygame.draw.circle(self.surface,
                pygame.Color('white'),
                (vx, vy), r)

            # draw edge e in edges es connected to vertex v 
            for e in es:
                if not (e, v) in edges:
                    edges.append((e, v))
                    pygame.draw.line(self.surface,
                        pygame.Color('white'),
                        (sp[0]+v[0], sp[1]+v[1]), 
                        (sp[0]+e[0], sp[1]+e[1]),
                        2)
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

        ############## NEURAL GAS LOGIC STARTS HERE ##################

        # raw data has a 2d normal distribution
        self.raw_data = Graph()
        
        self.max_x, self.min_x = 10, 0
        self.mu_x, self.std_x = (self.max_x - self.min_x) / 2, ((self.max_x - self.min_x) / 2 ) / 3 

        self.max_y, self.min_y = 10, 0
        self.mu_y, self.std_y = (self.max_y - self.min_y) / 2, ((self.max_y - self.min_y) / 2 ) / 3 

        self.R  = (self.min_x, self.min_y, self.max_x, self.max_y)

        self.b = 20 # b = the number of bins the histogram is wide and tall
        self.raw_histogram = [[0 for x in range(self.b)] for y in range(self.b)]


        self.neural_gas = NeuralGas(self)

        self.gas_histogram = [[0 for x in range(self.b)] for y in range(self.b)]
        self.gas_std_dev = 1.0

        ###################### continued in update ####################

    def update(self, controller):
        
        # create new data point in 2d normal distribution
        new_data_point = random2dPoint(
            self.min_x, self.max_x, self.mu_x, self.std_x, 
            self.min_y, self.max_y, self.mu_y, self.std_y,
            'normal')

        # add it to list of data
        # self.raw_data.add_vertex(new_data_point)
        self.num_data_points += 1

        # add it to raw data histogram
        bx = math.trunc(self.b * (new_data_point[0] - self.min_x) / (self.max_x - self.min_x))
        if bx == self.b: bx -= 1
        by = math.trunc(self.b * (new_data_point[1] - self.min_y) / (self.max_y - self.min_y))
        if by == self.b: by -= 1
        self.raw_histogram[by][bx] += 1

        # update the neural gas
        self.neural_gas.update(new_data_point)

        # update neural gas histogram
        self.update_gas_histogram()

    def update_gas_histogram(self):

        # reset
        self.gas_histogram = [[0 for x in range(self.b)] for y in range(self.b)]

        half_bin_width = (float(self.max_x) - self.min_x) / (2*self.b) # half a bin width on x axis
        half_bin_height = (float(self.max_y) - self.min_y) / (2*self.b) # half a bin width on y axis

        # sum fourier series
        for u in self.neural_gas.vertices:
            for i in range(self.b):
                for j in range(self.b):
                    bin_x = i * ((float(self.max_x) - self.min_x) / self.b)
                    bin_y = j * ((float(self.max_y) - self.min_y) / self.b)
                    self.gas_histogram[j][i] += normpdf(dist(u, (bin_x+half_bin_width,bin_y+half_bin_height)), 0, self.gas_std_dev)


class PyGameKeyboardController(object):

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

    SCREEN_SIZE = (750, 600)
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


