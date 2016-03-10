import Cocoa
import CoreFoundation
from LaunchServices import kLSSharedFileListFavoriteItems
import platform

os_vers = int(platform.mac_ver()[0].split('.')[1])
if os_vers > 10:
	from Foundation import NSBundle
	import objc
	SFL_bundle = NSBundle.bundleWithIdentifier_('com.apple.coreservices.SharedFileList')
	functions  = [('LSSharedFileListCreate',              '^{OpaqueLSSharedFileListRef=}^{__CFAllocator=}^{__CFString=}@'),
				  ('LSSharedFileListCopySnapshot',        '^{__CFArray=}^{OpaqueLSSharedFileListRef=}o^I'),
				  ('LSSharedFileListItemCopyDisplayName', '^{__CFString=}^{OpaqueLSSharedFileListItemRef=}'),
				  ('LSSharedFileListItemResolve',         'i^{OpaqueLSSharedFileListItemRef=}Io^^{__CFURL=}o^{FSRef=[80C]}'),
				  ('LSSharedFileListItemMove',            'i^{OpaqueLSSharedFileListRef=}^{OpaqueLSSharedFileListItemRef=}^{OpaqueLSSharedFileListItemRef=}'),
				  ('LSSharedFileListItemRemove',          'i^{OpaqueLSSharedFileListRef=}^{OpaqueLSSharedFileListItemRef=}'),
				  ('LSSharedFileListInsertItemURL',       '^{OpaqueLSSharedFileListItemRef=}^{OpaqueLSSharedFileListRef=}^{OpaqueLSSharedFileListItemRef=}^{__CFString=}^{OpaqueIconRef=}^{__CFURL=}^{__CFDictionary=}^{__CFArray=}'),
				  ('kLSSharedFileListItemBeforeFirst',    '^{OpaqueLSSharedFileListItemRef=}'),]
	objc.loadBundleFunctions(SFL_bundle, globals(), functions)
else:
	from LaunchServices import kLSSharedFileListItemBeforeFirst, LSSharedFileListCreate, LSSharedFileListCopySnapshot, LSSharedFileListItemCopyDisplayName, LSSharedFileListItemResolve, LSSharedFileListItemMove, LSSharedFileListItemRemove, LSSharedFileListInsertItemURL

class FinderSidebar(object):

    def __init__(self):
        self.tuples   = None
        self.names    = None
        self.items    = None
        self.snapshot = None
        self.update()

    def update(self):
        self.tuples   = list()
        self.names    = list()
        self.items    = LSSharedFileListCreate(CoreFoundation.kCFAllocatorDefault, kLSSharedFileListFavoriteItems, None)
        self.snapshot = LSSharedFileListCopySnapshot(self.items, None)
        for item in self.snapshot[0]:
            name = LSSharedFileListItemCopyDisplayName(item)
            path = ""
            if name not in ("AirDrop", "All My Files", "iCloud"):
                path = LSSharedFileListItemResolve(item,0,None,None)[1]
            self.names.append(name.upper())
            self.tuples.append((name, path))

    def synchronize(self):
        CoreFoundation.CFPreferencesSynchronize(CoreFoundation.kCFPreferencesAnyApplication,CoreFoundation.kCFPreferencesCurrentUser,CoreFoundation.kCFPreferencesCurrentHost)
        CoreFoundation.CFPreferencesAppSynchronize("com.apple.sidebarlists")

    def move(self, to_mv, after):
        to_mv = to_mv.upper()
        after = after.upper()

        if to_mv == after:
        	return

        for item in self.snapshot[0]:
            name = LSSharedFileListItemCopyDisplayName(item).upper()
                
            if name == after:
                after = item
            if name == to_mv:
                to_mv = item

        LSSharedFileListItemMove(self.items, to_mv, after)
        self.synchronize()
        self.update()

    def remove(self, to_rm):
        for item in self.snapshot[0]:
            name = LSSharedFileListItemCopyDisplayName(item)
            if to_rm.upper() == name.upper():
                LSSharedFileListItemRemove(self.items, item)

        self.synchronize()
        self.update()

    def add(self, to_add, uri="file://localhost"):
        path = "%s%s" % (uri, to_add)
        url = Cocoa.NSString.alloc().initWithString_(path)
        item = Cocoa.NSURL.alloc().init()
        item = Cocoa.NSURL.URLWithString_(url.stringByAddingPercentEscapesUsingEncoding_(Cocoa.NSASCIIStringEncoding))
        LSSharedFileListInsertItemURL(self.items, kLSSharedFileListItemBeforeFirst, None, None, item, None, None)
        self.synchronize()
        self.update()

    def getItemName(self, n):
        return self.tuples[n][0]


# Example usage

# sidebar = FinderSidebar()
# sidebar.remove("All My Files")
# sidebar.remove("iCloud")
# sidebar.add("/Library")
# sidebar.move("Library", "Applications")
