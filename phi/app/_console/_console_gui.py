import shutil
from logging import Handler, LogRecord

from .._display import AppDisplay
from ._console_plot import heatmap
from .._display_util import ordered_field_names
from ... import field
from ...field import StaggeredGrid


class ConsoleGui(AppDisplay):

    # def setup(self):
    #     app = self.app
    #     self.app.logger.removeHandler(self.app.console_handler)
    #     terminal_size = shutil.get_terminal_size(fallback=(80, 20))
    #
    #     class CustomHandler(Handler):
    #
    #         def emit(self, record: LogRecord) -> None:
    #             pass
    #
    #         def handle(self, record: LogRecord) -> None:
    #             line = app.message + " " * (max(1, terminal_size[0]-len(app.message)-1))
    #             print(line, end="\r")
    #
    #         def createLock(self) -> None:
    #             pass
    #
    #     self.app.logger.addHandler(CustomHandler())

    def show(self, caller_is_main: bool) -> bool:
        print("PhiFlow console interface active. Type 'help' for a list of available commands.")
        while True:
            print("PhiFlow>", end="")
            command = input()
            if command == 'step':
                self.app.step()
            elif command == 'play':
                self.app.play()
            elif command == 'pause':
                self.app.pause()
            elif command == 'show':
                self.draw()
            elif command.startswith('show '):
                fields = command[len('show '):].split(',')
                fields = [f.strip() for f in fields]
                self.draw(fields)
            elif command == 'help':
                print("Commands: help, step, play, pause, show, show <comma-separated fieldnames>")
            else:
                print(f"Command {command} not recognized.")

    def draw(self, field_names: list = None):
        if field_names is None:
            shown_fields = ordered_field_names(self.app, self.config.get('display'))
            if len(shown_fields) == 0:
                print("Nothing to show.")
                return
            field_names = shown_fields[:2] if len(shown_fields) > 2 else shown_fields
        values = []
        for n in field_names:
            try:
                values.append(self.app.get_field(n))
            except KeyError:
                print(f"The field {n} does not exist. Available fields are {self.app.fieldnames}")
                return
        cols, rows = shutil.get_terminal_size(fallback=(80, 20))
        plt_width = cols // len(values)
        plt_height = rows - 1
        lines = [""] * plt_height
        for v in values:
            if isinstance(v, StaggeredGrid):
                v = v.at_centers()
            v = field.vec_squared(v)
            plt_lines = heatmap(v, plt_width, plt_height)
            lines = [l+p for l, p in zip(lines, plt_lines)]
        print("\n".join(lines))
