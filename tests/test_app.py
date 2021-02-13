from adventure.app import Adventure


def test_house_open_mailbox():
    adventure = Adventure()
    assert(adventure.open(['mailbox']) == "You open the mailbox, revealing a small leaflet.")


def test_house_open_mailbox_read_leaflet():
    adventure = Adventure()
    adventure.open(['mailbox'])
    assert(adventure.examine(['leaflet']) == """(Taking the leaflet first)
    ZORK is a game of adventure, danger, and low cunning.  In it you will
explore some of the most amazing territory ever seen by mortal man.  Hardened
adventurers have run screaming from the terrors contained within!

    In ZORK the intrepid explorer delves into the forgotten secrets of a lost
labyrinth deep in the bowels of the earth, searching for vast treasures long
hidden from prying eyes, treasures guarded by fearsome monsters and diabolical
traps!

    No PDP-10 should be without one!

    ZORK was created at the MIT Laboratory for Computer Science, by Tim
Anderson, Marc Blank, Bruce Daniels, and Dave Lebling.  It was inspired by the
ADVENTURE game of Crowther and Woods, and the long tradition of fantasy and
science fiction adventure.  ZORK was originally written in MDL (alias MUDDLE).
The current version was written by Brandon Corfman.""")


def test_house_read_leaflet_check_inventory():
    adventure = Adventure()
    adventure.open(['mailbox'])
    adventure.examine(['leaflet'])
    assert(adventure.list_inventory([]) == 'You are holding a leaflet.')


def test_unknown_verb():
    adventure = Adventure()
    assert(adventure.execute('watch', ['mat']) == "I don't understand how to watch something.")


def test_examine_unknown_object():
    adventure = Adventure()
    assert (adventure.execute('examine', ['printer']) == "I don't see any printer here.")


def test_drop_unknown_object():
    adventure = Adventure()
    assert (adventure.execute('drop', ['printer']) == "I don't see any printer here.")


def test_drop_known_but_not_held_object():
    adventure = Adventure()
    assert (adventure.execute('drop', ['mat']) == "The mat is already here.")


def test_take_unknown_object():
    adventure = Adventure()
    assert (adventure.execute('take', ['printer']) == "I don't see any printer here.")


def test_take_inaccessible_object():
    adventure = Adventure()
    assert (adventure.execute('take', ['leaflet']) == "I don't see any leaflet here.")


def test_take_and_drop_mat():
    adventure = Adventure()
    adventure.take(['mat'])
    assert(adventure.drop(['mat']) == 'Dropped.')
    assert(adventure.list_inventory([]) == 'You are empty handed.')
    assert(any((item.name == 'mat' for item in adventure.current_room.items)))


def test_take_and_drop_mat_and_leaflet():
    adventure = Adventure()
    adventure.take(['mat'])
    adventure.open(['mailbox'])
    adventure.take(['leaflet'])
    assert(adventure.drop(['mat', 'leaflet']) == 'mat: Dropped.\nleaflet: Dropped.')
    assert(adventure.list_inventory([]) == 'You are empty handed.')
    assert(any((item.name == 'mat' or item.name == item.name == 'leaflet' for item in adventure.current_room.items)))


def test_close_already_closed_mailbox():
    adventure = Adventure()
    assert(adventure.close(['mailbox']) == "That's already closed.")


def test_open_opened_mailbox():
    adventure = Adventure()
    adventure.open(['mailbox'])
    assert(adventure.open(['mailbox']) == "The mailbox is already open.")
