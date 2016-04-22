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

	def test_get_index(self):
		self.finder.removeAll()
		self.finder.add("/tmp")
		assert self.finder.getIndexFromName("tmp") == 0
		self.finder.add("/usr")
		assert self.finder.getIndexFromName("usr") == 1
		self.finder.removeAll()

	def test_add_then_remove_all(self):
		self.finder.add("/tmp")
		assert 'tmp' in self.finder.favorites.keys()
		self.finder.removeAll()
		assert not self.finder.favorites
		self.finder.removeAll()

	def test_add_then_remove(self):
		self.finder.add("/usr")
		assert 'usr' in self.finder.favorites.keys()
		self.finder.remove("usr")
		assert not self.finder.favorites
		self.finder.removeAll()

	def test_add_then_move_items(self):
		self.finder.removeAll()
		self.finder.add("/usr")
		self.finder.add("/tmp")
		self.finder.move("usr", "tmp")
		assert self.finder.getIndexFromName("tmp") < self.finder.getIndexFromName("usr")
		self.finder.removeAll()

if __name__ == '__main__':
    unittest.main()
