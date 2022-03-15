import pygame
import random
import pdb
import os
import re
import sys

from InputBox import InputBox
try:
   import queue
except ImportError:
   import Queue as queue

pygame.init()

WIDTH, HEIGHT = 900, 500
GRID_WIDTH = 30
GRID_HEIGHT = 30

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breadth First Search Visualization ({}x{})".format(GRID_WIDTH, GRID_HEIGHT))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (128,0,128)
VIOLET = (238,130,238)
BACKGROUND_RGB = (34, 113, 60)


FPS = 60

SQUARE_WIDTH, SQUARE_HEIGHT = 10, 10

start_x, start_y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
goal_x, goal_y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)

LEGEND_FONT = pygame.font.SysFont('comicsans', 20)

frontier_text = LEGEND_FONT.render('frontier', 1, WHITE)
neighbor_text = LEGEND_FONT.render('neighbor(s)', 1, WHITE)
current_text = LEGEND_FONT.render('current node', 1, WHITE)
path_text = LEGEND_FONT.render('path', 1, WHITE)
searched_text = LEGEND_FONT.render('searched nodes', 1, WHITE)
start_goal_text = LEGEND_FONT.render('start/goal', 1, WHITE)
border_text = LEGEND_FONT.render('border', 1, WHITE)

clock = pygame.time.Clock()
input_box_src_text = LEGEND_FONT.render('Enter a start coordinate', 1, WHITE)
input_box_dest_text = LEGEND_FONT.render('Enter a destination coordinate', 1, WHITE)

border_note_text = LEGEND_FONT.render('Click and drag to add borders', 1, WHITE)
  
def draw_window(grid, src_input_box, dest_input_box, starting_node, goal_node, frontier, parent):
  WIN.fill(BACKGROUND_RGB)
  for i, row in enumerate(grid):
    for j, square in enumerate(row):
      if parent.has_key((i, j)):
        pygame.draw.rect(WIN, BLUE, square.rect)
      elif square.is_border:
        pygame.draw.rect(WIN, WHITE, square.rect)
      else:
        pygame.draw.rect(WIN, BLACK, square.rect)
      if (i, j) in frontier:
        pygame.draw.rect(WIN, GREEN, square.rect)

  pygame.draw.rect(WIN, VIOLET, grid[starting_node[0]][starting_node[1]].rect)
  pygame.draw.rect(WIN, VIOLET, grid[goal_node[0]][goal_node[1]].rect)

  pygame.draw.rect(WIN, GREEN, pygame.Rect(50, 5, SQUARE_WIDTH, SQUARE_HEIGHT))
  pygame.draw.rect(WIN, YELLOW, pygame.Rect(50, 20, SQUARE_WIDTH, SQUARE_HEIGHT))
  pygame.draw.rect(WIN, RED, pygame.Rect(50, 35, SQUARE_WIDTH, SQUARE_HEIGHT))
  pygame.draw.rect(WIN, PURPLE, pygame.Rect(50, 50, SQUARE_WIDTH, SQUARE_HEIGHT))
  pygame.draw.rect(WIN, BLUE, pygame.Rect(50, 65, SQUARE_WIDTH, SQUARE_HEIGHT))
  pygame.draw.rect(WIN, VIOLET, pygame.Rect(50, 80, SQUARE_WIDTH, SQUARE_HEIGHT))
  pygame.draw.rect(WIN, WHITE, pygame.Rect(50, 95, SQUARE_WIDTH, SQUARE_HEIGHT))

  WIN.blit(frontier_text, (70, 5))
  WIN.blit(current_text, (70, 20))
  WIN.blit(neighbor_text, (70, 35))
  WIN.blit(path_text, (70, 50))
  WIN.blit(searched_text, (70, 65))
  WIN.blit(start_goal_text, (70, 80))
  WIN.blit(border_text, (70, 95))
  WIN.blit(border_note_text, (GRID_HEIGHT - 20, HEIGHT - 20))

  WIN.blit(input_box_src_text, (WIDTH - 230, 20))
  WIN.blit(input_box_dest_text, (WIDTH - 230, 90))

  src_input_box.draw(WIN)
  dest_input_box.draw(WIN)
     
  pygame.display.update()

