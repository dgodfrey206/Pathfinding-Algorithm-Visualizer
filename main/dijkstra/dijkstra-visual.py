import pygame
import random
import pdb
import os
import re
from InputBox import InputBox
try:
   import queue
except ImportError:
   import Queue as queue

pygame.font.init()
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 900, 500
GRID_WIDTH = 30
GRID_HEIGHT = 30

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dijkstra Visualization ({}x{})".format(GRID_WIDTH, GRID_HEIGHT))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (128,0,128)
VIOLET = (238,130,238)
BACKGROUND_RGB = (171, 137, 58)


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


def get_borders():
  borders = []
  i = 5
  j = 29
  while j >= 15:
    borders.append([i, j])
    j -= 1
  i = 10
  j = 10
  while i < 17:
    borders.append([i, j])
    i += 1
  i = 8
  while i < 25:
    borders.append([11, i])
    i += 1
  return borders
  
def draw_window(unvisited, current_node, came_from,
                starting_node, goal_node, src_box, dest_box, goal_path=[]):
  window.fill(BACKGROUND_RGB)
  #draw grid, start/end node, legend for border
  
  y = 10 # starting y-coordinate
  for i in range(GRID_HEIGHT):
    x = SCREEN_WIDTH//2 - (GRID_WIDTH * SQUARE_WIDTH )//2 - 100  # starting x-coordinate
    row = []
    for j in range(GRID_WIDTH):
      # determine color
      color = BLACK
      a = [i,j]
      if a == current_node:
        color = YELLOW
      elif a == starting_node or a == goal_node:
        color = VIOLET
      elif a in goal_path:
        color = PURPLE
      elif a in get_borders():
        color = WHITE
      elif a in get_neighbors(current_node):
        color = RED
      elif a in [node[1] for node in list(unvisited.queue)]:
        color = GREEN
      elif index_to_str(a) in came_from:
        color = BLUE
      
      pygame.draw.rect(window, color, pygame.Rect((x,y), (SQUARE_WIDTH, SQUARE_HEIGHT)))
      x += 15 # add 15 pixels to keep squares spaced out
    y += 15

  pygame.draw.rect(window, GREEN, pygame.Rect(50, 5, SQUARE_WIDTH, SQUARE_HEIGHT))
  pygame.draw.rect(window, YELLOW, pygame.Rect(50, 20, SQUARE_WIDTH, SQUARE_HEIGHT))
  pygame.draw.rect(window, RED, pygame.Rect(50, 35, SQUARE_WIDTH, SQUARE_HEIGHT))
  pygame.draw.rect(window, PURPLE, pygame.Rect(50, 50, SQUARE_WIDTH, SQUARE_HEIGHT))
  pygame.draw.rect(window, BLUE, pygame.Rect(50, 65, SQUARE_WIDTH, SQUARE_HEIGHT))
  pygame.draw.rect(window, VIOLET, pygame.Rect(50, 80, SQUARE_WIDTH, SQUARE_HEIGHT))
  pygame.draw.rect(window, WHITE, pygame.Rect(50, 95, SQUARE_WIDTH, SQUARE_HEIGHT))

  window.blit(frontier_text, (70, 5))
  window.blit(current_text, (70, 20))
  window.blit(neighbor_text, (70, 35))
  window.blit(path_text, (70, 50))
  window.blit(searched_text, (70, 65))
  window.blit(start_goal_text, (70, 80))
  window.blit(border_text, (70, 95))

  window.blit(input_box_src_text, (SCREEN_WIDTH - 230, 20))
  window.blit(input_box_dest_text, (SCREEN_WIDTH - 230, 90))

  src_box.draw(window)
  dest_box.draw(window)
     
  pygame.display.update()

def get_neighbors(node):
  dxy = [(-1, 0), (0, 1), (1, 0), (0, -1), (-1, -1), (-1, 1), (1, 1), (1, -1)] # each pair represents a change in the (x,y) coordinate
  neighbors = []
  for p in dxy:
    sq = [node[0] + p[0], node[1] + p[1]]
    if 0 <= node[0] + p[0] < GRID_WIDTH and 0 <= node[1] + p[1] < GRID_HEIGHT and sq not in get_borders(): # check for border
      neighbors.append(sq)
  return neighbors

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

def manhattan(a, b):
  return abs(a[0] - b[0]) + abs(a[1] - b[1])

def index_to_str(p):
  return ','.join(str(e) for e in p)

def get_parent(dict, node):
  return dict[index_to_str(node)]

def set_parent(dict, parent, child):
  dict[index_to_str(child)] = parent
    

def main():
  global start_x, start_y, goal_x, goal_y

  src_input_box = InputBox(SCREEN_WIDTH - 230, 35, 5, 40, text='({},{})'.format(start_x, start_y))
  dest_input_box = InputBox(SCREEN_WIDTH - 230, 105, 5, 40, text='({},{})'.format(goal_x, goal_y))
  src_input_box.COLOR_ACTIVE = '#2D3635'
  src_input_box.COLOR_INACTIVE = 'lightskyblue3'
  dest_input_box.COLOR_ACTIVE = '#2D3635'
  dest_input_box.COLOR_INACTIVE = 'lightskyblue3'

  run = True

  starting_node = [start_x, start_y]
  goal_node = [goal_x, goal_y]

  unvisited = queue.PriorityQueue()
  unvisited.put((0, starting_node))
  cost = {}
  came_from = {}
  set_parent(came_from, None, starting_node)

  path = []

  found = False
  cur = None # current node in the search

  while run:
    clock.tick(FPS)
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          run = False
          
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
      if not path:
        current = goal_node
        while current != None:
          path.append(current)
          current = get_parent(came_from, current)
    elif not unvisited.empty():
      cur = unvisited.get()
      if (cur[1] == goal_node):
        found = True
        continue
      for next in get_neighbors(cur[1]):
        if index_to_str(next) not in came_from:
          p = manhattan(goal_node, next)
          unvisited.put((p, next))
          set_parent(came_from, cur[1], next)
    
    pygame.display.update()
    pygame.time.delay(int(150 * 1.5))

    draw_window(unvisited, cur[1], came_from, starting_node, 
                goal_node, src_input_box, dest_input_box, path)

if __name__ == "__main__":
  main()
