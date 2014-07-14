![GSI Logo](http://gsi.dit.upm.es/templates/jgsi/images/logo.png)
[EUROSENTIMETN Reviews Cloud And Explore](http://eurosentiment-resources.herokuapp.com) 
=========================================
This is a simple application that uses both lexica and corpora in the EUROSENTIMENT portal to show reviews and their associated keywords.

Although this application does not show the full potential of the portal, it can get you started with building your own service or application.

It is built using Flask and Request, and can be easily deployed to a PaaS such as Heroky.
You can see it working here:

[DEMO on Heroku](http://eurosentiment-resources.herokuapp.com)

If you want to deploy your own copy, make sure you set your token and endpoint via ``config.py``,``.env`` (for Heroku) or setting your variables:

Example .env file:
```
TOKEN=<your token goes here>
RESOURCES_ENDPOINT=http://54.201.101.125/sparql/
```

Acknowledgement
---------------
EUROSENTIMENT PROJECT
Grant Agreement no: 296277
Starting date: 01/09/2012
Project duration: 24 months

![Eurosentiment Logo](https://avatars2.githubusercontent.com/u/2904232?s=100)
![FP7 logo](logo_fp7.gif)
