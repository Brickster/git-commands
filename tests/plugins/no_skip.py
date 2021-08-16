import logging

from nose2.events import Plugin

log = logging.getLogger('nose2.plugins.noskip')

class NoSkip(Plugin):
    configSection = 'noskip'
    commandLineSwitch = (None, 'no-skip', 'Do not skip tests marked to be skipped')

    def startTestRun(self, event):
        log.info('Test skipping disable!')
