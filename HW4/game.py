from dataclasses import dataclass
from math import inf
from typing import Dict, List, Optional, Tuple

WHITE, BLACK = "W", "B"
FILES = "abc"
Move = Tuple[Tuple[int, int], Tuple[int, int]]


@dataclass(frozen=True)
class HexapawnState:
    to_move: str
    board: Tuple[Tuple[Tuple[int, int], str], ...]

    def pieces(self) -> Dict[Tuple[int, int], str]:
        return dict(self.board)


class Hexapawn:
    def __init__(self) -> None:
        board = {(file, 0): WHITE for file in range(3)}
        board.update({(file, 2): BLACK for file in range(3)})
        self.initial = HexapawnState(WHITE, tuple(sorted(board.items())))

    @staticmethod
    def opponent(player: str) -> str:
        return BLACK if player == WHITE else WHITE

    def actions(self, state: HexapawnState) -> List[Move]:
        board = state.pieces()
        direction = 1 if state.to_move == WHITE else -1
        moves: List[Move] = []
        for (file, rank), piece in sorted(board.items()):
            if piece != state.to_move:
                continue
            forward = (file, rank + direction)
            if 0 <= forward[1] < 3 and forward not in board:
                moves.append(((file, rank), forward))
            for file_delta in (-1, 1):
                capture = (file + file_delta, rank + direction)
                if (0 <= capture[0] < 3 and 0 <= capture[1] < 3
                        and board.get(capture) == self.opponent(piece)):
                    moves.append(((file, rank), capture))
        return moves

    def result(self, state: HexapawnState, move: Move) -> HexapawnState:
        if move not in self.actions(state):
            raise ValueError("Illegal move")
        board = state.pieces()
        origin, destination = move
        piece = board.pop(origin)
        board[destination] = piece
        return HexapawnState(self.opponent(state.to_move), tuple(sorted(board.items())))

    def winner(self, state: HexapawnState) -> Optional[str]:
        board = state.pieces()
        if any(piece == WHITE and rank == 2 for (_, rank), piece in board.items()):
            return WHITE
        if any(piece == BLACK and rank == 0 for (_, rank), piece in board.items()):
            return BLACK
        if not self.actions(state):
            return self.opponent(state.to_move)
        return None

    def terminal_test(self, state: HexapawnState) -> bool:
        return self.winner(state) is not None

    def utility(self, state: HexapawnState, player: str) -> int:
        winner = self.winner(state)
        if winner is None:
            return 0
        return 1 if winner == player else -1

    def display(self, state: HexapawnState) -> None:
        board = state.pieces()
        print("  a b c")
        for rank in range(3, 0, -1):
            print(f"{rank} " + " ".join(board.get((file, rank - 1), ".")
                                           for file in range(3)))


def alpha_beta_search(state: HexapawnState, game: Hexapawn) -> Optional[Move]:
    root_player = state.to_move

    def value(node: HexapawnState, alpha: float, beta: float) -> float:
        if game.terminal_test(node):
            return game.utility(node, root_player)
        if node.to_move == root_player:
            best = -inf
            for action in game.actions(node):
                best = max(best, value(game.result(node, action), alpha, beta))
                alpha = max(alpha, best)
                if alpha >= beta:
                    break
            return best
        best = inf
        for action in game.actions(node):
            best = min(best, value(game.result(node, action), alpha, beta))
            beta = min(beta, best)
            if alpha >= beta:
                break
        return best

    best_move: Optional[Move] = None
    best_score = -inf
    for action in game.actions(state):
        score = value(game.result(state, action), best_score, inf)
        if score > best_score:
            best_score, best_move = score, action
    return best_move


def alpha_beta_player(game: Hexapawn, state: HexapawnState) -> Optional[Move]:
    return alpha_beta_search(state, game)


def format_move(move: Move) -> str:
    def square(position: Tuple[int, int]) -> str:
        return f"{FILES[position[0]]}{position[1] + 1}"
    return f"{square(move[0])} {square(move[1])}"


