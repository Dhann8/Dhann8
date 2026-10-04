import sys
import re
import json
import random

README_PATH = "README.md"
REPO_NAME = "Dhann8/Dhann8"

def check_winner(board):
    # Rows
    for row in board:
        if row[0] == row[1] == row[2] and row[0] != " ":
            return row[0]
    # Columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] != " ":
            return board[0][col]
    # Diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != " ":
        return board[0][2]
    # Draw check
    if all(cell != " " for row in board for cell in row):
        return "DRAW"
    return None

def bot_move(board):
    empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] == " "]
    if not empty_cells:
        return None
    
    # 1. Check if bot can win in 1 move
    for r, c in empty_cells:
        board[r][c] = "O"
        if check_winner(board) == "O":
            return (r, c)
        board[r][c] = " "
        
    # 2. Check if player X can win in 1 move, then block
    for r, c in empty_cells:
        board[r][c] = "X"
        if check_winner(board) == "X":
            board[r][c] = "O"
            return (r, c)
        board[r][c] = " "

    # 3. Take center if available
    if (1, 1) in empty_cells:
        board[1][1] = "O"
        return (1, 1)

    # 4. Take random corner
    corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
    avail_corners = [c for c in corners if c in empty_cells]
    if avail_corners:
        move = random.choice(avail_corners)
        board[move[0]][move[1]] = "O"
        return move

    # 5. Take any remaining cell
    move = random.choice(empty_cells)
    board[move[0]][move[1]] = "O"
    return move

def render_board(board, status_msg, last_player, game_over):
    cell_icons = {
        "X": "❌",
        "O": "⭕",
        " ": "⬜"
    }

    issue_base_url = f"https://github.com/{REPO_NAME}/issues/new"

    lines = []
    lines.append(f"<!-- STATE: {json.dumps(board)} | GAMEOVER: {'true' if game_over else 'false'} -->\n")
    lines.append(f"> **Status:** {status_msg}\n")
    lines.append(f"> **Pemain Terakhir:** @{last_player}\n\n")

    lines.append("| | Kolom 0 | Kolom 1 | Kolom 2 |\n")
    lines.append("| :---: | :---: | :---: | :---: |\n")

    for r in range(3):
        row_str = f"| **Baris {r}** | "
        for c in range(3):
            val = board[r][c]
            if val == " ":
                if not game_over:
                    # Clickable link to make move
                    title = f"ttc%7C{r}%7C{c}"
                    body = f"Klik 'Submit new issue' untuk melangkah di Baris {r}, Kolom {c}!"
                    link = f"{issue_base_url}?title={title}&body={re.sub(r' ', '+', body)}"
                    cell_md = f"[{cell_icons[' ']}]({link})"
                else:
                    cell_md = cell_icons[" "]
            else:
                cell_md = cell_icons[val]
            row_str += f"{cell_md} | "
        lines.append(row_str + "\n")

    reset_link = f"{issue_base_url}?title=ttc%7Creset&body=Klik+'Submit+new+issue'+untuk+mereset+papan+game!"
    lines.append(f"\n<br/>\n\n[![Mulai Game Baru](https://img.shields.io/badge/🔄_Mulai_Game_Baru_/_Reset_Papan-3E2723?style=for-the-badge&logo=github&logoColor=D4AF37&labelColor=231610)]({reset_link})\n")

    return "".join(lines)

def main():
    if len(sys.argv) < 3:
        print("Usage: python tictactoe.py '<issue_title>' '<actor>'")
        sys.exit(1)

    import urllib.parse
    issue_title = urllib.parse.unquote(sys.argv[1].strip())
    actor = sys.argv[2].strip()

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Match state
    state_match = re.search(r'<!-- STATE: (\[.*?\]) \| GAMEOVER: (true|false) -->', content)
    if state_match:
        board = json.loads(state_match.group(1))
        game_over = state_match.group(2) == "true"
    else:
        board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        game_over = False

    status_msg = ""

    if issue_title.startswith("ttc|reset"):
        board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        game_over = False
        status_msg = f"Game baru telah dimulai oleh @{actor}! Silakan klik salah satu kotak kosong untuk melangkah (Kamu: ❌ | Bot: ⭕)."
    elif issue_title.startswith("ttc|"):
        if game_over:
            status_msg = "⚠️ Permainan sudah selesai! Silakan klik tombol 'Mulai Game Baru' di bawah untuk main lagi."
        else:
            parts = issue_title.split("|")
            if len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
                r, c = int(parts[1]), int(parts[2])
                if 0 <= r <= 2 and 0 <= c <= 2:
                    if board[r][c] == " ":
                        board[r][c] = "X"
                        winner = check_winner(board)
                        if winner == "X":
                            status_msg = f"🎉 Luar biasa @{actor}! Kamu (❌) berhasil mengalahkan Bot!"
                            game_over = True
                        elif winner == "DRAW":
                            status_msg = f"🤝 Permainan berakhir Seri (Draw)! Hebat, duel sengit @{actor}!"
                            game_over = True
                        else:
                            # Bot's turn
                            b_move = bot_move(board)
                            bot_winner = check_winner(board)
                            if bot_winner == "O":
                                status_msg = f"🤖 Bot (⭕) berhasil menang di langkah ({b_move[0]}, {b_move[1]})! Mau coba lagi?"
                                game_over = True
                            elif bot_winner == "DRAW":
                                status_msg = f"🤝 Permainan berakhir Seri (Draw) setelah langkah Bot!"
                                game_over = True
                            else:
                                status_msg = f"Langkah @{actor} (❌) di ({r}, {c}) diterima. Bot (⭕) melangkah di ({b_move[0]}, {b_move[1]}). Giliranmu lagi!"
                    else:
                        status_msg = f"⚠️ Kotak ({r}, {c}) sudah terisi! Pilih kotak kosong yang lain."
                else:
                    status_msg = "⚠️ Koordinat tidak valid."
            else:
                status_msg = "⚠️ Perintah tidak valid."
    else:
        print("Issue title does not match ttc pattern.")
        sys.exit(0)

    new_board_md = render_board(board, status_msg, actor, game_over)

    # Replace between markers
    pattern = r'<!-- START_TICTACTOE -->[\s\S]*?<!-- END_TICTACTOE -->'
    replacement = f'<!-- START_TICTACTOE -->\n{new_board_md}\n<!-- END_TICTACTOE -->'

    new_content = re.sub(pattern, replacement, content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("Board updated successfully.")

if __name__ == "__main__":
    main()