def get_neighbors(grid, node):
  dxy = [(-1, 0), (0, 1), (1, 0), (0, -1)]#, (-1, -1), (-1, 1), (1, 1), (1, -1)] # each pair represents a change in the (x,y) coordinate
  valid_neighbors = []
  for p in dxy:
    if 0 <= node[0] + p[0] < GRID_WIDTH and 0 <= node[1] + p[1] < GRID_HEIGHT and not grid[node[0] + p[0]][node[1] + p[1]].is_border:
      valid_neighbors.append((node[0] + p[0], node[1] + p[1]))
  return valid_neighbors

def draw_path(grid, goal, parent):
  while goal != None:
    pygame.draw.rect(WIN, PURPLE, grid[goal[0]][goal[1]].rect)
    goal = parent[goal]
  pygame.display.update()

def try_parse_coords(coords):
  if re.search("^\s*\(?\d{1,2}\s*,\s*\d{1,2}\)?\s*$", coords):
    coords = coords.strip('() ').replace('.', ',')
    xy = coords.split(',')
    if 0 <= int(xy[0]) < GRID_WIDTH and 0 <= int(xy[1]) < GRID_HEIGHT:
      return (int(xy[0]), int(xy[1]))

class Rect:
  def __init__(self, rect, is_border):
    self.rect = rect
    self.is_border = is_border

def is_mouse_hovering(square, pos):
  x_len = SQUARE_WIDTH
  y_len = SQUARE_HEIGHT
  mos_x, mos_y = pos
  if mos_x > square.x and (mos_x < square.x + x_len):
      x_inside = True
  else: x_inside = False
  if mos_y > square.y and (mos_y < square.y + y_len):
      y_inside = True
  else: y_inside = False
  return x_inside and y_inside
    

def main():
  global start_x, start_y, goal_x, goal_y

  src_input_box = InputBox(WIDTH - 230, 35, 5, 40, text='({},{})'.format(start_x, start_y))
  dest_input_box = InputBox(WIDTH - 230, 105, 5, 40, text='({},{})'.format(goal_x, goal_y))

  grid = []
  
  run = True

  starting_node = (start_x, start_y)
  goal_node = (goal_x, goal_y)

  frontier = [starting_node]
  parent = {}
  parent[starting_node] = None

  found = False

  y = 10 # starting y-coordinate
  for i in range(GRID_WIDTH):
    x = WIDTH//2 - (GRID_WIDTH * SQUARE_WIDTH )//2 - 100  # starting x-coordinate
    
    row = []
    for j in range(GRID_HEIGHT):
      row.append(Rect(pygame.Rect((x, y), (SQUARE_WIDTH, SQUARE_HEIGHT)), False))
      x += 15 # add 15 pixels to keep squares spaced out
    grid.append(row)
    y += 15

  while run:
    clock.tick(FPS)
    pos = pygame.mouse.get_pos()
    if (pygame.mouse.get_pressed()[0]):
      for i, row in enumerate(grid):
        for j, elem in enumerate(row):
          if is_mouse_hovering(elem.rect, pos):
            elem.is_border = True

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          run = False
      if event.type == pygame.MOUSEBUTTONDOWN:
        for i, row in enumerate(grid):
          for j, elem in enumerate(row):
            if is_mouse_hovering(elem.rect, pos):
              elem.is_border = True
      
      if event.type == dest_input_box.RETURN_HIT:
        if src_input_box.active:
          if try_parse_coords(src_input_box.text):
            (start_x, start_y) = try_parse_coords(src_input_box.text)
            main()
            return
        elif dest_input_box.active:
          if try_parse_coords(dest_input_box.text):
            (goal_x, goal_y) = try_parse_coords(dest_input_box.text)
            main()
            return

      src_input_box.handle_event(event)
      dest_input_box.handle_event(event)

    if not run:
      break

    src_input_box.update()
    dest_input_box.update()

    if found:
      draw_path(grid, goal_node, parent)
    elif frontier:
      node = frontier.pop(0)
      if node == goal_node:
        found = True
        continue
      pygame.draw.rect(WIN, YELLOW, grid[node[0]][node[1]].rect)
      for neighbor in get_neighbors(grid, node):
        n = grid[neighbor[0]][neighbor[1]]
        pygame.draw.rect(WIN, RED, n.rect)
        if not parent.has_key(neighbor):
          frontier.append(neighbor)
          parent[neighbor] = node
    
    pygame.display.update()
    pygame.time.delay(int(150 * 1.5))
    draw_window(grid, src_input_box, dest_input_box, starting_node, goal_node, frontier, parent)
    

if __name__ == "__main__":
  main()
