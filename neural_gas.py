import random
import time
import math
import os, sys
import numpy as np



def dist(a, b):
	# a is of type Unit or Vertex
	# b is a tuple: (x, y)
	return math.sqrt((a.pos[0] - b[0])**2 + (a.pos[1] - b[1])**2)
def random2dPoint(
	min_x, max_x, mu_x, std_x,
	min_y, max_y, mu_y, std_y,
	distribution):

	if distribution == 'uniform':
	    x = np.random.uniform(mu_x, std_x, 1)[0]
	    if x > max_x: x = max_x
	    if x < min_x: x = min_x
	    y = np.random.uniform(mu_x, std_x, 1)[0]
	    if y > max_y: y = max_y
	    if y < min_y: y = min_y

	elif distribution == 'normal':
	    x = np.random.normal(mu_x, std_x, 1)[0]
	    if x > max_x: x = max_x
	    if x < min_x: x = min_x
	    y = np.random.normal(mu_x, std_x, 1)[0]
	    if y > max_y: y = max_y
	    if y < min_y: y = min_y

	else:
		print 'invalid distribution. must be: \'uniform\' or \'normal\''
		sys.exit() 

	return (x, y)

class Vertex():

	def __init__(self, pos):
		# pos is a tuple: (x, y)
		self.pos = pos

	def move(self, dx, dy):

		self.pos = (self.pos[0] + dx, self.pos[1] + dy)

	def print_vertex(self):
		print '\tVertex: (%.4f, %.4f)' % ( \
			self.pos[0],
			self.pos[1])
class Unit(Vertex):

	def __init__(self, x, y):
		Vertex.__init__(self, (x, y))
		self.error = 0

	def __init__(self, v):
		Vertex.__init__(self, v)
		self.error = 0

class Edge():

	def __init__(self, v1, v2):
		# v1 and v2 are of type Vertex
		self.vertices = (v1, v2)

	def has_vertex(self, v):

		return self.vertices[0] == v or self.vertices[1] == v
		
	def print_edge(self):
		print '\tEdge: (%.4f, %.4f)-(%.4f, %.4f)' % ( \
			self.vertices[0].pos[0],
			self.vertices[0].pos[1], 
			self.vertices[1].pos[0], 
			self.vertices[1].pos[1])
class GasEdge(Edge):

	def __init__(self, u1, u2):
		# u1 and u2 are of type Unit
		Edge.__init__(self, u1, u2)
		self.age = 0

	def increment_age(self):

		self.age += 1



class Graph():

	def __init__(self):

		self.vertices = []
		self.edges = []

	def add_vertex(self, v):
		# v is a tuple: (x, y)
		self.vertices.append(Vertex(v))
	def remove_vertex(self, v):
		# v is of type Vertex
		if v in self.vertices:
			self.vertices.remove(v)
			return v
		return None
	def get_vertex(self, v):
		# v is a tuple: (x, y)
		for v0 in self.vertices:
			if v0.pos == v:
				return v0
		return None

	def add_edge(self, v1, v2):
		# v1 and v2 are of type Vertex
		self.edges.append(Edge(v1, v2))
	def remove_edge(self, e):
		if e in self.edges:
			self.edges.remove(e)
			return e
		return None
	def remove_edge2(self, v1, v2):
		# v1 and v2 are of type Vertex
		e = self.get_edge(v1, v2)
		return self.remove_edge(e)
	def get_edge(self, v1, v2):
		# v1 and v2 are of type Vertex
		for e in self.edges:
			if e.vertices[0] == v1 and e.vertices[1] == v2 or \
				e.vertices[0] == v2 and e.vertices[1] == v1:
				return e
		return None

	def neighbors(self, v1, v2):
		# v1 and v2 are of type Vertex
		# returns true if v1 and v2 are neighbors
		return any(map(lambda e: e.has_vertex(v1) and e.has_vertex(v2), self.edges))
	def isolated(self, v1):
		# v1 is of type Vertex
		# returns true if v1 has not edges to any other vertices
		return not any(map(lambda e: e.has_vertex(v1), self.edges))

	def print_graph(self):
		print '-----------'
		print 'VERTICTES:'
		for v in self.vertices:
			v.print_vertex()
		print 'EDGES:'
		for e in self.edges:
			e.print_edge()
		print '-----------\n'

