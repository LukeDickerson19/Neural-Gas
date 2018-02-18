import random
import time
import math
import os, sys
import numpy as np




def dist(a, b):
	# a is of type Unit or Vertex
	# b is a tuple: (x, y)
	return math.sqrt((a.pos[0] - b[0])**2 + (a.pos[1] - b[1])**2)



class NeuralGas(Graph):

	def __init__(self, model):
		super(self)

		self.model = model
		self.graph = {}

		# add points a and b
		a = self.model.random2dPoint()
		b = self.model.random2dPoint()
		self.add_unit(a)
		self.add_unit(b)

		self.Eb = 0.2
		self.En = 0.006
		self.alpha = 0.5
		self.a_max = 50 # max age an edge can have
		self.lmbda = 100
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
		# input space to a local counter variable
		counter += self.dist(s1, new_data)**2

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
			self.add_edge(s1, s2)
		
		# Remove edges with an age larger than a_max. If this results in points having
		# no emanating edges, remove them as well.
		for i, e in enumerate(self.edges):
			if e.age > self.a_max:
				eu1, eu2 = e.vertices
				self.remove_edge(e)
				if self.isolated(eu1):
					self.remove_vertex(eu1)
				if self.isolated(eu2):
					self.remove_vertex(eu2)

		# If the number of input signals generated so far is an integer multiple of a
		# parameter lambda, insert a new unit as follows:

		# 	Determine the unit q with the maximum accumulated error.
		q = max(map(lambda u: u.get_error(), self.vertices))

		# WHATS NEXT??? see paper ... IS THE WAY Q IS FOUND CORRECT?

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

	def add_unit(self, v):
		# v is a tuple: (x, y)
		self.vertices.append(Unit(v))
	def remove_unit(self, u):
		# v is of type Unit
		if u in self.vertices:
			self.vertices.remove(u)
			return u
		return None
	def get_unit(v):
		# v is a tuple: (x, y)
		for u0 in self.vertices:
			if u0.pos == v:
				return u0
		return None

	def add_gas_edge(self, u1, u2):
		# u1 and u2 are of type Unit
		self.edges.add(GasEdge(u1, u2))
	def remove_gas_edge(self, u1, u2):
		# u1 and u2 are of type Unit
		e = self.get_gas_edge(u1, u2)
		if e != None:
			self.edges.remove(e)
			return e
		return None
	def get_gas_edge(u1, u2):
		# u1 and u2 are of type Unit
		for e in self.edges:
			if e.vertices[0] == u1 and e.vertices[1] == u2 or \
				e.vertices[0] == u2 and e.vertices[1] == u1:
				return e
		return None


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
	def get_vertex(v):
		# v is a tuple: (x, y)
		for v0 in self.vertices:
			if v0.pos == v:
				return v0
		return None

	def add_edge(self, v1, v2):
		# v1 and v2 are of type Vertex
		self.edges.add(Edge(v1, v2))
	def remove_edge(self, e):
		if e in self.edges:
			self.edges.remove(e):
			return e
		return None
	def remove_edge(self, v1, v2):
		# v1 and v2 are of type Vertex
		e = self.get_edge(v1, v2)
		return remove_edge(e)
	def get_edge(v1, v2):
		# v1 and v2 are of type Vertex
		for e in self.edges:
			if e.vertices[0] == v1 and e.vertices[1] == v2 or \
				e.vertices[0] == v2 and e.vertices[1] == v1:
				return e
		return None

	def neighbors(v1, v2):
		# v1 and v2 are of type Vertex
		# returns true if v1 and v2 are neighbors
		return any(map(lambda e: e.has_vertex(v1) and e.has_vertex(v2), self.edges))
	def isolated(v1):
		# v1 is of type Vertex
		# returns true if v1 has not edges to any other vertices
		return not any(map(lambda e: e.has_vertex(v1), self.edges))

class Vertex():

	def __init__(self, pos):
		# pos is a tuple: (x, y)
		self.pos = pos

	def move(self, dx, dy):

		self.pos = (self.pos[0] + dx, self.pos[1] + dy)


class Unit(Vertex):

	def __init__(self, x, y):
		super(x, y)
		self.original_pos = (x, y)

	def get_error(self):
		
		return dist(self.original_pos, self.pos)


class Edge():

	def __init__(self, v1, v2):
		# v1 and v2 are of type Vertex
		self.vertices = (v1, v2)

	def has_vertex(v):

		return self.vertices[0] == v or self.vertices[1] == v
		
class GasEdge(Edge):

	def __init__(self, u1, u2):
		# u1 and u2 are of type Unit
		super(u1, u2)
		self.age = 0

	def increment_age(self):

		self.age += 1

