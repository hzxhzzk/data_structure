#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

class Node:
    def __init__(self, key):
        self.left = None
        self.right = None
        self.val = key


"""
         A     val
        / \
       B   C    B is left children, C is right children.
"""


def printInorder(root):
    if root:
        printInorder(root.left)
        print(root.val, end=' ')
        printInorder(root.right)


def printPreorder(root):
    if root:
        print(root.val, end=' ')
        printPreorder(root.left)
        printPreorder(root.right)


def printPostorder(root):
    if root:
        printPostorder(root.left)
        printPostorder(root.right)
        print(root.val, end=' ')


if __name__ == "__main__":
    root = Node(1)
    root.left = Node(2)
    root.right = Node(3)
    root.left.left = Node(4)
    root.left.right = Node(5)

    print("In: ")
    printInorder(root)
    print("\nPre: ")
    printPreorder(root)
    print("\nPost: ")
    printPostorder(root)
