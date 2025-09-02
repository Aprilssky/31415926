import pygame
import random
import time
from typing import List, Tuple, Optional

# 初始化 Pygame
pygame.init()

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

class Grid:
    def __init__(self, width: int, height: int, cell_size: int):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.obstacles = set()  # 存储障碍物位置
        self.entities = []  # 存储网格中的实体
        
    def add_obstacle(self, position: Tuple[int, int]):
        """添加障碍物"""
        if 0 <= position[0] < self.width and 0 <= position[1] < self.height:
            self.obstacles.add(position)
            
    def add_entity(self, entity):
        """添加实体到网格"""
        self.entities.append(entity)
        
    def is_valid_position(self, position: Tuple[int, int]) -> bool:
        """检查位置是否有效（在网格内且没有障碍物）"""
        x, y = position
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
            
        # 检查是否有障碍物
        if position in self.obstacles:
            return False
            
        # 检查是否有其他实体（除了自己）
        for entity in self.entities:
            if entity.position == position and entity != self:
                return False
                
        return True
        
    def draw(self, screen):
        """绘制网格"""
        total_width = self.width * self.cell_size
        total_height = self.height * self.cell_size
        
        # 绘制背景
        screen.fill(WHITE)
        
        # 绘制网格线
        for x in range(0, total_width + 1, self.cell_size):
            pygame.draw.line(screen, BLACK, (x, 0), (x, total_height))
        for y in range(0, total_height + 1, self.cell_size):
            pygame.draw.line(screen, BLACK, (0, y), (total_width, y))
        
        # 绘制坐标标签
        font = pygame.font.SysFont(None, 20)
        for i in range(self.width):
            text = font.render(str(i), True, BLACK)
            screen.blit(text, (i * self.cell_size + 5, 5))
        for i in range(self.height):
            text = font.render(str(i), True, BLACK)
            screen.blit(text, (5, i * self.cell_size + 5))
            
        # 绘制障碍物
        for obstacle in self.obstacles:
            x = obstacle[0] * self.cell_size
            y = obstacle[1] * self.cell_size
            pygame.draw.rect(screen, GRAY, (x, y, self.cell_size, self.cell_size))


