import libtcodpy as libtcod

#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

#size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 45

#map constants
WALL_CONST = '#'
FLOOR_CONST = '.'
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

LIMIT_FPS = 20  #20 frames-per-second maximum

#create random number generator
rng = libtcod.random_new_from_seed(1, algo=libtcod.RNG_MT)

color_dark_wall = libtcod.lightest_grey
color_dark_ground = libtcod.lightest_grey

class Rect:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)

    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

def create_h_tunnel(x1, x2, y, dungeon_map):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        dungeon_map[x][y].blocked = False
        dungeon_map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x, dungeon_map):
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        dungeon_map[x][y].blocked = False
        dungeon_map[x][y].block_sight = False

class GenshiObject:
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, x, y, char, color, dungeon_map):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.dungeon_map = dungeon_map

    def move(self, dx, dy):
        #move by the given amount, if the destination is not blocked
        if not self.dungeon_map[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy

    def draw(self):
        #set the color and then draw the character that represents this object at its position
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

def create_room(room, dungeon_map):
    #go through the tiles in the rectangle and make them passable
    for x in range(room.x1, room.x2 + 1):
        for y in range(room.y1, room.y2 + 1):
            dungeon_map[x][y].blocked = False
            dungeon_map[x][y].block_sight = False

def make_dungeon_map():
    #fill dungeon_map with "blocked" tiles
    dungeon_map = [[ Tile(True)
        for _ in range(MAP_HEIGHT) ]
            for _ in range(MAP_WIDTH) ]

    #create two rooms
    room1 = Rect(20, 15, 10, 15)
    room2 = Rect(50, 15, 10, 15)
    create_room(room1, dungeon_map)
    create_room(room2, dungeon_map)
    create_h_tunnel(25, 55, 23, dungeon_map)
    return dungeon_map

def render_all():
    global color_light_wall
    global color_light_ground
    map_rng = libtcod.random_new_from_seed(1, algo=libtcod.RNG_MT)

    #go through all tiles, and set their background color
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall = dungeon_map[x][y].block_sight
            if wall:
                libtcod.console_put_char_ex(con, x, y,  WALL_CONST, color_dark_wall, libtcod.light_grey * libtcod.random_get_float(map_rng, 0.7, 0.8) )
            else:
                libtcod.console_put_char_ex(con, x, y, FLOOR_CONST, color_dark_ground, libtcod.dark_grey * libtcod.random_get_float(map_rng, 0.2, 0.5) )

    #draw all objects in the list
    for obj in objects:
        obj.draw()

    #blit the contents of "con" to the root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

def handle_keys():
    #key = libtcod.console_check_for_keypress()  #real-time
    key = libtcod.console_wait_for_keypress(True)  #turn-based

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return True  #exit game

    #movement keys
    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        player.move(0, -1)

    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        player.move(0, 1)

    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        player.move(-1, 0)

    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        player.move(1, 0)


#############################################
# Initialization & Main Loop
#############################################

libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

#generate map (at this point it's not drawn to the screen)
dungeon_map = make_dungeon_map()

#create object representing the player
player = GenshiObject(25, 23, '@', libtcod.white, dungeon_map)

#create an NPC
npc = GenshiObject(SCREEN_WIDTH/2 - 5, SCREEN_HEIGHT/2, 'k', libtcod.yellow, dungeon_map)

#the list of objects with those two
objects = [npc, player]


while not libtcod.console_is_window_closed():

    #render the screen
    render_all()

    libtcod.console_flush()

    #erase all objects at their old locations, before they move
    for obj in objects:
        obj.clear()

    #handle keys and exit game if needed
    ex = handle_keys()
    if ex:
        break