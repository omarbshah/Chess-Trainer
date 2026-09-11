"""Lichess puzzle theme reference data.

Theme ids are Lichess's own taxonomy (as used in `PuzzleDashboard.themes` keys and
`PuzzleActivityPuzzle.themes`), sourced from lichess-org/lila's puzzleTheme
translation strings. Kept as one flat mapping since that's how the API keys them;
grouped by comment below purely for human readability.
"""

from __future__ import annotations

THEME_NAMES: dict[str, str] = {
    # Tactical motifs
    "advancedPawn": "Advanced pawn",
    "attraction": "Attraction",
    "capturingDefender": "Capture the defender",
    "clearance": "Clearance",
    "defensiveMove": "Defensive move",
    "deflection": "Deflection",
    "discoveredAttack": "Discovered attack",
    "discoveredCheck": "Discovered check",
    "doubleCheck": "Double check",
    "exposedKing": "Exposed king",
    "fork": "Fork",
    "hangingPiece": "Hanging piece",
    "interference": "Interference",
    "intermezzo": "Intermezzo",
    "pin": "Pin",
    "quietMove": "Quiet move",
    "sacrifice": "Sacrifice",
    "skewer": "Skewer",
    "trappedPiece": "Trapped piece",
    "xRayAttack": "X-Ray attack",
    "zugzwang": "Zugzwang",
    "attackingF2F7": "Attacking f2 or f7",
    "kingsideAttack": "Kingside attack",
    "queensideAttack": "Queenside attack",
    "collinearMove": "Collinear move",
    # Checkmate patterns
    "mate": "Checkmate",
    "mateIn1": "Mate in 1",
    "mateIn2": "Mate in 2",
    "mateIn3": "Mate in 3",
    "mateIn4": "Mate in 4",
    "mateIn5": "Mate in 5 or more",
    "anastasiaMate": "Anastasia's mate",
    "arabianMate": "Arabian mate",
    "backRankMate": "Back rank mate",
    "balestraMate": "Balestra mate",
    "blindSwineMate": "Blind Swine mate",
    "bodenMate": "Boden's mate",
    "cornerMate": "Corner mate",
    "doubleBishopMate": "Double bishop mate",
    "dovetailMate": "Dovetail mate",
    "epauletteMate": "Epaulette mate",
    "hookMate": "Hook mate",
    "killBoxMate": "Kill box mate",
    "morphysMate": "Morphy's mate",
    "operaMate": "Opera mate",
    "pillsburysMate": "Pillsbury's mate",
    "smotheredMate": "Smothered mate",
    "swallowstailMate": "Swallow's tail mate",
    "triangleMate": "Triangle mate",
    "vukovicMate": "Vuković mate",
    # Endgame types
    "endgame": "Endgame",
    "pawnEndgame": "Pawn endgame",
    "knightEndgame": "Knight endgame",
    "bishopEndgame": "Bishop endgame",
    "rookEndgame": "Rook endgame",
    "queenEndgame": "Queen endgame",
    "queenRookEndgame": "Queen and Rook",
    "promotion": "Promotion",
    "underPromotion": "Underpromotion",
    "enPassant": "En passant",
    "castling": "Castling",
    "equality": "Equality",
    # Game phase
    "opening": "Opening",
    "middlegame": "Middlegame",
    # Puzzle length / difficulty
    "oneMove": "One-move puzzle",
    "short": "Short puzzle",
    "long": "Long puzzle",
    "veryLong": "Very long puzzle",
    "advantage": "Advantage",
    "crushing": "Crushing",
    "mix": "Healthy mix",
    # Puzzle source
    "master": "Master games",
    "masterVsMaster": "Master vs Master games",
    "superGM": "Super GM games",
    "playerGames": "Player games",
}
