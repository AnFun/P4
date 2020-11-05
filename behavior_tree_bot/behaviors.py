import logging
import sys
import time
from math import ceil, sqrt

import planet_wars

sys.path.insert(0, '../')
from planet_wars import issue_order

logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)


def attack_weakest_enemy_planet(state):
  # (1) If we currently have a fleet in flight, abort plan.

  # (2) Find my strongest planet.
  strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

  # (3) Find the weakest enemy planet.
  weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)
  if not strongest_planet or not weakest_planet \
    or strongest_planet.num_ships < weakest_planet.num_ships + \
    state.distance(strongest_planet.ID, weakest_planet.ID) * weakest_planet.growth_rate + 1:
    # No legal source or destination
    return False
  else:
    # (4) Send half the ships from my strongest planet to the weakest enemy planet.
    return issue_order(state, strongest_planet.ID, weakest_planet.ID,
                       weakest_planet.num_ships + state.distance(strongest_planet.ID,
                                                                 weakest_planet.ID) * weakest_planet.growth_rate) + 1


def defend_planet_attack(state):
  for enemy_fleet in state.enemy_fleets():

    attacked_planet = enemy_fleet.destination_planet

    for friendly_planet in state.my_planets():

      if attacked_planet == friendly_planet.ID:
        friendly_ships = get_fleet_ship_count(state.my_fleets(), attacked_planet)
        friendly_total = friendly_ships + friendly_planet.num_ships
        enemy_ships = get_fleet_ship_count(state.enemy_fleets(), attacked_planet)
        for helper_planet in state.my_planets():
          enemy_distance_growth = (state.distance(helper_planet.ID, enemy_fleet.source_planet) - state.distance(
            attacked_planet, enemy_fleet.source_planet)) * friendly_planet.growth_rate
          if helper_planet.ID != attacked_planet and \
            friendly_total < enemy_ships + enemy_distance_growth + 1 < helper_planet.num_ships + friendly_total > 0:
            return issue_order(state, helper_planet.ID, attacked_planet,
                               enemy_ships + enemy_distance_growth + 1 - friendly_total)

  return False


def planet_from_id(planet_id, planets):
  for p in planets:
    if p.ID == planet_id:
      return p


def spread_to_weakest_neutral_planet(state):
  # (1) If we currently have a fleet in flight, just do nothing.
  ##if len(state.my_fleets()) > 4:
  ##return False

  # (2) Find my strongest planet.
  strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

  # (3) Find the weakest neutral planet.
  weakest_planet = sorted(state.neutral_planets(), key=lambda p: p.num_ships)
  weakest_planeta = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)
  for neut in weakest_planet:
    if strongest_planet.num_ships <= neut.num_ships + 1:
      return False
    is_attacked = False
    for fleet in state.fleets:
      if neut.ID == fleet.destination_planet:
        is_attacked = True
        break
    if not is_attacked:
      return issue_order(state, strongest_planet.ID, neut.ID, neut.num_ships + 1)

  if len(state.my_fleets()) < 1 and strongest_planet.num_ships > weakest_planeta.num_ships:
    return issue_order(state, strongest_planet.ID, weakest_planeta.ID, weakest_planeta.num_ships + 1)
  return False


def spread_to_closest_neutral_planet(state):
  # (2) Find my strongest planet.
  parent_planet = None

  # (3) Find the weakest neutral planet.
  closest_planet = None

  distance = 42781394789231

  for m in state.my_planets():
    for n in state.neutral_planets():
      distance_temp = state.distance(m.ID, n.ID)
      if distance_temp < distance and m.num_ships > n.num_ships + 1 and not is_targeted(state.fleets, n.ID):
        distance = distance_temp
        closest_planet = n
        parent_planet = m

  if not parent_planet or not closest_planet:
    # No legal source or destination
    return False
  else:
    # (4) Send half the ships from my strongest planet to the weakest enemy planet.
    return issue_order(state, parent_planet.ID, closest_planet.ID, closest_planet.num_ships + 1)


def is_targeted(fleets, planet_id):
  for fleet in fleets:
    if fleet.destination_planet == planet_id:
      return True
  return False


def get_fleet_ship_count(fleets, planet_id):
  ship_count = 0
  for fleet in fleets:
    if fleet.destination_planet == planet_id:
      ship_count += fleet.num_ships

  return ship_count
