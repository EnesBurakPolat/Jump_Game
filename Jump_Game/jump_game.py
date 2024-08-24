import pygame
import random
from pygame.locals import *
from tkinter import Tk, filedialog

#Eksiklikler
#1.Platformlar sabit ve yukarı çıktıkça aşşağı inmiyor
#2.Player 3.platformdan sonra yukarı çıkamıyor
#3. Resim ve Karakter yüklemelerinde buglar olabiliyor eğer boyut kötüyse scale etmek lazım her zaman belli bir standarta
#4 kapanırken exit hatası veriyor

#python -m PyInstaller --onefile --noconsole jump_game.py
# Pygame başlangıç ayarları
pygame.init()
pygame.font.init()

# Ekran boyutları
WIDTH, HEIGHT = 700, 800
FPS = 60

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DEFAULT_COLOR = (255, 0, 0)
BUTTON_COLOR = (0, 100, 255)
BUTTON_HOVER_COLOR = (0, 150, 255)
BG_COLOR = WHITE

font = pygame.font.SysFont(None, 36)

# Ekran ayarları
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zıplama Oyunu")
clock = pygame.time.Clock()

background = None
bg_y = 0
player_image = None
score = 0
game_state = "menu"  # 'menu', 'playing', 'paused'

# Arka plan ve karakter boyutlandırma için yardımcı fonksiyon
def scale_image(image, width, height):
    return pygame.transform.scale(image, (width, height))

# Platform sınıfı
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, moving=False):
        """Platform nesnesinin başlatılmasını sağlar."""
        super().__init__()
        self.image = pygame.Surface((100, 20))  # Platformun boyutu (genişlik, yükseklik)
        self.image.fill((0, 255, 0))  # Platformun rengi yeşil
        self.rect = self.image.get_rect(topleft=(x, y))  # Platformun ekran üzerindeki konumu
        self.moving = moving  # Platformun hareket edip etmeyeceğini belirler
        self.move_direction = random.choice([-1, 1])  # Sağ (+1) veya sol (-1) hareket

    def update(self, *args):
        """Platformun ekranın altına geçip geçmediğini ve hareketini kontrol eder."""
        if self.moving:
            self.rect.x += self.move_direction * 2  # Platformun yatay hareket hızı
            if self.rect.left <= 0 or self.rect.right >= WIDTH:
                self.move_direction *= -1  # Ekranın kenarına çarpınca yön değiştir
        if self.rect.top > HEIGHT:
            self.kill()  # Ekranın altına geçen platformu kaldır
            return True
        return False

def create_platforms(platforms):
    """Başlangıçta platformları oluşturur ve `platforms` grubuna ekler."""
    for i in range(7):  # Toplamda 7 platform oluştur
        x = random.randint(0, WIDTH - 100)  # Platformun x konumunu rastgele belirle
        y = HEIGHT - (i + 1) * 150  # Platformun y konumunu belirle; her yeni platform daha yüksekte olacak
        moving = random.choice([True, False])  # Platformun hareket edip etmeyeceğini rastgele belirle
        platform = Platform(x, y, moving)  # Yeni bir Platform nesnesi oluştur
        platforms.add(platform)  # Platformu `platforms` grubuna ekle

def add_platforms(platforms, player):
    """Eksik platformları ekler ve ekranda yeni platformlar oluşturur."""
    if len(platforms.sprites()) == 0:
        create_platforms(platforms)  # Platformlar yoksa başlangıçta 7 platform oluştur
    
    if len(platforms.sprites()) > 0:
        last_platform = platforms.sprites()[-1]  # Son platformu al
        y = last_platform.rect.top - 120  # Yeni platformun y konumunu belirle; son platformdan biraz daha yüksekte
    else:
        y = HEIGHT - 120  # Eğer hiç platform yoksa, ekranın en altına yeni bir platform ekle
    
    new_platform = Platform(random.randint(0, WIDTH - 100), y)  # Yeni platform oluştur
    platforms.add(new_platform)  # Yeni platformu `platforms` grubuna ekle

