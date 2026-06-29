
class CuratedProtein(object):

    def __init__(self, protein_accession, genome_accession):
        pass

    @property
    def proteome_source(self):


    def sequence(self):


    def genomic_locus(self):


    def sequence_with_leader(self):


    def genomic_locus_with_leader(self):


    def detected_pfam(self):
        """Returns DetectedTable dictionary array"""


    def detected_ko(self):
        """Returns DetectedTable dictionary array"""


    def hmm_align(self, hmm_profile_fn):



class GenomicLocus(object):

    def __init__(self, locus_id, product, genome_accession, contig_accession, left1b, right1b, strand):

    def start_codon_position_1b(self):

    def stop_codon_position_1b(self):

    def dss_positions_1b(self):

    def ass_positions_1b(self):



class ProteinHMMAlignment(object):

    def aa_at_hmm_pos_1b(self):
