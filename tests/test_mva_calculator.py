'''
Module containing tests for MVACalculator class
'''
import os
import pytest
import matplotlib.pyplot as plt
from ROOT                         import RDF, RDataFrame
from dmu.logging.log_store        import LogStore
from rx_data.rdf_getter           import RDFGetter
from rx_classifier.mva_calculator import MVACalculator

log=LogStore.add_logger('rx_classifier:test_mva_calculator')
# ----------------------
class Data:
    '''
    Class meant to be used to share attributes
    '''
    l_trigger= ['Hlt2RD_BuToKpMuMu_MVA', 'Hlt2RD_BuToKpEE_MVA']
    nentries = 30_000
# ----------------------
def _validate_rdf(
    rdf     : RDF.RNode,
    name    : str,
    out_dir : str) -> None:
    '''
    Parameters
    -------------
    rdf: ROOT dataframe with MVA scores
    '''
    log.info('Validating dataframe')

    os.makedirs(out_dir, exist_ok=True)
    assert isinstance(rdf, (RDF.RNode, RDataFrame))

    nentries = rdf.Count().GetValue()
    assert nentries == Data.nentries

    log.info('Found columns:')
    for col_name in rdf.GetColumnNames():
        log.info(f'    {col_name}')

    log.info('Extracting data')
    data = rdf.AsNumpy()

    log.info('Plotting')

    plt.hist(data['mva_cmb'], bins=50, range=(-1,+1), histtype='step', label='Combinatorial')
    plt.hist(data['mva_prc'], bins=50, range=(-1,+1), histtype='step', label='Part reco')
    plt.savefig(f'{out_dir}/{name}.png')
    plt.close()
# ----------------------
@pytest.mark.parametrize('trigger', Data.l_trigger)
def test_data(trigger : str, out_dir : str) -> None:
    '''
    Simplest test validating MVACalculator
    '''
    sample = 'DATA_24*'
    version= 'v7p7'

    with RDFGetter.max_entries(value=Data.nentries):
        gtr = RDFGetter(sample=sample, trigger=trigger)
        rdf = gtr.get_rdf()

    cal = MVACalculator(
    rdf     = rdf,
    sample  = sample,
    trigger = trigger,
    version = version)

    rdf = cal.get_rdf()
    _validate_rdf(rdf=rdf, out_dir=f'{out_dir}/data', name='data')
# --------------------------------
