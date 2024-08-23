

## Ur / Sacred Harp

Prototype code for modular procedural generation with flexible constraints (Ur), applied to experimental generation of *Sacred Harp*-inspired music.

## Requirements

Python librairies
- [music21](https://www.music21.org/music21docs/)
- [rich](https://rich.readthedocs.io/en/stable/introduction.html)
- [anytree](https://anytree.readthedocs.io/en/latest/)

## Usage

```

# Generate some Sacred Harp re-harmonization
python3 src/ur/harmonization.py

# Generate some music from scratch, in the style of the Holly Herndon project
python3 src/ur/sacred.py

(output is written to `data/gen/` in both cases)
```

## Credits

Ur is open-source, licensed under the GPL version 3 or any later version. Ur is based on previous works in the Algomus Team, in particular from the [Awab project](http://algomus.fr/awab/), in collaboration with Véronique Béland and Guillaume Libersart, and was recoded in 2024 using a more modular approach.

Ur is developed by Romain Carl, Ken Déguernel, and Mathieu Giraud,
in collaboration with Holly Herndon and Ian Berman
