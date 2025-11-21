import copy
from enum import Enum
from graphviz import Digraph
import random
from warnings import warn

class DAG(Digraph):
	def __init__(self, nodes, edges):
		super().__init__()
		self.nodes = nodes
		self.edges = edges
		self.conditional_set = set()

		# internal vars with a bit more functionality. Need to bookkeep this properly
		self._nodes: dict[str, Node] = {}

		# routines
		self.add_nodes(nodes)
		self.add_edges(edges)

	def add_nodes(self, nodes):
		for node in nodes:
			self.node(node, node)  # , color="red")
			self._nodes[node] = Node(node)

	def add_edges(self, edges):
		for head, tail in edges:
			if head in self.nodes and tail in self.nodes:
				self.edge(head, tail)
				self._nodes[head].add_child(tail)
				self._nodes[tail].add_parent(head)
			else:
				warn(f"Node {head} or {tail} not in node list, edge not added")

	def set_conditionals(self, nodes: list['Node']):
		self.conditional_set = set(nodes)

	def find_all_paths(
			self,
			start: 'Node'|str,
			end: 'Node'|str,
			current_path=None,
			all_paths=None
	):

		if all_paths is None:
			all_paths = []

		if current_path is None:
			current_path = []

		start = self.node_by_name(start)
		end = self.node_by_name(end)

		current_path = current_path + [start]

		if start == end:
			all_paths.append(Path(current_path, self))
			return all_paths

		for relative in start.get_relatives():
			if isinstance(relative, str):
				relative = self._nodes.get(relative)

			if relative not in current_path:
				self.find_all_paths(relative, end, current_path, all_paths)

		return all_paths

	def node_by_name(self, name):
		if isinstance(name, str):
			return self._nodes[name]
		else:
			return name

	def link_type(self, n1, n2):
		if not {n1}.issubset(n2.get_relatives()):
			raise ValueError(f"Nodes {n1}, {n2} are not neighbours")
		if n1 in n2.children:
			return "1"
		else:
			return "0"

	def node_type(self, n1, n2, n3):
		n1, n2, n3 = self.node_by_name(n1), self.node_by_name(n2), self.node_by_name(n3)
		# assert that these are existing nodes
		# assert that these are actually neighbours
		if not {n1, n3}.issubset(n2.get_relatives()):
			raise ValueError(f"Nodes {n1}, {n2}, {n3} are not neighbours")

		# get connection between nodes. 0 is right, 1 is left
		# 01: collider; 10: fork; 11, 00: mediator
		if n1 in n2.children:
			link = "1"
		else:
			link = "0"

		if n3 in n2.children:
			link += "0"
		else:
			link += "1"

		if link == "01":
			return Link.COLLIDER
		elif link == "10":
			return Link.FORK
		else:
			return Link.MEDIATOR

	def get_descendants(self, node):
		descendants = []
		node = self.node_by_name(node)

		if not node.children:
			return []

		for child in node.children:
			descendants.append(child)
			descendants.extend(self.get_descendants(child))

		return set(descendants)

	def conditional_paths(self, node1, node2, condition=None):
		if condition is None:
			condition = set(self.conditional_set)
		else:
			if isinstance(condition, str):
				condition = set([condition])
			else:
				condition = set(condition)

		paths = self.find_all_paths(node1, node2)
		open_paths = []
		blocked_paths = []

		for path in paths:
			blocked = False
			for i, node in enumerate(path.path[1:-1]):
				j = i + 1 # legibility
				link_type = self.node_type(path.path[j - 1], node, path.path[j + 1])

				if link_type == Link.MEDIATOR or link_type == Link.FORK:
					if node in condition:
						blocked = True
						temp_path = copy.deepcopy(path)  # unique copies per path
						temp_path.set_blocked_node(j)
						blocked_paths.append(temp_path)
						break
				elif link_type == Link.COLLIDER:
					nodes = set([node]).union(self.get_descendants(node))
					if len(condition.intersection(nodes)) == 0:
						blocked = True
						temp_path = copy.deepcopy(path)  #
						temp_path.set_blocked_node(j)
						blocked_paths.append(temp_path)
						break

			if not blocked:
				open_paths.append(path)
				#return True, (open_paths, blocked_paths)

		# none of the paths turned out to be unblocked
		return open_paths, blocked_paths

	def conditionally_independent(self, node1, node2, condition=None, verbose=False):
		open_paths, blocked_paths = self.conditional_paths(node1, node2, condition)
		if len(open_paths) == 0:
			indep = True
		else:
			indep = False

		if verbose:
			print(f"{node1} and {node2} are{"" if indep else " not"} independent conditioned on {condition}.")
			if not indep:
				print(f"{len(open_paths)} open paths. "
				      f"Example: {open_paths[random.randint(0, len(open_paths)-1)]}")
		return indep, (open_paths, blocked_paths)


class Node:
	def __init__(self, name):
		self.name = name
		self.children = []
		self.parents = []
		self.blocked = False

	def add_child(self, child: 'Node'):
		self.children.append(child)

	def add_parent(self, child: 'Node'):
		self.parents.append(child)

	def get_relatives(self):
		return self.children + self.parents

	# for set comparison
	def __eq__(self, other):
		if isinstance(other, Node):
			return self.name == other.name
		elif isinstance(other, str):
			return self.name == other
		else:
			return False

	def __hash__(self):
		return hash(self.name)

	def __str__(self):
		return self.name

class Path:
	def __init__(self, path, parent_graph: DAG):
		self.path = path
		self.parent_graph = parent_graph
		self.edges = []
		self.blocked_node_index = -1

		# routines
		self.assign_edges()

	def assign_edges(self):
		for i in range(len(self.path)-1):
			node1 = self.path[i]
			node2 = self.path[i+1]

			self.edges.append(self.parent_graph.link_type(node1, node2))

	def set_blocked_node(self, index):
		self.blocked_node_index = index
		self.path[index].blocked = True

	def __str__(self):
		nodes = [f"{'\033[91m\033[4m'}{n.name}{'\033[0m'}" if n.blocked else f"{n.name}"
		         for n in self.path]
		edges = ['->' if e=='0' else '<-' for e in self.edges] + [""]
		return "".join(str(n)+str(e) for n, e in zip(nodes, edges))

class Link(Enum):
	COLLIDER=1
	FORK=2
	MEDIATOR=3

	def __str__(self):
		return self.name