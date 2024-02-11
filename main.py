import pygame
import sys
from params import WIDTH, HEIGHT, pipe_size, pipe_gap, pipe_pair_sizes, ground_space, import_sprite
import random

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT + ground_space))
pygame.display.set_caption("Flappy Bird")


# Класс, отвечающий за текст
class GameIndicator:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont('Bahnschrift', 60)
        self.inst_font = pygame.font.SysFont('Bahnschrift', 35)
        self.color = pygame.Color(245, 7, 114)
        self.inst_color = pygame.Color(232, 28, 174)

    # очки
    def show_score(self, int_score):
        bird_score = f'ОЧКИ: {int_score}'
        score = self.font.render(bird_score, True, self.color)
        self.screen.blit(score, (WIDTH - 270, 10))

    # памятка как двигаться и перезапускать игру
    def instructions(self):
        inst_text1 = 'Нажимайте "Пробел" чтобы прыгать'
        inst_text2 = 'Нажмите "R" чтобы перезапустить'
        ins1 = self.inst_font.render(inst_text1, True, self.inst_color)
        ins2 = self.inst_font.render(inst_text2, True, self.inst_color)
        self.screen.blit(ins1, (150, 550))
        self.screen.blit(ins2, (150, 600))


# Класс Птицы
class Bird(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.frame_index = 0
        self.animation_delay = 3
        self.jump_move = -9

        # Взмахи крыльями
        self.bird_img = import_sprite("img/bird")
        self.image = self.bird_img[self.frame_index]
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect(topleft=pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.direction = pygame.math.Vector2(0, 0)
        self.score = 0

    # анимация полета
    def _animate(self):
        sprites = self.bird_img
        sprite_index = (self.frame_index // self.animation_delay) % len(sprites)
        self.image = sprites[sprite_index]
        self.frame_index += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)
        if self.frame_index // self.animation_delay > len(sprites):
            self.frame_index = 0

    # прыжок
    def _jump(self):
        self.direction.y = self.jump_move

    def update(self, is_jump):
        if is_jump:
            self._jump()
        self._animate()


# Класс трубы
class Pipe(pygame.sprite.Sprite):
    def __init__(self, pos, width, height, flip):
        super().__init__()
        self.width = width
        img_path = 'img/world/pipe.png'
        self.image = pygame.image.load(img_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        if flip:
            flipped_image = pygame.transform.flip(self.image, False, True)
            self.image = flipped_image
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift

        # Убираем трубу при выходе за экран
        if self.rect.right < (-self.width):
            self.kill()


class World:
    def __init__(self, screen):
        self.screen = screen
        self.world_shift = 0
        self.current_x = 0
        self.gravity = 0.6
        self.current_pipe = None
        self.pipes = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self._generate_world()
        self.playing = False
        self.game_over = False
        self.passed = True
        self.game = GameIndicator(screen)

    # Де_генерация мира
    def _generate_world(self):
        self._add_pipe()
        bird = Bird((WIDTH // 2 - pipe_size, HEIGHT // 2 - pipe_size), 30)
        self.player.add(bird)

    # Добавляет новые трубы
    def _add_pipe(self):
        pipe_pair_size = random.choice(pipe_pair_sizes)
        top_pipe_height, bottom_pipe_height = pipe_pair_size[0] * pipe_size, pipe_pair_size[1] * pipe_size

        pipe_top = Pipe((WIDTH, 0 - (bottom_pipe_height + pipe_gap)), pipe_size, HEIGHT, True)
        pipe_bottom = Pipe((WIDTH, top_pipe_height + pipe_gap), pipe_size, HEIGHT, False)
        self.pipes.add(pipe_top)
        self.pipes.add(pipe_bottom)
        self.current_pipe = pipe_top

    # Движение мира
    def _scroll_x(self):
        if self.playing:
            self.world_shift = -6
        else:
            self.world_shift = 0

    # Физика падения для птички
    def _apply_gravity(self, player):
        if self.playing or self.game_over:
            player.direction.y += self.gravity
            player.rect.y += player.direction.y

    def _handle_collisions(self):
        bird = self.player.sprite
        # Прооверка коллизии
        if pygame.sprite.groupcollide(self.player, self.pipes, False,
                                      False) or bird.rect.bottom >= HEIGHT or bird.rect.top <= 0:
            self.playing = False
            self.game_over = True
        else:
            bird = self.player.sprite
            if bird.rect.x >= self.current_pipe.rect.centerx:
                bird.score += 1
                self.passed = True

    def update(self, player_event=None):
        if self.current_pipe.rect.centerx <= (WIDTH // 2) - pipe_size:
            self._add_pipe()

        self.pipes.update(self.world_shift)
        self.pipes.draw(self.screen)

        # Добавляем физику
        self._apply_gravity(self.player.sprite)
        self._scroll_x()
        self._handle_collisions()

        if player_event == "jump" and not self.game_over:
            player_event = True
        elif player_event == "restart":
            self.game_over = False
            self.pipes.empty()
            self.player.empty()
            self.player.score = 0
            self._generate_world()
        else:
            player_event = False

        if not self.playing:
            self.game.instructions()

        self.player.update(player_event)
        self.player.draw(self.screen)

        self.game.show_score(self.player.sprite.score)


class Main:
    def __init__(self, screen):
        self.screen = screen
        self.bg_img = pygame.image.load('img/world/bg.png')
        self.bg_img = pygame.transform.scale(self.bg_img, (WIDTH, HEIGHT))
        self.ground_img = pygame.image.load('img/world/ground.png')
        self.ground_scroll = 0
        self.scroll_speed = -6
        self.FPS = pygame.time.Clock()
        self.stop_ground_scroll = False

    def main(self):
        world = World(screen)
        while True:
            self.stop_ground_scroll = world.game_over
            self.screen.blit(self.bg_img, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if not world.playing and not world.game_over:
                        world.playing = True
                    if event.key == pygame.K_SPACE:
                        world.update("jump")
                    if event.key == pygame.K_r:
                        world.update("restart")

            world.update()

            self.screen.blit(self.ground_img, (self.ground_scroll, HEIGHT))
            if not self.stop_ground_scroll:
                self.ground_scroll += self.scroll_speed
                if abs(self.ground_scroll) > 35:
                    self.ground_scroll = 0

            pygame.display.update()
            self.FPS.tick(60)


if __name__ == "__main__":
    play = Main(screen)
    play.main()