def move_camera(player, platforms):
    """Kamera hareketini günceller ve oyuncu platformlara düzgün bir şekilde iniş yapmasını sağlar."""
    global bg_y, score  # `bg_y` ve `score` global değişkenleri kullanılır
    if player.rect.top < HEIGHT // 3:  # Oyuncunun üst kısmı ekranın üst üçte birine yaklaştığında
        bg_y += HEIGHT // 3 - player.rect.top  # Arka planı yukarı kaydır
        player.rect.top = HEIGHT // 3  # Oyuncunun üst kısmını ekranın üst üçte birine sabitle
    
        if background:  # Eğer bir arka plan resmi varsa
            screen.blit(background, (0, bg_y % HEIGHT))  # Arka planı ekranda kaydır
            screen.blit(background, (0, bg_y % HEIGHT - HEIGHT))  # Arka planın bir diğer parçasını ekle

        # Puanı yalnızca oyuncunun ekranın altına geçmesi durumunda artır
        if player.rect.bottom >= HEIGHT:
            score += 1

        # Oyuncu platforma düştüğünde doğru şekilde iniş yapmalı
        for platform in pygame.sprite.groupcollide(platforms, pygame.sprite.Group(player), False, False):
            if player.rect.bottom <= platform.rect.top + 10:  # Oyuncunun alt kısmı platformun üst kısmına yakınsa
                player.rect.bottom = platform.rect.top  # Oyuncunun alt kısmını platformun üst kısmına sabitle
                player.velocity = 0  # Oyuncunun hızını sıfırla
                player.jumping = False  # Atlama durumunu sıfırla
                break

def update_platforms(platforms, player):
    """Platformları günceller ve ekranın üstünden geçenleri kaldırır."""
    for platform in platforms:
        if platform.update():  # Platformları güncelle
            add_platforms(platforms, player)  # Ekranın üstünden geçen platformları yenileriyle değiştir
    
    # Platform sayısı 7'den azsa, daha fazla platform ekle
    if len(platforms) < 7:
        add_platforms(platforms, player)
    
    # Son platformun y konumu ekranın üst kısmında kalıyorsa, yeni platformlar ekle
    if platforms.sprites() and platforms.sprites()[-1].rect.top < HEIGHT:
        add_platforms(platforms, player)


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Oyuncu sınıfı
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        if player_image:
            self.image = pygame.image.load(player_image).convert_alpha()
        else:
            self.image = pygame.Surface((50, 50))
            self.image.fill(DEFAULT_COLOR)
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
        self.velocity = 0
        self.jumping = False

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5

        if keys[pygame.K_UP] and not self.jumping:  # Zıplama kontrolü
            self.velocity = -25 #ZIPLAMA YÜKSEKLİĞİ
            self.jumping = True

        self.rect.y += self.velocity
        self.velocity += 1  # Yer çekimi etkisi

        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity = 0
            self.jumping = False

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        global score
        update_platforms(platforms, self)
        self.check_landing(platforms)
        move_camera(self, platforms)  # platforms parametresini ekledik

    def check_landing(self, platforms):
        if self.velocity > 0:
            hits = pygame.sprite.spritecollide(self, platforms, False)
            if hits:
                highest_platform = max(hits, key=lambda p: p.rect.top)
                self.rect.bottom = highest_platform.rect.top
                self.velocity = 0
                self.jumping = False
            else:
                self.jumping = True  # Hava da zıplama

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
            # Arka planı ekran boyutuna göre ölçeklendir
            background = scale_image(background, WIDTH, HEIGHT)
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
    shapes[0].fill((255, 0, 0))
    pygame.draw.polygon(shapes[1], (0, 255, 0), [(25, 0), (50, 50), (0, 50)])
    return shapes

