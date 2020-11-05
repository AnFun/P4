
def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def is_being_attacked(state):
    for enemy in state.enemy_fleets():
        dest_planet = enemy.destination_planet
        for ally in state.my_planets():
            if dest_planet == ally.ID:
                return True
    return False

def is_attackable(state):
  return False
