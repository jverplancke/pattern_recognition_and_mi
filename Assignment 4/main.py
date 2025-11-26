import digraph

def test_hypotheses(graph, hypothesis_list):
	for nodes1, nodes2, conditionals in hypothesis_list:
		conditionals = set(conditionals)

		if conditionals.issubset(set(nodes)):
			overall_independence = True
			for node1 in nodes1:
				for node2 in nodes2:
					if node1 == node2:
						continue
					indep, paths = graph.conditionally_independent(node1, node2, conditionals) #, verbose=True)
					if not indep:
						overall_independence = False
			print(f"{nodes1} and {nodes2} are{"" if overall_independence else " not"} independent conditioned on {conditionals}.")
		else:
			print("Some conditionals are not part of the graph.")

	return indep, paths

if __name__ == '__main__':
	drivers = [f"A{i}" for i in range(1, 4)]
	context = [f"C{i}" for i in range(1, 4)]
	mediators = [f"M{i}" for i in range(1, 3)]
	intermediates = [f"B{i}" for i in range(1, 4)]
	outcome =["Y"]
	#outcome = []

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

	conditionals = set([])

	test = [
		[["A1"], ["A2"], []],
		[["A1"], ["A2"], ["B1"]],
		[["A2"], ["A3"], []],
		[["A2"], ["A3"], ["B2"]],
		[["A2"], ["A3"], ["B2", "M2"]],
		[["A1"], ["M1"], []],
		[["A1"], ["M1"], ["B3"]],
		[["B1", "B2", "B3", "M1", "C1"], ["B1", "B2", "B3", "M1", "C1"], []],
		[["B1", "B2", "B3", "M1", "C1"], ["B1", "B2", "B3", "M1", "C1"], ["Y"]],
		[["B1"], ["Y"], []],
		[["B1"], ["Y"], ["M2", "B2"]],
		[["M2"], ["Y"], []],
		[["M2"], ["Y"], ["B2"]],
		[["C3"], ["Y"], []],
		[["C3"], ["Y"], ["M1"]],
	]

	graph = digraph.DAG(nodes, edges)
	indep, (open_paths, closed_paths) = test_hypotheses(graph, test)

	#graph.view()
