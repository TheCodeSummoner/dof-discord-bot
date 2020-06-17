## Testing

### Prerequisites

On top of the standard requirements for running `dof-discord-bot`, you must also:

1. Install [`pytest`][1].
2. Set `DOF_TESTING_TOKEN` environment variable, which will be used to load a secondary bot used to simulate a real user
and perform integration tests.

### Usage

You should run the code by calling `pytest` in the root folder of the project. The library should then automatically
configure everything and run all detected tests. All logs will be redirected to the tests-specific log folder.

Note that currently, even if one bot fails to stop, the overall test run will be marked as success.

[1]: https://docs.pytest.org/en/stable/getting-started.html