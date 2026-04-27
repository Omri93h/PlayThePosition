# Product and Technical Decisions

## Decision 001 — No confirmation screen after upload
Upload should go directly to processing and then analysis board.

Reason:
The main product value is low-friction screenshot-to-board conversion.

## Decision 002 — Detection can be mock/stubbed before real CV
Build upload, board, edit, and share flows before real detection.

Reason:
Detection is the riskiest technical part and should not block product shell validation.

## Decision 003 — Edit mode is core MVP, not optional
Detection will be imperfect. Edit mode is the safety net that makes the product usable.

## Decision 004 — chess.com analyzer link is MVP
The app should not compete with full analysis tools at first. It should bridge screenshots to existing analysis workflows.
