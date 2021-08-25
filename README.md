# Chatbot-for-Dental-Clinic-Booking

![](https://github.com/n3ih7/Chatbot-for-Dental-Clinic-Booking/blob/main/archive/Screen_Shot_2019-07-27_at_6.05.38_pm.png?raw=true)
<img src="https://github.com/n3ih7/Chatbot-for-Dental-Clinic-Booking/blob/main/archive/Screen_Shot_2019-07-27_at_6.22.17_pm.png?raw=true" width="300">

## Fulfillments
The bot is able to respond to greeting.

The bot will ask for the preferred doctor and provide information about the doctor.

The bot can list all the available doctors in the clinic and the user can choose.

The bot can check if the selected timeslot available or suggest another timeslot.

The bot can confirm the booking and summarize at the end.

The bot can cancel the booking if the client requested it.

## How to use

`docker-compose up -d --build` (The default port is 80)

Then, use your browser (Chrome, Firefox recommended) to access [http://127.0.0.1](http://127.0.0.1) or [localhost](http://localhost)

If you need to specify another port, use `docker-compose build` then `docker-compose run -d --publish <YOUR DESIRED PORT NUMBER>:80 frontend`

## How to stop

If you are using port 80, use `docker-compose stop`

If you are using custom port, use `docker-compose stop` then `docker ps`, find something like 'frontend_run_xxxxxxxxxxx' in first column then type `docker stop frontend_run_xxxxxxxxxxx`

## Show case

![](https://github.com/n3ih7/Chatbot-for-Dental-Clinic-Booking/blob/main/archive/Screen%20Shot%202020-11-26%20at%209.15.29%20pm.png?raw=true)

![](https://github.com/n3ih7/Chatbot-for-Dental-Clinic-Booking/blob/main/archive/Screen%20Shot%202020-11-26%20at%209.15.33%20pm.png?raw=true)

![](https://github.com/n3ih7/Chatbot-for-Dental-Clinic-Booking/blob/main/archive/Screen%20Shot%202020-11-26%20at%209.15.35%20pm.png?raw=true)
