#Pokemon Account Creator made in Python 2.7
Based on [Pokemon Trainer Account Mass Account Generator](https://github.com/dannybess/PokemonGo-Account-Generator/) by [dannybess](https://github.com/dannybess), [PoGoTos](https://github.com/TachyonRSA/PoGoTos) by [Tachyon](https://github.com/TachyonRSA) and the [pgoapi](https://github.com/keyphact/pgoapi) by [KeyPhact Moon](https://github.com/keyphact)

##Features
* Create accounts
* Verify email
* Accept Pokémon Go ToS using API
* Ouput to neat json file

##Usage
`pgocreate.py [OPTIONS] [OUTFILE]`
####Options
* `--accounts` Number of accounts to make. Default is 50.
* `--size` Size of username, range between 6 and 16. Default is 10.
* `--password` Password to use for all accounts. If this option is not used passwords will be randomized for each account.

##Example output
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

##ToDo
- [X] Fix output to not overwrite
- [X] Fix json output to look like http://pastebin.com/dZy4ZNf5
- [x] If no password is given, randomize password for each account
- [ ] Make the different functions not wait for eachoter (Threading)
    - Too scared to do this part :/
