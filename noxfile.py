import nox

PYTHON = "3.10"


@nox.session(python=PYTHON)
def lint(session):
    session.install("flake8")
    session.run("flake8", ".", "--count", "--select=E9,F63,F7,F82", "--show-source", "--statistics")
    session.run("flake8", ".", "--count", "--exit-zero", "--max-complexity=10", "--statistics")


@nox.session(python=PYTHON)
def tests(session):
    session.install("-r", "requirements-test.txt")
    session.run("coverage", "run", "-m", "pytest", "-v", *session.posargs)
    session.run("coverage", "lcov", "-o", "coverage.lcov")
    session.run("coverage", "report")
