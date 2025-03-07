from platform import mac_ver

from Cocoa import NSURL
from CoreFoundation import CFPreferencesAppSynchronize
from CoreFoundation import CFURLCreateWithString
from CoreFoundation import kCFAllocatorDefault
from Foundation import NSBundle
from Foundation import NSDictionary
from LaunchServices import kLSSharedFileListFavoriteItems
from objc import loadBundleFunctions, initFrameworkWrapper, pathForFramework
from CoreServices import LSSharedFileListCreate, kLSSharedFileListFavoriteItems, LSSharedFileListInsertItemURL

os_version = int(mac_ver()[0].split('.')[1])
if os_version > 10:
    SFL_bundle = NSBundle.bundleWithIdentifier_(
        'com.apple.coreservices.SharedFileList'
    )
    functions = [
        ('LSSharedFileListCreate',              b'^{OpaqueLSSharedFileListRef=}^{__CFAllocator=}^{__CFString=}@'),
        ('LSSharedFileListCopySnapshot',        b'^{__CFArray=}^{OpaqueLSSharedFileListRef=}o^I'),
        ('LSSharedFileListItemCopyDisplayName', b'^{__CFString=}^{OpaqueLSSharedFileListItemRef=}'),
        ('LSSharedFileListItemResolve',         b'i^{OpaqueLSSharedFileListItemRef=}Io^^{__CFURL=}o^{FSRef=[80C]}'),
        ('LSSharedFileListItemMove',            b'i^{OpaqueLSSharedFileListRef=}^{OpaqueLSSharedFileListItemRef=}^{OpaqueLSSharedFileListItemRef=}'),
        ('LSSharedFileListItemRemove',          b'i^{OpaqueLSSharedFileListRef=}^{OpaqueLSSharedFileListItemRef=}'),
        ('LSSharedFileListRemoveAllItems',      b'i^{OpaqueLSSharedFileListRef=}'),
        ('LSSharedFileListInsertItemURL',       b'^{OpaqueLSSharedFileListItemRef=}^{OpaqueLSSharedFileListRef=}^{OpaqueLSSharedFileListItemRef=}^{__CFString=}^{OpaqueIconRef=}^{__CFURL=}^{__CFDictionary=}^{__CFArray=}'),
        ('kLSSharedFileListItemBeforeFirst',    b'^{OpaqueLSSharedFileListItemRef=}')
    ]
    loadBundleFunctions(SFL_bundle, globals(), functions)
    from LaunchServices import LSSharedFileListItemCopyResolvedURL
else:
    from LaunchServices import kLSSharedFileListItemBeforeFirst
    from LaunchServices import LSSharedFileListCreate
    from LaunchServices import LSSharedFileListCopySnapshot
    from LaunchServices import LSSharedFileListItemCopyDisplayName
    from LaunchServices import LSSharedFileListItemResolve
    from LaunchServices import LSSharedFileListItemMove
    from LaunchServices import LSSharedFileListItemRemove
    from LaunchServices import LSSharedFileListRemoveAllItems
    from LaunchServices import LSSharedFileListInsertItemURL


# Shoutout to Mike Lynn for the mount_share function below, allowing for the
# scripting of mounting network shares. See his blog post for more details:
# http://michaellynn.github.io/2015/08/08/learn-you-a-better-pyobjc-bridgesupport-signature/
class attrdict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


NetFS = attrdict()
# Can cheat and provide 'None' for the identifier, it'll just use
# frameworkPath instead scan_classes=False means only add the
# contents of this Framework
NetFS_bundle = initFrameworkWrapper(
    'NetFS', frameworkIdentifier=None,
    frameworkPath=pathForFramework('NetFS.framework'), globals=NetFS,
    scan_classes=False
)


def mount_share(share_path):
    # Mounts a share at /Volumes, returns the mount point or raises an error
    sh_url = CFURLCreateWithString(None, share_path, None)
    # Set UI to reduced interaction
    open_options = {NetFS.kNAUIOptionKey: NetFS.kNAUIOptionNoUI}
    # Allow mounting sub-directories of root shares
    mount_options = {NetFS.kNetFSAllowSubMountsKey: True}
    # Mount!
    result, output = NetFS.NetFSMountURLSync(
        sh_url, None, None, None, open_options, mount_options, None
    )
    # Check if it worked
    if result != 0:
        raise Exception('Error mounting url "%s": %s' % (share_path, output))
    # Return the mount path
    return str(output[0])


# https://developer.apple.com/library/mac/documentation/Cocoa/Conceptual/ObjCRuntimeGuide/Articles/ocrtTypeEncodings.html
# Fix NetFSMountURLSync signature
del NetFS['NetFSMountURLSync']
loadBundleFunctions(
    NetFS_bundle, NetFS, [('NetFSMountURLSync', b'i@@@@@@o^@')]
)


