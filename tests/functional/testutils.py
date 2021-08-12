def init_local_config(repo):
    writer = repo.config_writer('repository')

    writer.set_value('user', 'name', 'Marcus Rosenow')
    writer.set_value('user', 'email', 'Brickstertwo@users.noreply.github.com')

    writer.set_value('git-changes', 'default-commit-ish', 'refs/heads/master')
    writer.set_value('git-changes', 'default-view', 'log')

    writer.set_value('git-settings.list', 'format', 'compact')

    writer.set_value('git-state.status', 'show-clean-message', 'true')
    writer.set_value('git-state', 'format', 'compact')
    writer.set_value('git-state', 'show-empty', 'false')
    writer.set_value('git-state', 'clear', 'true')
    writer.set_value('color', 'ui', 'never')  # not the default but eases testing
    writer.set_value('git-state', 'order', '')

    writer.set_value('git-upstream', 'include-remote', 'never')

    writer.release()
