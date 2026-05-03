# BLOCK 07 — Real Image Recognition Discovery

## Status
In progress / discovery-only; ready for closeout review after 7.7 review.

## Purpose
Close the biggest MVP gap: uploaded chess screenshots currently produce scaffolded/synthetic detection results.

## Goal
Discover and design the path toward real screenshot-to-board recognition without promising production-level accuracy yet.

## Non-goals
- No engine or Stockfish work.
- No legal move display.
- No auth, accounts, payments, or premium enforcement.
- No external Chess.com/Lichess link-out.
- No SEO or distribution work.
- No CV/ML dependencies unless explicitly approved in a later implementation feature.

## Required discovery areas
- Supported screenshot sources and visual styles.
- Board detection and cropping.
- Orientation detection.
- Piece recognition.
- FEN generation.
- Confidence and failure reporting.
- Manual correction fallback through Edit Board.
- Debug/inspection view showing recognized pieces and squares, such as "black rook at h4" or "white king at d3".
- Fixture and test image strategy.
- Privacy/safety: avoid storing raw uploaded screenshots unless explicitly approved.

## Suggested feature breakdown

### 7.1 Discovery/spec and fixture strategy
- Status: implemented / ready for review.
- Define supported screenshot targets.
- Define initial measurement approach.
- Define fixture metadata expectations.

### 7.2 Detection debug/inspection UI design
- Status: implemented / ready for review.
- Design how users or developers can see what detection understood.
- Keep this as design/spec until implementation is approved.

### 7.3 Real screenshot fixture pipeline
- Status: implemented / ready for review.
- Plan a small curated fixture workflow.
- Avoid large, copyrighted, or raw user-uploaded datasets.

### 7.4 Board detection experiment
- Status: implemented / ready for review.
- Synthetic/control PPM experiment only; not real screenshot support.
- Explore board localization/cropping approaches.
- Measure against approved fixtures only.

### 7.5 Piece recognition experiment
- Status: implemented / ready for review.
- Synthetic/control marker experiment only; not real screenshot recognition.
- Explore piece recognition approaches.
- Avoid production accuracy claims.

### 7.6 Confidence/failure UX
- Status: implemented / ready for review.
- Backend metadata standardization and docs only; no upload/API response change and no frontend UI.
- Define confidence thresholds and recoverable failure states.
- Keep Edit Board as the fallback for uncertain results.

### 7.7 Integration plan for replacing scaffolded detection
- Status: implemented / ready for review.
- Docs/planning only; no upload/API response change and no real recognition integration.
- Define the safest path from scaffolded detection to real detection.
- Include rollout, testing, and fallback criteria.

## Success criteria
- A clear measurement approach exists before implementation.
- Accuracy is not overclaimed.
- All failures remain recoverable through Edit Board.
- Debug output makes detection understandable.

## Risks
- CV scope can balloon.
- Source screenshots vary heavily.
- Copyrighted or user-uploaded image handling may create privacy/safety concerns.
- Poor accuracy can hurt trust more than scaffolded honesty.

## Done definition
- BLOCK 07 discovery is complete when the supported scope, fixture strategy, measurement approach, debug plan, and integration path are documented.
- Real-world screenshot recognition implementation begins only after an approved follow-up feature.
