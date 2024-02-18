import sys
from .Lexer import Lexer
from .Tree import Tree

# function used for debugging purposes only
def print_tree(tree):
	queue = [tree]
	while len(queue) > 0:
		node = queue.pop(0)
		queue.extend(node.children)
		print(str(node.value) + ": " + ' '.join(map(lambda x: str(x.value), node.children)), file=sys.stderr)

# extract a list of numbers from a string
def extract_numbers(string):
	return map(int, list(filter(lambda x: x.isdigit(), string.split())))

# replace the variables from a lambda expression with the given value
def beta_reduction(node, var, value):
	if node.type == 'var' and node.value == var:
		node.value = value

	for child in node.children:
		beta_reduction(child, var, value)

# parse the syntax tree
def parse_tree(tree):
	if tree.type == 'number' or tree.type == 'var':
		return tree.value

	if tree.type == 'open':
		result = '('

		for child in tree.children:
			result += ' ' + parse_tree(child)

		result += ' )' if len(tree.children) > 0 else ')'
		return result
	
	if tree.type == 'concat':
		result = ''

		for child in tree.children[0].children:
			string = parse_tree(child)
			if child.type == 'number' or child.type == 'var':
				result += ' ' + string
			elif child.type == 'open' and len(child.children) > 0:
				result += ' ' + string[2:len(string) - 2]

		return '(' + result + ' )'

	if tree.type == 'sum':
		return str(sum(extract_numbers(parse_tree(tree.children[0]))))
	
	if tree.type == 'lambda':
		# perform beta reductions on lambda body first
		parse_tree(tree.children[1])

		beta_reduction(tree.children[1], tree.children[0].value, parse_tree(tree.children[2]))

		return parse_tree(tree.children[1])

# count the number of lambda functions with an id of type: <value><number>
def count_ids(ids, value):
	return len(list(filter(lambda id: id[0:len(value)] == value and id[len(value):].isnumeric(), ids)))

def needs_alpha_substitution(node):
	if node.type == 'lambda' and len(node.children) == 3 and node.children[2].type == 'lambda':
		return True

	for child in node.children:
		if needs_alpha_substitution(child):
			return True

	return False

# substitute all expressions of type:
#      λ
#   /  |  \
#  id expr λ
def alpha_substitution(root, tree):
	if tree.type == 'lambda' and len(tree.children) == 3 and tree.children[2].type == 'lambda':
		# rename id's and variables accordingly
		id = tree.children[0].value
		beta_tree = alpha_conversion(root, tree.children[2])

		tree.update(tree.children[1])

		# replace all id's with the beta-substituted lambda tree
		queue = [tree]
		while len(queue) > 0:
			node = queue.pop(0)
			queue.extend(node.children)

			if node.type == 'var' and node.value == id:
				node.update(Tree(beta_tree))

		return tree

	for child in tree.children:
		alpha_substitution(root, child)

	return tree

# when applying two lambda expressions with the same variable id, change the name of the one inside
# e.g.: ((λx.x) (λx.x)) becomes ((λx.x) (λx1.x1))
def alpha_conversion(root, tree):
	# create a set of ids of all lambda expressions in the root tree (except current tree)
	ids = set()
	queue = [root]
	while len(queue) > 0:
		node = queue.pop(0)
		if node != tree:
			queue.extend(node.children)
		if node.type == 'id':
			ids.add(node.value)

	# rename ids from current tree
	queue = [tree]
	while len(queue) > 0:
		node = queue.pop(0)
		queue.extend(node.children)

		if node.type == 'id':
			ids.add(node.value)
			node.value = node.value + str(count_ids(ids, node.value))

		elif node.type == 'var':
			node.value = node.value + str(count_ids(ids, node.value))

	return tree

# find the first incomplete lambda operation
def find_first_lambda(node):
	if node.type == 'lambda' and len(node.children) == 2:
		return node

	for child in node.children:
		result = find_first_lambda(child)
		if result != None:
			return result

	return None

