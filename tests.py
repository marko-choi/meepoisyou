from game import *
from actor import *
import pytest
import pygame
import os

# USE PYGAME VARIABLES INSTEAD
keys_pressed = [0] * 323

# Setting key constants because of issue on devices
pygame.K_RIGHT = 1
pygame.K_DOWN = 2
pygame.K_LEFT = 3
pygame.K_UP = 4
pygame.K_LCTRL = 5
pygame.K_z = 6
RIGHT = pygame.K_RIGHT
DOWN = pygame.K_DOWN
LEFT = pygame.K_LEFT
UP = pygame.K_UP
CTRL = pygame.K_LCTRL
Z = pygame.K_z


def setup_map(map: str) -> 'Game':
    """Returns a game with map1"""
    game = Game()
    game.new()
    game.load_map(os.path.abspath(os.getcwd()) + '/maps/' + map)
    game.new()
    game._update()
    game.keys_pressed = keys_pressed
    return game


def set_keys(up, down, left, right, CTRL=0, Z=0):
    keys_pressed[pygame.K_UP] = up
    keys_pressed[pygame.K_DOWN] = down
    keys_pressed[pygame.K_LEFT] = left
    keys_pressed[pygame.K_RIGHT] = right
    keys_pressed[pygame.K_LCTRL] = CTRL
    keys_pressed[pygame.K_z] = Z


def move(up, down, left, right, times, game):
    """
    Moves the character and updates the game for the character to be
    in the new position after each move by how many <times>.
    """
    for i in range(times):
        set_keys(up, down, left, right)
        game.player.player_move(game)


def test1_move_player_up():
    """
    Check if player is moved up correctly
    """
    game = setup_map("student_map1.txt")
    set_keys(1, 0, 0, 0)
    result = game.player.player_move(game)
    assert result == True
    assert game.player.y == 1


def test2_push_block():
    """
    Check if player pushes block correctly
    """
    game = setup_map("student_map2.txt")
    set_keys(0, 0, 0, 1)
    wall = \
        [i for i in game._actors if isinstance(i, Block) and i.word == "Wall"][
            0]
    result = game.player.player_move(game)
    assert result == True
    assert game.player.x == 3
    assert wall.x == 4


def test3_create_rule_wall_is_push():
    """
    Check if player creates wall is push rule correctly
    """
    game = setup_map("student_map2.txt")
    set_keys(0, 0, 0, 1)
    wall = \
        [i for i in game.get_actors() if
         isinstance(i, Block) and i.word == "Wall"][
            0]
    result = game.player.player_move(game)
    game._update()
    assert "Wall isPush" in game._rules
    assert game.player.x == 3
    assert wall.x == 4


def test_4_follow_rule_wall_is_push():
    """
    Check if player follows rules correctly
    """
    game = setup_map("student_map3.txt")
    set_keys(0, 0, 0, 1)
    wall_object = game.get_actors()[game.get_actors().index(game.player) + 1]
    result = game.player.player_move(game)
    assert game.player.x == 2
    assert wall_object.x == 3


def test_5_no_push():
    """
    Check if player is not able to push because of rule not existing
    """
    game = setup_map("student_map4.txt")
    set_keys(0, 0, 0, 1)
    wall_object = game._actors[game._actors.index(game.player) + 1]
    result = game.player.player_move(game)
    assert game.player.x == 2
    assert wall_object.x == 2


