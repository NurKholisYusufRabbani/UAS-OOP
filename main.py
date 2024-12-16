import pygame
import random
from abc import ABC, abstractmethod

# Ukuran kartu dan margin antar kartu.
CARD_WIDTH = 70
CARD_HEIGHT = 100
MARGIN = 20

# Ukuran papan permainan (4x4)
BOARD_SIZE = (4, 4)

# **Abstraction**
# Kelas abstrak 'BaseCard' digunakan untuk mendefinisikan kerangka dasar kartu,
# yang harus diimplementasikan oleh kelas turunan seperti Card dan SpecialCard.
class BaseCard(ABC):
    # Kelas abstrak untuk semua kartu
    @abstractmethod
    def draw(self, screen):
        pass

    @abstractmethod
    def flip(self):
        pass

# **Encapsulation**
# Menggunakan atribut private seperti 'self.flipped' dan 'self.rect'
# yang hanya bisa diakses atau dimodifikasi melalui metode yang telah disediakan
class Card(BaseCard):
    # Kelas untuk kartu biasa
    def __init__(self, value, x, y, front_image, back_image):
        self.value = value  # Nilai kartu
        self.flipped = False  # Status kartu terbuka atau tertutup (Encapsulation)
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)  # Posisi dan ukuran kartu
        self.front_image = pygame.image.load(front_image).convert_alpha()  # Gambar depan kartu
        self.front_image = pygame.transform.smoothscale(self.front_image, (CARD_WIDTH, CARD_HEIGHT))
        self.back_image = pygame.image.load(back_image).convert_alpha()  # Gambar belakang kartu
        self.back_image = pygame.transform.scale(self.back_image, (CARD_WIDTH, CARD_HEIGHT))

    # **Encapsulation**
    # Metode untuk menggambar kartu di layar, menjaga detail implementasi kartu
    # tidak bisa diakses langsung oleh luar
    def draw(self, screen):
        if self.flipped:
            screen.blit(self.front_image, self.rect.topleft)  # Tampilkan gambar depan
        else:
            screen.blit(self.back_image, self.rect.topleft)  # Tampilkan gambar belakang

    # **Encapsulation**
    # Metode untuk membalikkan kartu, mengubah status flipped
    def flip(self):
        self.flipped = not self.flipped

    # **Encapsulation**
    # Metode untuk mendapatkan nilai kartu
    def get_value(self):
        return self.value

    # **Encapsulation**
    # Menyediakan metode untuk mengecek apakah kartu terbuka
    def is_flipped(self):
        return self.flipped

# **Inheritance**
# Kelas SpecialCard mewarisi kelas Card dan menambahkan fungsionalitas baru berupa efek khusus
class SpecialCard(Card):
    # Kelas untuk kartu spesial
    def __init__(self, value, x, y, front_image, back_image, effect):
        super().__init__(value, x, y, front_image, back_image)  # Pewarisan properti dan metode dari Card
        self.effect = effect  # Efek khusus untuk kartu spesial
        self.effect_used = False  # Menandakan apakah efek sudah digunakan

    # **Polymorphism**
    # Mengubah perilaku metode 'use_effect' tergantung pada jenis efek kartu spesial
    def use_effect(self, game):
        if self.effect == "auto_match" and not self.effect_used:
            print("Efek kartu spesial: Auto match dua pasang kartu!")
            matched = 0
            unmatched_cards = [card for card in game.cards if not card.is_flipped()]

            # Mencari satu pasang kartu yang cocok dan membalikkan kartu
            for card in unmatched_cards:
                if matched == 1:
                    break
                for pair in unmatched_cards:
                    if card != pair and card.get_value() == pair.get_value():
                        card.flip()
                        pair.flip()
                        game.matches += 1
                        matched += 1
                        break

            self.effect_used = True  # Efek telah digunakan