# returns True if the syntax tree requires a lambda application, ie has a node of type:
#            (
#          /   \
#         λ		var
#        /\
#       id expr
def needs_lambda_application(node):
	if node.type == 'open' and len(node.children) == 2 and node.children[0].type == 'lambda':
		return True
	
	for child in node.children:
		if needs_lambda_application(child):
			return True
	
	return False

# update the syntax tree with the proper lambda application syntax:
#            (                              λ
#          /   \         becomes         /  |  \
#         λ		var	     ======>        id expr var
#        /\
#       id expr
def lambda_application(tree):
	if tree.type == 'open' and len(tree.children) == 2 and tree.children[0].type == 'lambda':
		# find first lambda missing a var
		queue = [tree.children[0]]
		while len(queue) > 0:
			node = queue.pop(0)
			queue.extend(node.children)

			if node.type == 'lambda' and len(node.children) == 2:
				tree.children[1].parent = node
				node.add(tree.children[1])
				tree.update(tree.children[0])
				return
	else:
		for child in tree.children:
			lambda_application(child)

# after adding the 'var' to a lambda expression (upon parsing ')'), performing the function application:
#            (                                 λ
#            |            becomes           /  |  \
#            λ            ======>          id expr var
#         /  |  \
#        id expr var
# do the same for concat, sum
def remove_parantheses(root, node):
	while node.type != 'open':
		node = node.parent
	
	if node.parent == None:
		return node.children[0]

	for i in range(len(node.parent.children)):
		if node.parent.children[i] == node:
			node.children[0].parent = node.parent
			node.parent.children[i] = node.children[0]

	return root

def main():
	if len(sys.argv) != 2:
		return
	
	# read the string from the input file, remove newlines and tabs
	file = open(sys.argv[1], "r")
	string = file.read().replace('\n', '').replace('\t', '')
	file.close()

	# define the lexer specification
	spec = [
		("number", r'(\ )*(0|([1-9][0-9]*)+)(\ )*'),
		("open", r'(\ )*\((\ )*'),
		("close", r'(\ )*\)(\ )*'),
		("sum", r'(\ )*\+(\ )*'),
		("concat", r'(\ )*\+\+(\ )*'),
		("lambda", r'(\ )*lambda(\ )*'),
		("id", r'(\ )*([a-z]|[A-Z])+(\ )*:(\ )*'),
		("var", r'(\ )*([a-z]|[A-Z])+(\ )*')
	]

	# use the lexer to split the string into lexemes
	lexer = Lexer(spec)
	lexemes = lexer.lex(string)

	# initialize the root
	tree = Tree(lexemes[0][0], lexemes[0][0], None)
	node = tree

	# build the syntax tree using the lexemes
	for lexeme in lexemes[1:]:
		if lexeme[0] in ['open', 'concat', 'sum', 'lambda']:
			if node.type == 'lambda' and len(node.children) > 1:
				node = find_first_lambda(tree)

			child = Tree(lexeme[0], lexeme[1].replace(' ', ''), node)
			node.add(child)
			node = child

		elif lexeme[0] == 'close':
			if node.type == 'lambda' or node.type == 'concat' or node.type == 'sum':
				tree = remove_parantheses(tree, node)

			if node.type != 'lambda':
				node = node.parent

		elif lexeme[0] == 'id' or lexeme[0] == 'var':
			node.add(Tree(lexeme[0], lexeme[1].replace(' ', '').replace(':', ''), node))

		elif lexeme[0] == 'number':
			if node.type == 'lambda' and len(node.children) > 1:
				node = find_first_lambda(tree)

			node.add(Tree(lexeme[0], lexeme[1].replace(' ', ''), node))

	while needs_alpha_substitution(tree) or needs_lambda_application(tree):
		alpha_substitution(tree, tree)

		lambda_application(tree)

	print(parse_tree(tree))

if __name__ == '__main__':
    main()
