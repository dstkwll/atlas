"""Engine validators — the checks that mint Core receipts.

Only code in this package (and Core) constructs a ``Receipt``. A HARD validator
attests that a done-contract was truly met by running executable checks; an
ADMISSIBILITY validator attests only well-formedness and can never claim a
command executed (invariant 3).
"""
