class Tree:
	def __init__(self, *args):
		if len(args) == 3:
			# initialise tree with given arguments
			self.type = args[0]
			self.value = args[1]
			self.parent = args[2]
			self.children = []

		elif len(args) == 1:
			# copy tree
			tree = args[0]
			root = Tree(tree.type, tree.value, tree.parent)

			# copy children
			original_queue = [tree]
			copy_queue = [root]

			while len(original_queue) > 0:
				original_node = original_queue.pop(0)
				copy_node = copy_queue.pop(0)

				for original_child in original_node.children:
					copy_child = Tree(original_child.type, original_child.value, copy_node)
					copy_node.add(copy_child)

					original_queue.append(original_child)
					copy_queue.append(copy_child)

			self.type = root.type
			self.value = root.value
			self.parent = root.parent
			self.children = root.children

	def add(self, node):
		self.children.append(node)
	
	def update(self, node):
		self.type = node.type
		self.value = node.value
		self.children = node.children
