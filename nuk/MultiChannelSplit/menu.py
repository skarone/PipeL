import nuke
import nuk.MultiChannelSplit as MultiChannelSplit

nuke.menu("Nuke").addCommand('Scripts/MultiChannelSplit', 'MultiChannelSplit.MultiChannelSplit()', 'alt+m')
