from FinderSidebarEditor import FinderSidebar
import unittest


class TestFinderSidebar(unittest.TestCase):
	def setUp(self):
		self.finder = FinderSidebar()
		self.pre_items = [
			str(uri).split("file://")[1]
			for uri in self.finder.favorites.values()
		]
		self.finder.remove_all()

	def tearDown(self):
		self.finder.remove_all()
		for uri in reversed(self.pre_items):
			self.finder.add(uri)

	def test_add(self):
		self.finder.add("/tmp")
		self.assertIn('tmp', self.finder.favorites.keys())

	def test_get_index(self):
		self.finder.add("/tmp")
		self.assertEqual(self.finder.get_index_from_name("tmp"), 0)

		self.finder.add("/usr")
		self.assertEqual(self.finder.get_index_from_name("usr"), 0)
		self.assertEqual(self.finder.get_index_from_name("tmp"), 1)

	def test_remove_all(self):
		self.finder.add("/tmp")
		self.finder.remove_all()
		self.assertFalse(self.finder.favorites)

	def test_remove(self):
		self.finder.add("/usr")
		self.finder.remove("usr")
		self.assertFalse(self.finder.favorites)

	def test_remove_by_path(self):
		self.finder.add("/usr")
		self.finder.remove_by_path("/usr")
		self.assertFalse(self.finder.favorites)

	def test_move_items(self):
		self.finder.add("/usr")
		self.finder.add("/tmp")
		self.assertEqual(self.finder.get_index_from_name('tmp'), 0)
		self.assertEqual(self.finder.get_index_from_name('usr'), 1)

		self.finder.move("tmp", "usr")
		self.assertEqual(self.finder.get_index_from_name('usr'), 0)
		self.assertEqual(self.finder.get_index_from_name('tmp'), 1)


if __name__ == '__main__':
	unittest.main()
