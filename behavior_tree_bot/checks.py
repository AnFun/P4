from behavior_tree_bot.behaviors import weight_hostile, weight_by, get_fleet_ship_count


def if_neutral_planet_available(state):
  strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)
  weakest_planet = min(state.neutral_planets(),
                       key=lambda t: t.num_ships - get_fleet_ship_count(state.enemy_fleets(), t.ID), default=None)
  if weakest_planet is not None and strongest_planet.num_ships > abs(
    weakest_planet.num_ships - get_fleet_ship_count(state.enemy_fleets(), weakest_planet.ID)) + 1:
    return True
  return False


def have_largest_fleet(state):
  #return len([n for n in state.enemy_planets() if weight_hostile(state, n) is not None]) > 0
  fleet_min = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)
  fleet_max = max(state.my_planets(), key=lambda t: t.num_ships, default=None)
  if fleet_min is not None and fleet_max is not None and fleet_min < fleet_max:
    return True
  return False


def is_being_attacked(state):
  for enemy in state.enemy_fleets():
    dest_planet = enemy.destination_planet
    for ally in state.my_planets():
      if dest_planet == ally.ID:
        return True
  return False

def neut_attacked(state):
  for planet in state.neutral_planets():
    for enemy in state.enemy_fleets():
      if enemy.destination_planet == planet.ID:
        return True
  return False