class FinderSidebar:
    """
    Finder Sidebar instance for modifying favorites entries for logged in user.

    Attributes:
        sflRef (LSSharedFileList): Reference to sfl object containing Finder
                                   favorites data.
        snapshot (tuple): Snapshot of Finder sfl object containing readable
                          entries for each favorite.
        favorites (dict): Dictionary containing name: uri pairs for
                          each favorite.
    """

    def __init__(self):
        self.sflRef = LSSharedFileListCreate(
            kCFAllocatorDefault, kLSSharedFileListFavoriteItems, None
        )
        self.snapshot = LSSharedFileListCopySnapshot(self.sflRef, None)
        self.favorites = dict()
        self.update()

    def update(self):
        """
        Updates snapshot and favorites attributes.

        """
        self.favorites = dict()
        self.snapshot = LSSharedFileListCopySnapshot(self.sflRef, None)
        for item in self.snapshot[0]:
            name = LSSharedFileListItemCopyDisplayName(item)
            path = ""
            if name not in ["AirDrop", "All My Files", "iCloud"]:
                path = LSSharedFileListItemResolve(item, 0, None, None)[1]
            self.favorites[name] = path

    @staticmethod
    def synchronize():
        """
        Synchronizes CF prefs for sidebarlists identifier.

        """
        CFPreferencesAppSynchronize("com.apple.sidebarlists")

    def move(self, to_mv, after):
        """
        Moves sidebar list item to position immediately other sidebar
        list item.

        Args:
            to_mv (str): Name of sidebar list item to move.
            after (str): Name of sidebar list item to move "to_mv" after.

        """
        if to_mv not in self.favorites.keys() or \
                after not in self.favorites.keys() or to_mv == after:
            return

        for item in self.snapshot[0]:
            name = LSSharedFileListItemCopyDisplayName(item)

            if name == after:
                after = item
            elif name == to_mv:
                to_mv = item

        LSSharedFileListItemMove(self.sflRef, to_mv, after)
        self.synchronize()
        self.update()

    def remove(self, to_rm):
        """
        Removes sidebar list item.

        Args:
            to_rm (str): Name of sidebar list item to remove.

        """
        for item in self.snapshot[0]:
            name = LSSharedFileListItemCopyDisplayName(item)
            if to_rm.upper() == name.upper():
                LSSharedFileListItemRemove(self.sflRef, item)
        self.synchronize()
        self.update()

    def remove_all(self):
        """
        Removes all sidebar list items.

        """
        LSSharedFileListRemoveAllItems(self.sflRef)
        self.synchronize()
        self.update()

    def remove_by_path(self, path):
        """
        Removes sidebar list item.

        Args:
            path (str): Path of sidebar list item to remove.

        """
        comparison_path = f'file://{path}/'.upper()
        for item in self.snapshot[0]:
            sidebar_item = LSSharedFileListItemResolve(item, 0, None, None)
            if comparison_path == str(sidebar_item[1]).upper():
                LSSharedFileListItemRemove(self.sflRef, item)
        self.synchronize()
        self.update()
        

    def add(self, to_add, uri="file://localhost", icon_path=None):
        """
        Append item to sidebar list items.

        Args:
            :param to_add: Path to item to append to sidebar list.

        Keyword Args:
            :param uri: URI of server where item resides if not on localhost.
            :param icon_path: Path to .icns file to be used as an icon.

        """
        if uri.startswith("afp") or uri.startswith("smb"):
            path = "%s%s" % (uri, to_add)
            to_add = mount_share(path)
        item = NSURL.alloc().initFileURLWithPath_(to_add)
        
        icon = None
        if icon_path:
            icon_url = NSURL.fileURLWithPath_(icon_path)
            icon = NSDictionary.dictionaryWithObject_forKey_(icon_url, "icon")

        LSSharedFileListInsertItemURL(
            self.sflRef, kLSSharedFileListItemBeforeFirst,
            None, None, item, icon, None
        )
        self.synchronize()
        self.update()

    def get_index_from_name(self, name):
        """
        Gets index of sidebar list item identified by name.

        Args:
            name (str): Display name to identfy sidebar list item by.

        Returns:
            Index of sidebar list item identified by name

        """
        for index, item in enumerate(self.snapshot[0]):
            found_name = LSSharedFileListItemCopyDisplayName(item)
            if name == found_name:
                return index

    def get_name_from_index(self, index):
        """
        Gets name of sidebar list item identified by index.

        Args:
            index (str): Index to identify sidebar list item by.

        Returns:
            Name of sidebar list item identified by index.

        """
        if index > len(self.snapshot[0]):
            index = -1
        return LSSharedFileListItemCopyDisplayName(self.snapshot[0][index])
