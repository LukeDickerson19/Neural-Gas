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

        need to read through the part that determines the std dev
            once you understand how it should work theoretically
                need to plot that stuff to verify it works according to theory
                this is how you will find how it deviates from theory, correct it, and test the theory
 
                da should be the same for (3,1) and (3,5) when (3,3) is selected
                what should the rate at which angle decay happens?
                    90 or 180
                    whats the equation though?
                    doesnt seem to be conforming as imagined
                    might need to do an exponetial decay

                C constant needs to be relative to stuff

                OK i think I might have got it
        -->     I need to verify that it works for multiple topologies
                if it does, i need to package it up and put it in the real code
                    might be to slow
                        might need to kNN optimization
                        closest and farthest updating?
                            closest can be done in constant time
                            farthest?

                also put the package in its own file and make a pretty readme for it


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

        # determine the selected vertex
        for v in graph.vertices:

            # interpolate v to screen
            vx = math.trunc((w * (v.pos[0] - model.min_x) / (model.max_x - model.min_x)) + sp[0])
            vy = math.trunc((h * (v.pos[1] - model.min_y) / (model.max_y - model.min_y)) + sp[1])

            # determine selected vertex sv
            if model.selecting_vertex:
                # interpolate sv to screen
                svx = math.trunc((w * (model.selected_vertex.pos[0] - model.min_x) / (model.max_x - model.min_x)) + sp[0])
                svy = math.trunc((h * (model.selected_vertex.pos[1] - model.min_y) / (model.max_y - model.min_y)) + sp[1])
                if math.sqrt((vx - model.mouse_pos[0])**2 + (vy - model.mouse_pos[1])**2) < \
                    math.sqrt((svx - model.mouse_pos[0])**2 + (svy - model.mouse_pos[1])**2):
                    model.selected_vertex = v
            
            if v == model.selected_vertex:
                col = pygame.Color('red')
            else:
                col = pygame.Color('white')

            # # draw angles of selected vertex
            # if not model.selecting_vertex and v == model.selected_vertex:
            #     amp = 20
            #     for m in model.m:
            #         amp += 5 

            #         # delta angle
            #         if m['relative'] == 'left':
            #             pygame.draw.arc(self.surface, col,
            #                 [vx-amp, vy-amp, 2*amp, 2*amp],
            #                 m['a'] + np.pi/2, m['a'] + np.pi/2 + m['da'])
            #         else:
            #             pygame.draw.arc(self.surface, col,
            #                 [vx-amp, vy-amp, 2*amp, 2*amp],
            #                 m['a'] + np.pi/2 - m['da'], m['a'] + np.pi/2)

            #         # # delta angle ahead
            #         # pygame.draw.arc(self.surface, col,
            #         #     [vx-amp, vy-amp, 2*amp, 2*amp],
            #         #     m['a'] + np.pi/2, m['a'] + np.pi/2 + m['da ahead'])

            #         # # delta angle behind
            #         # pygame.draw.arc(self.surface, col,
            #         #     [vx-amp, vy-amp, 2*amp, 2*amp],
            #         #     m['a'] + np.pi/2 - m['da behind'], m['a'] + np.pi/2)

            # draw vertex v
            pygame.draw.circle(self.surface,
                col, (vx, vy), r)

        # draw stuff for selected vertex
        if model.selected_vertex:
            rr = 2.0
            col = pygame.Color('blue')
            for i in range(360):
                a = np.pi * i / 180

                # # draw circle
                x = model.selected_vertex.pos[0] + rr*np.cos(a)
                y = model.selected_vertex.pos[1] + rr*np.sin(a)
                # xx = math.trunc((w * (x - model.min_x) / (model.max_x - model.min_x)) + sp[0])
                # yy = math.trunc((h * (y - model.min_y) / (model.max_y - model.min_y)) + sp[1])
                # pygame.draw.circle(self.surface, col, (xx,yy), 1)

                # draw standard deviation
                if model.selecting_vertex:
                    print 'pt = (%f,%f)' % (x,y)
                sigma = model.variable_std_dev2(model.selected_vertex, (x,y), model.selecting_vertex)
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
        # self.g.add_vertex((1,1))
        # self.g.add_vertex((1,3))
        # self.g.add_vertex((1,5))
        # self.g.add_vertex((3,1))
        # self.g.add_vertex((3,3))
        # self.g.add_vertex((3,5))
        # self.g.add_vertex((4,1))
        # self.g.add_vertex((4,5))
        # self.g.add_vertex((4,3))

        self.g.add_vertex((1,1))
        # self.g.add_vertex((2,1))
        # self.g.add_vertex((3,1))
        # self.g.add_vertex((4,1))
        # self.g.add_vertex((5,1))
        # self.g.add_vertex((3,2))
        # self.g.add_vertex((3,3))
        # self.g.add_vertex((3,4))
        # self.g.add_vertex((3,5))
        self.g.add_vertex((1,6))
        # self.g.add_vertex((2,6))
        self.g.add_vertex((3,6))
        # self.g.add_vertex((4,6))
        self.g.add_vertex((5,6))

        self.pt_of_interest = (7,3)

        # find closest and farthers points
        self.closest, self.farthest = 999999999999.9, -9999999999999.9
        for v0 in self.g.vertices:
            for v in self.g.vertices:
                if v != v0:
                    d = dist(v0, v.pos)
                    if d < self.closest:  self.closest = d
                    if d > self.farthest: self.farthest = d

        # create 2d histogram h of graph g with b^2 bins
        self.b = 80 # b = number of bins on each axis
        self.h = [[0 for x in range(self.b)] for y in range(self.b)]
        self.construct_histogram4()

    def construct_histogram2(self):

        bin_width  = ((float(self.max_x) - self.min_x) / self.b)
        bin_height = ((float(self.max_y) - self.min_y) / self.b)
        half_bin_width  = bin_width / 2.0  # half a bin width on x axis
        half_bin_height = bin_height / 2.0 # half a bin width on y axis

        for i in range(self.b):
            for j in range(self.b):
                bin_x = i * bin_width
                bin_y = j * bin_height
                x = bin_x + half_bin_width
                y = bin_y + half_bin_height
                for v in self.g.vertices:
                    self.h[j][i] += 1.0/(dist(v, (x, y))**0.25)
                # self.h[j][i] = 1.0 / self.h[j][i]

    def construct_histogram3(self):
        
        bin_width  = ((float(self.max_x) - self.min_x) / self.b)
        bin_height = ((float(self.max_y) - self.min_y) / self.b)
        half_bin_width  = bin_width / 2.0  # half a bin width on x axis
        half_bin_height = bin_height / 2.0 # half a bin width on y axis

        for i in range(self.b):
            for j in range(self.b):
                bin_x = i * bin_width
                bin_y = j * bin_height
                x = bin_x + half_bin_width
                y = bin_y + half_bin_height
                s0 = 0.0
                for v1 in self.g.vertices:
                    s0 += self.dist_kNN(v1, 4) / dist(v1, (x, y))
                    # s = 0.0
                    # for v2 in self.g.vertices:
                    #     s += dist(v1, v2.pos)
                    # s0 += s / dist(v1, (x, y))
                self.h[j][i] = s0

    def dist_kNN(self, v0, k):
        k_nearest = []
        for v in self.g.vertices:
            if v != v0:
                if len(k_nearest) < k:
                    k_nearest.append(dist(v0, v.pos))
                else:
                    k_nearest = sorted(k_nearest, reverse=True)
                    for i in range(len(k_nearest)):
                        d = dist(v0, v.pos)
                        if d < k_nearest[i]: k_nearest[i] = d
        return sum(k_nearest)

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
        print self.m
        print '\n'

    def da(self, a1, a2, direction): # delta angle from angle a1 to a2 either clockwise or counter clockwise direction
        da = a2 - a1
        while da < -np.pi: da += 2*np.pi
        while da > np.pi:  da -= 2*np.pi
        return da
        # if direction == 'counter-clockwise':

        # if a1 >= 0 and a2 >= 0:
    def da2(self, p0, p1, p2):
        
        v1 = (p1[0] - p0[0], p1[1] - p0[1]) # vector1
        v2 = (p2[0] - p0[0], p2[1] - p0[1]) # vector2

        # dot = x1*x2 + y1*y2      # dot product
        # det = x1*y2 - y1*x2      # determinant

        dot = v1[0]*v2[0] + v1[1]*v2[1]      # dot product
        det = v1[0]*v2[1] - v1[1]*v2[0]      # determinant
        if det <= 0:
            return np.arctan2(det, dot)
        return 2*np.pi - np.arctan2(det, dot)
    def da3(self, p0, p1, p2):
        
        v1 = (p1[0] - p0[0], p1[1] - p0[1]) # vector1
        v2 = (p2[0] - p0[0], p2[1] - p0[1]) # vector2

        # dot = x1*x2 + y1*y2      # dot product
        # det = x1*y2 - y1*x2      # determinant

        dot = v1[0]*v2[0] + v1[1]*v2[1]      # dot product
        det = v1[0]*v2[1] - v1[1]*v2[0]      # determinant

        if det <= 0:
            return np.arctan2(det, dot), 'right'
        return np.arctan2(det, dot), 'left'

    def construct_histogram4(self):
        
        bin_width  = ((float(self.max_x) - self.min_x) / self.b)
        bin_height = ((float(self.max_y) - self.min_y) / self.b)
        half_bin_width  = bin_width / 2.0  # half a bin width on x axis
        half_bin_height = bin_height / 2.0 # half a bin width on y axis

        for i in range(self.b):
            for j in range(self.b):
                bin_x = i * bin_width
                bin_y = j * bin_height
                x = bin_x + half_bin_width
                y = bin_y + half_bin_height
                for v0 in self.g.vertices:
                    sigma = self.variable_std_dev2(v0, (x, y), False)
                    if sigma != 0:
                        self.h[j][i] += normpdf(dist(v0, (x,y)), 0, sigma)
                    
    def variable_std_dev2(self, v0, pt, printt):

        # finds the variable standard deviation sigma of 1 vertex v0
        # along the line created between v0 and the point of interest pt
        # using the variable standard deviation technique
        # where the farther away a vertex v is from
        # v0 the less v adds to sigma
        # also the greater the angle between the vector
        # v0 to v and v0 pt is
        # the less v adds to sigma
        # the constant C needs to be updated to 
        # account for the fact that this method could
        # make the standard deviation too small
        sigma = 0.0
        self.m = []
   
        output = '--------------------------\n'
        output += 'closest = %f   farthest = %f\n' % (self.closest, self.farthest)
        output += 'v0 = (%d,%d)\n' % (v0.pos[0], v0.pos[1])
        for v in self.g.vertices:
            if v != v0:
                d = dist(v0, v.pos)
                da, rel = self.da3(v0.pos, pt, v.pos)
                output += '\tv = (%d,%d):  d = %f   da = %f   rel = %s\n' % (v.pos[0], v.pos[1], d, da, rel)
                effect, effect_output = self.effect(abs(da), d, self.closest, self.farthest)
                output += effect_output
                sigma += effect
                self.m.append({'da':abs(da), 'relative':rel, 'd':d})
        output += '--------------------------\n'

        if printt:
            print output
    
        return sigma

    def effect(self, a, d, closest, farthest):

        # THIS IS JUST A TEMPORARY SOLUTION
        # it needs to be determined how the mind
        # fundamentally constructs the idea
        # of density of points
        # POSSIBLE BETTER algorithm
        # density is the relative distance between points
        # find the k nearest neighbors (kNN) of every point
        # determine the sum euclidean distance of those k neighbors
        # the density of arbitrary point p equals
        # the sum distance of the kNN of the nearest
        # neighbor to point p relative to the summ kNN
        # of all the other points

        # a variers between 0 degrees and 180 degrees
        if a > np.pi:
            mapped_a = 0
        else:
            #mapped_a = np.cos(a / 2.0)
            mapped_a = 0.15**a

        output = '\t\tmapped da = %f\n' % mapped_a

        # d varies between 0 and whatever the max
        # diagonal distance of the graph is
        # mapped_d = 0.35**d
        
        # FUTURE OPTIMIZATION: need to incorrporate RELATIVE distance somehow
        # interpolate d between the closest and farthest d
        output += '\t\tmapped_d: '
        output += '%f' % d
        mapped_d = (d - closest) / (farthest - closest)
        output += ' --> %f' % mapped_d
        # exponential decay
        mapped_d = 0.0001**mapped_d
        output += ' --> %f' % mapped_d
        # scale that number thats between 0 and 1 to be between
        # max_percentage and min_percentage
        min_percentage, max_percentage = 0.01, 0.75
        mapped_d = mapped_d * (max_percentage - min_percentage) + min_percentage
        output += ' --> %f' % mapped_d
        # this is the percentage of d that sigma will have
        mapped_d *= d
        output += ' --> %f' % mapped_d

        output += '\t\tmapped d = %f\n' % mapped_d

        # C is just a constant to scale it
        # reset to 1.0 because the the mapped_d optimization
        C = 1.0

        output += '\t\teffect = %f\n' % (C * mapped_a * mapped_d)

        return C * mapped_a * mapped_d, output

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
            self.variable_std_dev2(self.selected_vertex, self.pt_of_interest, False)

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

