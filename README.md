# ottawa-final

Final version for the Ottawa app

Web sites to configure the social login:
* https://instagram.com/accounts/manage_access/
* https://account.live.com/developers/applications/apisettings/000000004414e1c0
* https://console.developers.google.com/project/southern-field-94921/apiui/credential?authuser=1
* https://www.linkedin.com/developer/apps

### Dev deployment

You'll need docker and docker-compose both installed on the host machine.

Running the app on port 80 is simple:

    docker-compose up

Then navigate to [http://localhost](http://localhost).

All code changes will be reflected inside the container.
