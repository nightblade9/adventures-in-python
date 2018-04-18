Title: Python's Interactive REPL
Date: 2018-04-17
Category: Posts

Did you ever write a bunch of Python code, save it into a file, run it, and wish you could somehow import all that content into a REPL session so you can poke it?

Turns out you can. [This long, thorough article about JSON in Python](https://realpython.com/python-json/) contains a real nugget of wisdom in the middle:

> **What’s interactive mode?** Ah, I thought you’d never ask! You know how you’re always jumping back and forth between the your editor and the terminal? Well, us sneaky Pythoneers use the -i interactive flag when we run the script. This is a great little trick for testing code because it runs the script and then opens up an interactive command prompt with access to all the data from the script!

Let's say you have a file called `cows.py` that looks like this:

```Python
class Cow:
    def __init__(self, name):
        print("{} says Moo!".format(name))

if __name__ == "__main__":
    goldie = Cow("Goldie")
```

If you run `python -i cows.py` from your terminal, not will see `Goldie says Moo!`, but you can reference the `goldie` variable:

```
Goldie says Moo!
>>> goldie
<__main__.Cow object at 0x02D1F510>
>>>
```

This is a really excellent way to combine the benefit of writing your code with an IDE and saving complex statements, with being able to quickly interact with it.