from FinderSidebarEditor import FinderSidebar
import unittest

class TestFinderSidebar(unittest.TestCase):
	def setUp(self):
		self.finder = FinderSidebar()
		self.pre_items = dict(self.finder.favorites)
		self.finder.removeAll()

	def tearDown(self):
		self.finder.removeAll()
		for name, uri in self.pre_items.iteritems():
			self.finder.add(uri)

if __name__ == '__main__':
    unittest.main()
