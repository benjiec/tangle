# not a project, not projEct the verb -- in this case feature projection to an
# original sequence. we can't project or lift-over coordinates because the
# matches can be between dna and rna, rna and protein, protein and structure,
# plus we don't know anything about potential in-dels, etc.

import duckdb
from .detected import DetectedTable


def recursive_project(start_accession, schema, fuzz):

    schema.duckdb_load()
    db = duckdb.connect(':default:')

    # Queue stores: (accession, start, end, strand_relative_to_root)

    queue = [(start_accession, None, None, 1)]
    results = []
    visited = set()

    while queue:
        curr_acc, curr_s, curr_e, strand_relative_to_root = queue.pop(0)
        assert curr_s is None or curr_s < curr_e

        # Prevent infinite loops
        state = (curr_acc, curr_s, curr_e)
        if state in visited: continue
        visited.add(state)

        coord_cond = ""
        if curr_s is not None:
            coord_cond = f"""AND ((query_start <= query_end AND query_start >= {curr_s-fuzz} AND query_end <= {curr_e+fuzz})
                               OR (query_start  > query_end AND query_end >= {curr_s-fuzz} AND query_start <= {curr_e+fuzz}))"""

        query = f"""
            SELECT query_start, query_end, target_accession, target_start, target_end
              FROM {schema.name}.{DetectedTable.name}
             WHERE query_accession = '{curr_acc}' {coord_cond}
        """

        # print(f"STATE {state}\nSQL {query}")
        matches = db.execute(query).fetchall()

        for q_s, q_e, t_acc, t_s, t_e in matches:
            if q_s < q_e and t_s <= t_e:
                matched_strand_relative_to_query = 1
            elif q_s < q_e and t_s > t_e:
                matched_strand_relative_to_query = -1
            elif q_s >= q_e and t_s <= t_e:
                matched_strand_relative_to_query = -1
            elif q_s >= q_e and t_s > t_e:
                matched_strand_relative_to_query = 1

            results.append((t_acc, min(t_s, t_e), max(t_s, t_e), strand_relative_to_root * matched_strand_relative_to_query))
            queue.append(results[-1])
            # print(f"ADD {results[-1]}")

    return results
