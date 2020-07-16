## Testing

### Prerequisites

On top of the standard requirements for running `dof-discord-bot`, you must also:

1. Install [`pytest`][1] and the [`pytest-cov`][2] plugin for code coverage.
2. Set `DOF_TESTING_TOKEN` environment variable, which will be used to load a secondary bot used to simulate a real user
and perform integration tests. You can also provide a `token-testing` file with the token - it should be located in the
package's resources folder, similarly to where the actual bot's token can be placed.

### Usage

You should run the code by calling `pytest --cov=dof_discord_bot` in the root folder of the project. The library should
then automatically configure everything and run all detected tests. In addition, a basic coverage report should be
generated (please refer to `pytest-cov` docs for getting more verbose information). Keep in mind that all logs will be
redirected to the tests-specific log folder for optional inspection.
Before running the code, make sure that dof tester bot has the "Defender" role.

Note that, currently, even if one bot fails to stop, the overall test run will be marked as a success.

[1]: https://docs.pytest.org/en/stable/getting-started.html
[2]: https://pypi.org/project/pytest-cov/