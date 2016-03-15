# FinderSidebarEditor
Python module for easily adding removing, and moving favorites from the Finder sidebar in the context of the logged in user.

Example Usage:
```
#!/usr/bin/python

import FinderSidebarEditor

sidebar = FinderSidebar() # Create a sidebar instance to act on.

sidebar.remove("All My Files") # Remove 'All My Files' favorite from sidebar
sidebar.remove("iCloud") # Remove 'iCloud' favorite from sidebar
sidebar.add("/Library") # Add '/Library' favorite to sidebar
sidebar.move("Library", "Applications") # Move newly added 'Library' favorite to just after 'Applications'

```
