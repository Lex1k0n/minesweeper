import pygame
from random import randint


class Field:
    tile = 24

    def __init__(self, x, y, id, pos_x, pos_y, game_field):
        self.x = x
        self.y = y
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.mine_count = None
        self.id = id
        self.is_open = False
        self.is_flag = False
        self.near_fields = []
        self.is_error = False
        self.game_field = game_field

    def draw(self, window: pygame.surface.Surface, img_path):
        img = pygame.image.load(img_path)
        img = pygame.transform.scale(img, (self.tile, self.tile))
        window.blit(img, (self.x, self.y))

    def draw_rect(self, window: pygame.surface.Surface, img_path, height):
        img = pygame.image.load(img_path)
        img = pygame.transform.scale(img, (self.tile, height))
        window.blit(img, (self.x, self.y))

    def draw_mouse_down(self, window: pygame.surface.Surface):
        img = pygame.image.load('img/mouse_down.png')
        img = pygame.transform.scale(img, (self.tile, self.tile))
        window.blit(img, (self.x, self.y))

    def is_collide(self, pos_x, pos_y):
        if self.x <= pos_x <= self.x + self.tile and self.y <= pos_y <= self.y + self.tile:
            return True
        else:
            return False

    def scan(self, mines, fields, window):
        self.is_open = True
        self.mine_count = 0
        for mine in mines:
            if mine.id == self.id:
                self.draw(window, 'img/err.png')
                self.is_error = True
                print('error')
            else:
                for field in self.near_fields:
                    if field[0] == mine.pos_x and field[1] == mine.pos_y:
                        self.mine_count += 1
        if self.mine_count != 0 and not self.is_error:
            self.draw(window, 'img/' + str(self.mine_count) + '.png')
        elif not self.is_error:
            self.draw(window, 'img/mouse_down.png')
            for field in self.near_fields:
                for temp in fields:
                    if field[0] == temp.pos_x and field[1] == temp.pos_y and temp.is_open is False:
                        temp.scan(mines, fields, window)
        elif self.is_error:
            for mine in mines:
                if mine.id != self.id:
                    mine.draw(window)

    def set_flag(self, window, game_field):
        if self.is_flag:
            self.draw(window, 'img/field.png')
            game_field.amount_of_mines += 1
            self.is_flag = not self.is_flag
        elif game_field.amount_of_mines > 0:
            self.draw(window, 'img/flag.png')
            game_field.amount_of_mines -= 1
            self.is_flag = not self.is_flag

    def open_near(self, mines, window, fields, key=None):
        flag_count = 0
        temp_near_fields = []
        for field in self.near_fields:
            for temp in fields:
                if field[0] == temp.pos_x and field[1] == temp.pos_y:
                    temp_near_fields.append(temp)
                    if temp.is_flag:
                        flag_count += 1
        if flag_count == self.mine_count and key is None:
            for field in temp_near_fields:
                if not field.is_flag:
                    field.scan(mines, fields, window)
                    self.is_error = field.is_error
        elif key is None:
            for field in temp_near_fields:
                if not field.is_flag and not field.is_open:
                    field.draw(window, 'img/field.png')
        elif key == 'btn_down':
            for field in temp_near_fields:
                if not field.is_open and not field.is_flag:
                    field.draw_mouse_down(window)

    @staticmethod
    def timer_update(window, num, index, timer):
        num = list(str(num))
        while len(num) < 3:
            num.insert(0, '0')
        number = num[index]
        timer.draw_rect(window, 'img/timer/' + number + '.png', 55)

    @staticmethod
    def count_update(window, num, index, count):
        num = list(str(num))
        while len(num) < 3:
            num.insert(0, '0')
        number = num[index]
        count.draw_rect(window, 'img/timer/' + number + '.png', 55)


class Mine:

    def __init__(self, x, y, id, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.x = x
        self.y = y
        self.id = id

    def draw(self, window):
        img = pygame.image.load('img/mine.png')
        img = pygame.transform.scale(img, (24, 24))
        window.blit(img, (self.x, self.y))


class GameField:

    def __init__(self, len_x, len_y, tile):
        self.amount_of_mines = None
        self.len_x = len_x
        self.len_y = len_y
        self.tile = tile
        self.open_count = 0
        self.mine_count = 0
        self.field_count = 0
        self.game_started = False

    def create_field(self, window, fields):
        field_id = 0
        for i in range(self.len_x):
            for j in range(self.len_y):
                current_btn = Field(10 + j * self.tile, 110 + i * self.tile, field_id, i, j, self)
                if i != 0:
                    current_btn.near_fields.append([i - 1, j])
                    if j != 0:
                        current_btn.near_fields.append([i - 1, j - 1])
                    if j != 19:
                        current_btn.near_fields.append([i - 1, j + 1])
                if i != 19:
                    current_btn.near_fields.append([i + 1, j])
                    if j != 0:
                        current_btn.near_fields.append([i + 1, j - 1])
                    if j != 19:
                        current_btn.near_fields.append([i + 1, j + 1])
                if j != 0:
                    current_btn.near_fields.append([i, j - 1])
                if j != 19:
                    current_btn.near_fields.append([i, j + 1])
                field_id += 1
                current_btn.draw(window, 'img/field.png')
                fields.append(current_btn)
                self.field_count += 1

    def generate_mines(self, mines_count: int, fields, mines, current_field):
        self.amount_of_mines = mines_count
        current_count = 0
        need_restart = False
        self.mine_count = mines_count
        while current_count < mines_count:
            x, y = 10 + randint(0, self.len_x - 1) * self.tile, 110 + randint(0, self.len_y - 1) * self.tile
            if current_field.x - self.tile - 1 < x < current_field.x + self.tile + 1 and current_field.y - self.tile - 1\
                    < y < current_field.y + self.tile + 1:
                need_restart = True
            else:
                for m in mines:
                    if m.x == x and m.y == y:
                        need_restart = True
                        break
            if not need_restart:
                for field in fields:
                    if field.x == x and field.y == y:
                        current_mine = Mine(x, y, field.id, field.pos_x, field.pos_y)
                        mines.append(current_mine)
                        current_count += 1
            else:
                need_restart = False

    def check_field(self, fields):
        temp = 0
        for field in fields:
            if field.is_open:
                temp += 1
            if field.is_error:
                return -1
        self.open_count = temp
        if self.open_count == self.field_count - self.mine_count:
            return -2
        return self.open_count