# **MemoryCardGame class**
# Kelas utama yang mengelola permainan
class MemoryCardGame:
    def __init__(self):
        pygame.init()
        self.board_size = BOARD_SIZE
        self.card_width = CARD_WIDTH
        self.card_height = CARD_HEIGHT
        self.margin = MARGIN
        self.screen_width = self.board_size[0] * (self.card_width + self.margin) + self.margin
        self.screen_height = self.board_size[1] * (self.card_height + self.margin) + self.margin + 50  # Tambahkan 50 piksel untuk teks "Matches:"
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Memory Card Game")
        self.clock = pygame.time.Clock()
        self.running = True  # Status game berjalan atau tidak
        self.cards = []  # Daftar kartu
        self.selected_cards = []  # Kartu yang dipilih
        self.matches = 0  # Jumlah pasangan yang cocok
        self.last_flip_time = 0  # Waktu pembalikan kartu terakhir
        self.create_cards()
        self.bg_image = pygame.image.load(f"assets/background.png").convert()  
        self.bg_image = pygame.transform.scale(self.bg_image, (self.screen_width, self.screen_height))

    def create_cards(self):
        # **Polymorphism**
        # Membuat dan mengacak kartu-kartu untuk permainan
        values = list(range(1, (self.board_size[0] * self.board_size[1]) // 2 + 1)) * 2
        random.shuffle(values)
        
        for i, value in enumerate(values):
            x = (i % self.board_size[0]) * (CARD_WIDTH + MARGIN) + MARGIN
            y = (i // self.board_size[0]) * (CARD_HEIGHT + MARGIN) + MARGIN
            self.cards.append(Card(value, x, y, f"assets/front{value}.png", "assets/back.png"))

        # Mengubah salah satu kartu menjadi kartu spesial dengan efek
        special_index = random.randint(0, len(self.cards) - 1)
        card = self.cards[special_index]
        self.cards[special_index] = SpecialCard(card.get_value(), card.rect.x, card.rect.y,
                                                f"assets/front{card.get_value()}.png", "assets/back.png", "auto_match")

    def handle_events(self):
        # Menangani input dari pengguna
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False  # Jika quit, game akan berhenti
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for card in self.cards:
                    if card.rect.collidepoint(pos) and not card.is_flipped() and len(self.selected_cards) < 2:
                        card.flip()
                        self.selected_cards.append(card)
                        self.last_flip_time = pygame.time.get_ticks()

                        # Jika kartu spesial digunakan, aktifkan efeknya
                        if isinstance(card, SpecialCard):
                            card.use_effect(self)

    def check_match(self):
        # Memeriksa apakah dua kartu yang dipilih cocok
        if len(self.selected_cards) == 2:
            card1, card2 = self.selected_cards
            if card1.get_value() == card2.get_value():
                self.matches += 1
                self.selected_cards.clear()  # Clear setelah cocok
            elif pygame.time.get_ticks() - self.last_flip_time > 1000:
                card1.flip()
                card2.flip()
                self.selected_cards.clear()  # Clear jika tidak cocok

    def draw(self):
        # Menggambar semua elemen game di layar
        self.screen.blit(self.bg_image, (0, 0))  # Gambar latar belakang
        for card in self.cards:
            card.draw(self.screen)  # Gambar semua kartu

        # Hitung posisi teks "Matches:"
        matches_x = 10
        matches_y = self.screen_height - 20

        # Menampilkan jumlah pasangan yang cocok
        font = pygame.font.Font(None, 36)
        text = font.render(f"Matches: {self.matches}", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.bottomleft = (matches_x, matches_y)
        self.screen.blit(text, text_rect)

        # Cek jika game sudah selesai
        if self.matches == len(self.cards) // 2:
            font = pygame.font.Font(None, 72)
            text = font.render("You Win!", True, (255, 255, 255))
            text_rect = text.get_rect()
            text_rect.center = (self.screen_width // 2, self.screen_height // 2)
            self.screen.blit(text, text_rect)
            
    def run(self):
        # Loop utama game
        while self.running:
            self.handle_events()
            self.check_match()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

            # Jika permainan selesai, keluar otomatis
            if self.matches == len(self.cards) // 2:
                pygame.time.wait(2000)  # Tunggu 2 detik sebelum keluar
                self.running = False

        pygame.quit()

# **Main Execution**
if __name__ == "__main__":
    game = MemoryCardGame()  # Membuat objek permainan
    game.run()  # Menjalankan permainan
