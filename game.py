from typing import Any, Type, Tuple, List, Sequence, Optional
import pygame
from settings import *
from stack import Stack, EmptyStackError
import actor


class Game:
    """
    Class representing the game.
    """
    size: Tuple[int, int]
    width: int
    height: int
    screen: Optional[pygame.Surface]
    x_tiles: int
    y_tiles: int
    tiles_number: Tuple[int, int]
    background: Optional[pygame.Surface]

    _actors: List[actor.Actor]
    _is: List[actor.Is]
    _running: bool
    _rules: List[str]
    _history: Stack

    player: Optional[actor.Actor]
    map_data: List[str]
    keys_pressed: Optional[Sequence[bool]]

    def __init__(self) -> None:
        """
        Initialize variables for this Class.
        """
        self.width, self.height = 0, 0
        self.size = (self.width, self.height)
        self.screen = None
        self.x_tiles, self.y_tiles = (0, 0)
        self.tiles_number = (self.x_tiles, self.y_tiles)
        self.background = None

        self._actors = []
        self._is = []
        self._running = True
        self._rules = []
        self._history = Stack()

        self.player = None
        self.map_data = []
        self.keys_pressed = None

    def load_map(self, path: str) -> None:
        """
        Reads a .txt file representing the map
        """
        with open(path, 'rt') as f:
            for line in f:
                self.map_data.append(line.strip())

        self.width = (len(self.map_data[0])) * TILESIZE
        self.height = len(self.map_data) * TILESIZE
        self.size = (self.width, self.height)
        self.x_tiles, self.y_tiles = len(self.map_data[0]), len(self.map_data)

        # center the window on the screen
        os.environ['SDL_VIDEO_CENTERED'] = '1'

    def new(self) -> None:
        """
        Initialize variables to be object on screen.
        """
        self.screen = pygame.display.set_mode(self.size)
        self.background = pygame.image.load(
            "{}/backgroundBig.png".format(SPRITES_DIR)).convert_alpha()
        for col, tiles in enumerate(self.map_data):
            for row, tile in enumerate(tiles):
                if tile.isnumeric():
                    self._actors.append(
                        Game.get_character(CHARACTERS[tile])(row, col))
                elif tile in SUBJECTS:
                    self._actors.append(
                        actor.Subject(row, col, SUBJECTS[tile]))
                elif tile in ATTRIBUTES:
                    self._actors.append(
                        actor.Attribute(row, col, ATTRIBUTES[tile]))
                elif tile == 'I':
                    is_tile = actor.Is(row, col)
                    self._is.append(is_tile)
                    self._actors.append(is_tile)

    def get_actors(self) -> List[actor.Actor]:
        """
        Getter for the list of actors
        """
        return self._actors

    def get_running(self) -> bool:
        """
        Getter for _running
        """
        return self._running

    def get_rules(self) -> List[str]:
        """
        Getter for _rules
        """
        return self._rules

    def get_is_blocks(self) -> List['Is']:
        """
        Getter for _is
        """
        return self._is

    def _draw(self) -> None:
        """
        Draws the screen, grid, and objects/players on the screen
        """
        self.screen.blit(self.background,
                         (((0.5 * self.width) - (0.5 * 1920),
                           (0.5 * self.height) - (0.5 * 1080))))
        for actor_ in self._actors:
            rect = pygame.Rect(actor_.x * TILESIZE,
                               actor_.y * TILESIZE, TILESIZE, TILESIZE)
            self.screen.blit(actor_.image, rect)

        # Blit the player at the end to make it above all other objects
        if self.player:
            rect = pygame.Rect(self.player.x * TILESIZE,
                               self.player.y * TILESIZE, TILESIZE, TILESIZE)
            self.screen.blit(self.player.image, rect)

        pygame.display.flip()

    def _events(self) -> None:
        """
        Event handling of the game window
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            # Allows us to make each press count as 1 movement.
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed = pygame.key.get_pressed()
                ctrl_held = self.keys_pressed[pygame.K_LCTRL]

                # handle undo button and player movement here
                if event.key == pygame.K_z and ctrl_held:  # Ctrl-Z
                    self._undo()
                else:
                    if self.player is not None:
                        assert isinstance(self.player, actor.Character)
                        save = self._copy()
                        if self.player.player_move(self) \
                                and not self.win_or_lose():
                            self._history.push(save)
        return

    def win_or_lose(self) -> bool:
        """
        Check if the game has won or lost
        Returns True if the game is won or lost; otherwise return False
        """
        assert isinstance(self.player, actor.Character)
        for ac in self._actors:
            if isinstance(ac, actor.Character) \
                    and ac.x == self.player.x and ac.y == self.player.y:
                if ac.is_win():
                    self.win()
                    return True
                elif ac.is_lose():
                    self.lose(self.player)
                    return True
        return False

    def run(self) -> None:
        """
        Run the Game until it ends or player quits.
        """
        while self._running:
            pygame.time.wait(1000 // FPS)
            self._events()
            self._update()
            self._draw()

    def set_player(self, actor_: Optional[actor.Actor]) -> None:
        """
        Takes an actor and sets that actor to be the player
        """
        self.player = actor_

    def remove_player(self, actor_: actor.Actor) -> None:
        """
        Remove the given <actor> from the game's list of actors.
        """
        self._actors.remove(actor_)
        self.player = None

    def _update(self) -> None:
        """
        Check each "Is" tile to find what rules are added and which are removed
        if any, and handle them accordingly.
        """

        # TODO Task 3: Add code here to complete this method
        # What you need to do in this method:
        # - Get the lists of rules that need to be added to and remove from the
        #   current list of rules. Hint: use the update() method of the Is
        #   class.

        # - Apply the additional and removal of the rules. When applying the
        #   rules of a type of character, make sure all characters of that type
        #   have their flags correctly updated. Hint: take a look at the
        #   get_character() method -- it can be useful.

        # - The player may change if the "isYou" rule is updated. Make sure set
        #   self.player correctly after you update the rules. Note that
        #   self.player could be None in some cases.

        # - Update self._rules to the new list of rules.

        # Gets a list of the most updated "is" rule blocks

        current_rules = []
        updated_rules = []
        remove_rules = []

        # 1. Gets all the current rules
        for is_tile in self._is:
            up = self.get_actor(is_tile.x, is_tile.y - 1)
            down = self.get_actor(is_tile.x, is_tile.y + 1)
            left = self.get_actor(is_tile.x - 1, is_tile.y)
            right = self.get_actor(is_tile.x + 1, is_tile.y)

            rule_up_down = is_tile.update(up, down, left, right)[0]
            rule_left_right = is_tile.update(up, down, left, right)[1]

            if rule_up_down != "":
                current_rules.append(rule_up_down)
            if rule_left_right != "":
                current_rules.append(rule_left_right)

        # 1 a) finds removed rules and place it into <rules> list
        for rule in self.get_rules():
            if rule not in current_rules:
                remove_rules.append(rule)

        # 1 b) Find new rules
        for rule in current_rules:
            if rule not in self.get_rules():
                updated_rules.append(rule)

        # Remove old rules
        for rule in remove_rules:
            old_subject = rule[:rule.index(' is')]
            old_attribute = rule[rule.find(' is') + 3:]

            # Remove all old rules' effects
            for current_actor in self._actors:
                if isinstance(current_actor, self.get_character(old_subject)):

                    if old_attribute == "Push":
                        current_actor.unset_push()
                    if old_attribute == "Stop":
                        current_actor.unset_stop()
                    if old_attribute == "Victory":
                        current_actor.unset_win()
                    if old_attribute == "Lose":
                        current_actor.unset_lose()
                    if old_attribute == "You":
                        current_actor.unset_player()
                        self.player = None

        # Updates self.rules by removing old rules
        for rule in remove_rules:
            if rule in self.get_rules():
                self.get_rules().remove(rule)

        # Updates self.rules with newly added rules
        for rule in updated_rules:
            if rule not in self.get_rules():
                self.get_rules().append(rule)

        # Refreshes rules
        for rule in self.get_rules():
            update_subject = rule[:rule.index(' is')]
            update_attribute = rule[rule.find(' is') + 3:]

            for current_actor in self._actors:
                if isinstance(current_actor,
                              self.get_character(update_subject)):

                    if update_attribute == "Push":
                        current_actor.set_push()
                    if update_attribute == "Stop":
                        current_actor.set_stop()
                    if update_attribute == "Victory":
                        current_actor.set_win()
                    if update_attribute == "Lose":
                        current_actor.set_lose()
                    if update_attribute == "You" \
                            and not isinstance(current_actor,
                                               type(self.player)):
                        current_actor.set_player()
                        self.player = current_actor

        return

    @staticmethod
    def get_character(subject: str) -> Optional[Type[Any]]:
        """
        Takes a string, returns appropriate class representing that string
        """
        if subject == "Meepo":
            return actor.Meepo
        elif subject == "Wall":
            return actor.Wall
        elif subject == "Rock":
            return actor.Rock
        elif subject == "Flag":
            return actor.Flag
        elif subject == "Bush":
            return actor.Bush
        return None

    def _undo(self) -> None:
        """
        Returns the game to a previous state based on what is at the top of the
        _history stack.
        """
        # Restores old player, actors and is blocks' locations
        try:
            old_data = self._history.pop()
            self.player = old_data.player
            self._actors = old_data.get_actors()
            self._is = old_data.get_is_blocks()
            return

        # Error Handling
        except EmptyStackError:
            print("Cannot undo.")

    def _copy(self) -> 'Game':
        """
        Copies relevant attributes of the game onto a new instance of Game.
        Return new instance of game
        """
        game_copy = Game()

        actors_copy = []
        is_blocks_copy = []

        # Copies all instances of actors in the game
        for copied_actor in self._actors:
            actor_copy = copied_actor.copy()
            actors_copy.append(actor_copy)

            if isinstance(copied_actor, actor.Is):
                is_blocks_copy.append(actor_copy)

            if copied_actor == self.player:
                game_copy.player = actor_copy

        game_copy._actors = actors_copy
        game_copy._is = is_blocks_copy

        return game_copy

    def get_actor(self, x: int, y: int) -> Optional[actor.Actor]:
        """
        Return the actor at the position x,y. If the slot is empty, Return None
        """
        for ac in self._actors:
            if ac.x == x and ac.y == y:
                return ac
        return None

    def win(self) -> None:
        """
        End the game and print win message.
        """
        self._running = False
        print("Congratulations, you won!")

    def lose(self, char: actor.Character) -> None:
        """
        Lose the game and print lose message
        """
        self.remove_player(char)
        print("You lost! But you can have it undone if undo is done :)")


if __name__ == "__main__":

    try:
        game = Game()
        # load_map public function
        game.load_map(MAP_PATH)
        game.new()
        game.run()
    except EmptyStackError:
        print("Error. Cannot undo.")

    # import python_ta
    # python_ta.check_all(config={
    #     'extra-imports': ['settings', 'stack', 'actor', 'pygame']
    # })
