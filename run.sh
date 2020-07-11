sudo docker build -t courseubc:latest .
sudo docker run -t -v /home/ec2-user/get-me-in-a-course/courses.txt:/usr/src/app/courses.txt courseubc:latest
