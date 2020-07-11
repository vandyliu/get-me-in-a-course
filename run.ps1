$person=$args[0]
if ($person -eq $null) {
    $person = "vandy"
}
docker build -t courseubc:latest .
# docker run -it --entrypoint /bin/sh -v $pwd/courses.txt:/usr/src/app/courses.txt courseubc:latest
docker run -t -v $pwd/courses.txt:/usr/src/app/courses.txt courseubc:latest $person