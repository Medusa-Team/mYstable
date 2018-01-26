import unittest
from bitmap import Bitmap

class BitmapUnitTest(unittest.TestCase):

    def test_instantination(self):
        self.assertRaises(BaseException, Bitmap, ())
        self.assertRaises(BaseException, Bitmap, ('s',))
        self.assertRaises(BaseException, Bitmap, (1,))

        self.assertIsInstance(Bitmap(0), Bitmap)            # int
        self.assertIsInstance(Bitmap(Bitmap(8)), Bitmap)    # Bitmap
        self.assertIsInstance(Bitmap(bytes(2)), Bitmap)     # bytes,
        self.assertIsInstance(Bitmap(bytearray(2)), Bitmap) # bytearray

    def test_set_bit(self):
        bm = Bitmap(16)  # bitmap = 00000000
        self.assertEqual(16, bm.length())
        self.assertFalse(bm.all())
        self.assertFalse(bm.any())

        bm[0] = True  # bitmap = 10000000
        self.assertFalse(bm.all())
        self.assertTrue(bm.any())

        self.assertTrue(bm[0])
        self.assertFalse(bm[1])

        bm.setall(True)
        self.assertTrue(bm.any())
        self.assertTrue(bm.all())

        bm[0] = False
        self.assertFalse(bm.all())
        self.assertTrue(bm.any())

        bm.setall(False)
        self.assertFalse(bm.any())
        self.assertFalse(bm.any())


if __name__ == '__main__':
    unittest.main()
