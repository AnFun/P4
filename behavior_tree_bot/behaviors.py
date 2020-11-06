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


def defend_planet(state):
  for enemy_fleet in state.enemy_fleets():
    attacked_planet_ID = enemy_fleet.destination_planet

    for friendly_planet in state.my_planets():
      if attacked_planet_ID == friendly_planet.ID:
        attacking_fleets = get_attacking_fleets(state.enemy_fleets(), attacked_planet_ID)
        closest_enemy = min(attacking_fleets, key=lambda f: f.turns_remaining)
        friendly_ships = get_fleet_ship_count(state.my_fleets(), attacked_planet_ID)
        friendly_total = friendly_ships + friendly_planet.num_ships + \
                         closest_enemy.turns_remaining
        enemy_ships = get_fleet_ship_count(state.enemy_fleets(), attacked_planet_ID)
        if friendly_total <= enemy_ships:
          strongest_planet = sorted(state.my_planets(), key=lambda p: p.num_ships + state.distance(p.ID, friendly_planet.ID))[::-1]
          for helper_planet in strongest_planet:

            enemy_distance_growth = state.distance(helper_planet.ID, attacked_planet_ID) * friendly_planet.growth_rate
            if not is_targeted(state.enemy_fleets(), helper_planet):
              if enemy_ships + enemy_distance_growth + 1 > helper_planet.num_ships + friendly_total:
                return issue_order(state, helper_planet.ID, attacked_planet_ID, helper_planet.num_ships - 1)
              elif enemy_ships + enemy_distance_growth + 1 < helper_planet.num_ships + friendly_total > 0:
                ships_sending = enemy_ships + enemy_distance_growth + 1 - friendly_ships
                return issue_order(state, helper_planet.ID, attacked_planet_ID, ships_sending)
            """if helper_planet.ID != attacked_planet_ID and not is_targeted(state.enemy_fleets(), helper_planet.ID) and \
              enemy_ships + enemy_distance_growth + 1 < helper_planet.num_ships + friendly_total > 0:
              ships_sending = enemy_ships + enemy_distance_growth + 1 - friendly_ships
              return issue_order(state, helper_planet.ID, attacked_planet_ID, ships_sending)"""

  return False


def planet_from_id(planet_id, planets):
  for p in planets:
    if p.ID == planet_id:
      return p


def being_attacked(state, planet):
  return len([f for f in state.fleets if f.destination_planet == planet.ID]) > 0


def attacking(state, planet):
  return len([f for f in state.fleets if f.destination_planet == planet.ID]) > 0


def planets_that_could_hurt_me(state, planet):
  return [p for p in state.my_planets() if
          p.num_ships > planet.num_ships * 1.2 and state.distance(p.ID, planet.ID) <= 10]


def weight_by(planets, fn):
  dist_owie = sorted(planets, key=fn)
  return fn(dist_owie[0])


def weight_neutral_planet(state, planet):
  owie_planets = [p for p in planets_that_could_hurt_me(state, planet) if not being_attacked(state, planet)]
  if not owie_planets:
    return None

  dist = 1 - max(0, min(1, (weight_by(owie_planets, lambda p: state.distance(p.ID, planet.ID)) / 10)))
  growth = weight_by(owie_planets, lambda p: planet.growth_rate) / 5
  price = 1 - (weight_by(owie_planets, lambda p: planet.num_ships / sum([p.num_ships for p in state.my_planets()])))
  logging.debug(f"dist weight: {dist}, growth weigth: {growth}, price: {price}")
  return dist * 0.8 + growth * 0.6 + price


def weight_hostile(state, planet):
  owie_planets = [p for p in planets_that_could_hurt_me(state, planet) if not attacking(state, planet)]
  if not owie_planets:
    return None

  dist = 1 - max(0, min(1, (weight_by(owie_planets, lambda p: state.distance(p.ID, planet.ID)) / 10)))
  price = 1 - (weight_by(owie_planets, lambda p: planet.num_ships / sum([p.num_ships for p in state.my_planets()])))
  return dist + price * 0.5


