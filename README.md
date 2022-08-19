# Distributed Continuous Integration System

## Files

## =====

- repo_observer.py -- Checks the repo for changes and notifies the dispatcher
- dispatcher.py -- Receives test requests and dispatches them to test runners
- test_runner.py -- Runs the tests and returns the results to dispatcher
- helpers.py -- Holds shared code
- update_repo.sh -- Updates the shared repo and drops a new file with the hash if there's a change
- test_runner_script.sh -- Updates the test runner's repository to the given commit hash
- run_or_fail.sh -- Helper method used in update_repo.sh and test_runner_script.sh

## Setup the CI System

### Create a folder test_repo in the root of the this project

```
mkdir test_repo
cd test_repo
git init
```

### Create a folder named tests in test_repo and in that create some testing scripts using unittest and then commit it

Example:

```
import unittest

class TestFileFail(unittest.TestCase):

    def test_fail(self):
        self.fail("I will fail. Yay!")

```

### Create clones of the test_repo by using following commands

```
git clone test_repo_clone_obs
git clone test_repo_clone_runner
```

## Running the CI System

### Start the dispatcher.py (Default port:8888)

```
python3 dispatcher.py
```

### In a new shell start test_runner.py (Default port:8900->9000) along with location of test_repo_clone_runner

```
python3 test_runner.py test_repo_clone_runner
```

### Lastly, in another new shell start repo_observer.py with the address of dispatcher server and location of test_repo_clone_obs

```
python3 repo_observer.py --dispatcher-server=localhost:8888 test_repo_clone_obs
```

### Once the setup is done we can check if it is able to run tests whenever new commits are made.

### Go to test_repo folder and create new commit

```
cd test_repo
touch file.txt
git add file.txt
git commit -m "."
```

## The test runners should run the tests and output the test results in test_results/ folder with the respective commit id's.
