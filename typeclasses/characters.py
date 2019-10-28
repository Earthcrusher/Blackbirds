# Python modules.
import re, random

# Evennia modules.
from evennia import DefaultCharacter
from evennia.utils import logger

# Blackbirds modules.
from utilities.color import color_ramp
from utilities.communication import ProcessSpeech
from utilities.display import header, divider, column, bullet
from utilities.string import an, capital, plural, message_token_pluralize, message_token_capitalize
import utilities.directions as dirs
from world.names import CURRENCY, CURRENCY_FULL

class Character(DefaultCharacter):
    def at_object_creation(self):
        self.db.surname = ""
        self.db.age = 18
        self.db.app_age = 18
        self.db.intro = ""
        self.db.height = 172 # Approx. 5' 8" in cm
        self.db.pronoun_they = "they"
        self.db.pronoun_them = "them"
        self.db.pronoun_their = "their"
        self.db.pronoun_theirs = "theirs"
        self.db.species = None

        # Stats.
        self.db.hp = {"current": 20, "max": 20} # Hit points.
        self.db.en = {"current": 100, "max": 100} # Endurance.
        self.db.sc = {"current": 0, "max": 3} # Scars (lives).
        self.db.xp = {"current": 0, "max": 1000} # Experience.
        self.db.archetype = None
        self.db.money = 0

        # Combat/RP-based statuses.
        self.db.prone = 0 # 1 for seated, 2 for lying down

        # Anatomy.
        self.db.has_breasts = True
        self.db.has_genitals = True
        self.db.can_carry_child = True
        self.db.exoskeletal_level = 0
        self.db.has_four_arms = False

        # Descriptions.
        self.db.fang_desc = "fangs"
        self.db.tail_desc = "feline"
        self.db.bioluminescence_desc = "white"

    def update(self):
        pass

    def at_before_say(self, message, **kwargs):
        return message

    def at_say(self, message, msg_self = None, msg_location = None, receivers = None, msg_receivers = None, **kwargs):
        ProcessSpeech(self, message, msg_self, msg_location, receivers, msg_receivers, **kwargs)

    def at_after_say(self, string):
        # Any processing to be done after saying something.
        pass

    def at_desc(self, looker = None, **kwargs):
        # Passed before the desc appears.
        pass

    def return_appearance(self, looker = None, **kwargs):
        if not looker:
            return ""

        surname = ""
        if self.db.surname:
            surname = f" {self.db.surname}"
        string = f"|xThis is |c{self.key}{surname}|n|x,|n |c{an(self.species())}|n|x.|n\n"
        string += divider()
        string += f"\n{self.db.desc}"

        return string

    def echo(self, string, prompt = False, error = False):
        # At this moment, simply a lazy method wrapper that sends a message to the object,
        # then displays a prompt.
        if error == True:
            string = "|x" + string + "|n"

        self.msg(string)
        if prompt == True:
            self.msg(prompt = self.prompt())

    def error_echo(self, string, prompt = False):
        self.echo(string, prompt = prompt, error = True)

    def hp(self):
        return self.db.hp["current"]

    def max_hp(self):
        return self.db.hp["max"]

    def en(self):
        return self.db.en["current"]

    def max_en(self):
        return self.db.en["max"]

    def sc(self):
        return self.db.sc["current"]

    def max_sc(self):
        return self.db.sc["max"]

    def xp(self):
        return self.db.xp["current"]

    def max_xp(self):
        return self.db.xp["max"]

    def in_chargen(self):
        c = self.location.__class__.__name__
        return c == "ChargenRoom"

    def prompt_status(self):
        if self.in_chargen():
            return "chargen"

        return "default"

    def prompt(self):
        "Returns the object's prompt, if applicable."
        status = self.prompt_status()
        p_string = ""

        if status == "default":
            stat_string = ""
            
            # Core stats.
            for stat in ["hp", "en"]:
                m_cur, m_max = getattr(self, stat), getattr(self, "max_" + stat)
                c = color_ramp(m_cur(), m_max(), cap = True)
                c_string = "".join(c)
                s_string = "|013%s|n|%s%s|n" % ("0" * (3 - len(str(m_cur()))), c_string, str(m_cur()))
                p_string += "|x%s|c|||n%s " % (stat.upper(), s_string)

            # Experience.
            p_string += "|504XP|c|||n|202%s|505%s|n " % ("0" * (len(str(self.max_xp())) - len(str(self.xp()))), self.xp())

            # Scars.
            p_string += "|411SC|r|||n|R%s|n " % ("*" * self.sc()) if self.sc() > 0 else ""

            # Statuses.
            stat_string += "|cp|n" if self.db.prone > 0 else ""

            stat_string += " " if len(stat_string) >= 1 else ""
            p_string += stat_string

            # Cap that bad boy off.
            p_string += "|x-|n "

        elif status == "chargen":
            p_string = "|035" + ("-" * 80)

        return p_string

    def coordinates(self):
        if not self.location:
            return [0, 0, 0]

        loc = self.location
        return [loc.db.x, loc.db.y, loc.db.z]

    def can_move(self):
        if self.db.prone > 0:
            return False, "You'll need to get up, first."

        return True, ""

    def move_call(self, dir = None):
        # Player is not in a room.
        if not self.location:
            self.error_echo("You can't figure out how to move anywhere from here.")
            return

        # Player somehow didn't specify a direction.
        if not dir:
            self.error_echo("Which way are you trying to go?")
            return

        # Direction existence passed, sanitize direction.
        dir = dirs.valid_direction(dir)

        # Check for various factors that might prevent a player from moving.
        # (afflictions, prone status, sleeping, etc.)
        cm_check, cm_msg = self.can_move()
        if cm_check == False:
            cm_msg = cm_msg if cm_msg else "You can't seem to move."
            self.error_echo(f"{cm_msg}")
            return

        # Ensure room has exit in the desired direction.
        loc = self.location
        if not loc.has_exit(dir):
            self.error_echo(f"There is no {dir}ward exit.")
            return

        # Player passed. Get destination, send them on through.
        exit = loc.db.exits[dir]
        destination = exit.get_destination()
        self.move_to(destination)

    def move_to(self, destination, quiet = False, move_hooks = True, **kwargs):
        # self: obvious.
        # destination: handled by dir-based move method
        # quiet: if true, won't display enter/exit messages
        # move_hooks: if False, bypasses at_move/before_move on objects

        # should return True if move was successful, and False if not

        # all access/ability checks should be handled before this method!
        # if we've gotten to move_to, everything is green and we are ready
        # to move the object.

        def error_msg(string = "", err = None):
            """Simple log helper method"""
            logger.log_trace()
            self.error_echo("%s%s" % (string, "" if err is None else " (%s)" % err))
            return

        errtxt = ("Couldn't perform move ('%s'). Contact an admin.")

        # Convert destination to actual room.
        destination = self.search(destination, global_search = True)
        if not destination:
            self.error_echo("You can't seem to figure out how to get there.")
            return False

        if move_hooks:
            try:
                if not self.at_before_move(destination):
                    return False
            except Exception as err:
                error_msg(errtxt % "at_before_move()", err)
                return False

        source_location = self.location
        if move_hooks and source_location:
            try:
                source_location.at_object_leave(self, destination)
            except Exception as err:
                error_msg(errtxt % "at_object_leave()", err)
                return False

        if not quiet:
            try:
                self.announce_move_from(destination, **kwargs)
            except Exception as err:
                error_msg(errtxt % "at_announce_move()", err)
                return False

        try:
            self.location = destination
        except Exception as err:
            error_msg(errtxt % "location change", err)
            return False

        if not quiet:
            # Tell the new room we are there.
            try:
                self.announce_move_to(source_location, **kwargs)
            except Exception as err:
                error_msg(errtxt % "announce_move_to()", err)
                return False

        if move_hooks:
            # Perform eventual extra commands on the receiving location
            # (the object has already arrived at this point)
            try:
                destination.at_object_receive(self, source_location)
            except Exception as err:
                error_msg(errtxt % "at_object_receive()", err)
                return False

        # Execute eventual extra commands on this object after moving it
        # (usually calling 'look')
        if move_hooks:
            try:
                self.at_after_move(source_location)
            except Exception as err:
                error_msg(errtxt % "at_after_move", err)
                return False

        return True

    def at_look(self, target = None, **kwargs):
        # If the player has no species or their species doesn't override at_look,
        # use the default functionality.
        if not self.db.species or self.db.species.at_look != True:
            if not target.access(self, "view"):
                try:
                    return "Could not view '%s'." % target.get_display_name(self, **kwargs)
                except AttributeError:
                    return "Could not view '%s'." % target.key

            description = target.return_appearance(self, **kwargs)

            # the target's at_desc() method.
            # this must be the last reference to target so it may delete itself when acted on.
            target.at_desc(looker = self, **kwargs)

            return description

        return self.db.species.at_look(self, target = None, **kwargs)

    def zone(self):
        loc = self.location
        return loc.zone()

    def x(self):
        loc = self.location
        return loc.db.x

    def y(self):
        loc = self.location
        return loc.db.y

    def z(self):
        loc = self.location
        return loc.db.z

    def coords(self):
        loc = self.location
        return [loc.db.x, loc.db.y, loc.db.z]

    def surname(self):
        return self.db.surname if self.db.surname else ""

    def species(self):
        return self.db.species.name if self.db.species else "Unknown"

    def archetype(self):
        return self.db.archetype.name if self.db.archetype else "None"

    def they(self):
        return self.db.pronoun_they

    def them(self):
        return self.db.pronoun_them

    def their(self):
        return self.db.pronoun_their

    def theirs(self):
        return self.db.pronoun_theirs

    def pronouns(self):
        return f"{self.they()}, {self.them()}, {self.their()}, {self.theirs()}"

    def score(self):
        col_width = 10

        full_name = f"{self.name} {self.db.surname}" if self.db.surname else self.name
        full_age = f"{self.db.app_age} |x(|n{self.db.age}|x)|n" if self.db.app_age != self.db.age else self.db.age

        hp_string = "|013%s|055%s |013%s|055%s|n" % ("0" * (4 - len(str(self.hp()))), self.hp(), "0" * (4 - len(str(self.max_hp()))), self.max_hp())
        en_string = "|013%s|055%s |013%s|055%s|n" % ("0" * (4 - len(str(self.en()))), self.en(), "0" * (4 - len(str(self.max_en()))), self.max_en())
        xp_string = "|202%s|505%s |202%s|505%s|n" % ("0" * (4 - len(str(self.xp()))), self.xp(), "0" * (4 - len(str(self.max_xp()))), self.max_xp())
        sc_string = "|200%s|511%s |200%s|511%s|n" % ("0" * (4 - len(str(self.sc()))), self.sc(), "0" * (4 - len(str(self.max_sc()))), self.max_sc())

        string = ""
        string += f"Infiltration Unit |W{full_name}|n, Prefect Initiate"
        string += "\n" + divider()
        string += "\n|cCharacter Information|n"

        string += "\n" + column("Age", full_age, title_width = col_width, value_width = 24)
        string += column("Health", hp_string, title_width = col_width)
        string += "\n" + column("Species", self.species(), title_width = col_width, value_width = 24)
        string += column("Endurance", en_string, title_width = col_width)
        string += "\n" + column("Pronouns", f"{self.pronouns()}", title_width = col_width, value_width = 24)
        string += column("Experience", xp_string, title_width = col_width)
        string += "\n" + column("Archetype", self.archetype(), title_width = col_width, value_width = 24)
        string += column("Scars", sc_string, title_width = col_width)

        string += "\n\n|cOrganizations & Allegiances|n"

        string += "\n" + bullet("You are a |WCitizen|n of the |WState of Brillante|n.")
        string += "\n" + bullet("You are a |WPrefect Initiate|n in the |WCoalhound Corps|n.")
        string += "\n" + bullet("You worship |WNever-Knows-Best, the Massacre Spirit|n.")

        string += "\n\n|cAssets & Money|n"
        string += "\n" + bullet("You do not own any buildings.")
        string += "\n" + bullet(f"You have accumulated |C{random.randint(1, 1000000):,}|n Karma.")
        string += "\n" + bullet(f"You have accumulated |M{random.randint(1, 1000):,}|n Neon.")
        string += "\n" + bullet(f"|yYour {CURRENCY_FULL} stands at |Y{self.db.money} {CURRENCY}|y.|n", color = "320")

        string += "\n" + divider()
        string += "\nType |Rab|n to see your learned abilities."
        string += "\nType |Rcr|n to see all currencies you own."

        return string

    def pluralize(self, string):
        "Shortcut for the plural() string utility. Only pluralizes the word if the character's pronouns are not neutral."
        if self.they() == "they":
            return string

        return plural(string)

    def message(self, self_m = None, target = None, tar_m = None, witness_m = None):
        """A specifically formatted message that originates from the Character. Special tokens are used to populate data and facilitate the writing of combat or other game messages.

        self_m = The message the originating character sees.
        target = A valid character object, not the self.
        tar_m = The message the target sees, if any.
        witness_m = A third-party message that others in the room see.
        
        TARGET: The target's name. Not used in tar_m.
        TARGET_THEY, TARGET_THEM, TARGET_THEIR, TARGET_THEIRS: The target's pronouns. Not used in tar_m.
        PLAYER: The character's name. Not used in self_m.
        PLAYER_THEY, PLAYER_THEM, PLAYER_THEIR, PLAYER_THEIRS: The character's pronouns. Not used in self_m.
        !verb: A verb originating from the character. Should be written in singular form, and will become plural if the pronouns accept it.
        #verb: A verb originating from the target. Should be written in singular form, and will become plural if the pronouns accept it.
        +word: The word is to be capitalized."""

        if self_m == None:
            return

        if target and tar_m == None:
            return

        if target:
            self_m = self_m.replace("TARGET_THEY", target.they())
            self_m = self_m.replace("TARGET_THEM", target.them())
            self_m = self_m.replace("TARGET_THEIR", target.their())
            self_m = self_m.replace("TARGET_THEIRS", target.theirs())
            self_m = self_m.replace("TARGET", target.name)
            self_m = message_token_pluralize(self_m, "#", target)
            self_m = message_token_capitalize(self_m)

        if tar_m:
            tar_m = tar_m.replace("PLAYER_THEY", self.they())
            tar_m = tar_m.replace("PLAYER_THEM", self.them())
            tar_m = tar_m.replace("PLAYER_THEIR", self.their())
            tar_m = tar_m.replace("PLAYER_THEIRS", self.theirs())
            tar_m = tar_m.replace("PLAYER", self.name)
            tar_m = message_token_pluralize(tar_m, "!", self)
            tar_m = message_token_capitalize(tar_m)

        if witness_m:
            witness_m = witness_m.replace("TARGET_THEY", target.they())
            witness_m = witness_m.replace("TARGET_THEM", target.them())
            witness_m = witness_m.replace("TARGET_THEIR", target.their())
            witness_m = witness_m.replace("TARGET_THEIRS", target.theirs())
            witness_m = witness_m.replace("TARGET", target.name)
            witness_m = witness_m.replace("PLAYER_THEY", self.they())
            witness_m = witness_m.replace("PLAYER_THEM", self.them())
            witness_m = witness_m.replace("PLAYER_THEIR", self.their())
            witness_m = witness_m.replace("PLAYER_THEIRS", self.theirs())
            witness_m = witness_m.replace("PLAYER", self.name)
            witness_m = message_token_pluralize(witness_m, "!", self)
            witness_m = message_token_pluralize(witness_m, "#", target)
            witness_m = message_token_capitalize(witness_m)

        self.echo(self_m, prompt = True)
        if tar_m:
            target.echo(tar_m, prompt = True)
        if witness_m:
            # room.echo(witness_m, prompt = True)
            pass