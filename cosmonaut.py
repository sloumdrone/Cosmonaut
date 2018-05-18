import curses, time, random, math
from curses import wrapper
from os import system


class Game:
    def __init__(self,screen):
        # curses.resizeterm(40,120)
        curses.curs_set(0)
        curses.start_color()
        curses.init_color(0, 0, 0, 0)
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)

        self.screen = screen
        self.width = curses.COLS - 1
        self.height = curses.LINES - 1
        self.bullets = []
        self.enemies = []
        self.explosions = []
        self.hero = Hero()
        self.score = 0
        self.level = 1
        self.enemy_count = 0
        self.status = 'menu'

        self.cover_animation = [1,2,3,4,5,6]

        self.screen.nodelay(True)
        self.screen.clear()

        self.play()

    def play(self):
        while 1:
            if self.status == 'menu':
                if not self.menu():
                    break
            elif self.status == 'death':
                if not self.death_screen():
                    break
            else:
                if not self.update():
                    break

            time.sleep(0.05)

    def menu(self):
        c = self.screen.getch()
        curses.flushinp()

        if c == 80 or c == 112:
            self.status = 'play'
        elif c == 113 or c == 81:
            return False

        word_x = self.width / 2 - 41
        word_x2 = self.width / 2 - 18

        if word_x < 1:
            word_x = 1

        #clear the screen and redraw the bounding box
        self.screen.erase()
        self.screen.box()

        if self.width > 90:
            self.cover_animation = [self.cover_animation.pop()] + self.cover_animation

            self.screen.addstr(5,word_x,' _______  _______  _______  __   __  _______  __    _  _______  __   __  _______ ',curses.color_pair(self.cover_animation[0]))
            self.screen.addstr(6,word_x,'|       ||       ||       ||  |_|  ||       ||  |  | ||   _   ||  | |  ||       |',curses.color_pair(self.cover_animation[1]))
            self.screen.addstr(7,word_x,'|       ||   _   ||  _____||       ||   _   ||   | | ||  | |  ||  | |  ||_     _|',curses.color_pair(self.cover_animation[2]))
            self.screen.addstr(8,word_x,'|      _||  | |  || |_____ |       ||  | |  ||    \| ||  |_|  ||  | |  |  |   |  ',curses.color_pair(self.cover_animation[3]))
            self.screen.addstr(9,word_x,'|     |  |  |_|  ||_____  ||       ||  |_|  || |\    ||       ||  |_|  |  |   |  ',curses.color_pair(self.cover_animation[4]))
            self.screen.addstr(10,word_x,'|     |_ |       | _____| || ||_|| ||       || | |   ||   _   ||       |  |   |  ',curses.color_pair(self.cover_animation[5]))
            self.screen.addstr(11,word_x,'|_______||_______||_______||_|   |_||_______||_|  |__||__| |__||_______|  |___|  ',curses.color_pair(self.cover_animation[0]))
        else:
            self.screen.addstr(8,word_x2,".-. .-. .-. .  . .-. . . .-. . . .-. ",curses.color_pair(1))
            self.screen.addstr(9,word_x2,"|   | | `-. |\/| | | |\| |-| | |  |  ",curses.color_pair(2))
            self.screen.addstr(10,word_x2,"`-' `-' `-' '  ` `-' ' ` ` ' `-'  '  ",curses.color_pair(3))


        message1 = '(P)lay         (Q)uit'
        self.screen.addstr(self.height - 5,self.width/2 - len(message1)/2,message1,curses.color_pair(2))
        self.screen.refresh()
        return True


    def death_screen(self):
        c = self.screen.getch()
        curses.flushinp()

        if c == 80 or c == 112:
            self.hero = Hero()
            self.bullets = []
            self.enemies = []
            self.explosions = []
            self.level = 1
            self.status = 'play'
            self.score = 0
        elif c == 113 or c == 81:
            return False

        word_x = self.width / 2 - 41

        if word_x < 1:
            word_x = 1

        #clear the screen and redraw the bounding box
        self.screen.erase()
        self.screen.box()
        message1 = 'Thank you for playing Cosmonaut!'
        self.screen.addstr(self.height - int(self.height/4 * 3),self.width/2 - len(message1)/2,message1)
        message2 = 'Your score was: ' + str(self.score)
        self.screen.addstr(self.height - int(self.height/2),self.width/2 - len(message2)/2,message2)
        message3 = '(P)lay Again         (Q)uit'
        self.screen.addstr(self.height - int(self.height/4),self.width/2 - len(message3)/2,message3)
        self.screen.refresh()
        return True


    def update(self):
        garbage_collection = {
            'b': [],
            'e': [],
            'ex': []
        }
        c = self.screen.getch()
        curses.flushinp()

        #spawn enemies
        if len(self.enemies) < self.level * 2 and random.randint(0,30) == 2:
            self.enemies.append(Enemy())
            self.enemy_count += 1
            if self.enemy_count == self.level * 10:
                self.level += 1

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
                if self.check_col(b,self.hero):
                    self.hero.health -= 1 # replace 1 with the weapon damage
                    if self.hero.health <= 0:
                        self.status = 'death'
                    garbage_collection['b'].append(i)
                    continue

                for ei, e in enumerate(self.enemies):
                    if self.check_col(e,self.hero):
                        self.status = 'death'
                    if self.check_col(b,e):
                        e.health -= 1
                        if e.yx[0] > 2:
                            e.yx[0] -= 0.5
                        garbage_collection['b'].append(i)
                        if e.health <= 0:
                            self.score += e.value
                            self.explosions.append(Explosion(b.yx,self.screen))
                            garbage_collection['e'].append(ei)
                            continue
                self.screen.addch(int(b.yx[0]),int(b.yx[1]),b.icon,curses.A_BOLD)
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
        self.screen.addstr(int(self.hero.yx[0]),int(self.hero.yx[1]),self.hero.icon,curses.A_BOLD)


        # Add health, title/level, and score
        health_display = 'HEALTH: '+'#'*self.hero.health
        score_add_zeros = 6 - len(str(self.score))
        score_string = 'SCORE: ' + '0' * score_add_zeros + str(self.score)
        title_string = 'COSMONAUT (Level ' + str(self.level) + ')'
        if self.width > len(health_display) + 6:
            self.screen.addstr(self.height-1,2,health_display,curses.color_pair(1))
        if self.width > len(health_display) + len(score_string) + 10:
            self.screen.addstr(self.height-1, self.width - len(score_string) - 2,score_string,curses.color_pair(2))
        if self.width > len(health_display) + len(score_string) + len(title_string) + 15:
            self.screen.addstr(self.height-1,self.width/2 - len(title_string)/2,title_string,curses.color_pair(3))


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
        if (int(obj1.yx[1]) <= int(obj2.yx[1] + obj2.width) and
            int(obj1.yx[0]) <= int(obj2.yx[0] + obj2.height + 1) and
            int(obj2.yx[1]) <= int(obj1.yx[1] + obj1.width) and
            int(obj2.yx[0]) <= int(obj1.yx[0] + obj1.height + 1)):
            return True
        else:
            return False