class Entity:
    def __init__(self, grid: Grid, color: Tuple[int, int, int] = RED):
        self.grid = grid
        self.color = color
        self.position = (0, 0)
        self.target_position = None
        self.path = []
        self.current_step = 0
        self.moving = False
        
        # 随机放置实体到有效位置
        self.place_randomly()
        
    def place_randomly(self):
        """将实体随机放置到有效位置"""
        valid_positions = []
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                if self.grid.is_valid_position((x, y)):
                    valid_positions.append((x, y))
                    
        if valid_positions:
            self.position = random.choice(valid_positions)
        
    def move(self, new_position: Tuple[int, int]):
        """将实体移动到新位置"""
        if self.grid.is_valid_position(new_position):
            self.position = new_position
            return True
        return False
        
    def find_shortest_path(self, target_position: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """使用A*算法寻找从当前位置到目标位置的最短路径，避开障碍物和其他实体"""
        # 如果目标位置无效，返回None
        if not self.grid.is_valid_position(target_position):
            return None
            
        # 如果已经在目标位置，返回空路径
        if self.position == target_position:
            return []
            
        # 简单的A*算法实现
        open_set = {self.position}
        closed_set = set()
        g_score = {self.position: 0}  # 从起点到当前点的成本
        f_score = {self.position: self.heuristic(self.position, target_position)}  # 估计的总成本
        came_from = {}  # 记录路径
        
        while open_set:
            # 找到f_score最小的节点
            current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
            
            # 如果到达目标，重建路径
            if current == target_position:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
                
            open_set.remove(current)
            closed_set.add(current)
            
            # 检查所有相邻节点
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # 上下左右四个方向
                neighbor = (current[0] + dx, current[1] + dy)
                
                # 如果邻居节点无效或已在关闭列表中，跳过
                if not self.grid.is_valid_position(neighbor) or neighbor in closed_set:
                    continue
                    
                # 计算从起点到邻居节点的成本
                tentative_g_score = g_score[current] + 1
                
                # 如果这是一个更好的路径，更新
                if neighbor not in open_set or tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, target_position)
                    if neighbor not in open_set:
                        open_set.add(neighbor)
                        
        # 如果没有找到路径
        return None
        
    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """计算两点之间的曼哈顿距离（启发式函数）"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
    def set_random_target(self):
        """随机选择一个有效目标位置"""
        valid_positions = []
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                if self.grid.is_valid_position((x, y)) and (x, y) != self.position:
                    valid_positions.append((x, y))
                    
        if valid_positions:
            self.target_position = random.choice(valid_positions)
            
            # 计算最短路径
            self.path = self.find_shortest_path(self.target_position)
            self.current_step = 0
            self.moving = self.path is not None
            
            if self.moving:
                print(f"实体目标位置: {self.target_position}")
                print(f"路径长度: {len(self.path)} 步")
            else:
                print("无法找到有效路径!")
        else:
            print("没有有效目标位置!")
        
    def update(self):
        """更新实体状态"""
        if self.moving and self.path and self.current_step < len(self.path):
            next_pos = self.path[self.current_step]
            if self.move(next_pos):
                self.current_step += 1
                
                # 检查是否到达目标
                if self.current_step == len(self.path):
                    self.moving = False
                    print("移动完成!")
            else:
                # 如果移动失败（例如被其他实体阻挡），重新规划路径
                print("移动被阻挡，重新规划路径...")
                self.set_random_target()
                
    def draw(self, screen):
        """绘制实体"""
        x = self.position[0] * self.grid.cell_size + self.grid.cell_size // 2
        y = self.position[1] * self.grid.cell_size + self.grid.cell_size // 2
        pygame.draw.circle(screen, self.color, (x, y), self.grid.cell_size // 3)
        
        # 如果正在移动，绘制目标位置
        if self.target_position:
            tx = self.target_position[0] * self.grid.cell_size + self.grid.cell_size // 2
            ty = self.target_position[1] * self.grid.cell_size + self.grid.cell_size // 2
            pygame.draw.circle(screen, GREEN, (tx, ty), 5)
            
        # 绘制路径
        if self.path:
            for i, pos in enumerate(self.path):
                if i >= self.current_step:  # 只绘制未走过的路径
                    px = pos[0] * self.grid.cell_size + self.grid.cell_size // 2
                    py = pos[1] * self.grid.cell_size + self.grid.cell_size // 2
                    pygame.draw.circle(screen, BLUE, (px, py), 2)


def main():
    # 设置参数
    grid_width = 15
    grid_height = 10
    cell_size = 50
    screen_width = grid_width * cell_size
    screen_height = grid_height * cell_size + 50  # 额外空间用于状态显示
    
    # 创建屏幕
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("多实体移动模拟")
    
    # 创建网格
    grid = Grid(grid_width, grid_height, cell_size)
    
    # 添加一些随机障碍物
    for _ in range(20):
        x = random.randint(0, grid_width - 1)
        y = random.randint(0, grid_height - 1)
        grid.add_obstacle((x, y))
    
    # 创建3个不同颜色的实体
    entities = []
    colors = [RED, BLUE, YELLOW, PURPLE]
    for i in range(3):
        entity = Entity(grid, colors[i])
        entities.append(entity)
        grid.add_entity(entity)
    
    # 为每个实体设置初始目标
    for entity in entities:
        entity.set_random_target()
    
    # 游戏循环
    running = True
    clock = pygame.time.Clock()
    last_move_time = time.time()
    move_interval = 0.5  # 移动间隔（秒）
    
    while running:
        current_time = time.time()
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # 空格键为所有实体设置新目标
                    for entity in entities:
                        entity.set_random_target()
        
        # 更新实体位置
        if current_time - last_move_time > move_interval:
            for entity in entities:
                entity.update()
            last_move_time = current_time
        
        # 如果实体停止移动，设置新目标
        for entity in entities:
            if not entity.moving:
                entity.set_random_target()
        
        # 绘制
        grid.draw(screen)
        for entity in entities:
            entity.draw(screen)
        
        # 显示状态信息
        font = pygame.font.SysFont(None, 24)
        status_text = "实体状态: "
        for i, entity in enumerate(entities):
            status_text += f"E{i}:{entity.position} "
            if entity.moving:
                status_text += f"(→{entity.target_position}) "
        text = font.render(status_text, True, BLACK)
        screen.blit(text, (10, screen_height - 40))
        
        # 显示操作提示
        hint_text = "按空格键为所有实体设置新目标"
        hint = font.render(hint_text, True, BLACK)
        screen.blit(hint, (10, screen_height - 20))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()
