import sys
from random import randint
import pygame

from core import *

pygame.init()

screen = pygame.display.set_mode((500, 600))
screen.fill([150, 150, 150])
pygame.display.set_icon(pygame.image.load('img/icon.ico'))
pygame.display.set_caption('MinesWeeWeeper')
fields, mines = [], []
mouse_down = False
first_click = True
game_over = False
field_id, tile = 0, 24
side_x, side_y = 20, 20
time = 0

game_field = GameField(side_x, side_y, tile)
game_field.create_field(screen, fields)

ramka = Field(210, 20, 9998, -1, -1, game_field)
ramka.tile = 80
ramka.draw(screen, 'img/ramka.png')
smile = Field(215, 25, 9999, -1, -1, game_field)
smile.tile = 70
smile.draw(screen, 'img/smile.png')
timers = []
counts = []
for i in range(3):
    timer = Field(360 + i * 30, 20, 10000 + i, -1, -1, game_field)
    timer.tile = 30
    timer.draw_rect(screen, 'img/timer/off.png', 55)
    timers.append(timer)

for i in range(3):
    count = Field(50 + i * 30, 20, 10000 + i, -1, -1, game_field)
    count.tile = 30
    count.draw_rect(screen, 'img/timer/off.png', 55)
    counts.append(count)

current_field, last_field = fields[0], fields[0]

pygame.time.set_timer(pygame.USEREVENT, 1000, 9999)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_down = True
            position = event.pos
            count = 0
            if smile.is_collide(event.pos[0], event.pos[1]):
                smile.draw(screen, 'img/think.png')
            elif not game_over:
                for field in fields:
                    count += 1
                    if field.is_collide(event.pos[0], event.pos[1]):
                        if not field.is_open and not field.is_flag:
                            field.draw_mouse_down(screen)
                        elif field.is_open:
                            field.open_near(mines, screen, fields, 'btn_down')
                        current_field = field

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_down = False
            if smile.is_collide(event.pos[0], event.pos[1]):
                smile.draw(screen, 'img/smile.png')
                for field in fields:
                    field.draw(screen, 'img/field.png')
                    field.is_flag = False
                    field.is_open = False
                    field.is_error = False
                    mines = []
                    first_click = True
                    game_over = False
            elif first_click and event.button == 1 and not game_over:
                game_field.game_started = True
                current_field.is_open = True
                game_field.generate_mines(10, fields, mines, current_field)
                current_field.scan(mines, fields, screen)
                first_click = False
                time = 0
                pygame.mixer.music.load('audio/greetings.mp3')
                pygame.mixer.music.play()
                for index, count in enumerate(counts):
                    count.count_update(screen, game_field.amount_of_mines, index, count)
            elif event.button == 3 and not current_field.is_open and not first_click:
                current_field.set_flag(screen, game_field)
                for index, count in enumerate(counts):
                    count.count_update(screen, game_field.amount_of_mines, index, count)
            elif not current_field.is_open and not current_field.is_flag:
                current_field.scan(mines, fields, screen)
                current_field.is_open = True
            elif current_field.is_open:
                current_field.open_near(mines, screen, fields)
            count = game_field.check_field(fields)
            if count == -1:
                smile.draw(screen, 'img/dead.png')
                game_over = True
                game_field.game_started = False
                pygame.mixer.music.load('audio/dead.mp3')
                pygame.mixer.music.play()
            elif count == -2:
                smile.draw(screen, 'img/grats.png')
                game_over = True
                game_field.game_started = False
                pygame.mixer.music.load('audio/win.mp3')
                pygame.mixer.music.play()

        elif event.type == pygame.MOUSEMOTION and not game_over:
            for field in fields:
                if field.is_collide(event.pos[0], event.pos[1]):
                    if field.id != current_field.id:
                        last_field = current_field
                        current_field = field
            if mouse_down and not current_field.is_open:
                smile.draw(screen, 'img/think.png')
                current_field.draw_mouse_down(screen)
            if not last_field.is_open and not last_field.is_flag:
                last_field.draw(screen, 'img/field.png')
            elif not mouse_down:
                smile.draw(screen, 'img/smile.png')

        elif event.type == pygame.USEREVENT:
            if game_field.game_started:
                time += 1
                for index, timer in enumerate(timers):
                    timer.timer_update(screen, time, index, timer)

        pygame.display.flip()
