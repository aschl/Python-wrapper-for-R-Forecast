import unittest
from rforecast import wrappers
from rforecast import converters
from rforecast import ts_io
from rpy2 import robjects
from rpy2.robjects.packages import importr
import numpy


NULL = robjects.NULL
NA = robjects.NA_Real


class WrappersTestCase(unittest.TestCase):


  def setUp(self):

    importr('fpp2')
    # self.oil = robjects.r('oil')
    # self.aus = robjects.r('austourists')
    # self.gold = robjects.r('gold')
    self.oil = ts_io.read_ts('oil', 'fpp2', as_pandas=True)
    self.aus = ts_io.read_ts('austourists', 'fpp2', as_pandas=True)
    self.gold = ts_io.read_ts('gold', 'fpp2', as_pandas=True)
    self.tsn = converters.ts([1, 2, NA, 4])
    self.tss = converters.ts([1, 2, 3, 1, 2, 3, 1, NA, 3], frequency=3)
    self.vss = [1,2,3,4] * 4
    self.vns = range(10)
    r = [ 0.00287731,  0.58436909,  0.37650672,  0.10024602,  0.46983146,
        0.36542408,  0.47136475,  0.79978803,  0.70349953,  0.69531808,
        0.54447409,  0.82227504,  0.99736304,  0.91404314,  0.42225177,
        0.14696605,  0.08098318,  0.11046747,  0.8412757 ,  0.73562921]
    self.rnd = converters.sequence_as_series(r, freq=4)
    self.fc = importr('forecast')
    
    
  def test_frequency(self):
    self.assertEqual(wrappers.frequency(self.oil), 1)
    self.assertEqual(wrappers.frequency(self.aus), 4)


  def test_na_interp(self):
    self.assertEquals(list(wrappers.na_interp(self.tsn)), [1, 2, 3, 4])
    seasonal = list(wrappers.na_interp(self.tss))
    self.assertAlmostEqual(seasonal[7], 2.0, places=3)


  def test_ts(self):
    ts = converters.ts(self.vss, deltat=0.25, end=(1,1))
    self.assertEqual(wrappers.frequency(ts), 4)
    self.assertEqual(tuple(robjects.r('end')(ts)), (1.0, 1.0))
    self.assertEqual(tuple(robjects.r('start')(ts)), (-3.0, 2.0))


  def test_get_horizon(self):
    self.assertEqual(wrappers._get_horizon(self.aus), 8)
    self.assertEqual(wrappers._get_horizon(self.aus, 10), 10)
    self.assertEqual(wrappers._get_horizon(self.oil), 10)


  def test_box_cox(self):
    bc = wrappers.BoxCox(self.oil, 0.5)
    bc1 = wrappers.BoxCox(self.oil, 1)
    bc0 = wrappers.BoxCox(self.oil, 0)
    self.assertAlmostEqual(self.oil[0], bc1[0] + 1, places=4)
    self.assertAlmostEqual(numpy.log(self.oil[0]), bc0[0], places=4)
    bc_value = (self.oil.rx(1)[0]**0.5 - 1) / 0.5
    self.assertAlmostEqual(bc[0], bc_value, places=2)
    inv_bc = wrappers.InvBoxCox(bc, 0.5)
    self.assertAlmostEqual(inv_bc[0], self.oil[0], places=4)

  def test_tsclean(self):
    gold_py = converters.ts_as_series(converters.ts(self.gold))
    clean_py = wrappers.tsclean(gold_py)
    self.assertFalse(clean_py.isnull().any())
    clean_r = self.fc.tsclean(converters.ts(self.gold))
    self.assertAlmostEqual(clean_py[770], clean_r.rx(770), places=3)

  def test_findfrequency(self):
    self.assertEqual(wrappers.findfrequency(self.aus), 4)
    self.assertEqual(wrappers.findfrequency(self.oil), 1)

  def test_ndiffs(self):
    self.assertEqual(wrappers.ndiffs(self.oil), 1)
    self.assertEqual(wrappers.ndiffs(self.rnd), 0)

  def test_nsdiffs(self):
    self.assertEqual(wrappers.nsdiffs(self.aus), 1)
    self.assertEqual(wrappers.nsdiffs(self.rnd), 0)







