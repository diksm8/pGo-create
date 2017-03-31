# NOT WORKING Pokemon Account Creator made in Python 2.7 NOT WORKING
Based on ~~[Pokemon Trainer Account Mass Account Generator](https://github.com/dannybess/PokemonGo-Account-Generator/) by [dannybess](https://github.com/dannybess)~~, [PoGoTos](https://github.com/TachyonRSA/PoGoTos) by [Tachyon](https://github.com/TachyonRSA) and the [pgoapi](https://github.com/keyphact/pgoapi) by [KeyPhact Moon](https://github.com/keyphact)

## Features
* Create accounts
* Verify email
* Accept Pokémon Go ToS using API
* Ouput to neat json file [Example](https://github.com/diksm8/pGo-create/blob/master/README.md#example-output)
* Threading

## Usage
`pgocreate.py [OPTIONS] [OUTFILE]`
#### Options
* `--accounts` Number of accounts to make. Default is 50.
* `--size` Size of username, range between 6 and 16. Default is 10.
* `--password` Password to use for all accounts. If this option is not used passwords will be randomized for each account.
* `--threads` Amount of threads for each task, range between 1 and 16. Default is 4.
* `--pos` Position, example `--pos LAT LON`

## Example output
```JSON
[
    {
        "Username": "XF00N8B", 
        "Date created": "2016-08-08 22:37:36", 
        "ToS accepted": true, 
        "Email verified": true, 
        "Password": "viET3Nhuv", 
        "Email": "dijjqew@x7mfj.anonbox.net"
    }, 
    {
        "Username": "1T0DAV7", 
        "Date created": "2016-08-08 22:38:25", 
        "ToS accepted": true, 
        "Email verified": true, 
        "Password": "77nU14y5O", 
        "Email": "b47zrg5@x7mfj.anonbox.net"
    }
]
```

## Install
### Windows
[Instalaltion video](https://u.pomf.is/rnugfa.mp4)
Installation on windows requires extra steps.


Navigate to www.lfd.uci.edu/~gohlke/pythonlibs/#lxml and download `lxml-3.6.1-cp27-cp27m-win32.whl`. Install it using `pip install lxml-3.6.1-cp27-cp27m-win32.whll`. If you get an error (very unlikely) try the `lxml-3.6.1-cp27-cp27m-win_amd64.whl` instead.

Install [Microsoft Visual C++ Compiler for Python 2.7](https://www.microsoft.com/en-us/download/details.aspx?id=44266)

After that you can install the actual script. Clone this repo and navigate to it, run `python setup.py install`.
### Unix (OSX/Linux)
Clone this repo and navigate to it, run `python setup.py install`.


## ToDo
- [X] Fix output to not overwrite
- [X] Fix json output to look like http://pastebin.com/dZy4ZNf5
- [x] If no password is given, randomize password for each account
- [x] Make the different functions not wait for eachoter (Threading)
    - ~~Too scared to do this part :/~~
- [ ] Gain publicity
    - Too scared to do this part :/ might gain issues we need to fix