# Ana menü fonksiyonu
def show_menu():
    def quit_game():
        pygame.quit()
        exit()

    global game_state
    game_state = "menu"

    menu_running = True
    start_button = Button("Başla", (WIDTH // 2, HEIGHT // 2 - 150), start_game)
    settings_button = Button("Ayarlar", (WIDTH // 2, HEIGHT // 2 - 50), show_settings)
    quit_button = Button("Çıkış", (WIDTH // 2, HEIGHT // 2 + 50), quit_game)
    buttons = [start_button, settings_button, quit_button]

    while menu_running:
        screen.fill(BG_COLOR)

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

def preview_background_image():
    if background:
        scaled_bg = scale_image(background, WIDTH // 2, HEIGHT // 3)
        screen.blit(scaled_bg, (WIDTH // 2 - scaled_bg.get_width() // 2, HEIGHT - scaled_bg.get_height() - 60))

def preview_character_image():
    if player_image:
        character_img = pygame.image.load(player_image).convert_alpha()
        scaled_character = scale_image(character_img, 100, 100)  # Örnek boyut, ihtiyaca göre ayarlayın
        screen.blit(scaled_character, (WIDTH // 2 - scaled_character.get_width() // 2, HEIGHT - 130))

def preview_background_color():
    screen.fill(BG_COLOR)

def show_settings():
    def change_bg_color():
        global BG_COLOR
        # Örnek olarak, rastgele bir renk seçiyoruz
        BG_COLOR = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    def back_to_menu():
        nonlocal settings_running
        settings_running = False

    def change_bg_color_callback():
        nonlocal bg_color_button
        change_bg_color()
        preview_background_color()
        bg_color_button.create_button()

    def select_bg_image():
        select_background()
        preview_background_image()

    def select_character_image():
        select_character()
        preview_character_image()

    settings_running = True
    bg_color_button = Button("Renk Değiştir", (WIDTH // 2, HEIGHT // 2 - 150), change_bg_color_callback)
    bg_image_button = Button("Arka Plan Resmi Seç", (WIDTH // 2, HEIGHT // 2 - 100), select_bg_image)
    character_button = Button("Karakter Resmi Seç", (WIDTH // 2, HEIGHT // 2 - 50), select_character_image)
    back_button = Button("Geri", (WIDTH // 2, HEIGHT // 2), back_to_menu)

    while settings_running:
        screen.fill(BG_COLOR)
        for button in [bg_color_button, bg_image_button, character_button, back_button]:
            button.check_hover()
            button.draw(screen)
        
        # Önizlemeleri butonların altına yerleştir
        preview_background_image()
        preview_character_image()

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            for button in [bg_color_button, bg_image_button, character_button, back_button]:
                button.check_click(event)

def show_pause_menu():
    def resume_game():
        nonlocal paused_running
        paused_running = False
        global game_state
        game_state = "playing"  # Oyun durumunu "playing" olarak ayarla

    def quit_to_menu():
        nonlocal paused_running
        paused_running = False
        global game_state
        game_state = "menu"  # Menüye dönme işlevi

    paused_running = True
    resume_button = Button("Devam Et", (WIDTH // 2, HEIGHT // 2 - 50), resume_game)
    menu_button = Button("Menüye Dön", (WIDTH // 2, HEIGHT // 2), quit_to_menu)

    while paused_running:
        screen.fill(BG_COLOR)
        title_text = font.render("Oyun Duraklatıldı", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))

        for button in [resume_button, menu_button]:
            button.check_hover()
            button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            for button in [resume_button, menu_button]:
                button.check_click(event)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def start_game():
    global game_state
    game_state = "playing"
    
    player = Player()
    platforms = pygame.sprite.Group()
    create_platforms(platforms)

    while game_state == "playing":
        screen.fill(BG_COLOR)  # Arka plan rengini doldur
        if background:
            # Arka planı ekranda düzgün bir şekilde göster
            screen.blit(background, (0, bg_y % HEIGHT))
            screen.blit(background, (0, bg_y % HEIGHT - HEIGHT))
        
        player.update(platforms)
        platforms.update()  # `platforms.update()` çağrısında `player` argümanı geçmeyin

        screen.blit(player.image, player.rect)
        platforms.draw(screen)

        score_text = font.render(f"Puan: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = "paused"
                    show_pause_menu()

show_menu()
