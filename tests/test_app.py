from adventure.app import Adventure


def test_house_open_mailbox():
    adventure = Adventure()
    assert adventure.open(['mailbox']) == "You open the mailbox, revealing a small leaflet."


def test_house_open_mailbox_read_leaflet():
    adv = Adventure()
    adv.open(['mailbox'])
    assert (adv.examine(['leaflet']) == '(Taking the leaflet first)\n'
                                        '    ZORK is a game of adventure, danger, and low cunning.  In it you will '
                                        'explore some of the most amazing territory ever seen by mortal man.  Hardened '
                                        'adventurers have run screaming from the terrors contained within!\n\n'
                                        '    In ZORK the intrepid explorer delves into the forgotten secrets of a lost '
                                        'labyrinth deep in the bowels of the earth, searching for vast treasures long '
                                        'hidden from prying eyes, treasures guarded by fearsome monsters and diabolical '
                                        'traps!\n\n'
                                        '    No PDP-10 should be without one!\n\n'
                                        '    ZORK was created at the MIT Laboratory for Computer Science, by Tim '
                                        'Anderson, Marc Blank, Bruce Daniels, and Dave Lebling.  It was inspired by the '
                                        'ADVENTURE game of Crowther and Woods, and the long tradition of fantasy and '
                                        'science fiction adventure.  ZORK was originally written in MDL (alias MUDDLE). '
                                        'The current version was written by Brandon Corfman.')


def test_house_read_leaflet_check_inventory():
    adventure = Adventure()
    adventure.open(['mailbox'])
    adventure.examine(['leaflet'])
    assert adventure.list_inventory([]) == 'You are holding a small leaflet.'


def test_unknown_verb():
    adventure = Adventure()
    assert adventure.execute(['watch', 'mat']) == "I don't understand how to watch something."


def test_examine_unknown_object():
    adventure = Adventure()
    assert adventure.execute(['examine', 'printer']) == "I don't see any printer here."


def test_drop_unknown_object():
    adventure = Adventure()
    assert adventure.execute(['drop', 'printer']) == "I don't see any printer here."


def test_drop_known_but_not_held_object():
    adventure = Adventure()
    assert adventure.execute(['drop', 'mat']) == "The mat is already here."


def test_take_unknown_object():
    adventure = Adventure()
    assert adventure.execute(['take', 'printer']) == "I don't see any printer here."


def test_take_inaccessible_object():
    adventure = Adventure()
    assert adventure.execute(['take', 'leaflet']) == "I don't see any leaflet here."


def test_take_and_drop_mat():
    adventure = Adventure()
    adventure.take(['mat'])
    assert adventure.drop(['mat']) == 'Dropped.'
    assert adventure.list_inventory([]) == 'You are empty handed.'
    assert any((item.name == 'mat' for item in adventure.current_room.items))


def test_take_and_drop_mat_and_leaflet():
    adventure = Adventure()
    adventure.take(['mat'])
    adventure.open(['mailbox'])
    adventure.take(['leaflet'])
    assert adventure.drop(['mat', 'leaflet']) == 'mat: Dropped.\nleaflet: Dropped.'
    assert adventure.list_inventory([]) == 'You are empty handed.'
    assert any((item.name == 'mat' or item.name == item.name == 'leaflet' for item in adventure.current_room.items))


def test_open_mailbox_and_look():
    adventure = Adventure()
    adventure.open(['mailbox'])
    assert adventure.look([]) == """**West of House**
This is an open field west of a white house, with a boarded front door.
There is a small mailbox here.
The mailbox contains:
    A small leaflet.
A rubber mat saying 'Welcome to Zork!' lies by the door."""


def test_close_already_closed_mailbox():
    adventure = Adventure()
    assert adventure.close(['mailbox']) == "That's already closed."


def test_open_opened_mailbox():
    adventure = Adventure()
    adventure.open(['mailbox'])
    assert adventure.open(['mailbox']) == "The mailbox is already open."


def test_go_north_of_house():
    adventure = Adventure()
    assert adventure.go_north([]) == """**North of House**
You are facing the north side of a white house.  There is no door here, and all the windows are barred."""
    assert adventure.current_room.title == "North of House"


def test_go_north_then_west_of_house():
    adventure = Adventure()
    adventure.go_north([])
    adventure.go_west([])
    assert adventure.current_room.title == "West of House"


def test_take_mat_go_north_then_drop_mat():
    adventure = Adventure()
    adventure.take(['mat'])
    adventure.go_north([])
    adventure.drop(['mat'])
    assert adventure.current_room.description == """**North of House**
You are facing the north side of a white house.  There is no door here, and all the windows are barred.
There is a welcome mat here."""


def test_take_mat_and_leaflet():
    adventure = Adventure()
    adventure.open(['mailbox'])
    assert adventure.take(['mat', 'leaflet']) == """mat: Taken.
leaflet: Taken."""


def test_take_leaflet_and_mat():
    adventure = Adventure()
    adventure.open(['mailbox'])
    assert adventure.take(['leaflet', 'mat']) == """leaflet: Taken.
mat: Taken."""


def test_take_and_drop_leaflet_and_mat_then_look():
    adventure = Adventure()
    adventure.open(['mailbox'])
    adventure.take(['leaflet', 'mat'])
    adventure.drop(['mat', 'leaflet'])
    assert adventure.look([]) == """**West of House**
This is an open field west of a white house, with a boarded front door.
There is a small mailbox, a welcome mat, and a small leaflet here."""


def test_inventory_after_taking_mat_and_leaflet():
    adventure = Adventure()
    adventure.open(['mailbox'])
    adventure.take(['mat', 'leaflet'])
    assert adventure.list_inventory([]) == """You are holding a welcome mat and a small leaflet."""


def test_empty_mailbox():
    adventure = Adventure()
    adventure.open(['mailbox'])
    adventure.take(['leaflet'])
    adventure.close(['mailbox'])
    assert adventure.open(['mailbox']) == """You open the mailbox."""
