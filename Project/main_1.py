import pygame
import random
import heapq
from collections import deque

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 50, 255)
GREEN = (50, 200, 50)
RED = (255, 50, 50)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 100)
DARK_BLUE = (30, 30, 150)

# Размеры
TILE_SIZE = 40
GRID_SIZE = 12
WINDOW_MARGIN_BOTTOM = 150
MAX_ATTEMPTS = 50


# Класс для самой игры
class Game:
    # Основные переменные
    def __init__(self):
        self.level = 1
        self.grid_size = GRID_SIZE
        self.max_obstacles = self.grid_size ** 2 - 2
        self.maze = []
        self.player = Player()
        self.end = (self.grid_size - 1, self.grid_size - 1)
        self.show_path = False
        self.path = []
        self.window_width = self.grid_size * TILE_SIZE
        self.window_height = self.grid_size * TILE_SIZE + WINDOW_MARGIN_BOTTOM
        self.show_btn = pygame.Rect(10, self.grid_size * TILE_SIZE + 50, 150, 35)
        self.hide_btn = pygame.Rect(170, self.grid_size * TILE_SIZE + 50, 150, 35)
        self.restart_btn = pygame.Rect(330, self.grid_size * TILE_SIZE + 50, 150, 35)
        self.won = False
        self.lost = False
        self.steps_left = 100
        self.selected_algorithm = "A*"
        self.alg_btns = {
            "A*": pygame.Rect(10, self.grid_size * TILE_SIZE + 100, 80, 30),
            "BFS": pygame.Rect(100, self.grid_size * TILE_SIZE + 100, 80, 30),
            "Dijkstra": pygame.Rect(190, self.grid_size * TILE_SIZE + 100, 100, 30),
        }

        self.music_files = [
            "music/track1.mp3",
            "music/track2.mp3",
            "music/track3.mp3",
            "music/track4.mp3",
            "music/track5.mp3"
        ]
        self.current_track = 0
        self.music_volume = 0.5
        pygame.mixer.init()
        self.play_music()
        self.generate_maze()

        self.generate_maze()

    # Начать проигрывать музыку
    def play_music(self):
        pygame.mixer.music.load(self.music_files[self.current_track])
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(-1)

    # Остановить или продолжить играть музыку
    def stop_or_play_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

    # Следующая музыка
    def next_track(self):
        self.current_track = (self.current_track + 1) % len(self.music_files)
        self.play_music()

    # Предыдущая музыка
    def previous_track(self):
        self.current_track = (self.current_track - 1) % len(self.music_files)
        self.play_music()

    # Погромче
    def volume_up(self):
        self.music_volume = min(1.0, self.music_volume + 0.1)
        pygame.mixer.music.set_volume(self.music_volume)

    # Потише
    def volume_down(self):
        self.music_volume = max(0.0, self.music_volume - 0.1)
        pygame.mixer.music.set_volume(self.music_volume)

    # Генерация лабиринта
    def generate_maze(self):
        attempts = 0
        obstacles = min(20 + self.level * 2, self.max_obstacles)
        self.path = []

        while attempts < MAX_ATTEMPTS:
            # Рандомное распределение преград
            maze = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
            positions = [(x, y) for y in range(self.grid_size) for x in range(self.grid_size) if (x, y) not in [(0, 0), self.end]]
            random.shuffle(positions)

            for i in range(obstacles):
                x, y = positions[i]
                maze[y][x] = 1

            # Использование одного из алгоритмов для нахождения пути
            path = self.find_path(maze, (0, 0), self.end)
            if path:
                self.maze = maze
                self.player.reset()
                self.steps_left = max(10, 100 - (self.level - 1) * 5)
                if len(path) > self.steps_left:
                    self.won = True
                    self.lost = False
                    self.path = path
                else:
                    self.won = False
                    self.lost = False
                    self.path = path if self.show_path else []
                return
            attempts += 1

        # Не удалось сгенерировать проходимый лабиринт
        self.won = True
        self.lost = False
        self.steps_left = 1
        self.player.reset()
        self.path = []

    # Начать сначала
    def restart(self):
        self.level = 1
        self.generate_maze()

    # Найти путь при помощи разных алгоритмов
    def find_path(self, maze, start, end):
        if self.selected_algorithm == "A*":
            return a_star(maze, start, end)
        elif self.selected_algorithm == "BFS":
            return bfs(maze, start, end)
        elif self.selected_algorithm == "Dijkstra":
            return dijkstra(maze, start, end)
        return []


# Шаги пользователя
class Player:
    def __init__(self):
        self.pos = (0, 0)

    def reset(self):
        self.pos = (0, 0)

    def move(self, dx, dy, maze):
        x, y = self.pos
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] == 0:
            self.pos = (nx, ny)
            return True
        return False


# Алгоритм A* (данный код написан при помощи чата GPT, так как есть неизвестный алгоритм A*)
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star(maze, start, goal):
    open_set = [(heuristic(start, goal), 0, start)]
    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, _, current = heapq.heappop(open_set)
        if current == goal:
            break

        x, y = current
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)
            if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] == 0:
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor))
                    came_from[neighbor] = current

    return reconstruct_path(came_from, goal)


# BFS (данный код написан с небольшой помощью чата GPT, так как я не знала, как известный мне алгоритм подкорректировать под нужный проект)
def bfs(maze, start, goal):
    queue = deque([start])
    came_from = {start: None}

    while queue:
        current = queue.popleft()
        if current == goal:
            break

        x, y = current
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)
            if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] == 0 and neighbor not in came_from:
                came_from[neighbor] = current
                queue.append(neighbor)

    return reconstruct_path(came_from, goal)