def parse_move(text: str) -> Move:
    parts = text.lower().replace("-", " ").split()
    if len(parts) != 2 or any(len(square) != 2 for square in parts):
        raise ValueError("Use two squares, e.g. a1 a2")

    def coordinate(square: str) -> Tuple[int, int]:
        if square[0] not in FILES or square[1] not in "123":
            raise ValueError("Squares must range from a1 to c3")
        return FILES.index(square[0]), int(square[1]) - 1
    return coordinate(parts[0]), coordinate(parts[1])


def play_human_vs_ai(human: str = WHITE) -> str:
    if human not in (WHITE, BLACK):
        raise ValueError("human must be 'W' or 'B'")
    game = Hexapawn()
    state = game.initial
    print(f"You are {human}. Enter moves like: a1 a2")
    while not game.terminal_test(state):
        game.display(state)
        if state.to_move == human:
            legal = game.actions(state)
            print("Legal moves:", ", ".join(map(format_move, legal)))
            while True:
                try:
                    move = parse_move(input("Your move: "))
                    if move in legal:
                        break
                    print("That is not a legal move.")
                except ValueError as error:
                    print(error)
        else:
            move = alpha_beta_player(game, state)
            print("AI move:", format_move(move))
        state = game.result(state, move)
    game.display(state)
    winner = game.winner(state)
    print(f"{winner} wins!")
    return winner


