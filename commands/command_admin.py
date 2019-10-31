# Python modules.
import inspect, sys

# Evennia modules.
from evennia.server.sessionhandler import SESSIONS
from evennia.utils import search
from evennia.utils.utils import mod_import, variable_from_module, class_from_module

# Blackbirds modules.
from commands.command import Command
from utilities.classes import class_from_name
from utilities.display import notify, bullet, header, divider
from utilities.menu import Menu
from server.conf import settings

from typeclasses.accounts import Account
from typeclasses.archetypes import Archetype, Blackbird, Citizen, Privileged, Survivalist
from typeclasses.areas import Area
from typeclasses.characters import Character
from typeclasses.environments import Environment
from typeclasses.exits import Exit
from typeclasses.species import Species, Human, Carven, Sacrilite, Luum, Idol
from typeclasses.zones import Zone

class CmdReload(Command):
    """
    reload the server

    Usage:
      reload [reason]

    This restarts the server. The Portal is not
    affected. Non-persistent scripts will survive a reload (use
    reset to purge) and at_reload() hooks will be called.
    """
    key = "reload"
    aliases = ['restart']
    locks = "cmd:perm(reload) or perm(Developer)"
    help_category = "System"

    def func(self):
        "Reload the system."
        reason = ""
        if self.args:
            reason = "%s" % self.args.rstrip(".")
        SESSIONS.announce_all(notify("Game", f"The system is reloading{reason}, please be patient."))
        SESSIONS.portal_restart_server()

class CmdUpdate(Command):
    key = "update"
    locks = "perm(Developer)"
    help_category = "Admin"

    def func(self):
        ply = self.caller

        obj_type = self.word(1)
        valid_objs = ("accounts", "rooms", "characters", "environments", "zones", "areas", "archetypes", "species", "exits")

        if not obj_type:
            ply.error_echo("You must specify a Python class to update. Valid classes are:")
            for o in valid_objs:
                ply.echo(bullet(o))
            return

        obj_type = obj_type.lower()

        if obj_type == "accounts":
            for o in Account.objects.all():
                o.update()
        elif obj_type == "rooms":
            Room = class_from_module(settings.BASE_ROOM_TYPECLASS)
            for o in Room.objects.all():
                o.update()
        elif obj_type == "characters":
            for o in Characters.objects.all():
                o.update()
        elif obj_type == "environments":
            for o in Environments.objects.all():
                o.update()
        elif obj_type == "zones":
            for o in Zones.objects.all():
                o.update()
        elif obj_type == "areas":
            for o in Areas.objects.all():
                o.update()
        elif obj_type == "archetypes":
            for o in Archetypes.objects.all():
                o.update()
        elif obj_type == "species":
            for o in Species.objects.all():
                o.update()
        elif obj_type == "exits":
            for o in Exits.objects.all():
                o.update()
        else:
            ply.error_echo("You must specify a Python class to update. Valid classes are:")
            for o in valid_objs:
                ply.echo(bullet(o))
            return

        ply.echo(f"All |W{obj_type}|n have been updated.")

class CmdList(Command):
    key = "list"
    locks = "perm(Developer)"

    def func(self):
        ply = self.caller
        obj_type = self.word(1)
        obj_list = []
        valid_objs = ("accounts", "rooms", "characters", "environments", "zones", "areas", "archetypes", "species", "exits")

        if obj_type not in valid_objs:
            ply.error_echo("You must specify a valid Python class to list. Valid classes are:")
            for o in valid_objs:
                ply.echo(bullet(o))
            return

        if obj_type == "rooms":
            obj_list = [o for o in class_from_module(settings.BASE_ROOM_TYPECLASS).objects.all()]
        else:
            # To-do: make this less ghetto as all hell
            d_o = obj_type[:-1] if obj_type != "species" else "species" # quick depluralizing of obj_type
            obj_list = [o for o in class_from_name("typeclasses." + obj_type, d_o.capitalize()).objects.all()]

        ply.echo(header(obj_type.capitalize()))

        for o in obj_list:
            ply.echo(bullet(f"{o.name}"))

        ply.echo(divider())