class NeuralGas(Graph):

	def __init__(self, model):
		Graph.__init__(self)

		self.model = model
		self.graph = {}

		# add points a and b
		a = random2dPoint(
            model.min_x, model.max_x, model.mu_x, model.std_x, 
            model.min_y, model.max_y, model.mu_y, model.std_y,
            'uniform')
		b = random2dPoint(
            model.min_x, model.max_x, model.mu_x, model.std_x, 
            model.min_y, model.max_y, model.mu_y, model.std_y,
            'uniform')
		self.add_unit(a)
		self.add_unit(b)

		self.Eb = 0.2
		self.En = 0.006
		self.alpha = 0.5
		self.a_max = 50 # max age an edge can have
		self.num_input_signals = 0
		self.lmbda = 100
		self.d = 0.995

	def update(self, new_data):

		# find nearst(s1) and 2nd nearest(s2) units (vertices)
		# in neural gas graph to new_data point
		s1, s2 = self.find_nearest_2_points(new_data)

		# print 's1:'
		# s1.print_vertex()
		# print 's2:'
		# s2.print_vertex()

		# print '\nincrementing age of edges eminating from s1'
		# print 'ages before:'		
		# for e in self.edges:
		# 	e.print_edge()
		# 	print e.age

		# increment age of all edges eminating from s1
		for e in self.edges:
			if e.has_vertex(s1):
				e.increment_age()

		# print 'ages after:'
		# for e in self.edges:
		# 	e.print_edge()
		# 	print e.age


		# Add the squared distance between the input signal and the nearest unit in
		# input space to a local counter variable (pretty sure they're talking about
		# the error of s1 here)
		# print '\nadding dist(d1, new_data)**2 to s1.error'
		# print 'before: %f' % s1.error
		s1.error += dist(s1, new_data)**2
		# print 'after: %f' % s1.error

		# Move s1 and its direct topological neighbors towards new_data by fractions
		# Eb and En, respectively, of the total distance
		# print '\nmoving s1 and neighbors by Eb and En'
		# print 'before'
		# for u in self.vertices:
		# 	u.print_vertex()
		for i, u in enumerate(self.vertices):
			if u == s1:
				self.vertices[i].move(self.Eb*(new_data[0]-u.pos[0]), self.Eb*(new_data[1]-u.pos[1]))
			elif self.neighbors(u, s1):
				self.vertices[i].move(self.Eb*(new_data[0]-u.pos[0]), self.Eb*(new_data[1]-u.pos[1]))
		# print 'after'
		# for u in self.vertices:
		# 	u.print_vertex()


		# If s1 and s2 are connected by an edge, set the age of this edge to zero. If
		# such an edge does not exist, create it.
		# print '\nsetting age of s1-s2 to 0 if it exists, or creating it'
		edge_s1_s2 = self.get_edge(s1, s2)
		if edge_s1_s2 != None:
			# print 'before'
			# edge_s1_s2.print_edge()
			edge_s1_s2.age = 0
		else:
			# print 'before: edge did not exist'
			self.add_gas_edge(s1, s2)
		# print 'after'
		# self.get_edge(s1, s2).print_edge()
		
		# Remove edges with an age larger than a_max. If this results in points having
		# no emanating edges, remove them as well.
		# print '\nremoving edges older than %d' % self.a_max
		# print 'before'
		# for e in self.edges:
		# 	e.print_edge()
		for i, e in enumerate(self.edges):
			if e.age > self.a_max:
				eu1, eu2 = e.vertices
				self.remove_gas_edge(e)
				if self.isolated(eu1):
					self.remove_vertex(eu1)
				if self.isolated(eu2):
					self.remove_vertex(eu2)
		# print 'after'
		# for e in self.edges:
		# 	e.print_edge()

		# If the number of input signals generated so far is an integer multiple of a
		# parameter lmbda, insert a new unit as follows:
		self.num_input_signals += 1
		if self.num_input_signals % self.lmbda == 0:

			# print 'entered if self.num_input_signals % self.lmbda == 0'

			# 	Determine the unit q with the maximum accumulated error.
			q = self.vertices[0]
			for u in self.vertices:
				if u.error > q.error:
					q = u
			# print 'q:'
			# print q.print_vertex()

 			# Insert a new unit r halfway between q and its neighbor f with the
			# largest error variable: Wr = 0.5 (wq + wf)
			f = self.vertices[0]
			if f == q: f = self.vertices[1]
			for u in self.vertices:
				if self.get_gas_edge(u, q) != None:
					if u.error > f.error:
						f = u

			#f = max([u.error for u in (set(self.vertices) - set([q]))])
			# print 'f:'
			# print f.print_vertex()
			
			r = Unit((0.5*(q.pos[0]+f.pos[0]),0.5*(q.pos[1]+f.pos[1])))
			# print 'r:'
			# print r.print_vertex()
			# print 'adding r'
			# print 'before'
			# for u in self.vertices:
			# 	u.print_vertex()
			self.add_unit(r)
			# print 'after'
			# for u in self.vertices:
			# 	u.print_vertex()

			# Insert edges connecting the new unit r with units q and f, and remove
			# the original edge between q and f.
			# print '\ncreating q-r and r-f and removing q-f'
			# print 'before'
			# for e in self.edges:
			# 	e.print_edge()
			self.add_gas_edge(q, r)
			self.add_gas_edge(f, r)
			self.remove_gas_edge2(q, f)
			# print 'after'
			# for e in self.edges:
			# 	e.print_edge()

			# Decrease the error variables of q and f by multiplying them with a
			# constant self.alpha Initialize the error variable of r with the new value of the
			# error variable of q.
			# print '\nq and f error *= alpha'
			# print 'before'
			# print q.error
			# print f.error
			q.error *= self.alpha
			f.error *= self.alpha
			# print 'after'
			# print q.error
			# print f.error
			# print 'r error = q error'
			# print 'before'
			# print r.error
			r.error = q.error
			# print 'after'
			# print r.error

		# else:
		# 	print 'NO entered if self.num_input_signals % self.lmbda == 0'
		# 	print 'num_input sigs = %d, lmda = %d' % (self.num_input_signals, self.lmbda)

		# Decrease all error variables by multiplying them with a constant d.
		# print '\ndecreasing all errors by *= d'
		# print 'before'
		# for u in self.vertices:
		# 	print u.error
		for u in self.vertices:
			u.error *= self.d
		# print 'after'
		# for u in self.vertices:
		# 	print u.error

		# sys.exit()

	def find_nearest_2_points(self, new_data):

		s1 = self.vertices[0]
		d1 = dist(s1, new_data)
		for u in self.vertices:
			d = dist(u, new_data)
			if d < d1:
				s1 = u
				d1 = d

		s2 = self.vertices[0]
		if s2 == s1: s2 = self.vertices[1]
		d2 = dist(s2, new_data)
		for u in self.vertices:
			if u != s1:
				d = dist(u, new_data)
				if d < d2:
					s2 = u
					d2 = d

		return s1, s2


	def add_unit(self, n):
		# n is a tuple: (x, y) or of type Unit
		if isinstance(n, Unit):
			self.vertices.append(n)
		else:
			self.vertices.append(Unit(n))
	def remove_unit(self, u):
		# v is of type Unit
		if u in self.vertices:
			self.vertices.remove(u)
			return u
		return None
	def get_unit(self, v):
		# v is a tuple: (x, y)
		for u0 in self.vertices:
			if u0.pos == v:
				return u0
		return None

	def add_gas_edge(self, u1, u2):
		# u1 and u2 are of type Unit
		self.edges.append(GasEdge(u1, u2))
	def remove_gas_edge(self, e):

		return self.remove_edge(e)
	def remove_gas_edge2(self, u1, u2):

		return self.remove_edge2(u1, u2)
	def get_gas_edge(self, u1, u2):
		# u1 and u2 are of type Unit
		for e in self.edges:
			if e.vertices[0] == u1 and e.vertices[1] == u2 or \
				e.vertices[0] == u2 and e.vertices[1] == u1:
				return e
		return None
