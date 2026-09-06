import unittest
from importer import Importer
class Source:
    def fetch(self, tenant): return ["a", "b"]
class TestImport(unittest.TestCase):
    def test_import(self):
        worker=Importer(Source())
        self.assertEqual(worker.run("one", "job")['count'],2)
        self.assertEqual(len(worker.records),2)
    def test_repeat(self):
        worker=Importer(Source())
        worker.run("one", "job")
        worker.run("one", "job")
        self.assertEqual(len(worker.records),2)
