from adventure.westofhouse import Leaflet, Mailbox, WelcomeMat, WestOfHouse, BoardedDoor


def test_leaflet():
    leaflet = Leaflet()
    assert(leaflet.contents == '    ZORK is a game of adventure, danger, and low cunning.  In it you will ' 
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


def test_examine_closed_mailbox():
    mailbox = Mailbox()
    assert(mailbox.examine() == 'I see nothing special about the mailbox.')


def test_open_mat():
    mat = WelcomeMat()
    assert(mat.open() == "That's not something you can open.")


def test_examine_mat():
    mat = WelcomeMat()
    assert (mat.examine() == "Welcome to Zork!")


def test_open_door():
    door = BoardedDoor()
    assert(door.open() == "The door cannot be opened.")


def test_house_description():
    h = WestOfHouse()
    assert(h.description == """**West of House**
This is an open field west of a white house, with a boarded front door.
There is a small mailbox here.
A rubber mat saying 'Welcome to Zork!' lies by the door.""")


def test_house_list_items_at_start():
    h = WestOfHouse()
    assert (h.list_items() == """There is a small mailbox here.
A rubber mat saying 'Welcome to Zork!' lies by the door.""")
