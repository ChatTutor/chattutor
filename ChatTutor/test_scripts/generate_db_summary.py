import sys 
sys.path.insert(0, ".")

import db_summary
db_summary.create_embeddings_with_levels_of_information()
db_summary.create_db_summary()
print(db_summary.get_db_summary())

