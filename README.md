Python script that uses Selenium and BS4 to check if a course has a spot, and gets in them.

Have a courses.txt in same directory as script.py.
Courses.txt should look like

```
CPSC 330 102
CPSC 317 201
```

It will check each course and register if possible.
Also export your UBC Username and UBC Password in the script. I did it with loadenv.
```
export USER="user"
export PASSWORD="password"
```

Types of seats still needs to be worked on. Can add something in courses.txt to signify which type of seat. I'm not going to do that right now because I don't really need to.

To run script forever, put `main()` in a loop that runs forever.