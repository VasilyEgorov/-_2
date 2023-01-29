import pygame
from pygame.locals import *
import random

pygame.init()

a = pygame.time.Clock()
fps = 70

p = 800
u = 900
b = (218, 165, 32)
q = pygame.display.set_mode((p, u))
pygame.display.set_caption('Flappy Bird')

started = False

# определить шрифт
font = pygame.font.SysFont('Bauhaus 93', 70)

# определяем цвета
white = (255, 255, 255)

# определить игровые переменные
c = 0
d = 4
flying = False
game_over = False
f = 160
v = 1600  # милисекунды
w = pygame.time.get_ticks() - v
n = 0
pass_pipe = False

# загруженные изображения
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
restartButton = pygame.image.load('img/restart_btn.png')
startButton = pygame.image.load('img/start_btn.png')
exitButton = pygame.image.load('img/exit_btn.png')


# функция вывода текста на экран
def draw_text(text, font, text_col, z, t):
    e = font.render(text, True, text_col)
    q.blit(e, (z, t))


def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(u / 2)
    score = 0
    return score


class Bird(pygame.sprite.Sprite):

    def __init__(self, z, t):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f"img/bird{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [z, t]
        self.vel = 0
        self.clicked = False

    def update(self):

        if flying == True:
            # применять гравитацию
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if game_over == False:
            # прыжок
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # обрабатывать анимацию
            flap_cooldown = 5
            self.counter += 1

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]

            # повернуть птицу
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            # направьте птицу на землю
            self.image = pygame.transform.rotate(self.images[self.index], -95)


class Button():
    def __init__(self, z, t, image, k):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * k), int(height * k)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (z, t)
        self.clicked = False

    def draw(self, surface):
        r = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                r = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        surface.blit(self.image, (self.rect.x, self.rect.y))
        return r


class Pipe(pygame.sprite.Sprite):

    def __init__(self, z, t, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/pipe.png")
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [z, t - int(f / 2)]
        elif position == -1:
            self.rect.topleft = [z, t + int(f / 2)]

    def update(self):
        self.rect.x -= d
        if self.rect.right < 0:
            self.kill()


pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

flappy = Bird(100, int(u / 2))

bird_group.add(flappy)

# создать экземпляр кнопки перезагрузки
startB = Button(250, 200, startButton, 1)
exitB = Button(272, 400, exitButton, 1)
im = pygame.transform.scale(restartButton, (200, 90))
restartB = Button(300, 300, im, 1)

g = True
while g:
    a.tick(fps)
    if not started:
        pygame.display.flip()
        q.fill(b)
        if startB.draw(q):
            started = True
        elif exitB.draw(q):
            g = False
    else:
        q.blit(bg, (0, 0))

        pipe_group.draw(q)
        bird_group.draw(q)
        bird_group.update()

        # рисовать и прокручивать землю
        q.blit(ground_img, (c, 768))
        if len(pipe_group) > 0:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                    and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                    and pass_pipe == False:
                pass_pipe = True
            if pass_pipe == True:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                    n += 1
                    pass_pipe = False
        draw_text(str(n), font, white, int(p / 2), 20)

        # искать столкновение
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
            game_over = True
        # как только птица упадет на землю, игра окончена, и она больше не летает
        if flappy.rect.bottom >= 768:
            game_over = True
            flying = False

        if flying == True and game_over == False:
            # генерировать новые трубы
            time_now = pygame.time.get_ticks()
            if time_now - w > v:
                pipe_height = random.randint(-100, 100)
                btm_pipe = Pipe(p, int(u / 2) + pipe_height, -1)
                top_pipe = Pipe(p, int(u / 2) + pipe_height, 1)
                pipe_group.add(btm_pipe)
                pipe_group.add(top_pipe)
                w = time_now

            pipe_group.update()

            c -= d
            if abs(c) > 35:
                c = 0

        # проверить завершение игры и сбросить
        if game_over == True:
            if restartB.draw(q):
                game_over = False
                n = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            g = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                g = False

    pygame.display.update()

pygame.quit()