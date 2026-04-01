# not a project, not projEct the verb -- in this case feature projection to an
# original sequence. we can't project or lift-over coordinates because the
# matches can be between dna and rna, rna and protein, protein and structure,
# plus we don't know anything about potential in-dels, etc.

import duckdb
from .detected import DetectedTable
from dataclasses import dataclass


@dataclass
class Feature:
    accession: str
    database: str
    type: str

    def tuple(self):
        return (self.accession, self.database, self.type)


class Match(object):

    def __init__(self, match_dict, last_match):
        self._m = match_dict
        self.last_match = last_match

        if last_match is None:
            self.target_strand_relative_to_start = 1
        else:
            assert self.query_feature == last_match.target_feature
            if self._m["query_start"] < self._m["query_end"] and self._m["target_start"] <= self._m["target_end"]:
                matched_strand_relative_to_query = 1
            elif self._m["query_start"] < self._m["query_end"] and self._m["target_start"] > self._m["target_end"]:
                matched_strand_relative_to_query = -1
            elif self._m["query_start"] >= self._m["query_end"] and self._m["target_start"] <= self._m["target_end"]:
                matched_strand_relative_to_query = -1
            elif self._m["query_start"] >= self._m["query_end"] and self._m["target_start"] > self._m["target_end"]:
                matched_strand_relative_to_query = 1
            self.target_strand_relative_to_start = last_match.target_strand_relative_to_start * matched_strand_relative_to_query

    @property
    def query_feature(self):
        return Feature(
            accession=self._m["query_accession"],
            database=self._m["query_database"],
            type=self._m["query_type"]
        )

    @property
    def target_feature(self):
        return Feature(
            accession=self._m["target_accession"],
            database=self._m["target_database"],
            type=self._m["target_type"]
        )

    @property
    def t_s_ordered(self):
        return min(self._m["target_start"], self._m["target_end"]) if self._m["target_start"] is not None else None

    @property
    def t_e_ordered(self):
        return max(self._m["target_start"], self._m["target_end"]) if self._m["target_start"] is not None else None

    # mostly for testing
    def summary(self):
        return (self.target_feature, self.t_s_ordered, self.t_e_ordered, self.target_strand_relative_to_start)

    @staticmethod
    def start_with(start_feature):
        m = dict(
          target_database = start_feature.database,
          target_type = start_feature.type,
          target_accession = start_feature.accession,
          target_start = None,
          target_end = None,
        )
        return Match(m, None)
        

def recursive_project(start_feature, schema, fuzz):

    schema.duckdb_load()
    db = duckdb.connect(':default:')

    queue = [Match.start_with(start_feature)]
    results = []
    visited = set()

    while queue:
        last_match = queue.pop(0)
        curr_feature = last_match.target_feature
        curr_s = last_match.t_s_ordered
        curr_e = last_match.t_e_ordered

        # Prevent infinite loops
        state = (curr_feature.tuple(), curr_s, curr_e)
        if state in visited:
          continue
        visited.add(state)

        coord_cond = ""
        if curr_s is not None:
            coord_cond = f"""AND ((query_start <= query_end AND query_start >= {curr_s-fuzz} AND query_end <= {curr_e+fuzz})
                               OR (query_start  > query_end AND query_end >= {curr_s-fuzz} AND query_start <= {curr_e+fuzz}))"""

        query = f"""
            SELECT *
              FROM {schema.name}.{DetectedTable.name}
             WHERE query_accession = '{curr_feature.accession}'
               AND query_database = '{curr_feature.database}'
               AND query_type = '{curr_feature.type}'
               {coord_cond}
        """

        # print(f"STATE {state}\nSQL {query}")
        matches = db.execute(query).fetchdf().to_dict('records')

        for match_dict in matches:
            match = Match(match_dict, last_match)
            results.append(match)
            queue.append(match)

    return results


def results_to_detected_table(results, tsv_fn, append = False):
    rows = [m._m for m in results]
    DetectedTable.write_tsv(tsv_fn, rows, append = append)
