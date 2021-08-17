class Functional(object):
    @classmethod
    def setUp(cls):
        pass


class Unit(object):
    @classmethod
    def setUp(cls):
        pass


class GitAbandon(Unit):
    @classmethod
    def setUp(cls):
        pass


class GitAbandonFunctional(Functional):
    @classmethod
    def setUp(cls):
        pass


class GitChanges(Unit):
    @classmethod
    def setUp(cls):
        pass


class GitChangesFunctional(Functional):
    @classmethod
    def setUp(cls):
        pass


class GitReindex(Unit):
    @classmethod
    def setUp(cls):
        pass


class GitReindexFunctional(Functional):
    @classmethod
    def setUp(cls):
        pass


class GitRestash(Unit):
    @classmethod
    def setUp(cls):
        pass


class GitRestashFunctional(Functional):
    @classmethod
    def setUp(cls):
        pass


class GitSettings(Unit):
    @classmethod
    def setUp(cls):
        pass


class GitSettingsFunctional(Functional):
    @classmethod
    def setUp(cls):
        pass


class GitSnapshot(Unit):
    @classmethod
    def setUp(cls):
        pass


class GitSnapshotFunctional(Functional):
    @classmethod
    def setUp(cls):
        pass


class GitState(Unit):
    @classmethod
    def setUp(cls):
        pass


class GitStateFunctional(Functional):
    @classmethod
    def setUp(cls):
        pass


class GitStateExtensions(GitState):
    @classmethod
    def setUp(cls):
        pass


class GitUpstream(Unit):
    @classmethod
    def setUp(cls):
        pass


class GitUpstreamFunctional(Functional):
    @classmethod
    def setUp(cls):
        pass


class Utils(Unit):
    @classmethod
    def setUp(cls):
        pass


class UtilsDirectories(Utils):
    @classmethod
    def setUp(cls):
        pass


class UtilsExecute(Utils):
    @classmethod
    def setUp(cls):
        pass


class UtilsGit(Utils):
    @classmethod
    def setUp(cls):
        pass


class UtilsMessages(Utils):
    @classmethod
    def setUp(cls):
        pass


class UtilsParseActions(Utils):
    @classmethod
    def setUp(cls):
        pass


class UtilsParseString(Utils):
    @classmethod
    def setUp(cls):
        pass


class Issues(Functional):
    @classmethod
    def setUp(cls):
        pass
