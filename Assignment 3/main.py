import digraph

if __name__ == '__main__':
	drivers = [f"A{i}" for i in range(1, 4)]
	context = [f"C{i}" for i in range(1, 4)]
	mediators = [f"M{i}" for i in range(1, 3)]
	intermediates = [f"B{i}" for i in range(1, 4)]
	outcome =["Y"]

	nodes = drivers + context + mediators + intermediates + outcome
	edges = [
		["C1", "A1"],
		["C1", "B2"],
		["C1", "Y"],
		["C2", "A2"],
		["C2", "B1"],
		["C3", "A3"],
		["C3", "M1"],
		["A1", "B1"],
		["A1", "B3"],
		["A2", "B1"],
		["A2", "B2"],
		["A3", "B2"],
		["B1", "M2"],
		["M2", "B2"],
		["M1", "B3"],
		["M1", "Y"],
		["B1", "Y"],
		["B2", "Y"],
		["B3", "Y"],
	]

	graph = digraph.DAG(nodes, edges)
	all_paths = graph.find_all_paths("A1", "A2")
	paths = [[n.name for n in p.path] for p in all_paths]
	print(f"{"Y"} is a {graph.node_type("B1", "Y", "C1")}")
	print(graph.get_descendants("C1"))
	indep, paths = graph.conditionally_independent("A2", "A3", verbose=True)
	indep, paths2 = graph.conditionally_independent("A2", "A3", "B2", verbose=True)
	indep, paths2 = graph.conditionally_independent("A2", "A3", ["B2", "M2"], verbose=True)

	#print(graph.source)
	#graph.render(view=True)