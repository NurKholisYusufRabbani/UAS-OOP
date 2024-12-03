import pygame
import random
from abc import ABC, abstractmethod

# Konstanta
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CARD_WIDTH, CARD_HEIGHT = 70, 100  # Ukuran kartu disesuaikan untuk papan 4x4
MARGIN = 10  # Margin antar kartu
FPS = 60

# Ukuran papan 4x4
BOARD_SIZE = (4, 4)

# Kelas abstrak untuk dasar semua kartu
class BaseCard(ABC):
    @abstractmethod
    def draw(self, screen):
        pass

    @abstractmethod
    def flip(self):
        pass

# Kelas Card dasar
class Card(BaseCard):
    def __init__(self, value, x, y):
        self.__value = value  # Private attribute
        self._flipped = False  # Protected attribute
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

    def draw(self, screen):
        if self._flipped:
            pygame.draw.rect(screen, WHITE, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)
            font = pygame.font.Font(None, 40)
            text = font.render(str(self.__value), True, BLACK)
            screen.blit(
                text,
                (self.rect.x + CARD_WIDTH // 2 - text.get_width() // 2,
                 self.rect.y + CARD_HEIGHT // 2 - text.get_height() // 2),
            )
        else:
            pygame.draw.rect(screen, BLACK, self.rect)

    def flip(self):
        self._flipped = not self._flipped

    # Getter untuk value
    def get_value(self):
        return self.__value

    # Setter untuk value (dengan validasi)
    def set_value(self, value):
        if value > 0:
            self.__value = value
        else:
            raise ValueError("Value must be positive")

    # Getter untuk flipped state
    def is_flipped(self):
        return self._flipped

# Kelas kartu spesial
class SpecialCard(Card):
    def __init__(self, value, x, y, effect):
        super().__init__(value, x, y)
        self.__effect = effect  # Private attribute
        self.__used = False  # Private attribute

    def activate_effect(self, game):
        if not self.__used:
            print(f"Special Effect Activated: {self.__effect}")
            if self.__effect == "Reveal All":
                game.reveal_all_cards()
            self.__used = True

    def is_used(self):  # Getter untuk cek apakah efek sudah digunakan
        return self.__used

    def get_effect(self):  # Getter untuk efek
        return self.__effect

    def draw(self, screen):
        if self._flipped:
            pygame.draw.rect(screen, (0, 255, 0), self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)
            font = pygame.font.Font(None, 40)
            text = font.render(str(self.get_value()), True, BLACK)
            screen.blit(
                text,
                (self.rect.x + CARD_WIDTH // 2 - text.get_width() // 2,
                 self.rect.y + CARD_HEIGHT // 2 - text.get_height() // 2),
            )
        else:
            pygame.draw.rect(screen, BLACK, self.rect)

# Kelas Game
class MemoryCardGame:
    def __init__(self):
        self.board_size = BOARD_SIZE
        self.screen_width = self.board_size[0] * (CARD_WIDTH + MARGIN) + MARGIN
        self.screen_height = self.board_size[1] * (CARD_HEIGHT + MARGIN) + MARGIN
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Memory Card Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.cards = []
        self.selected_cards = []
        self.matches = 0
        self.last_flip_time = 0
        self.create_cards()
        self.revealing_all_cards = False

    def create_cards(self):
        values = list(range(1, (self.board_size[0] * self.board_size[1]) // 2 + 1)) * 2
        random.shuffle(values)
        special_positions = random.sample(range(len(values)), 1)

        for i, value in enumerate(values):
            x = (i % self.board_size[0]) * (CARD_WIDTH + MARGIN) + MARGIN
            y = (i // self.board_size[0]) * (CARD_HEIGHT + MARGIN) + MARGIN

            if i in special_positions:
                self.cards.append(SpecialCard(value, x, y, "Reveal All"))
            else:
                self.cards.append(Card(value, x, y))

    def check_match(self):
        if len(self.selected_cards) == 2:
            card1, card2 = self.selected_cards
            if card1.get_value() == card2.get_value():
                print(f"Match found: {card1.get_value()}")
                self.matches += 1
                self.selected_cards.clear()
            else:
                if pygame.time.get_ticks() - self.last_flip_time > 1000:
                    card1.flip()
                    card2.flip()
                    self.selected_cards.clear()

    def reveal_all_cards(self):
        self.revealing_all_cards = True
        for card in self.cards:
            card.flip()
        pygame.time.set_timer(pygame.USEREVENT, 1000)

    def run(self):
        while self.running:
            self.screen.fill(WHITE)
            self.handle_events()
            self.draw()
            self.check_match()

            if self.revealing_all_cards and pygame.time.get_ticks() - self.last_flip_time > 1000:
                for card in self.cards:
                    card.flip()
                self.revealing_all_cards = False
                pygame.time.set_timer(pygame.USEREVENT, 0)

            pygame.display.flip()
            self.clock.tick(FPS)

            if self.matches == len(self.cards) // 2:
                print("You Win!")
                self.running = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for card in self.cards:
                    if card.rect.collidepoint(pos) and not card.is_flipped() and len(self.selected_cards) < 2:
                        card.flip()
                        self.selected_cards.append(card)
                        if isinstance(card, SpecialCard):
                            card.activate_effect(self)
                        self.last_flip_time = pygame.time.get_ticks()

    def draw(self):
        for card in self.cards:
            card.draw(self.screen)

# Main program
if __name__ == "__main__":
    game = MemoryCardGame()
    game.run()
    pygame.quit()
