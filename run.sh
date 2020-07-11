sudo docker build -t courseubc:latest .
sudo docker run -t -v $(pwd)/courses.txt:/usr/src/app/courses.txt courseubc:latest