Setup (in folder 'demo'):

`docker-compose up -d`

`pip3 install --user requests`

`docker network inspect demo_bridge`

- Network name is \[parent folder\]\_bridge

`python ./mk_data.py --elastic-host [elastic search ip address] -n 10000`

- Load [Kibana](http://localhost:5601/app/kibana#/dev_tools/console?_g=())
