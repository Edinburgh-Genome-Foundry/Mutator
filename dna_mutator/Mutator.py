import os
import random

import pandas

from Bio import SeqIO
from Bio.Seq import Seq, MutableSeq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation


class Mutator:
    """Class to generate simulations of structural and single nucleotide variants.


    Parameters
    ----------

    reference
      A `SeqRecord` instance.

    library_size
      Library size (`int`).
    """

    def __init__(self, reference, library_size=10):
        self.reference = reference
        self.library_size = library_size
        self.variant_records = []

    def write_sample_sheet(self, csv_file):
        """Create a sample sheet (for use with Sequeduct)."""
        barcode_dir = [
            "barcode" + ("{0:02d}".format(i + 1))
            for i in range(len(self.variant_records))
        ]

        variants = [variant_record.id for variant_record in self.variant_records]
        df_variants = pandas.DataFrame({"Sample": variants, "Barcode_dir": barcode_dir})
        df_variants.to_csv(csv_file, index=False)

    @staticmethod
    def subtract_bases(seq, pos, n):
        """Substract N bases from a sequence.


        Parameters
        ----------

        seq
          `Seq` instance.

        pos
          Location of change (`int`).

        n
          Number of bases to subtract (`int`).
        """
        modified_sequence = MutableSeq(seq)
        deleted_sequence = modified_sequence[pos : pos + n]
        del modified_sequence[pos : pos + n]

        return (
            modified_sequence,
            pos,
            deleted_sequence,
        )

    @staticmethod
    def get_random_pos(record, n=1):
        """Get n different random positions in a record."""
        positions = random.sample(range(0, len(record)), n)

        return positions

    @staticmethod
    def read_genbank(genbank, use_file_name_as_id=True):
        """Get the reference sequence and features from input file.


        Parameters
        ----------

        genbank
          Path to Genbank file (`str`).

        use_file_name_as_id
          Replace record id and name with the filename (`bool`).
        """
        record = SeqIO.read(genbank, "genbank")
        if use_file_name_as_id:
            record.name = os.path.splitext(os.path.basename(genbank))[0]
            record.id = record.name

        return record

    @staticmethod
    def write_genbank(record, file_name):
        """Write SeqRecord to a Genbank file."""
        SeqIO.write(record, file_name, "gb")

    def write_all_records(self, dir_name):
        """Write original record and all variants into a directory"""
        extension = ".gb"  # standard file ext for GenBank files
        os.mkdir(dir_name)
        # ORIGINAL REFERENCE RECORD
        ref_path = os.path.join(dir_name, self.reference.id + extension)
        self.write_genbank(self.reference, ref_path)
        # VARIANTS
        for variant in self.variant_records:
            variant_path = os.path.join(dir_name, variant.id)
            self.write_genbank(variant, variant_path + extension)

    def DelN(self, bases=1):
        """Simulate N base deletion."""
        positions = self.get_random_pos(self.reference, n=self.library_size)
        for i in range(self.library_size):
            position = positions[i]
            modified_sequence, position, deleted_sequence = self.subtract_bases(
                self.reference.seq, position, bases
            )
            if len(deleted_sequence) == 1:  # show the letter if there's only one
                suffix = str(deleted_sequence)
            else:
                suffix = str(len(deleted_sequence))
            # We append the original name according to nomenclature:
            variant_name = self.reference.id + "_" + str(position) + "D" + suffix
            variant_record = SeqRecord(
                Seq(modified_sequence),
                id=variant_name,
                name=variant_name,
                annotations={"molecule_type": "DNA", "topology": "circular"},
            )
            label = "@mutator(del)"
            description = (
                "Deletion in position "
                + str(position)
                + " of "
                + str(bases)
                + " bases ("
                + str(deleted_sequence)
                + ")"
            )
            feature = SeqFeature(
                FeatureLocation(position, position),
                type="misc_feature",
                id="@mutator",
                qualifiers={"label": label, "note": description},
            )
            variant_record.features.append(feature)

            self.variant_records.append(variant_record)
