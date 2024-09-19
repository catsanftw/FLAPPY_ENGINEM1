import pygame
import random
import numpy as np
import sounddevice as sd

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GROUND_HEIGHT = 100

# Game settings
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
PIPE_WIDTH = 70
PIPE_HEIGHT = 500
PIPE_GAP = 160
BIRD_JUMP = -10
GRAVITY = 0.5
PIPE_SPEED = 3

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 150, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Font
font = pygame.font.SysFont(None, 48)

# Generate a sound wave
def generate_sound_wave(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    return wave

# Create sounds
jump_sound_wave = generate_sound_wave(440, 0.1)
game_over_sound_wave = generate_sound_wave(220, 0.3)

# Bird class
class Bird:
    def __init__(self):
        self.x = 60
        self.y = SCREEN_HEIGHT // 2
        self.width = BIRD_WIDTH
        self.height = BIRD_HEIGHT
        self.velocity = 0
        self.alive = True

    def draw(self):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))

    def update(self):
        if self.alive:
            self.velocity += GRAVITY
            self.y += self.velocity

    def jump(self):
        self.velocity = BIRD_JUMP
        sd.play(jump_sound_wave, 44100)  # Play jump sound asynchronously

    def reset(self):
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.alive = True

# Pipe class
class Pipe:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.height = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - GROUND_HEIGHT)
        self.passed = False

    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x, 0, PIPE_WIDTH, self.height))
        pygame.draw.rect(screen, GREEN, (self.x, self.height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - self.height - PIPE_GAP - GROUND_HEIGHT))

    def update(self):
        self.x -= PIPE_SPEED

# Main game function
def main_game():
    clock = pygame.time.Clock()
    bird = Bird()
    pipes = [Pipe()]
    score = 0
    running = True
    game_over = False
    game_started = False

    while running:
        screen.fill(BLUE)

        # Draw ground
        pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_started:
                        game_started = True  # Start the game on the first space press
                    if not game_over:
                        bird.jump()
                    else:
                        # Restart the game
                        bird.reset()
                        pipes = [Pipe()]
                        score = 0
                        game_over = False

        # Game logic
        if not game_over and game_started:
            bird.update()

            # Add new pipes
            if pipes[-1].x < SCREEN_WIDTH - 300:
                pipes.append(Pipe())

            # Update pipes and check for collisions
            for pipe in pipes:
                pipe.update()
                if pipe.x + PIPE_WIDTH < 0:
                    pipes.remove(pipe)

                # Check for score
                if pipe.x + PIPE_WIDTH < bird.x and not pipe.passed:
                    score += 1
                    pipe.passed = True

                # Check for collision with pipes
                if bird.x + BIRD_WIDTH > pipe.x and bird.x < pipe.x + PIPE_WIDTH:
                    if bird.y < pipe.height or bird.y + BIRD_HEIGHT > pipe.height + PIPE_GAP:
                        bird.alive = False
                        game_over = True
                        sd.play(game_over_sound_wave, 44100)  # Play game over sound asynchronously

            # Check if bird hits the ground or flies too high
            if bird.y + BIRD_HEIGHT > SCREEN_HEIGHT - GROUND_HEIGHT or bird.y < 0:
                bird.alive = False
                game_over = True
                sd.play(game_over_sound_wave, 44100)  # Play game over sound asynchronously

        # Draw pipes and bird
        for pipe in pipes:
            pipe.draw()
        bird.draw()

        # Display score
        score_text = font.render(str(score), True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 50))

        if game_over:
            game_over_text = font.render("Game Over", True, WHITE)
            restart_text = font.render("Press SPACE to restart", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

# Run the game
if __name__ == "__main__":
    main_game()
