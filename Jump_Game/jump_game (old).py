import pygame
import random
import os
from tkinter import Tk, filedialog
from pygame.locals import *

# Oyun ekranı boyutları
WIDTH, HEIGHT = 400, 600
FPS = 60

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DEFAULT_COLOR = (255, 0, 0)  # Varsayılan karakter rengi
BUTTON_COLOR = (0, 100, 255)
BUTTON_HOVER_COLOR = (0, 150, 255)
BG_COLOR = WHITE  # Ana menü arka plan rengi

# Platform özellikleri
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 10
PLATFORM_COLOR = (0, 255, 0)

# Pygame başlangıç ayarları
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zıplama Oyunu")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)

background = None
bg_y = 0
player_image = None
score = 0  # Skor değişkeni

# Platform sınıfı
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image.fill(PLATFORM_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.scored = False

    def update(self, player):
        if player.rect.top <= HEIGHT // 4:
            self.rect.y += abs(player.velocity)
            if self.rect.top >= HEIGHT:
                self.kill()
        if not self.scored and player.rect.bottom <= self.rect.top and player.velocity > 0:
            self.scored = True
            return True
        return False

# Oyuncu sınıfı
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        if player_image:
            self.image = pygame.image.load(player_image).convert_alpha()
        else:
            self.image = pygame.Surface((50, 50))
            self.image.fill(DEFAULT_COLOR)
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT // 2))
        self.velocity = 0
        self.jumping = False

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5

        if keys[pygame.K_UP] and not self.jumping:
            self.velocity = -15
            self.jumping = True

        self.rect.y += self.velocity
        self.velocity += 1

        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity = 0
            self.jumping = False

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        global score
        for platform in platforms:
            if platform.update(self):
                score += 1

        self.check_landing(platforms)
        self.add_platforms(platforms)

    def check_landing(self, platforms):
        if self.velocity > 0:
            hits = pygame.sprite.spritecollide(self, platforms, False)
            if hits:
                self.rect.bottom = hits[0].rect.top
                self.velocity = 0
                self.jumping = False

    def add_platforms(self, platforms):
        if len(platforms) < 5:
            if len(platforms) == 0 or platforms.sprites()[-1].rect.y < HEIGHT // 2:
                x = random.randint(0, WIDTH - PLATFORM_WIDTH)
                y = platforms.sprites()[-1].rect.y - 120 if platforms else HEIGHT - 100
                platform = Platform(x, y)
                platforms.add(platform)

# Platformları oluşturma
def create_platforms():
    platforms = pygame.sprite.Group()
    for i in range(5):
        x = random.randint(0, WIDTH - PLATFORM_WIDTH)
        y = i * 120 + 100
        platform = Platform(x, y)
        platforms.add(platform)
    return platforms

# Buton sınıfı
class Button:
    def __init__(self, text, pos, action=None):
        self.text = text
        self.pos = pos
        self.action = action
        self.font = pygame.font.SysFont(None, 36)
        self.rect = None
        self.rendered_text = None
        self.create_button()

    def create_button(self):
        self.rendered_text = self.font.render(self.text, True, BLACK)
        self.rect = self.rendered_text.get_rect(center=self.pos)
        self.button_rect = pygame.Rect(self.rect.x - 10, self.rect.y - 10, self.rect.width + 20, self.rect.height + 20)

    def draw(self, screen):
        pygame.draw.rect(screen, BUTTON_COLOR, self.button_rect, border_radius=10)
        screen.blit(self.rendered_text, self.rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                if self.action:
                    self.action()

    def check_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR, self.button_rect, border_radius=10)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, self.button_rect, border_radius=10)

# Arka plan resmini seçmek için fonksiyon
def select_background():
    global background, bg_y
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        try:
            background = pygame.image.load(file_path).convert()
            bg_y = 0
        except pygame.error:
            print("Resim yüklenemedi.")
    root.destroy()

# Karakter resmini seçmek için fonksiyon
def select_character():
    global player_image
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        try:
            player_image = file_path
        except pygame.error:
            print("Resim yüklenemedi.")
    root.destroy()

# Varsayılan karakter seçenekleri
def default_characters():
    shapes = [pygame.Surface((50, 50)), pygame.Surface((50, 50))]
    shapes[0].fill((255, 0, 0))  # Kırmızı kare
    pygame.draw.polygon(shapes[1], (0, 255, 0), [(25, 0), (50, 50), (0, 50)])  # Yeşil üçgen
    return shapes