class Hero:
    def __init__(self):
        self.yx = [curses.LINES - 6, curses.COLS / 2]
        self.icon = '>o<'
        self.speed = 1.2
        self.movement = 0
        self.width = 2
        self.height = 0
        self.health = 5

    def move(self):
        new_location = self.yx[1] + self.movement * self.speed
        if new_location >= 2 and new_location <= curses.COLS - 3:
            self.yx[1] = new_location
        elif new_location < 2:
            self.yx[1] = 2
            self.movement *= -1
        elif new_location > curses.COLS - self.width - 2:
            self.yx[1] = curses.COLS - self.width - 2
            self.movement *= -1


    def fire(self,count):
        if count < 5:
            return Bullet([self.yx[0]-random.randint(1,2),self.yx[1]+1],-1,'|')
        return False


class Bullet:
    def __init__(self,src,dir,icon):
        self.yx = src #list
        self.icon = icon
        self.speed = 2.23
        self.dir = dir
        self.width = 0
        self.height = 0

    def move(self):
        new_location = int(self.yx[0] + self.speed * self.dir)
        return new_location





class Enemy:

    def __init__(self):
        self.enemy_options = [
            {
                'yx': [1,random.randint(3,curses.COLS - 7)],
                'icon': ['\ ||| /',' ! o ! '],
                'speed': 0.2,
                'max_fire_count': 5,
                'width': 6,
                'height': 1,
                'bullet_icon': '=',
                'bullet_pattern': 1,
                'movement_pattern': 1,
                'movement_max': random.randint(20,70),
                'health': 4,
                'movement_dir': random.randint(1,5),
                'value': random.randint(30,50)
            },
            {
                'yx': [1,random.randint(3,curses.COLS - 7)],
                'icon': ['|-o-|'],
                'speed': 1,
                'max_fire_count': 5,
                'width': 4,
                'height': 0,
                'bullet_icon': ':',
                'bullet_pattern': 2,
                'movement_pattern': 2,
                'movement_max': random.randint(20,70),
                'health': 1,
                'movement_dir':[-1,1][random.randint(0,1)],
                'value': random.randint(60,90)
            },
            {
                'yx': [1,random.randint(3,curses.COLS - 7)],
                'icon': ['/-o-\\'],
                'speed': 0.5,
                'max_fire_count': 6,
                'width': 4,
                'height': 0,
                'bullet_icon': ':',
                'bullet_pattern': 3,
                'movement_pattern': 3,
                'movement_max': random.randint(5,int(curses.LINES / 2)),
                'health': 2,
                'movement_dir':[-1,1][random.randint(0,1)],
                'value': random.randint(40,80)
            },
            {
                'yx': [1,random.randint(3,curses.COLS - 9)],
                'icon': ['||_|_||','   V   '],
                'speed': 0.25,
                'max_fire_count': 7,
                'width': 6,
                'height': 1,
                'bullet_icon': 'I',
                'bullet_pattern': 4,
                'movement_pattern': 4,
                'movement_max': random.randint(20,70),
                'health': 6,
                'movement_dir':[-1,1][random.randint(0,1)],
                'value': random.randint(25,60)
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
        self.value = self.enemy_options[self.fighter_model]['value']

    def move(self):
        if self.movement_pattern == 1:
            self.movement_ident += 1
            new_location = [
                self.yx[0] + self.speed / random.randint(1,2),
                self.yx[1] + 1 * math.cos((math.pi * 2) * self.movement_ident / 30)
            ]

            if new_location[1] < 3:
                new_location[1] = 3
            elif new_location[1] > curses.COLS - self.width - 4:
                new_location[1] = curses.COLS - self.width - 4

        elif self.movement_pattern == 2:
            self.movement_ident += 1
            new_location = [self.yx[0] + self.speed, self.yx[1] + (self.speed * self.movement_dir)]
            if new_location[1] < 3:
                new_location[1] = 3
                self.movement_dir = 1
            elif new_location[1] > curses.COLS - self.width - 4:
                new_location[1] = curses.COLS - self.width - 4
                self.movement_dir = -1

            if self.movement_ident >= self.movement_max:
                self.movement_dir *= -1
                self.movement_ident = 0
        elif self.movement_pattern == 3:
            if self.yx[0] < self.movement_max:
                new_location = [self.yx[0] + self.speed,self.yx[1]]
            elif self.yx[0] == self.movement_max and self.movement_ident < 200:
                new_location = [self.yx[0],self.yx[1]  + self.speed * self.movement_dir]
                self.movement_ident += 1
                if new_location[1] < 3:
                    new_location[1] = 3
                    self.movement_dir *= -1
                elif new_location[1] > curses.COLS - self.width - 4:
                    new_location[1] = curses.COLS - self.width - 4
                    self.movement_dir *= -1
            else:
                new_location = [self.yx[0] + self.speed,self.yx[1]]

        else:
            new_location = [self.yx[0] + self.speed,self.yx[1]]

        return new_location

    def fire(self):
        if self.fire_count < self.max_fire_count and random.randint(0,30) == 5:
            self.fire_count += 1
            x_loc = self.yx[1]+(self.width-1)/2
            if self.width > 5:
                x_loc = self.yx[1] + random.randint(1,self.width-1)

            return Bullet([self.yx[0]+self.height+1,x_loc],1,self.bullet_icon)
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
                self.screen.addch(int(self.yx[0] - 1),int(self.yx[1]),self.icon2,curses.color_pair(1))
            if self.yx[0] + 1 < curses.LINES - 3:
                self.screen.addch(int(self.yx[0] + 1),int(self.yx[1]),self.icon2,curses.color_pair(1))
            if self.yx[1] - 1 > 2:
                self.screen.addch(int(self.yx[0]),int(self.yx[1] - 1),self.icon2,curses.color_pair(1))
            if self.yx[1] + 1 < curses.COLS - 2:
                self.screen.addch(int(self.yx[0]),int(self.yx[1] + 1),self.icon2,curses.color_pair(1))
        elif self.count < 10:
            if self.yx[0] - 2 > 2:
                self.screen.addch(int(self.yx[0] - 2),int(self.yx[1]),self.icon3,curses.color_pair(2))
            if self.yx[0] - 1 > 2 and self.yx[1] - 1 > 2:
                self.screen.addch(int(self.yx[0] - 2),int(self.yx[1]),self.icon3,curses.color_pair(2))
            if self.yx[0] + 2 < curses.LINES - 3:
                self.screen.addch(int(self.yx[0] + 2),int(self.yx[1]),self.icon3,curses.color_pair(2))
            if self.yx[1] - 2 > 2:
                self.screen.addch(int(self.yx[0]),int(self.yx[1] - 2),self.icon3,curses.color_pair(2))
            if self.yx[0] + 1 < curses.LINES - 3 and self.yx[1] + 1 < curses.COLS - 2:
                self.screen.addch(int(self.yx[0] - 2),int(self.yx[1]),self.icon3,curses.color_pair(2))
            if self.yx[1] + 2 < curses.COLS - 2:
                self.screen.addch(int(self.yx[0]),int(self.yx[1] + 2),self.icon3,curses.color_pair(2))




if __name__ == "__main__":
    # system('printf "\e[8;50;110;t"t')
    wrapper(Game)
