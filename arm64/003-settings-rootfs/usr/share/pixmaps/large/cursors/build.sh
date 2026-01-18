#!/bin/bash
#find . -name "*.svg" -exec rsvg -w 96 -h 96 {} ../{}.png \;

xcursorgen default.config default
xcursorgen pointer.config pointer
xcursorgen all-scroll.config all-scroll
xcursorgen alias.config alias
xcursorgen copy.config copy
xcursorgen col-resize.config col-resize
xcursorgen row-resize.config row-resize
xcursorgen help.config help
xcursorgen ne-resize.config ne-resize
xcursorgen se-resize.config se-resize
xcursorgen not-allowed.config not-allowed
xcursorgen progress.config progress
xcursorgen text.config text
xcursorgen wait.config wait

# TODO
ln -s not-allowed no-drop
ln -s all-scroll grabbing
ln -s all-scroll move
ln -s default context-menu
ln -s default cross
ln -s default zoom-in
ln -s default zoom-out


ln -s col-resize      14fef782d02440884392942c11205230
ln -s row-resize      2870a09082c103050810ffdffffe0204

ln -s se-resize     c7088f0f3e6c8088236ef8e1e3e70000
ln -s ne-resize     fcf1c3c7cd4491d801f1e1c78f100000
ln -s row-resize       00008160000006810000408080010102
ln -s col-resize       028006030e0e7ebffc7f7070c0600140

ln -s pointer         e29285e634086352946a0e7090d73106
ln -s move            4498f0e0c1937ffe01fd06f973665830

ln -s alias           640fb0e74195791501fd1ed57b41487f
ln -s copy            6407b0e94181790501fd1e167b474872

ln -s no-drop         03b6e0fcb3499374a867c041f52298f0
ln -s help            d9ce0ab605698f320427677b458ad60b
ln -s wait            0426c94ea35c87780ff01dc239897213
ln -s progress        9116a3ea924ed2162ecab71ba103b17f

ln -s all-scroll      9d800788f1b08800ae810202380a0822 # hand1, not seen by now
ln -s progress        3ecb610c1bf2410f44200f48c40d3599 # left_ptr_watch, not seen by now
ln -s copy            1081e37283d90000800003c07f3ef6bf # copy, not seen by now
ln -s alias           3085a0e285430894940527032f8b26df # link, not seen by now
ln -s move            9081237383d90e509aa00f00170e968f # move, not seen by now


# the Gnome cursor links

ln -s ne-resize     top_right_corner
ln -s ne-resize     bottom_left_corner
ln -s se-resize     top_left_corner
ln -s se-resize     bottom_right_corner
ln -s col-resize       left_side
ln -s col-resize       right_side
ln -s row-resize       top_side
ln -s row-resize       bottom_side
ln -s all-scroll      plus

# since gtk 2.8
ln -s help            dnd-ask
ln -s copy            dnd-copy
ln -s alias           dnd-link
ln -s move            dnd-move
ln -s no-drop         dnd-none


# the Mozilla cursor hashes

ln -s progress        08e8e1c95fe2fc01f976f1e063a24ccd # moz-spinning
ln -s help            5c6cd98b3f3ebcb1f9c7f1c204630408 # mozilla's question_arrow
ln -s all-scroll      5aca4d189052212118709018842178c0 # moz-grab
ln -s grabbing        208530c400c041818281048008011002 # moz-grabbing
ln -s zoom-in         f41c0e382c94c0958e07017e42b00462 # moz-zoom-in
ln -s zoom-out        f41c0e382c97c0938e07017e42800402 # moz-zoom-out
ln -s copy            08ffe1cb5fe6fc01f906f1c063814ccf # moz-copy
ln -s alias           0876e1c15ff2fc01f906f1c363074c0f # moz-alias
ln -s context-menu    08ffe1e65f80fcfdf9fff11263e74c48 # moz-context-menu
# what is moz-cell?

# Mozilla cursor hashes for CSS3 cursor property

ln -s no-drop         03b6e0fcb3499374a867d041f52298f0 # no-drop/not-allowed
#ln -s vertical-text   048008013003cff3c00c801001200000 # vertical-text
ln -s col-resize      043a9f68147c53184671403ffa811cc5 # col-resize
ln -s row-resize      c07385c7190e701020ff7ffffd08103c # row-resize
ln -s ne-resize     50585d75b494802d0151028115016902 # nesw-resize
ln -s se-resize     38c5dff7c7b8962045400281044508d2 # nwse-resize

# Qt4 cursor names
# Reference: <URL:http://doc.trolltech.com/4.6/qcursor.html#a-note-for-x11-users>

ln -s default         left_ptr
#ln -s up-arrow        up_arrow
ln -s crosshair       cross
ln -s text            ibeam
ln -s wait            wait
ln -s progress        left_ptr_watch
ln -s not-allowed     forbidden
ln -s pointer         pointing_hand
ln -s help            whats_this
ln -s row-resize       size_ver
ln -s col-resize       size_hor
ln -s ne-resize     size_bdiag
ln -s se-resize     size_fdiag
ln -s all-scroll      size_all
ln -s row-resize      split_v
ln -s col-resize      split_h
ln -s all-scroll      openhand
ln -s grabbing        closedhand