# Ana menü fonksiyonu
def show_menu():
    def quit_game():
        pygame.quit()
        exit()

    menu_running = True
    start_button = Button("Başla", (WIDTH // 2, HEIGHT // 2 - 50), start_game)
    settings_button = Button("Ayarlar", (WIDTH // 2, HEIGHT // 2), show_settings)
    quit_button = Button("Çıkış", (WIDTH // 2, HEIGHT // 2 + 50), quit_game)
    buttons = [start_button, settings_button, quit_button]

    while menu_running:
        screen.fill(BG_COLOR)
        title_text = font.render("Zıplama Oyunu", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))

        for button in buttons:
            button.check_hover()
            button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            for button in buttons:
                button.check_click(event)

# Ayarlar menüsü fonksiyonu
def show_settings():
    settings_running = True
    bg_button = Button("Arka Plan Seçimi", (WIDTH // 2, HEIGHT // 2 - 100), select_background)
    char_button = Button("Karakter Seçimi", (WIDTH // 2, HEIGHT // 2 - 50), select_character)
    color_button = Button("Arka Plan Rengi", (WIDTH // 2, HEIGHT // 2), change_bg_color)
    back_button = Button("Geri", (WIDTH // 2, HEIGHT // 2 + 50), show_menu)
    buttons = [bg_button, char_button, color_button, back_button]

    while settings_running:
        screen.fill(WHITE)
        settings_title = font.render("Ayarlar", True, BLACK)
        screen.blit(settings_title, (WIDTH // 2 - settings_title.get_width() // 2, HEIGHT // 4))

        # Arka plan ön izlemesi
        preview_bg = pygame.Surface((WIDTH, 100))
        if background:
            preview_bg.blit(pygame.transform.scale(background, (WIDTH, 100)), (0, 0))
        else:
            preview_bg.fill(BG_COLOR)
        screen.blit(preview_bg, (0, HEIGHT - 200))

        # Karakter ön izlemesi
        preview_char = pygame.Surface((50, 50))
        if player_image:
            char_image = pygame.image.load(player_image)
            preview_char.blit(pygame.transform.scale(char_image, (50, 50)), (0, 0))
        else:
            preview_char.fill(DEFAULT_COLOR)
        screen.blit(preview_char, (WIDTH // 2 - 25, HEIGHT - 150))

        # Arka plan renginin ön izlenmesi
        color_preview_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 - 50, 100, 100)
        pygame.draw.rect(screen, BG_COLOR, color_preview_rect)

        for button in buttons:
            button.check_hover()
            button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            for button in buttons:
                button.check_click(event)

# Arka plan rengini değiştiren fonksiyon
def change_bg_color():
    global BG_COLOR
    BG_COLOR = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Oyunu başlatan fonksiyon
def start_game():
    global score
    score = 0
    player = Player()
    platforms = create_platforms()
    all_sprites = pygame.sprite.Group(player, *platforms)

    menu_button = Button("Ana Menü", (WIDTH - 60, 30), show_menu_confirm)

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            menu_button.check_click(event)

        # Oyuncuyu güncelle
        player.update(platforms)  # Player.update() fonksiyonuna platforms argümanını geçiyoruz

        # Platformları güncelle
        for platform in platforms:
            platform.update(player)

        # Ekranı güncelleme
        if background:
            screen.blit(background, (0, bg_y))
        else:
            screen.fill(WHITE)

        all_sprites.draw(screen)
        menu_button.check_hover()
        menu_button.draw(screen)

        score_text = font.render(f"Skor: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()


def show_menu_confirm():
    confirm_running = True
    yes_button = Button("Evet", (WIDTH // 2 - 50, HEIGHT // 2), show_menu)
    no_button = Button("Hayır", (WIDTH // 2 + 50, HEIGHT // 2), None)
    buttons = [yes_button, no_button]

    while confirm_running:
        screen.fill(WHITE)
        confirm_text = font.render("Ana Menüye Dönmek İstiyor musunuz?", True, BLACK)
        screen.blit(confirm_text, (WIDTH // 2 - confirm_text.get_width() // 2, HEIGHT // 3))

        for button in buttons:
            button.check_hover()
            button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            for button in buttons:
                button.check_click(event)
        confirm_running = False

if __name__ == "__main__":
    show_menu()
