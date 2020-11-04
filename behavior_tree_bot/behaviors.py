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
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)
    if not strongest_planet or not weakest_planet \
            or strongest_planet.num_ships / 2 < weakest_planet.num_ships:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID,
                           strongest_planet - strongest_planet / 4)


def defend_planet_attack(state):
    if len(state.my_fleets()) >= 2:
        return False
    for enemy_fleet in state.enemy_fleets():
        attacked_planet = enemy_fleet.destination_planet
        for friendly_planet in state.my_planets():
            if attacked_planet == friendly_planet.ID:
                for helper_planet in state.my_planets():
                    if helper_planet.num_ships > enemy_fleet.num_ships:
                        return issue_order(state, helper_planet.ID, attacked_planet, enemy_fleet.num_ships+1)

def planet_from_id(planet_id, planets):
    for p in planets:
        if p.ID == planet_id:
            return p



def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) > 4:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = sorted(state.neutral_planets(), key=lambda p: p.num_ships)

    for neut in weakest_planet:
        for fleet in state.my_fleets():
            if neut.ID != fleet.destination_planet and strongest_planet.ID != neut.ID and strongest_planet.num_ships > neut.num_ships:
                return issue_order(state, strongest_planet.ID, neut.ID, neut.num_ships+1)
    return False


def spread_to_closest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 5:
        return False

    # (2) Find my strongest planet.
    parent_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    closest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)
    distance = sqrt((parent_planet.x - closest_planet.x) * (parent_planet.x - closest_planet.x)
                    + (parent_planet.y - closest_planet.y) * (parent_planet.y - closest_planet.y))

    for m in state.my_planets():
        for n in state.neutral_planets():
            dx = m.x - n.x
            dy = m.y - n.y
            distance_temp = sqrt(dx * dx + dy * dy)
            if distance_temp < distance and m.num_ships > n.num_ships and is_targeted(state.my_fleets(), n.ID):
                distance = distance_temp
                closest_planet = n
                parent_planet = m

    if not parent_planet or not closest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, parent_planet.ID, closest_planet.ID, parent_planet.num_ships)

def is_targeted(fleets, planet_id):
    for fleet in fleets:
        if fleet.destination_planet == planet_id:
            return True
    return False

def big_boy_party_time(state):
    # (2) Find my strongest planet.
    big_boy = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    for m in state.my_planets():
        if m.num_ships > 50:
            return issue_order(state, m.ID, big_boy.ID, big_boy.num_ships / 2)

    return False
