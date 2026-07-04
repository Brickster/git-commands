import nox

PYTHON = "3.10"


@nox.session(python=False)
def quality(session):
    # For a full check, run: nox -s quality -- --all
    session.run('qlty', 'check', *session.posargs, external=True)


@nox.session(python=PYTHON)
def typecheck(session):
    session.install("-r", "requirements-test.txt")
    session.run("mypy", "bin/")


@nox.session(python=PYTHON)
def tests(session):
    session.install("-r", "requirements-test.txt")
    session.run("coverage", "run", "-m", "pytest", "-v", *session.posargs)
    session.run("coverage", "lcov", "-o", "coverage.lcov")
    session.run("coverage", "report")


@nox.session(python=PYTHON, default=False)
def test(session):
    tests(session)

@nox.session(python=PYTHON, default=False)
def unit(session):
    session.install("-r", "requirements-test.txt")
    session.run("coverage", "run", "-m", "pytest", "-v", "tests/unit/", *session.posargs)
    session.run("coverage", "lcov", "-o", "coverage.lcov")
    session.run("coverage", "report")