def test_6_win():
    """
    Check if player won the game after pushing multiple blocks unstopped
    by other blocks, with a rule updated, and finally reaches to the object
    that is set to be winning
    """
    game = setup_map("student_map5.txt")
    move(up=0, down=0, left=0, right=1, times=4, game=game)
    move(up=0, down=1, left=0, right=0, times=4, game=game)
    move(up=0, down=0, left=0, right=1, times=2, game=game)
    move(up=1, down=0, left=0, right=0, times=1, game=game)
    move(up=0, down=0, left=0, right=1, times=1, game=game)

    move(up=0, down=1, left=0, right=0, times=4, game=game)

    move(up=0, down=0, left=1, right=0, times=2, game=game)
    move(up=0, down=1, left=0, right=0, times=3, game=game)
    move(up=0, down=0, left=0, right=1, times=1, game=game)

    # Check if the rules are updated

    # Implicitly checks if Meepo was able to push 2 pushable
    # blocks with nothing stopping it in front
    assert game.player.x == 11
    assert game.player.y == 12

    game._update()

    # Check if the new rule "Flag isVictory" is in the rules
    assert "Flag isVictory" in game._rules

    flag = [i for i in game._actors if isinstance(i, Flag)][0]
    assert flag._is_win == True

    move(up=0, down=1, left=0, right=0, times=1, game=game)
    move(up=0, down=0, left=0, right=1, times=2, game=game)
    move(up=1, down=0, left=0, right=0, times=8, game=game)
    move(up=0, down=0, left=0, right=1, times=6, game=game)

    game.win_or_lose()
    assert game._running == False


def test_7_lose():
    """
    Check if the player loses the game when walking into an object
    that is set to be losing
    """
    game = setup_map("student_map5.txt")
    move(up=0, down=0, left=0, right=1, times=4, game=game)
    move(up=0, down=1, left=0, right=0, times=3, game=game)
    move(up=0, down=0, left=0, right=1, times=1, game=game)

    game._update()
    assert "Wall isLose" in game.get_rules()

    walls = [i for i in game.get_actors() if isinstance(i, Wall)]
    for wall in walls:
        assert wall._is_lose == True

    move(up=0, down=0, left=1, right=0, times=1, game=game)
    move(up=0, down=1, left=0, right=0, times=3, game=game)

    game.win_or_lose()
    assert game.player is None


def test_8_changing_meepo_sprite():
    """
    Check if the player, as Meepo, has its sprite changing as it walks.
    """
    game = setup_map("student_map5.txt")

    # walk right
    move(up=0, down=0, left=0, right=1, times=1, game=game)
    assert game.player.image == game.player.walk_right[1]

    move(up=0, down=0, left=0, right=1, times=1, game=game)
    assert game.player.image == game.player.walk_right[0]

    # walk left
    move(up=0, down=0, left=1, right=0, times=1, game=game)
    assert game.player.image == game.player.walk_left[0]

    move(up=0, down=0, left=1, right=0, times=1, game=game)
    assert game.player.image == game.player.walk_left[1]

    # walk up
    move(up=1, down=0, left=0, right=0, times=1, game=game)
    assert game.player.image == game.player.walk_up[0]

    move(up=1, down=0, left=0, right=0, times=1, game=game)
    assert game.player.image == game.player.walk_up[1]

    # walk down
    move(up=0, down=1, left=0, right=0, times=1, game=game)
    assert game.player.image == game.player.walk_down[1]

    move(up=0, down=1, left=0, right=0, times=1, game=game)
    assert game.player.image == game.player.walk_down[0]


def test_9_changing_players():
    """
    Testing when another "Subject isYou", the player is changed
    """
    game = setup_map("student_map5.txt")
    move(up=0, down=0, left=1, right=0, times=1, game=game)
    move(up=0, down=1, left=0, right=0, times=8, game=game)
    move(up=0, down=0, left=1, right=0, times=2, game=game)
    move(up=0, down=1, left=0, right=0, times=2, game=game)
    move(up=0, down=0, left=0, right=1, times=4, game=game)
    move(up=1, down=0, left=0, right=0, times=1, game=game)
    move(up=0, down=1, left=0, right=1, times=1, game=game)
    move(up=0, down=1, left=0, right=0, times=3, game=game)

    game._update()
    assert "Rock isYou" in game.get_rules()
    assert type(game.player) == Rock


