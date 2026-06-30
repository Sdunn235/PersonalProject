# migrations/ — ordered, hand-written schema migrations (TheForge discipline).
#
# Each entry: (version:int, name:str, fn(conn)->None). The runner in db.py applies
# pending versions in order and records them in schema_migrations. Module files are
# named m####_<name>.py (Python modules can't start with a digit).
from Mechanics.data.migrations.m0001_initial_content import migrate as m0001

MIGRATIONS = [
    (1, "initial_content", m0001),
]
