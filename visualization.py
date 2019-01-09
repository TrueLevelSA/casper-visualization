import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

from os import listdir
from os.path import isfile, join

# utility classes

import json


class LogFile(object):

    def __init__(self, json_content, file_name=None):
        self._file_name = file_name if file_name is not None else "noname"
        self._steps = [Step(s) for s in json_content]
        if len(self._steps) <= 0:
            self._max_length = 0
            self._sender_count = 0
        else:
            self._max_length = max([s._max_length for s in self._steps])
            self._sender_count = self._steps[0]._sender_count

    def __repr__(self):
        s = "LogFile{"
        for step in self._steps:
            s += "%s," % step
        if len(self._steps) > 0:
            s = s[:-1]
        s += "}"
        return s

    @staticmethod
    def parse_json_file(filename):
        with open(filename, 'r') as f:
            json_content = json.load(f)
        return LogFile(json_content, filename)


class Step(object):
    def __init__(self, json_content):
        self._sender_count = json_content["sendercount"]
        self._cliques = json_content["clqs"]
        # reversed so that validator 0 is at the bottom
        self._last_messages = [View(j) for j in json_content["lms"]]
        self._max_length = max([v.get_max_length() for v in self._last_messages])

    def __repr__(self):
        s = "Step{sender_count: %d, cliques: %s, last_messages: %s}" % (
            self._sender_count, self._cliques, self._last_messages)
        return s


class View(object):
    def __init__(self, json_content):
        _json_content = json_content[0]
        self.heights = {}
        self._messages = {key: Message(value) for (key, value) in _json_content.items()}
        self.compute_heights()

    def __repr__(self):
        return "View%s" % self._messages

    def get_max_length(self):
        return max([len(m._justification) for m in self._messages.values()])

    def compute_heights(self):
        for name, message in self._messages.items():
            for index, block in enumerate(reversed(message._justification)):
                if block is not None:
                    self.heights[block[1]] = index
                    last_block = block
                else:
                    self.heights[None] = -1


class Message(object):
    def __init__(self, json_content):
        # formatting?
        assert len(json_content) == 1
        # get first key
        self._name, justification = json_content.popitem()
        self._justification = [tuple(j) if j != 'None' else None for j in justification]

    def __repr__(self):
        return "Message{name: %s, justification: %s}" % (self._name, self._justification)


class IndexSteps(object):
    _FAST_FORWARD_STEP = 5

    def __init__(self, fig, log_files):
        self._fig = fig
        self._log_files = log_files
        self._selected_log_file = 0
        self._log_file = log_files[self._selected_log_file]
        self._axes = fig.subplots(self._log_file._sender_count, sharex=True, sharey=True)
        self._fix_axes()
        self._selected_step = 0
        self._min = 0
        self._max = len(self._log_file._steps)-1
        self._plot()
        self._print_title()

    def _perform_step(self, step):
        self._selected_step += step
        # clamp value
        self._selected_step = min(self._max, self._selected_step)
        self._selected_step = max(self._min, self._selected_step)
        self._plot()

    def _fix_axes(self):
        '''if there is only one validator, there is only one axe and
        matplotlib returns only an object, not a list of objects.
        as everything is based on loops over a list of axes it is easier to fix it here once'''
        if not isinstance(self._axes, np.ndarray):
            self._axes = [self._axes]

    def next(self, event):
        self._perform_step(1)

    def prev(self, event):
        self._perform_step(-1)

    def next_ff(self, event):
        self._perform_step(self._FAST_FORWARD_STEP)

    def prev_ff(self, event):
        self._perform_step(-self._FAST_FORWARD_STEP)

    def _plot(self):
        self._clear_axes()

        current_step = self._log_file._steps[self._selected_step]
        length = len(current_step._last_messages) - 1

        for i, view in enumerate(current_step._last_messages):
            for key, in sorted(view._messages):
                message = view._messages[key]
                x = [view.heights[m[1]] for m in message._justification if m is not None]
                y = [-1 if m is None else int(m[0]) for m in message._justification if m is not None]
                self._axes[length - i].plot(x, y, 'bo', linestyle='solid')
            self._axes[length-1].set_ylabel(i)

        # set x,y ticks for each axes
        plt.setp(
            self._axes,
            xticks=range(1, self._log_file._max_length),
            yticks=range(0, self._log_file._sender_count)
        )

        self._print_subtitle()
        self._fig.canvas.draw()

    def prev_log_file(self, event):
        self._perform_log(-1)

    def next_log_file(self, event):
        self._perform_log(1)

    def _clear_axes(self):
        for axe in self._axes:
            axe.cla()

    def _print_title(self):
        self._fig.suptitle(self._log_file._file_name)
        self._print_subtitle()

    def _print_subtitle(self):
        self._axes[0].set_title("Step %d/%d" % (self._selected_step + 1, self._max + 1))


    def _perform_log(self, selected_log_file_step):
        self._selected_log_file += selected_log_file_step
        # self._plot()
        # pass

        min_index = 0
        max_index = len(self._log_files)-1

        self._selected_log_file = max_index if self._selected_log_file >= max_index else self._selected_log_file
        self._selected_log_file = min_index if self._selected_log_file <= min_index else self._selected_log_file

        self._axes[0].set_title("couille %s" % self._selected_log_file)
        self._log_file = self._log_files[self._selected_log_file]
        self._min = 0
        self._max = len(self._log_file._steps)-1
        self._selected_step = self._min

        self._clear_axes()

        plt.setp(self._axes, xticks=[], yticks=[])
        self._axes = self._fig.subplots(self._log_file._sender_count, sharex=True, sharey=True)
        self._fix_axes()
        self._print_title()
        self._plot()


def main():
    # json files loading
    directory = "./generated"

    # all files (no folders) in directory
    onlyfiles = sorted([f for f in listdir(directory) if isfile(join(directory, f))])

    log_files = [LogFile.parse_json_file(directory+'/'+f) for f in onlyfiles]

    # filter out empty files
    log_files = [log_file for log_file in log_files if len(log_file._steps) > 0]

    size_x = 0.075
    size_y = 0.054

    size_x_large = size_x * 1.4
    offset_x = 0.01

    fig = plt.figure(figsize=(8, 12), dpi=100)

    callback = IndexSteps(fig, log_files)

    axprev = plt.axes([0.15 + 1 * size_x, offset_x, size_x, size_y])
    axnext = plt.axes([0.15 + 2 * size_x, offset_x, size_x, size_y])

    axprev_ff = plt.axes([0.15 + 0 * size_x, offset_x, size_x, size_y])
    axnext_ff = plt.axes([0.15 + 3 * size_x, offset_x, size_x, size_y])

    axprev_log = plt.axes([0.65, offset_x, size_x_large, size_y])
    axnext_log = plt.axes([0.65 + size_x_large, offset_x, size_x_large, size_y])

    bnext = Button(axnext, '>')
    bnext.on_clicked(callback.next)

    bprev = Button(axprev, '<')
    bprev.on_clicked(callback.prev)

    bnext_ff = Button(axnext_ff, '>>')
    bnext_ff.on_clicked(callback.next_ff)

    bprev_ff = Button(axprev_ff, '<<')
    bprev_ff.on_clicked(callback.prev_ff)

    bnext_log = Button(axnext_log, "Next Log")
    bnext_log.on_clicked(callback.next_log_file)

    bprev_log = Button(axprev_log, "Prev Log")
    bprev_log.on_clicked(callback.prev_log_file)

    plt.show()


if __name__ == '__main__':
    main()
