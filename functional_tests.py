from FinderSidebarEditor import FinderSidebar
import unittest

class TestFinderSidebar(unittest.TestCase):
	def setUp(self):
		self.finder = FinderSidebar()
		self.pre_items = [str(uri).split("file://")[1] for uri in self.finder.favorites.values()]
		self.finder.removeAll()

	def tearDown(self):
		self.finder.removeAll()
		for uri in self.pre_items:
			self.finder.add(uri)

	def test_add_then_remove_all(self):
		self.finder.add("/tmp")
		assert 'tmp' in self.finder.favorites.keys()
		self.finder.removeAll()
		assert not self.finder.favorites

if __name__ == '__main__':
    unittest.main()
