# Proppi Scrapper
This is a web scrapper that downloads houses' information available on the internet

## Requirements
1) Python 3
2) Pip 3

## First Use
1) Clone this repo
2) Verify the location of python3 with:
`which python3`
3) Create a virutalenv called 'proppienv' in the folder venv with the following command
```
cd venv
virtualenv -p \path\to\python3 proppienv
cd ..
```
4) Activate the virutalenv
`source venv/proppienv/bin/activate`
5) Install the requirments
`pip3 intall -r requirements.txt`

## Excecution
You can start scrapping by executing the file `scrapper.sh`

## Configuration
If you want to configure better the scrapper you should take a look in the config.json file