# migrations/ — ordered, hand-written schema migrations (TheForge discipline).
#
# Each entry: (version:int, name:str, fn(conn)->None). The runner in db.py applies
# pending versions in order and records them in schema_migrations. Module files are
# named m####_<name>.py (Python modules can't start with a digit).
from Mechanics.data.migrations.m0001_initial_content import migrate as m0001
from Mechanics.data.migrations.m0002_runtime_state import migrate as m0002
from Mechanics.data.migrations.m0003_relational_items import migrate as m0003
from Mechanics.data.migrations.m0004_bag_column import migrate as m0004
from Mechanics.data.migrations.m0005_chests import migrate as m0005
from Mechanics.data.migrations.m0006_panel_coords import migrate as m0006

MIGRATIONS = [
    (1, "initial_content",  m0001),
    (2, "runtime_state",    m0002),
    (3, "relational_items", m0003),
    (4, "bag_column",       m0004),
    (5, "chests",           m0005),
    (6, "panel_coords",     m0006),
]