class HexapawnGUI:
    SQUARE = 112
    BOARD_SIZE = SQUARE * 3

    def __init__(self) -> None:
        import tkinter as tk

        self.tk = tk
        self.game = Hexapawn()
        self.human = WHITE
        self.state = self.game.initial
        self.selected: Optional[Tuple[int, int]] = None
        self.root = tk.Tk()
        self.root.title("HW4 — Hexapawn vs Alpha-Beta AI")
        self.root.configure(bg="#18212f")
        self.root.resizable(False, False)

        frame = tk.Frame(self.root, bg="#18212f", padx=22, pady=20)
        frame.pack()
        left = tk.Frame(frame, bg="#18212f")
        left.grid(row=0, column=0, padx=(0, 22))
        tk.Label(left, text="HEXAPAWN", font=("Helvetica", 22, "bold"),
                 fg="#f6c86e", bg="#18212f").pack(anchor="w")
        tk.Label(left, text="Human vs Alpha-Beta AI", font=("Helvetica", 11),
                 fg="#c9d6e5", bg="#18212f").pack(anchor="w", pady=(0, 10))
        self.canvas = tk.Canvas(left, width=self.BOARD_SIZE, height=self.BOARD_SIZE,
                                bg="#f0d9b5", highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        side = tk.Frame(frame, bg="#243246", padx=18, pady=16)
        side.grid(row=0, column=1, sticky="ns")
        self.status = tk.StringVar()
        tk.Label(side, textvariable=self.status, width=25, justify="left", wraplength=205,
                 font=("Helvetica", 12, "bold"), fg="#ffffff", bg="#243246").pack(anchor="w")
        tk.Label(side, text="Choose your side", font=("Helvetica", 10, "bold"),
                 fg="#f6c86e", bg="#243246").pack(anchor="w", pady=(22, 4))
        self.side = tk.StringVar(value=WHITE)
        for label, value in (("White — moves first", WHITE), ("Black — AI moves first", BLACK)):
            tk.Radiobutton(side, text=label, value=value, variable=self.side,
                           selectcolor="#30445e", activebackground="#243246",
                           activeforeground="#ffffff", bg="#243246", fg="#dbe7f3",
                           font=("Helvetica", 10)).pack(anchor="w")
        tk.Button(side, text="New game", command=self.new_game, bg="#f6c86e", fg="#17202d",
                  activebackground="#ffd884", relief="flat", font=("Helvetica", 11, "bold"),
                  padx=15, pady=7).pack(anchor="w", pady=(20, 18))
        tk.Label(side, text=("How to play\n"
                             "• Click one of your pawns.\n"
                             "• Click a highlighted destination.\n\n"
                             "Move one square forward into an empty square,\n"
                             "or capture diagonally forward.\n"
                             "Reach the far rank—or leave the other player\n"
                             "without a move—to win."), justify="left", wraplength=215,
                 font=("Helvetica", 9), fg="#c9d6e5", bg="#243246").pack(anchor="w")
        self.draw()

    def new_game(self) -> None:
        self.human = self.side.get()
        self.state = self.game.initial
        self.selected = None
        self.draw()
        if self.human == BLACK:
            self.status.set("AI is thinking…")
            self.root.after(350, self.ai_turn)

    def legal_destinations(self) -> List[Tuple[int, int]]:
        if self.selected is None:
            return []
        return [end for start, end in self.game.actions(self.state) if start == self.selected]

    def on_click(self, event: object) -> None:
        if self.game.terminal_test(self.state) or self.state.to_move != self.human:
            return
        file, row_from_top = event.x // self.SQUARE, event.y // self.SQUARE
        square = (file, 2 - row_from_top)
        board = self.state.pieces()
        if board.get(square) == self.human:
            self.selected = square
        elif self.selected is not None and square in self.legal_destinations():
            self.state = self.game.result(self.state, (self.selected, square))
            self.selected = None
            self.draw()
            if not self.game.terminal_test(self.state):
                self.status.set("AI is thinking…")
                self.root.after(350, self.ai_turn)
            return
        self.draw()

    def ai_turn(self) -> None:
        if self.game.terminal_test(self.state):
            self.draw()
            return
        move = alpha_beta_player(self.game, self.state)
        self.state = self.game.result(self.state, move)
        self.draw()

    def draw(self) -> None:
        c = self.canvas
        c.delete("all")
        light, dark = "#f0d9b5", "#b58863"
        for row in range(3):
            for file in range(3):
                x, y = file * self.SQUARE, row * self.SQUARE
                c.create_rectangle(x, y, x + self.SQUARE, y + self.SQUARE,
                                   fill=light if (file + row) % 2 == 0 else dark, outline="")
        for file, label in enumerate(FILES):
            c.create_text(file * self.SQUARE + 12, self.BOARD_SIZE - 12, text=label,
                          fill="#4e342e", font=("Helvetica", 10, "bold"))
        for row in range(3):
            c.create_text(12, row * self.SQUARE + 12, text=str(3 - row),
                          fill="#4e342e", font=("Helvetica", 10, "bold"))
        for file, rank in self.legal_destinations():
            x, y = file * self.SQUARE, (2 - rank) * self.SQUARE
            c.create_oval(x + 44, y + 44, x + 68, y + 68, fill="#55d6be", outline="")
        for (file, rank), piece in self.state.pieces().items():
            x, y = file * self.SQUARE, (2 - rank) * self.SQUARE
            fill, outline = ("#f8fafc", "#64748b") if piece == WHITE else ("#263548", "#0f172a")
            width = 5 if self.selected == (file, rank) else 2
            c.create_oval(x + 19, y + 19, x + 93, y + 93, fill=fill, outline=outline, width=width)
            c.create_text(x + 56, y + 56, text=piece, fill="#243246" if piece == WHITE else "#ffffff",
                          font=("Helvetica", 20, "bold"))
        winner = self.game.winner(self.state)
        if winner:
            self.status.set("You win!" if winner == self.human else "AI wins. Try another opening!")
        elif self.state.to_move == self.human:
            self.status.set("Your turn — select a pawn.")
        else:
            self.status.set("AI is thinking…")

    def run(self) -> None:
        self.root.mainloop()


def launch_gui() -> None:
    HexapawnGUI().run()


if __name__ == "__main__":
    try:
        launch_gui()
    except Exception as error:
        print(f"GUI unavailable ({error}); starting terminal mode instead.")
        play_human_vs_ai()
