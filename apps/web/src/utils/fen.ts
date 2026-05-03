type FenBoard = Array<Array<string | null>>;
export type FenActiveColor = "w" | "b";

const boardFiles = "abcdefgh";

export function movePieceInFen({
  fen,
  piece,
  sourceSquare,
  targetSquare,
}: {
  fen: string;
  piece: string;
  sourceSquare: string;
  targetSquare: string;
}) {
  const [placement, ...metadataParts] = fen.trim().split(/\s+/);
  const board = parsePlacement(placement);
  const source = squareToIndices(sourceSquare);
  const target = squareToIndices(targetSquare);
  const fenPiece = pieceCodeToFenPiece(piece);

  if (!source || !target || !fenPiece) {
    return fen;
  }

  board[source.row][source.column] = null;
  board[target.row][target.column] = fenPiece;

  const metadata = metadataParts.join(" ");
  const nextPlacement = serializePlacement(board);

  return metadata ? `${nextPlacement} ${metadata}` : nextPlacement;
}

export function removePieceFromFen({ fen, square }: { fen: string; square: string }) {
  const [placement, ...metadataParts] = fen.trim().split(/\s+/);
  const board = parsePlacement(placement);
  const target = squareToIndices(square);

  if (!target) {
    return fen;
  }

  board[target.row][target.column] = null;

  const metadata = metadataParts.join(" ");
  const nextPlacement = serializePlacement(board);

  return metadata ? `${nextPlacement} ${metadata}` : nextPlacement;
}

export function placePieceInFen({
  fen,
  piece,
  square,
}: {
  fen: string;
  piece: string;
  square: string;
}) {
  const [placement, ...metadataParts] = fen.trim().split(/\s+/);
  const board = parsePlacement(placement);
  const target = squareToIndices(square);
  const fenPiece = pieceCodeToFenPiece(piece);

  if (!target || !fenPiece) {
    return fen;
  }

  board[target.row][target.column] = fenPiece;

  const metadata = metadataParts.join(" ");
  const nextPlacement = serializePlacement(board);

  return metadata ? `${nextPlacement} ${metadata}` : nextPlacement;
}

export function getFenActiveColor(fen: string): FenActiveColor {
  return fen.trim().split(/\s+/)[1] === "b" ? "b" : "w";
}

export function setFenActiveColor({
  fen,
  activeColor,
}: {
  fen: string;
  activeColor: FenActiveColor;
}) {
  const [placement, , castling = "-", enPassant = "-", halfmove = "0", fullmove = "1"] =
    fen.trim().split(/\s+/);

  return [placement, activeColor, castling, enPassant, halfmove, fullmove].join(" ");
}

function parsePlacement(placement: string): FenBoard {
  return placement.split("/").map((rank) => {
    const row: Array<string | null> = [];

    for (const character of rank) {
      const emptySquares = Number(character);

      if (Number.isInteger(emptySquares) && emptySquares > 0) {
        row.push(...Array<null>(emptySquares).fill(null));
      } else {
        row.push(character);
      }
    }

    return row;
  });
}

function serializePlacement(board: FenBoard) {
  return board
    .map((row) => {
      let serialized = "";
      let emptySquares = 0;

      for (const square of row) {
        if (!square) {
          emptySquares += 1;
          continue;
        }

        if (emptySquares > 0) {
          serialized += emptySquares;
          emptySquares = 0;
        }

        serialized += square;
      }

      return emptySquares > 0 ? `${serialized}${emptySquares}` : serialized;
    })
    .join("/");
}

function squareToIndices(square: string) {
  const file = square[0];
  const rank = Number(square[1]);
  const column = boardFiles.indexOf(file);

  if (column < 0 || !Number.isInteger(rank) || rank < 1 || rank > 8) {
    return null;
  }

  return {
    column,
    row: 8 - rank,
  };
}

function pieceCodeToFenPiece(piece: string) {
  if (/^[kqrbnpKQRBNP]$/.test(piece)) {
    return piece;
  }

  const color = piece[0];
  const pieceType = piece[1];

  if (!pieceType) {
    return null;
  }

  return color === "b" ? pieceType.toLowerCase() : pieceType.toUpperCase();
}