def spread_that_fun(state):
  has_weight = [n for n in state.neutral_planets() if weight_neutral_planet(state, n) is not None]
  if not has_weight:
    return False

  best_neut = max(has_weight, key=lambda n: weight_neutral_planet(state, n))
  closest_to_neut = planets_that_could_hurt_me(state, best_neut)[0]
  return issue_order(state, closest_to_neut.ID, best_neut.ID, best_neut.num_ships + 1)


def neut_overtake(state):
  enemy_fleets = state.enemy_fleets()
  my_fleets = state.my_fleets()
  def_planet = None
  my_planet = None
  neut_planet_change = 100000
  for neut_planet in state.planets:
    for enemy_fleet in enemy_fleets:
      if enemy_fleet.destination_planet == neut_planet.ID:
        sorted_allies = sorted(state.my_planets(), key=lambda n: state.distance(n.ID, neut_planet.ID))
        for ally in sorted_allies:

          if not is_targeted(enemy_fleets, ally.ID) and \
            enemy_fleet.turns_remaining - state.distance(ally.ID, neut_planet.ID) >= 1:

            enemy_fleet_total = get_fleet_ship_count(enemy_fleets, neut_planet.ID) - neut_planet.num_ships
            if enemy_fleet_total >= 0:
              enemy_fleet_total += planet_growth(state.distance(ally.ID, neut_planet.ID) - enemy_fleet.turns_remaining,
                                                 neut_planet.growth_rate)
            else:
              enemy_fleet_total *= -1

            if enemy_fleet_total < neut_planet_change and ally.num_ships > enemy_fleet_total + 1:
              neut_planet_change = enemy_fleet_total
              def_planet = neut_planet
              my_planet = ally

  if my_planet is not None and def_planet is not None and neut_planet_change + 1 >= 1:
    return issue_order(state, my_planet.ID, def_planet.ID, neut_planet_change + 1)

  return False


def spread_time(state):
  my_planets = sorted(state.my_planets(), key=lambda f: f.num_ships)[::-1]
  for my_planet in my_planets:
    if not is_targeted(state.enemy_fleets(), my_planet.ID):
      neutral_planets = sorted(state.neutral_planets(), key=lambda n: spread_weight(state, my_planet, n))[::-1]
      for neutral_planet in neutral_planets:
        if not is_targeted(state.my_fleets(),
                           neutral_planet.ID) and my_planet.num_ships > neutral_planet.num_ships + get_fleet_ship_count(
          state.enemy_fleets(), my_planet.ID) + 1:
          return issue_order(state, my_planet.ID, neutral_planet.ID, neutral_planet.num_ships + get_fleet_ship_count(
            state.enemy_fleets(), my_planet.ID) + 1)


def spread_weight(state, planet, src_planet):
  return planet.num_ships + state.distance(planet.ID, src_planet.ID) * planet.growth_rate


def attack_fun(state):
  has_weight = [n for n in state.enemy_planets() if weight_hostile(state, n) is not None]
  if not has_weight:
    return False

  hostile_sorted = sorted(has_weight, key=lambda n: weight_hostile(state, n))[::-1]
  for best_hostile in hostile_sorted:
    if not is_targeted(state.enemy_fleets(), best_hostile.ID):
      closest_to_neut = planets_that_could_hurt_me(state, best_hostile)[0]

      attack_with = best_hostile.num_ships + state.distance(best_hostile.ID, closest_to_neut.ID
                                                            ) * best_hostile.growth_rate
      return issue_order(state, closest_to_neut.ID, best_hostile.ID, attack_with + 1)

  return False


def spread_to_closest_neutral_planet(state):
  # (2) Find my strongest planet.
  parent_planet = None

  # (3) Find the weakest neutral planet.
  closest_planet = None

  distance = float('inf')

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


def attack_planets(state):
  """
  sorted list of planet values by weight
  :param state:
  :return:
  """


def planet_growth(turns, growth_rate):
  return turns * growth_rate


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


def get_attacking_fleets(fleets, planet_id):
  ret_fleets = []
  for fleet in fleets:
    if fleet.destination_planet == planet_id:
      ret_fleets.append(fleet)
  return ret_fleets
