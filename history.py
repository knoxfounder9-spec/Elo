from database import execute

def add_match(winner, loser):
    execute(
        "INSERT INTO match_history (winner, loser) VALUES (%s, %s)",
        (str(winner), str(loser))
    )
