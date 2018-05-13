import curses, time, random, math
from curses import wrapper


class Game:
    def __init__(self,screen):
        curses.curs_set(0)
        curses.start_color()

        self.screen = screen
        self.width = curses.COLS - 1
        self.height = curses.LINES - 1
        self.bullets = []
        self.enemies = []
        self.explosions = []
        self.hero = Hero()
        self.level = 1

        self.screen.nodelay(True)
        self.screen.clear()

        self.play()

    def play(self):
        while 1:
            if not self.update():
                break
            time.sleep(0.05)

    def update(self):
        garbage_collection = {
            'b': [],
            'e': [],
            'ex': []
        }
        c = self.screen.getch()
        curses.flushinp()

        #spawn enemies
        if len(self.enemies) < self.level * 3 and random.randint(0,30) == 2:
            self.enemies.append(Enemy())

        #handle key input
        if c == curses.KEY_RIGHT:
            self.hero.movement = 1
        elif c == curses.KEY_LEFT:
            self.hero.movement = -1
        elif c == curses.KEY_UP or c == 32:
            shot = self.hero.fire(len(self.bullets))
            if shot:
                self.bullets.append(shot)
        elif c == curses.KEY_DOWN:
            self.hero.movement = 0
        elif c == 113 or c == 81:
            return False

        #clear the screen and redraw the bounding box
        self.screen.erase()
        self.screen.box()

        #handle player movement
        self.hero.move()


        # move bullets, check bullet collision, add explosions, draw bullets
        for i, b in enumerate(self.bullets):
            loc = b.move()
            if loc > 1 and loc < self.height - 1:
                b.yx[0] = loc
                for ei, e in enumerate(self.enemies):
                    if self.check_col(b,e):
                        e.health -= 1
                        if e.yx[0] > 2:
                            e.yx[0] -= 0.5
                        garbage_collection['b'].append(i)
                        if e.health <= 0:
                            self.explosions.append(Explosion(b.yx,self.screen))
                            garbage_collection['e'].append(ei)
                            continue
                self.screen.addch(int(b.yx[0]),int(b.yx[1]),b.icon)
            else:
                garbage_collection['b'].append(i)

        #move enemies, fire, draw enemies
        for i, e in enumerate(self.enemies):
            loc = e.move()
            if int(loc[0]) < curses.LINES - 2:
                e.yx = loc
                e.draw(self.screen)
                if abs(e.yx[1] - self.hero.yx[1]) < 15:
                    shot = e.fire()
                    if shot:
                        self.bullets.append(shot)
            else:
                garbage_collection['e'].append(i)

        #update explosions (includes draw)
        for i, ex in enumerate(self.explosions):
            ex.update()
            if ex.count >= 10:
                garbage_collection['ex'].append(i)

        # draw player
        self.screen.addch(int(self.hero.yx[0]),int(self.hero.yx[1]),self.hero.icon)

        self.screen.refresh()

        # Remove dead items from lists/garbage collect
        for i, trash in enumerate(garbage_collection['b']):
            del self.bullets[trash - i]

        for i, trash in enumerate(garbage_collection['e']):
            del self.enemies[trash - i]

        for i, trash in enumerate(garbage_collection['ex']):
            del self.explosions[trash - i]

        return True

    def check_col(self,obj1, obj2):
        if obj1.yx[1] > obj2.yx[1] + obj2.width or obj1.yx[0] > obj2.yx[0] + obj2.height or obj2.yx[1] > obj1.yx[1] + obj1.width or obj2.yx[0] > obj1.yx[0] + obj1.width:
            return False
        else:
            return True




class Hero:
    def __init__(self):
        self.yx = [curses.LINES - 4, curses.COLS / 2]
        self.icon = '^'
        self.speed = 1.2
        self.movement = 0
        self.width = 1
        self.height = 1

    def move(self):
        new_location = self.yx[1] + self.movement * self.speed
        if new_location >= 2 and new_location <= curses.COLS - 3:
            self.yx[1] = new_location
        elif new_location < 2:
            self.yx[1] = 2
            self.movement *= -1
        elif new_location > curses.COLS - 3:
            self.yx[1] = curses.COLS - 3
            self.movement *= -1


    def fire(self,count):
        if count < 6:
            return Bullet([self.yx[0]-1,self.yx[1]],-1,'|')
        return False


class Bullet:
    def __init__(self,src,dir,icon):
        self.yx = src #list
        self.icon = icon
        self.speed = 2.23
        self.dir = dir
        self.width = 1
        self.height = 1

    def move(self):
        new_location = self.yx[0] + self.speed * self.dir
        return new_location





