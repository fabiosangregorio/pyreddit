# PyReddit
> Reddit API for [telereddit](https://github.com/fabiosangregorio/telereddit) and [discoreddit](https://github.com/fabiosangregorio/discoreddit).

## Installation

1. Clone the repository
1. Install requirements

    ```bash
    pip install -r requirements/requirements.txt
    ```

## Usage
Before using pyreddit you must initialize it with a valid configuration secret using [python-dotenv](https://github.com/theskumar/python-dotenv).

1. Duplicate `/pyreddit/config/.env.template`
1. Fill the required secrets (this duplicated file should NOT be committed.)
1. Initialize the environment variables

    ```python
    import os
    from dotenv import load_dotenv
    from pyreddit.services.services_wrapper import ServicesWrapper


    load_dotenv(
        dotenv_path=os.path.join(os.path.dirname(__file__), "../config/.env")
    )
    ServicesWrapper.init_services()
    
    reddit.get_post("https://www.reddit.com/r/DidntKnowIWantedThat/comments/iruaqs/but_do_i_really_need_it/")
    ```

## Bugs and feature requests
If you want to report a bug or would like a feature to be added, feel free to open an issue.

## Contributing
1. Open an issue to discuss the change you want to make
1. Fork the repository
1. Install dev requirements

    ```bash
    pip install -r requirements/dev.txt
    ```

1. Make changes
1. Run tests

    ```bash
    python -m unittest
    ```
    
1. Open a pull request and make sure all checks pass

## Versioning
We follow Semantic Versioning. The version X.Y.Z indicates:

* X is the major version (backward-incompatible),
* Y is the minor version (backward-compatible), and
* Z is the patch version (backward-compatible bug fix).
 
## License
**[GPL v3](https://www.gnu.org/licenses/gpl-3.0)** - Copyright 2020 © <a href="http://fabio.sangregorio.dev"
  target="_blank">fabio.sangregorio.dev</a>.
 