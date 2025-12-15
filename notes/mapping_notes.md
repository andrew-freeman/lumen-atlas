# Mapping notes

- Treat atlas UV space as a stable parameterization for navigation, not as physical ground truth.
- Favor short semantic tags and descriptions; they are invaluable when interpreting camera footage or prompting LLMs for review.
- When adding nodes, record at least one camera observation per activation to preserve traceability.
- Edge sets should be explicit: wiring continuity belongs in `strip`, perceptual proximity in `surface`, and any manual grouping in `region`.
- Iterate: add nodes while scanning, then run relaxation or smoothing passes to rebalance surface neighbors.