class Enemy:

    def __init__(self):
        self.enemy_options = [
            {
                'yx': [1,random.randint(3,curses.COLS - 7)],
                'icon': ['|_|_|','! o !'],
                'speed': 0.2,
                'max_fire_count': 2,
                'width': 5,
                'height': 2,
                'bullet_icon': '=',
                'bullet_pattern': 1,
                'movement_pattern': 1,
                'movement_max': random.randint(20,70),
                'health': 4,
                'movement_dir': random.randint(1,5)
            },
            {
                'yx': [1,random.randint(3,curses.COLS - 7)],
                'icon': ['|-o-|'],
                'speed': 1,
                'max_fire_count': 3,
                'width': 5,
                'height': 1,
                'bullet_icon': ':',
                'bullet_pattern': 2,
                'movement_pattern': 2,
                'movement_max': random.randint(20,70),
                'health': 1,
                'movement_dir':[-1,1][random.randint(0,1)]
            },
            {
                'yx': [1,random.randint(3,curses.COLS - 7)],
                'icon': ['/-o-\\'],
                'speed': 0.25,
                'max_fire_count': 2,
                'width': 5,
                'height': 1,
                'bullet_icon': ':',
                'bullet_pattern': 3,
                'movement_pattern': 3,
                'movement_max': random.randint(20,70),
                'health': 2,
                'movement_dir':[-1,1][random.randint(0,1)]
            },
            {
                'yx': [1,random.randint(3,curses.COLS - 9)],
                'icon': ['||_|_||','   V   '],
                'speed': 0.1,
                'max_fire_count': 7,
                'width': 7,
                'height': 2,
                'bullet_icon': 'I',
                'bullet_pattern': 4,
                'movement_pattern': 4,
                'movement_max': random.randint(20,70),
                'health': 6,
                'movement_dir':[-1,1][random.randint(0,1)]
            }
        ]
        self.fire_count = 0
        self.fighter_model = random.randint(0,len(self.enemy_options)-1)
        self.yx = self.enemy_options[self.fighter_model]['yx']
        self.icon = self.enemy_options[self.fighter_model]['icon']
        self.speed = self.enemy_options[self.fighter_model]['speed']
        self.max_fire_count = self.enemy_options[self.fighter_model]['max_fire_count']
        self.width = self.enemy_options[self.fighter_model]['width']
        self.height = self.enemy_options[self.fighter_model]['height']
        self.fire_src = [self.yx[0] + self.height,self,self.yx[1] + (self.width - 1) / 2],
        self.bullet_icon = self.enemy_options[self.fighter_model]['bullet_icon']
        self.bullet_pattern = self.enemy_options[self.fighter_model]['bullet_pattern']
        self.movement_pattern = self.enemy_options[self.fighter_model]['movement_pattern']
        self.movement_ident = 1
        self.movement_dir = self.enemy_options[self.fighter_model]['movement_dir']
        self.movement_max = self.enemy_options[self.fighter_model]['movement_max']
        self.health = self.enemy_options[self.fighter_model]['health']

    def move(self):
        if self.movement_pattern == 1:
            self.movement_ident += 1
            new_location = [
                self.yx[0] + self.speed / random.randint(1,2),
                self.yx[1] + 1 * math.cos((math.pi * 2) * self.movement_ident / 30)
            ]

            if new_location[1] < 3:
                new_location[1] = 3
            elif new_location[1] > curses.COLS - self.width - 3:
                new_location[1] = curses.COLS - self.width - 3

        elif self.movement_pattern == 2:
            self.movement_ident += 1
            new_location = [self.yx[0] + self.speed, self.yx[1] + (self.speed * self.movement_dir)]
            if new_location[1] < 3:
                new_location[1] = 3
                self.movement_dir = 1
            elif new_location[1] > curses.COLS - self.width - 3:
                new_location[1] = curses.COLS - self.width - 3
                self.movement_dir = -1

            if self.movement_ident >= self.movement_max:
                self.movement_dir *= -1
                self.movement_ident = 0
        else:
            new_location = [self.yx[0] + self.speed,self.yx[1]]

        return new_location

    def fire(self):
        if self.fire_count < self.max_fire_count and random.randint(0,30) == 5:
            self.fire_count += 1
            return Bullet([self.yx[0]+self.height,self.yx[1]+(self.width-1)/2],1,self.bullet_icon)
        return False

    def draw(self,screen):
        for i, x in enumerate(self.icon):
            screen.addstr(int(self.yx[0])+i,int(self.yx[1]),self.icon[i])


class Explosion:
    def __init__(self, loc, screen):
        self.yx = loc
        self.screen = screen
        self.count = 0
        self.icon = '*'
        self.icon2 = '+'
        self.icon3 = ','

    def update(self):
        self.count += 1
        if self.count < 3:
            self.screen.addch(int(self.yx[0]),int(self.yx[1]),self.icon)
        elif self.count < 6:
            if self.yx[0] - 1 > 2:
                self.screen.addch(int(self.yx[0] - 1),int(self.yx[1]),self.icon2)
            if self.yx[0] + 1 < curses.LINES - 3:
                self.screen.addch(int(self.yx[0] + 1),int(self.yx[1]),self.icon2)
            if self.yx[1] - 1 > 2:
                self.screen.addch(int(self.yx[0]),int(self.yx[1] - 1),self.icon2)
            if self.yx[1] + 1 < curses.COLS - 2:
                self.screen.addch(int(self.yx[0]),int(self.yx[1] + 1),self.icon2)
        elif self.count < 10:
            if self.yx[0] - 2 > 2:
                self.screen.addch(int(self.yx[0] - 2),int(self.yx[1]),self.icon3)
            if self.yx[0] - 1 > 2 and self.yx[1] - 1 > 2:
                self.screen.addch(int(self.yx[0] - 2),int(self.yx[1]),self.icon3)
            if self.yx[0] + 2 < curses.LINES - 3:
                self.screen.addch(int(self.yx[0] + 2),int(self.yx[1]),self.icon3)
            if self.yx[1] - 2 > 2:
                self.screen.addch(int(self.yx[0]),int(self.yx[1] - 2),self.icon3)
            if self.yx[0] + 1 < curses.LINES - 3 and self.yx[1] + 1 < curses.COLS - 2:
                self.screen.addch(int(self.yx[0] - 2),int(self.yx[1]),self.icon3)
            if self.yx[1] + 2 < curses.COLS - 2:
                self.screen.addch(int(self.yx[0]),int(self.yx[1] + 2),self.icon3)




if __name__ == "__main__":
    wrapper(Game)
