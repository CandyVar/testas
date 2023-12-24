import os
import sys
import pygame


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Wall(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(walls_group, all_sprites)
        self.image = tile_images['wall']
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Portal(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(portals_group, all_sprites)
        self.image = tile_images['wall']
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    ...


class Enemy(pygame.sprite.Sprite):
    ...


class Camera:
    ...


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def terminate():
    pygame.quit()
    sys.exit()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Wall(x, y)
            elif level[y][x] == '&':
                Enemy(x, y, speed=1)
                Tile('empty', x, y)
            elif level[y][x] == '!':
                Portal(x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)

    return new_player, x, y


def move_check():
    if pygame.sprite.spritecollideany(player, walls_group) or not pygame.sprite.spritecollideany(player, tiles_group):
        return 'wb'


def start_screen():
    ...


def smooth_player_move_up():
    ...


def smooth_player_move_down():
    ...


def smooth_player_move_left():
    ...


def smooth_player_move_right():
    ...


def fade_out_and_load_new_world(screen, clock, new_map_filename):
    fade_duration = 2000
    fade_steps = 50
    fade_step_duration = fade_duration // fade_steps

    fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
    fade_surface.fill((0, 0, 0))

    for alpha in range(fade_steps + 1):
        fade_surface.set_alpha(int(alpha / fade_steps * 255))
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(fade_step_duration)
        clock.tick(60)

    new_player, level_x, level_y = generate_level(load_level(new_map_filename))
    camera.update(new_player)
    all_sprites.empty()
    tiles_group.empty()
    walls_group.empty()
    portals_group.empty()
    player_group.empty()
    enemy_group.empty()

    all_sprites.add(new_player)
    tiles_group.add(new_player, *tiles_group.sprites())
    walls_group.add(*walls_group.sprites())
    portals_group.add(*portals_group.sprites())
    player_group.add(new_player)
    enemy_group.add(*enemy_group.sprites())

    pygame.time.delay(1000)


pygame.init()
FPS = 50
WIDTH, HEIGHT = 500, 500
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill((0, 0, 255))
start_screen()
STEP = 50

tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png'),
    'enemy': load_image('arrow.png'),
}
player_image = pygame.transform.scale(load_image('1.png'), (50, 50))

base = load_level('map.txt')
tile_width = tile_height = 50
camera = Camera()
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
portals_group = pygame.sprite.Group()
player, level_x, level_y = generate_level(load_level('map.txt'))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                smooth_player_move_left()
                if move_check() == 'wb':
                    if pygame.sprite.spritecollideany(player, portals_group):
                        continue
                    smooth_player_move_right()
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                smooth_player_move_right()
                if move_check() == 'wb':
                    if pygame.sprite.spritecollideany(player, portals_group):
                        continue
                    smooth_player_move_left()
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                smooth_player_move_up()
                if move_check() == 'wb':
                    if pygame.sprite.spritecollideany(player, portals_group):
                        continue
                    smooth_player_move_down()
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                smooth_player_move_down()
                if move_check() == 'wb':
                    if pygame.sprite.spritecollideany(player, portals_group):
                        fade_out_and_load_new_world(screen, clock, 'map.txt')
                        continue
                    smooth_player_move_up()

    for enemy in enemy_group:
        enemy.move_towards_player(player.rect)

    screen.fill((0, 0, 255))
    tiles_group.draw(screen)
    walls_group.draw(screen)
    portals_group.draw(screen)
    player_group.draw(screen)
    enemy_group.draw(screen)
    camera.update(player)

    for sprite in all_sprites:
        camera.apply(sprite)

    pygame.display.flip()
    clock.tick(FPS)
