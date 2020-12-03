import datajoint as dj
from elements_animal import subject
from elements_lab import lab
from elements_ephys import probe, ephys

from .paths import get_ephys_probe_data_dir, get_ks_data_dir, get_paramset_idx


if 'custom' not in dj.config:
    dj.config['custom'] = {}

db_prefix = dj.config['custom'].get('database.prefix', '')


# ------------ Activate the "lab" and "subject" schemas ----------------

lab.activate(db_prefix + 'lab')

subject.activate(db_prefix + 'subject',
                 add_objects={'Source': lab.Source,
                              'Lab': lab.Lab,
                              'Protocol': lab.Protocol,
                              'User': lab.User})


@lab.schema
class SkullReference(dj.Lookup):
    definition = """
    skull_reference   : varchar(60)
    """
    contents = zip(['Bregma', 'Lambda'])


# ------------ Declare the Session table --------------

schema = dj.schema(db_prefix + 'experiment')


@schema
class Session(dj.Manual):
    definition = """
    -> subject.Subject
    session_datetime: datetime
    """


# -------------- Activate the "ephys" schema ---------
ephys.activate(db_prefix + 'ephys', db_prefix + 'probe',
               add_objects=dict(
                   # upstream tables
                   Session=Session,
                   SkullReference=SkullReference,
                   # functions
                   get_neuropixels_data_directory=get_ephys_probe_data_dir,
                   get_paramset_idx=get_paramset_idx,
                   get_kilosort_output_directory=get_ks_data_dir))

# ---- Add neuropixels probes ----
for probe_type in ('neuropixels 1.0 - 3A', 'neuropixels 1.0 - 3B',
                   'neuropixels 2.0 - SS', 'neuropixels 2.0 - MS'):
    probe.ProbeType.create_neuropixels_probe(probe_type)
