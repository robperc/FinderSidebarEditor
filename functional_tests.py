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

if __name__ == '__main__':
    unittest.main()
