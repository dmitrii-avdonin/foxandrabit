from bst import BST, Node

class TaggedNode(Node):
    def __init__(self, value, tag):
        Node.__init__(self, value)
        self.tag = tag

class MyBST(BST):
    def __init__(self):
        BST.__init__(self)
        self.duplicatesCount = 0

    def insertList(self, list):
     for i in range(len(list)):
        self.insert(list[i], i)       

    def insert(self, value, tag=None):
        if self.root is None:
            self.root = TaggedNode(value, tag)
            return self.root

        return self.__insert(self.root, TaggedNode(value, tag))        

    def search(self, value):
        if self.root is None:
            return None

        return self.__search(self.root, value)

    def __search(self, node, value):
        if node is None:
            return None

        if value.tolist() == node.value.tolist():
            return node
        elif value.tolist() < node.value.tolist():
            return self.__search(node.left, value)
        else:
            return self.__search(node.right, value)

    def __insert(self, node, newNode):
        if newNode.value.tolist() == node.value.tolist():
            print('duplicates found: ' + str(newNode.tag) + "  " + str(node.tag))
            self.duplicatesCount += 1
            return None
        elif newNode.value.tolist() < node.value.tolist():
            if node.left is None:
                node.left = newNode
                return node.left
            else:
                return self.__insert(node.left, newNode)
        else:
            if node.right is None:
                node.right = newNode
                return node.right
            else:
                return self.__insert(node.right, newNode)