def test_9_undo():
    """
    Checks if undo copies all flags, position, and sprites of the player
    before moving.
    """
    game = setup_map("student_map1.txt")
    copy = game._copy()
    game._history.push(game._copy())
    move(up=1, down=0, left=0, right=0, times=1, game=game)
    game._undo()

    assert game.player.y == 2
    assert game.player._is_player == True
    assert game.player._is_push == False
    assert game.player.image == copy.player.image


def test_10_subject_is_stop():
    """
    Checks if "Subject isStop" works where the rule is updated and also the
    player is stopped if tried to go through the Subject character
    """
    game = setup_map("student_map5.txt")

    assert "Rock isStop" in game.get_rules()

    move(up=0, down=1, left=0, right=0, times=2, game=game)
    assert game.player.y == 3


def test_11_undo_moved_actor():
    """
    Checks if undoing will undo the sprite of the player (as Meepo) and also
    the moved block will return to its originally position before moved.
    """
    game = setup_map("student_map2.txt")

    assert game.get_actor(4, 1) is None
    assert type(game.get_actor(3, 1)) == Subject

    copy = game._copy()
    game._history.push(game._copy())
    move(up=0, down=0, left=0, right=1, times=1, game=game)

    assert game.get_actor(4, 1).word == "Wall"
    assert (game.player.x, game.player.y) == (3, 1)

    game._undo()

    assert game.player.x == 2
    assert game.get_actor(5, 1).image == copy.get_actor(5, 1).image


def test_12_check_is_block_properties():
    """
    Checks if the Is blocks are implemented correctly with changing sprite
    images upon validly formed rules
    """
    game = setup_map("student_map5.txt")

    move(up=0, down=0, left=0, right=1, times=4, game=game)
    move(up=0, down=1, left=0, right=0, times=5, game=game)
    move(up=0, down=0, left=0, right=1, times=1, game=game)
    move(up=1, down=0, left=0, right=0, times=1, game=game)
    move(up=0, down=0, left=1, right=0, times=1, game=game)

    move(up=1, down=0, left=0, right=0, times=1, game=game)
    move(up=0, down=0, left=0, right=1, times=1, game=game)

    game._update()
    is_block = game._is[0]
    update = is_block.update(up=game.get_actor(is_block.x, is_block.y - 1),
                             down=game.get_actor(is_block.x, is_block.y + 1),
                             left=game.get_actor(is_block.x - 1, is_block.y),
                             right=game.get_actor(is_block.x + 1, is_block.y))
    assert "Flag isLose" in game.get_rules()
    assert "" in update and "Flag isLose" in update

    move(up=0, down=0, left=1, right=0, times=1, game=game)
    move(up=1, down=0, left=0, right=0, times=1, game=game)
    move(up=0, down=0, left=0, right=1, times=2, game=game)

    move(up=0, down=0, left=1, right=0, times=1, game=game)
    move(up=0, down=1, left=0, right=0, times=3, game=game)
    move(up=0, down=0, left=0, right=1, times=1, game=game)
    move(up=0, down=1, left=0, right=0, times=4, game=game)

    move(up=0, down=0, left=1, right=0, times=1, game=game)

    move(up=0, down=1, left=0, right=0, times=2, game=game)
    move(up=0, down=0, left=0, right=1, times=1, game=game)
    move(up=1, down=0, left=0, right=0, times=6, game=game)

    move(up=0, down=0, left=1, right=0, times=1, game=game)
    move(up=1, down=0, left=0, right=0, times=1, game=game)
    move(up=0, down=0, left=0, right=1, times=1, game=game)

    game._update()
    update = is_block.update(up=game.get_actor(is_block.x, is_block.y - 1),
                             down=game.get_actor(is_block.x, is_block.y + 1),
                             left=game.get_actor(is_block.x - 1, is_block.y),
                             right=game.get_actor(is_block.x + 1, is_block.y))

    assert "Wall isVictory" in game.get_rules()
    assert "Wall isVictory" in update and "Flag isLose" in update


if __name__ == "__main__":
    import pytest

    pytest.main(['student_tests.py'])
