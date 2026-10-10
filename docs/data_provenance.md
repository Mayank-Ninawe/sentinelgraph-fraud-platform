# PaySim Data Provenance

Source:

https://www.kaggle.com/datasets/ealaxi/paysim1/data

PaySim is a synthetic mobile-money transaction dataset generated using the
PaySim simulator.

Original fields used:

- step
- type
- amount
- nameOrig
- nameDest
- isFraud

Excluded from the initial model:

- oldbalanceOrg
- newbalanceOrig
- oldbalanceDest
- newbalanceDest
- isFlaggedFraud

The balance fields are excluded initially because they may expose transaction
outcome information and create unrealistic leakage.

The fields device_id, ip_id, and location_id are deterministic simulated
enrichment fields. They are not original PaySim fields and are used only to
demonstrate graph-based fraud-ring detection.