# Дейкстра (данный код написан с небольшой помощью чата GPT, так как я не знала, как известный мне алгоритм подкорректировать под нужный проект)
def dijkstra(maze, start, goal):
    heap = [(0, start)]
    came_from = {}
    cost_so_far = {start: 0}

    while heap:
        cost, current = heapq.heappop(heap)
        if current == goal:
            break

        x, y = current
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)
            if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] == 0:
                new_cost = cost + 1
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    heapq.heappush(heap, (new_cost, neighbor))
                    came_from[neighbor] = current

    return reconstruct_path(came_from, goal)


# Генерация пути
def reconstruct_path(came_from, goal):
    if goal not in came_from:
        return []
    path = []
    while goal in came_from:
        path.append(goal)
        goal = came_from[goal]
    path.reverse()
    return path


# Отрисовка всей игры
def draw(screen, game):
    screen.fill(WHITE)
    maze = game.maze
    size = game.grid_size

    for y in range(size):
        for x in range(size):
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            color = WHITE if maze[y][x] == 0 else BLACK
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)

    if game.show_path:
        for (x, y) in game.path:
            pygame.draw.rect(screen, YELLOW, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    px, py = game.player.pos
    ex, ey = game.end
    pygame.draw.rect(screen, RED, (px*TILE_SIZE, py*TILE_SIZE, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, GREEN, (ex*TILE_SIZE, ey*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    font = pygame.font.SysFont(None, 24)
    steps = font.render(f"Осталось шагов: {game.steps_left}", True, BLACK)
    level = font.render(f"Уровень: {game.level}", True, BLACK)
    algo = font.render(f"Алгоритм: {game.selected_algorithm}", True, BLACK)

    screen.blit(steps, (10, game.grid_size * TILE_SIZE + 10))
    screen.blit(level, (game.window_width - 150, game.grid_size * TILE_SIZE + 10))
    screen.blit(algo, (10, game.grid_size * TILE_SIZE + 130))

    pygame.draw.rect(screen, BLUE, game.show_btn)
    pygame.draw.rect(screen, DARK_BLUE if game.show_path else GRAY, game.hide_btn)
    pygame.draw.rect(screen, BLUE, game.restart_btn)

    screen.blit(font.render("Показать путь", True, WHITE), (game.show_btn.x + 10, game.show_btn.y + 5))
    screen.blit(font.render("Скрыть путь", True, WHITE), (game.hide_btn.x + 10, game.hide_btn.y + 5))
    screen.blit(font.render("Начать сначала", True, WHITE), (game.restart_btn.x + 10, game.restart_btn.y + 5))

    for name, rect in game.alg_btns.items():
        pygame.draw.rect(screen, DARK_BLUE if game.selected_algorithm == name else GRAY, rect)
        screen.blit(font.render(name, True, WHITE), (rect.x + 10, rect.y + 5))

    if game.won:
        msg = pygame.font.SysFont(None, 48).render("Вы выиграли!", True, (0, 180, 0))
        screen.blit(msg, ((game.window_width - msg.get_width()) // 2, (game.window_height - msg.get_height()) // 2))
    if game.lost:
        msg = pygame.font.SysFont(None, 48).render("Вы проиграли!", True, (200, 0, 0))
        screen.blit(msg, ((game.window_width - msg.get_width()) // 2, (game.window_height - msg.get_height()) // 2))


def main():
    pygame.init()
    game = Game()
    screen = pygame.display.set_mode((game.window_width, game.window_height))
    pygame.display.set_caption("Лабиринт")
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN and not (game.won or game.lost):
                moved = False
                # Шаги
                if event.key in [pygame.K_LEFT, pygame.K_a]:
                    moved = game.player.move(-1, 0, game.maze)
                if event.key in [pygame.K_RIGHT, pygame.K_d]:
                    moved = game.player.move(1, 0, game.maze)
                if event.key in [pygame.K_UP, pygame.K_w]:
                    moved = game.player.move(0, -1, game.maze)
                if event.key in [pygame.K_DOWN, pygame.K_s]:
                    moved = game.player.move(0, 1, game.maze)
                if moved:
                    game.steps_left -= 1
                    if game.steps_left <= 0:
                        game.lost = True
                    if game.show_path:
                        game.path = game.find_path(game.maze, game.player.pos, game.end)

                # Изменения музыки
                if event.key == pygame.K_0:
                    game.stop_or_play_music()
                elif event.key == pygame.K_9:
                    game.volume_up()
                elif event.key == pygame.K_8:
                    game.volume_down()
                elif event.key == pygame.K_2:
                    game.next_track()
                elif event.key == pygame.K_1:
                    game.previous_track()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Показать путь
                if game.show_btn.collidepoint(event.pos):
                    game.show_path = True
                    game.path = game.find_path(game.maze, game.player.pos, game.end)
                # Скрыть путь
                elif game.hide_btn.collidepoint(event.pos):
                    game.show_path = False
                    game.path = []
                # Начать сначала
                elif game.restart_btn.collidepoint(event.pos):
                    game.restart()

                # Выбрать алгоритм
                for name, rect in game.alg_btns.items():
                    if rect.collidepoint(event.pos):
                        game.selected_algorithm = name
                        if game.show_path:
                            game.path = game.find_path(game.maze, game.player.pos, game.end)

        # Следующий уровень
        if not game.won and not game.lost and game.player.pos == game.end:
            game.level += 1
            game.generate_maze()

        draw(screen, game)
        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
