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
	distribution, topology, R,
	mu_x, std_x, mu_y, std_y):

	x, y = -1.0, -1.0
	if distribution == 'uniform':
		while not point_in_topology(x, y, topology):
		    x = np.random.uniform(R[0], R[2], 1)[0]
		    y = np.random.uniform(R[1], R[3], 1)[0]
	elif distribution == 'normal':
		while not point_in_topology(x, y, topology):
		    x = np.random.normal(mu_x, std_x, 1)[0]
		    y = np.random.normal(mu_x, std_x, 1)[0]
	else:
		print 'invalid distribution. must be: \'uniform\' or \'normal\''
		sys.exit() 

	return (x, y)
def point_in_topology(x, y, topology):
	# topology = [(x_min, y_min, x_max, y_max), ... ]
	return any(map(lambda region:
			region[0] <= x and x <= region[2] and
			region[1] <= y and y <= region[3],
		topology))
def normpdf(x, mean, sd):
    # curtesy of: https://stackoverflow.com/questions/12412895/calculate-probability-in-normal-distribution-given-mean-std-in-python
    # future optimization: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html
    var = float(sd)**2
    pi = 3.1415926
    denom = (2*pi*var)**.5
    num = math.exp(-(float(x)-float(mean))**2/(2*var))
    return num/denom


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
		a = new_data_point = random2dPoint(
            'normal', model.topology, model.R,
            model.mu_x, model.std_x, model.mu_y, model.std_y)
		b = new_data_point = random2dPoint(
            'normal', model.topology, model.R,
            model.mu_x, model.std_x, model.mu_y, model.std_y)

		self.add_unit(a)
		self.add_unit(b)

		# # hyper parameters used in paper
		# self.Eb = 0.2
		# self.En = 0.006
		# self.alpha = 0.5
		# self.a_max = 50 # max age an edge can have
		# self.num_input_signals = 0
		# self.lmbda = 100 # number of units * lmbda =(approx.) number of data points
		# self.d = 0.995

		self.Eb = 0.2
		self.En = 0.006
		self.alpha = 0.5
		self.a_max = 1 # max age an edge can have
		self.num_input_signals = 0
		self.lmbda = 5 # number of units * lmbda =(approx.) number of data points
		self.d = 0.995

	def update(self, new_data):

		# find nearst(s1) and 2nd nearest(s2) units (vertices)
		# in neural gas graph to new_data point
		s1, s2 = self.find_nearest_2_points(new_data)

		# increment age of all edges eminating from s1
		for e in self.edges:
			if e.has_vertex(s1):
				e.increment_age()

		# Add the squared distance between the input signal and the nearest unit in
		# input space to a local counter variable (pretty sure they're talking about
		# the error of s1 here)
		s1.error += dist(s1, new_data)**2

		# Move s1 and its direct topological neighbors towards new_data by fractions
		# Eb and En, respectively, of the total distance
		for i, u in enumerate(self.vertices):
			if u == s1:
				self.vertices[i].move(self.Eb*(new_data[0]-u.pos[0]), self.Eb*(new_data[1]-u.pos[1]))
			elif self.neighbors(u, s1):
				self.vertices[i].move(self.Eb*(new_data[0]-u.pos[0]), self.Eb*(new_data[1]-u.pos[1]))

		# If s1 and s2 are connected by an edge, set the age of this edge to zero. If
		# such an edge does not exist, create it.
		edge_s1_s2 = self.get_edge(s1, s2)
		if edge_s1_s2 != None:
			edge_s1_s2.age = 0
		else:
			self.add_gas_edge(s1, s2)

		# Remove edges with an age larger than a_max. If this results in points having
		# no emanating edges, remove them as well.
		for i, e in enumerate(self.edges):
			if e.age > self.a_max:
				eu1, eu2 = e.vertices
				self.remove_gas_edge(e)
				if self.isolated(eu1):
					self.remove_vertex(eu1)
				if self.isolated(eu2):
					self.remove_vertex(eu2)

		# If the number of input signals generated so far is an integer multiple of a
		# parameter lmbda, insert a new unit as follows:
		self.num_input_signals += 1
		if self.num_input_signals % self.lmbda == 0:

			# 	Determine the unit q with the maximum accumulated error.
			q = self.vertices[0]
			for u in self.vertices:
				if u.error > q.error:
					q = u

 			# Insert a new unit r halfway between q and its neighbor f with the
			# largest error variable: Wr = 0.5 (wq + wf)
			f = self.vertices[0]
			if f == q: f = self.vertices[1]
			for u in self.vertices:
				if self.get_gas_edge(u, q) != None:
					if u.error > f.error:
						f = u
			
			r = Unit((0.5*(q.pos[0]+f.pos[0]),0.5*(q.pos[1]+f.pos[1])))
			self.add_unit(r)

			# Insert edges connecting the new unit r with units q and f, and remove
			# the original edge between q and f.
			self.add_gas_edge(q, r)
			self.add_gas_edge(f, r)
			self.remove_gas_edge2(q, f)

			# Decrease the error variables of q and f by multiplying them with a
			# constant self.alpha Initialize the error variable of r with the new value of the
			# error variable of q.
			q.error *= self.alpha
			f.error *= self.alpha
			r.error = q.error

		# Decrease all error variables by multiplying them with a constant d.
		for u in self.vertices:
			u.error *= self.d

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
