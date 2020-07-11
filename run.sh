sudo docker build -t courseubc:latest /home/ec2-user/get-me-in-a-course
sudo docker run -t -v /home/ec2-user/get-me-in-a-course/courses.txt:/usr/src/app/courses.txt courseubc:latest
