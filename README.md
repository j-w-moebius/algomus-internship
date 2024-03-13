

## Ur / Sacred Harp

Prototype code for modular procedural generation with flexible constraints (Ur), applied to experimental generation of *Sacred Harp*-inspired music.

## Requirements

Python librairies
- music21
- rich

## Usage

```
cd src/ur

# Generate some draft songs in /data/gen/
python3 sacred.py 

# Generate some draft songs in /data/gen/, opens them (needs Verovio + Firefox)
python3 sacred.py --open

# Generate 20 songs in /data/gen/200-219, starting from 200
python3 sacred.py -s 200 -n 20
```

## Credits

Ur is open-source, licensed under the GPL version 3 or any later version. Ur is based on previous works in the Algomus Team, in particular from the [Awab project](http://algomus.fr/awab/), in collaboration with Véronique Béland and Guillaume Libersart, and was recoded in 2024 using a more modular approach.

Ur is developed by Romain Carl, Ken Déguernel, and Mathieu Giraud,
in collaboration with Holly Herndon and Ian Berman
