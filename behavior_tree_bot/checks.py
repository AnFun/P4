from behavior_tree_bot.behaviors import weight_hostile, weight_by, get_fleet_ship_count, planet_from_id, being_attacked



def if_neutral_planet_available(state):
  neut_planet = [p for p in state.neutral_planets() if not being_attacked(state, p)]
  my_planet = [p for p in state.my_planets() if not being_attacked(state, p)]
  neut_min = min(neut_planet, key=lambda t: t.num_ships, default=None)
  my_max = max(my_planet, key=lambda t: t.num_ships, default=None)
  if neut_min is not None and my_max is not None and my_max.num_ships > neut_min.num_ships:
    return True
  return False


def killing_blow(state):
  if sum(t.num_ships for t in state.enemy_planets()) * 2 < sum(t.num_ships for t in state.my_planets()):
    return True
  return False


def have_largest_fleet(state):
  # return len([n for n in state.enemy_planets() if weight_hostile(state, n) is not None]) > 0
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
        fleets = get_fleet_ship_count(state.my_fleets(), ally.ID)
        enemy_fleets = get_fleet_ship_count(state.enemy_fleets(), ally.ID)
        if fleets + ally.num_ships < enemy_fleets:
          return True
  return False


def neut_attacked(state):
  for planet in state.neutral_planets():
    for enemy in state.enemy_fleets():
      if enemy.destination_planet == planet.ID:
        return True
  return False
