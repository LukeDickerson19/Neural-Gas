import random
import time
import math
import os, sys
import numpy as np

class NeuralGas():

	def __init__(self, model):
		# R = region of space points can fall in

		self.model = model
		self.graph = {}

		# add points a and b
		a = self.model.random2dPoint()
		b = self.model.random2dPoint()
		self.graph[a] = [(b[0], b[1], 0)] # (x, y, edge_age)
		self.graph[b] = [(b[0], b[1], 0)]

		self.Eb = 0.2
		self.En = 0.006
		self.alpha = 0.5
		self.a_max = 50 # max age an edge can have
		self.d = 0.995

	def update(self, new_data):
		# new_data = (x, y)

		# find nearst(s1) and 2nd nearest(s2) units (verteces)
		# in neural gas graph to new_data point
		s1, s2 = find_nearest_2_points(new_data)

		# increment age of all edges eminating from s1
		for i in range(len(self.graph[s1])):
			self.graph[s1][i][2] += 1

		# Add the squared distance between the input signal and the nearest unit in
		# input space to a local counter variable
		d1 = self.dist(new_data, s1)**2
		counter += d1

		# Move s1 and its direct topological neighbors1 towards new_data by fractions
		# Eb and En, respectively, of the total distance
		dx, dy = self.Eb * (new_data[0] - s1[0]), self.Eb * (new_data[1] - s1[1])
		for v, e in self.graph.iteritems():
			if v == s1:
				self.graph[v][0] += dx
				self.graph[v][1] += dy
			else:
				for i, ee in enumerate(self.graph[v]):
					if (ee[0], ee[1]) == s1:
						self.graph[v][i] = (ee[0] + dx, ee[1] + dy, ee[2])

		# update s1 when finished
		s1 = (s1[0] + dx, s1[0] + dy)

		for neighbor in self.graph[s1]:
			dx, dy = self.En * (new_data[0] - neighbor[0]), self.En * (new_data[1] - neighbor[1])
			for v, e in self.graph.iteritems():
				if v == neighbor:
					new_x = self.graph[v][0] + dx
					new_y = self.graph[v][1] + dy
					self.graph[v][0] = new_x
					self.graph[v][1] = new_y
					if v == s2:
						s2 = (new_x, new_y)
				else:
					for i, ee in enumerate(self.graph[v]):
						if (ee[0], ee[1]) == neighbor:
							self.graph[v][i] = (ee[0] + dx, ee[1] + dy, ee[2])


		# If s1 and s2 are connected by an edge, set the age of this edge to zero. If
		# such an edge does not exist, create it.
		edge_exists = False
		for i, e in enumerate(self.graph[s1]):
			if (e[0], e[1]) == s2:
				edge_exists = True
				self.graph[s1][i][2] = 0
		for i, e in enumerate(self.graph[s2]):
			if (e[0], e[1]) == s1:
				edge_exists = True
				self.graph[s2][i][2] = 0
		if not edge_exists:
			self.graph[s1].append((s2[0], s2[1], 0))
			self.graph[s2].append((s1[0], s1[1], 0))

		
		# Remove edges with an age larger than a_max If this results in points having
		# no emanating edges, remove them as well.
		


	def find_nearest_2_points(self, new_data):

		s1 = self.graph.keys()[0]
		d1 = self.dist(s1, new_data)
		for unit, neighbors in self.graph.iteritems():
			d = self.dist(unit, new_data)
			if d < d1:
				s1 = unit
				d0 = d1

		s2 = self.graph.keys()[0]
		if s2 == s1: s2 = self.graph.keys()[1]
		d2 = self.dist(s2, new_data)
		for unit, neighbors in self.graph.iteritems():
			if unit != s1:
				d = self.dist(unit, new_data)
				if d < d2:
					s2 = unit
					d = d0

		return s1, s2

	def dist(self, a, b):
		# a = (ax, ay)
		# a = (bx, by)
		return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)



