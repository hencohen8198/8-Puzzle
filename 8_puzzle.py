import random
import itertools
import collections
import time
import tkinter as tk
from tkinter import font

labels = []
node_path = []
heuristic = "SOMD"


class Node:

    def __init__(self, puzzle, parent=None, action=None):

        global heuristic

        self.puzzle = puzzle
        self.parent = parent
        self.action = action
        self.heuristics = heuristic
        if self.parent is not None:
            self.g = parent.g + 1
        else:
            self.g = 0

    @property
    def state(self):
        """
        Return a hashable representation of self
        """
        return str(self)

    @property 
    def path(self):
        """
        Reconstruct a path from to the root 'parent'
        """
        node, p = self, []
        while node:
            p.append(node)
            node = node.parent
        yield from reversed(p)

    @property
    def solved(self):
        """ Wrapper to check if 'puzzle' is solved """
        return self.puzzle.solved

    @property
    def actions(self):
        """ Wrapper for 'actions' accessible at current state """
        return self.puzzle.actions

    @property
    def h(self):
        """"h"""
        if self.heuristics == "SOMD":
            return self.puzzle.manhattan
        elif self.heuristics == "NOMT":
            return self.puzzle.NOMT
        else:
            raise TypeError(f"heuristics {self.heuristics} is not supported")

    @property
    def f(self):
        """"f"""
        return self.h + self.g

    def __str__(self):
        return str(self.puzzle)


class Solver:

    def __init__(self, start):
        self.start = start

    def solve(self):
        """
        Perform breadth first search and return a path
        to the solution, if it exists
        """
        queue = collections.deque([Node(self.start)])
        seen = set()
        seen.add(queue[0].state)
        steps = 0
        while queue:
            steps += 1
            queue = collections.deque(sorted(list(queue), key=lambda node: node.f))
            node = queue.popleft()
            if node.solved:
                return node.path, steps

            for move, action in node.actions:
                child = Node(move(), node, action)

                if child.state not in seen:
                    queue.appendleft(child)
                    seen.add(child.state)


class Puzzle:

    def __init__(self, board):
        self.width = len(board[0])
        self.board = board

    @property
    def solved(self):
        """
        The puzzle is solved if the flattened board's numbers are in
        increasing order from left to right and the '0' tile is in the
        last position on the board
        """
        n = self.width * self.width
        return str(self) == ''.join(map(str, range(1, n))) + '0'

    @property 
    def actions(self):
        """
        Return a list of 'move', 'action' pairs. 'move' can be called
        to return a new puzzle that results in sliding the '0' tile in
        the direction of 'action'.
        """
        def create_move(at, to):
            return lambda: self._move(at, to)

        moves = []
        for i, j in itertools.product(range(self.width),
                                      range(self.width)):
            direcs = {'R': (i, j-1),
                      'L': (i, j+1),
                      'D': (i-1, j),
                      'U': (i+1, j)}

            for action, (r, c) in direcs.items():
                if 0 <= r < self.width and 0 <= c < self.width and self.board[r][c] == 0:
                    move = create_move((i, j), (r, c)), action
                    moves.append(move)
        return moves

    @property
    def manhattan(self):
        distance = 0
        for i in range(3):
            for j in range(3):
                if self.board[i][j] != 0:
                    x, y = divmod(self.board[i][j]-1, 3)
                    distance += abs(x - i) + abs(y - j)
        return distance

    @property
    def NOMT(self):
        distance = 0
        for i in range(3):
            for j in range(3):
                if self.board[i][j] != 0:
                    if self.board[i][j] != i*3 + j + 1:
                        distance += 1
        return distance

    def shuffle(self):
        """
        Return a new puzzle that has been shuffled with 20 random moves
        """
        puzzle = self
        for _ in range(20):
            puzzle = random.choice(puzzle.actions)[0]()
        return puzzle

    def copy(self):
        """
        Return a new puzzle with the same board as 'self'
        """
        board = []
        for r in self.board:
            board.append([x for x in r])
        return Puzzle(board)

    def _move(self, at, to):
        """
        Return a new puzzle where 'at' and 'to' tiles have been swapped.
        NOTE: all moves should be 'actions' that have been executed
        """
        copy = self.copy()
        i, j = at
        r, c = to
        copy.board[i][j], copy.board[r][c] = copy.board[r][c], copy.board[i][j]
        return copy

    def __str__(self):
        return ''.join(map(str, self))

    def __iter__(self):
        for r in self.board:
            yield from r


def draw_board(e):

    global node_path
    global labels

    try:
        node = node_path.pop(0)
        for i, state in enumerate(str(node)):
            if state == '0':
                labels[i]['text'] = ""
            else:
                labels[i]['text'] = state
    except:
        return


def set_to_nomt():
    global heuristic
    heuristic = "NOMT"
    restart_game()


def set_to_somd():
    global heuristic
    heuristic = "SOMD"
    restart_game()


def restart_game():
    # example of use
    global labels
    global node_path

    board = [[1, 2, 3], [4, 5, 0], [6, 7, 8]]
    puzzle = Puzzle(board)
    puzzle = puzzle.shuffle()

    s = Solver(puzzle)
    res_s = s.solve()
    node_path = list(res_s[0])
    node_path.pop(0)
    draw_board(None)
    print(res_s[1])


if __name__ == "__main__":

    root = tk.Tk()
    root.resizable(False, False)
    root.bind("<space>", draw_board)

    menu = tk.Menu(root)
    root.config(menu=menu)

    conf_menu = tk.Menu(menu)
    conf_menu.add_command(label="Number of mismatched tiles", command=set_to_nomt)
    conf_menu.add_command(label="Sum of Manhattan distance", command=set_to_somd)
    menu.add_cascade(label="Configure", menu=conf_menu)

    game_menu = tk.Menu(menu)
    game_menu.add_command(label="Restart", command=restart_game)
    menu.add_cascade(label="Game", menu=game_menu)

    myFont = font.Font(size=15)

    for row in range(3):
        for col in range(3):

            b = tk.Button(root, text=f"{row * 3 + col}", height=1, width=2, bg='white', padx=15, pady=15)
            b["state"] = "disabled"
            b["fg"] = "black"
            b['font'] = myFont
            b["text"] = ""
            b.grid(row=row, column=col)
            labels.append(b)

    tk.mainloop()