class CmdTest(Command):
    key = "test"
    locks = "perm(Admin)"

    def func(self):
        pass
        # Menu(self.caller, "menus.testmenu", cmdset_mergetype = "Replace", cmd_on_exit = "look", startnode = "node_test", debug = True)

class CmdSpeciesChange(Command):
    key = "specieschange"
    aliases = ["specchange"]
    locks = "perm(Admin)"

    def func(self):
        ply = self.caller
        species = self.word(1).lower()
        if species == "human":
            ply.db.species = Human()
            ply.echo("Species changed to Human.")
        elif species == "carven":
            ply.db.species = Carven()
            ply.echo("Species changed to Carven.")
        elif species == "sacrilite":
            ply.db.species = Sacrilite()
            ply.echo("Species changed to Sacrilite.")
        elif species == "luum":
            ply.db.species = Luum()
            ply.echo("Species changed to Luum.")
        elif species == "idol":
            ply.db.species = Idol()
            ply.echo("Species changed to Idol.")
        else:
            ply.error_echo("That is not a valid species name.")

class CmdArchetypeChange(Command):
    key = "archetypechange"
    aliases = ["archchange"]
    locks = "perm(Admin)"

    def func(self):
        ply = self.caller
        archetype = self.word(1).lower()

        if archetype == "blackbird":
            ply.db.archetype = Blackbird()
            ply.echo("Archetype changed to Blackbird.")
        elif archetype == "citizen":
            ply.db.archetype = Citizen()
            ply.echo("Archetype changed to Citizen.")
        elif archetype == "privileged":
            ply.db.archetype = Privileged()
            ply.echo("Archetype changed to Privileged.")
        elif archetype == "survivalist":
            ply.db.archetype = Survivalist()
            ply.echo("Archetype changed to Survivalist.")
        else:
            ply.error_echo("That is not a valid archetype.")

class CmdSetHp(Command):
    key = "sethp"
    locks = "perm(Admin)"

    def func(self):
        ply = self.caller
        hp = self.word(1)
        if not hp.isnumeric():
            ply.error_echo("Use a number, ding-dong.")
            return

        ply.db.hp["current"] = int(hp)
        ply.echo(f"You set your HP to |G{hp}|n.")

class CmdPronounChange(Command):
    key = "pronounchange"
    aliases = ["prochange"]
    locks = "perm(Admin)"

    def func(self):
        ply = self.caller
        pronoun_set = self.word(1)

        if pronoun_set in ["1", "he", "male", "m"]:
            ply.db.pronoun_they = "he"
            ply.db.pronoun_them = "him"
            ply.db.pronoun_their = "his"
            ply.db.pronoun_theirs = "his"
        elif pronoun_set in ["2", "she", "female", "f"]:
            ply.db.pronoun_they = "she"
            ply.db.pronoun_them = "her"
            ply.db.pronoun_their = "her"
            ply.db.pronoun_theirs = "hers"
        elif pronoun_set in ["3", "plural", "t"]:
            ply.db.pronoun_they = "they"
            ply.db.pronoun_them = "them"
            ply.db.pronoun_their = "their"
            ply.db.pronoun_theirs = "theirs"
        elif pronoun_set in ["4", "neuter", "genderless", "n", "g"]:
            ply.db.pronoun_they = "it"
            ply.db.pronoun_them = "it"
            ply.db.pronoun_their = "its"
            ply.db.pronoun_theirs = "its"
        else:
            ply.error_echo("Please choose from the following values:\n  1, 2, 3, 4\n  he, she, plural, neuter\n  male, female, genderless  \n  m, f, t, n/g")
            return

        ply.echo(f"Your pronouns have been set to {ply.pronouns()}.")