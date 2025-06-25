'''
Module with SignalCalculator class
'''
import pandas as pnd
from dmu.logging.log_store                 import LogStore
from dmu.generic                           import utilities as gut
from rx_efficiencies.efficiency_scanner    import EfficiencyScanner
from rx_efficiencies.efficiency_calculator import EfficiencyCalculator
from rx_efficiencies.decay_names           import DecayNames

log=LogStore.add_logger('rx_classifier:signal_calculator')
# -----------------------------------
class SignalCalculator:
    '''
    Class meant to calculate expected value of
    signal yield for different working points
    '''
    # -----------------------------------
    def __init__(self, cfg : dict, q2bin : str):
        '''
        Picks configuration
        '''
        self._cfg   = cfg
        self._q2bin = q2bin
    # -----------------------------------
    def _get_eff(self, is_signal : bool) -> pnd.DataFrame:
        '''
        Parameters
        -------------
        is_signal: If true, will run efficiency scan for signal, otherwise control mode

        Returns
        -------------
        Dataframe with the total efficiency for each working point
        '''
        cfg = {'input' : {}}
        if is_signal:
            cfg['input']['sample'] = self._cfg['samples']['signal']
            cfg['input']['q2bin' ] = self._q2bin
        else:
            cfg['input']['sample'] = self._cfg['samples']['control']
            cfg['input']['q2bin' ] = 'jpsi'

        cfg['input']['trigger'] = self._cfg['samples']['trigger']
        cfg['variables']        = self._cfg['variables']

        obj = EfficiencyScanner(cfg=cfg)
        df  = obj.run()

        return df
    # -----------------------------------
    def _get_eff_ratio(self) -> pnd.DataFrame:
        df_sig_eff = self._get_eff(is_signal=True)
        df_ctr_eff = self._get_eff(is_signal=False)

        df         = df_sig_eff.copy()
        df['rat']  = df_sig_eff['eff'] / df_ctr_eff['eff']
        df         = df.drop(columns=['yield', 'eff'])

        return df
    # -----------------------------------
    def _get_bfr_ratio(self) -> float:
        '''
        Returns ratio of branching fractions between the signal and control channel

        BR_sig / BR_ctr
        '''
        sig_sam = self._cfg['samples']['signal' ]
        ctr_sam = self._cfg['samples']['control']

        data    = gut.load_data(package='rx_efficiencies_data', fpath='scales/fr_bf.yaml')

        l_dec   = DecayNames.subdecays_from_sample(sample=sig_sam)
        bf_sig  = 1
        for dec in l_dec:
            bf_sig *= data['bf'][dec][0] # The zeroth element is the value, first is the error

        l_dec   = DecayNames.subdecays_from_sample(sample=ctr_sam)
        bf_ctr  = 1
        for dec in l_dec:
            bf_ctr *= data['bf'][dec][0]

        return bf_sig / bf_ctr
    # -----------------------------------
    def get_signal(self, control : int) -> pnd.DataFrame:
        '''
        Parameters
        --------------
        control: Integer with the yield of candidates for norminal working point

        Reuturns
        --------------
        pandas dataframe with signal yields
        '''
        df        = self._get_eff_ratio()
        rat_bfr   = self._get_bfr_ratio()
        df['sig'] = df['rat'] * rat_bfr * control

        return df
# -----------------------------------
