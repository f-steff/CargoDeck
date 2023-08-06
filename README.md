
# CargoDeck
A Docker image to creates webpages with a dynamic inventory of containers and links.

## What is CargoDeck?
CargoDeck is a web application developed with Python, Flask, Gunicorn, and Gevent. It provides a dynamic dashboard displaying all the Docker Containers that are specified by the user, as well as user defined links. The dynamic part of the dashboard, is due to the use of Docker labels, which can be associated to all running containers. These labels can be easily administered using Docker command line instructions and are especially suited to be used with docker-compose.yml files.

## Features
- Simple web interface providing site info, sections with section info, and clickable links to your specified services, including additional links.
- No administration GUI, everything is text based:
	- Configure site settings through environment variables.
	- Output is Dynamically tied to Docker labels, associated with all running Docker containers.
- Option to run multiple instances on different ports with unique label matches.
- Error visulization when unexpected container behaviors are detected.
- Style customization via CSS and jinja2 templates.

## Availability
Docker Hub: Pre-built image available at the [CargoDeck Docker Hub Repository](https://hub.docker.com/r/fsteff/cargodeck). 
GitHub: Source code is available at the [CargoDeck GitHub Repository](https://github.com/f-steff/CargoDeck).

## Installation

### Execute CargoDeck with Docker command line
Although using Docker Compose is recommended, you can execute CargoDeck directly from the command line. 
All configurations have sensible defaults, so only minor changes may be needed.

Here's a command line example, which is setting one environment variable, and two labels:

    docker run -d --name=CargoDeck --restart=unless-stopped -p 9080:80 -e LOGLEVEL=INFO -l "CargoDeck.site_name=My Super Inventory" -l "CargoDeck.site_auto_refresh=60" -v /var/run/docker.sock:/var/run/docker.sock:ro fsteff/cargodeck

You can now access CargoDesk at http://localhost:9080 in your web browser.

### Execute CargoDeck with Docker-Compose

Use the following small `docker-compose.yml` file, or download the bigger example [docker-compose.yml](https://github.com/f-steff/CargoDeck/blob/main/docker-compose.yml) from the [CargoDock GitHub page](https://github.com/f-steff/CargoDock), then execute this command:

    docker-compose -p cargodeck up -d

You can now access CargoDesk at http://localhost:9080 in your web browser.

#### Small example `docker-compose.yml` file:
```
version: '3.9'

services:
    CargoDeck:
        image: fsteff/cargodeck
        container_name: CargoDeck
        restart: unless-stopped
        environment:
            - LOGLEVEL=INFO
            - PORT=80
        ports:
            - 9080:80
        volumes:
            - cargodeck:/usr/src/app:ro
            - /var/run/docker.sock:/var/run/docker.sock:ro
        labels:
            - "CargoDeck.site_name=CargoDeck - dynamic container inventory"
            - "CargoDeck.site_icon=fa fa-university fa-3x"
            - "CargoDeck.section_header=Section header test."
            - "CargoDeck.section_header_icon=fa fa-birthday-cake"
            - "CargoDeck.section_header_body=Brief intro. Nothing fancy.<br>"
            - 
            - "CargoDeck.display_right=Info"
            
            - "CargoDeck.card_url=http://localhost:9080"
            - "CargoDeck.card_icon=fa fa-university"
            - "CargoDeck.card_note=CargoDeck link"

            - "CargoDeck.index.example.card_url=https://example.com"
            - "CargoDeck.index.example.card_note=Example link"

            - "CargoDeck.Info.Google.card_url=https://google.com"
            - "CargoDeck.Info.Google.card_image=https://static-00.iconduck.com/assets.00/google-icon-2048x2048-czn3g8x8.png"
            - "CargoDeck.Info.Google.card_note=Esessential serach Tool"

            - "CargoDeck.Info.Traefik.card_url=https://traefik.io/traefik/"
            - "CargoDeck.Info.Traefik.card_image=https://traefik.io/static/traefik-proxy-logo--white-82153be41e0ce620a921b4bce974f6d8.svg"
            - "CargoDeck.Info.Traefik.card_note=Great Reverse Proxy"

            - "CargoDeck.Info.Homer.card_url=https://homer-demo.netlify.app/#"
            - "CargoDeck.Info.Homer.card_image=https://homer-demo.netlify.app/logo.png"
            - "CargoDeck.Info.Homer.card_note=UI inspiration for this tool."

volumes:
    cargodeck:
        name: cargodeck
        driver: local
```

## Execute a Container to show up in CargoDeck 
To display a container as a container card in CargoDeck, you must attatch at least one of these labels to the container:  ***card_name, card_note, card_url, card_icon, or card_image***.

### Special card_* labels:
The ***card_unique_id*** is always set whenever a card is defined, but you can specify it, too, and perhaps use it in the template. It's value is currently not used. 
The ***card_expected_name*** can be set on another container, which will make sure a card with a warning is displayed if a container with the expected name is not running.

Refer to the two sections above for how to actually start a container, either using the command line or docker-compose.
    
## Customization and Data Persistence
To access and modify template files, you can mount the folders inside the container. For example, use `cargodeck:/usr/src/app` to volume mount or `./cargodeck:/usr/src/app` to bind mount. The container must be restarted to apply edits made to the template files.

Custom error handling can be added by adding files such as `404.html` to the `templates/` folder.


## CargoDeck Site Layout
The layout includes the following elements, as seen in Fig.1:

* **Site Header**: Displays optional image/icon, site name, and current section.
* **Site Navigation**: Lists section names/links alphabetically, and can display icons.
* **Section Header**: (Optional) Contains one or more of the optional header icon, text, and body (with HTML support).
* **Cards Section**: Displays cards defined by Docker labels, containing images/icon, names, and notes.
* **Section Footer**: (Optional) Contains one or more of the optional footer icon, text, and body (with HTML support).
* **Site Footer**: Defaults to the version number and may contain auto-update info.

![An example of CargoDeck running](https://raw.githubusercontent.com/f-steff/CargoDeck/main/Screenshot.png)
Fig 1. Example output with the `docker-compose.yml` file from the repository.

## Configuration of the CargoDesk: Labels

The configuration is 100% done by setting labels on containers, easiest performed through various 
docker-compose.yml files.

Labels are collected from all running containers, so it's possible to have one container add info to all parts of CargoDeck.

It's easy at add labels, and the closer to the target container they are specified, the simpler the syntax there is:

A very simple docker-compose.yml may look like this:

    version: '3.9'
    services:
        SomeApp:
            image: org/someapp
            container_name: SomeApp
            ports:
                - 9081:80
            volumes:
                - /var/run/docker.sock:/var/run/docker.sock:ro
            labels:
                - "CargoDeck.card_url=http://localhost:9081"
                - "CargoDeck.card_note=The great SomeApp"

Note that since a section isn't part of the lable above, the above card will be associated with the index section.
To directly specify a section, change the labels like this:

                - "CargoDeck.Specific_Section.card_url=http://localhost:9081"
                - "CargoDeck.Specific_Section.card_note=The great SomeApp"

From another docker-compose.yml file, it's possible to extend the same entry, by adding the following lable:

                - "CargoDeck.Specific_Section.SomeApp.card_icon=fa fa-university"

All labels follow this rule, which will be described in more details below.

Beware: 
: Labels and values related to labels are case-sensitive!

### Label syntax
Supported label syntax is as follows:

1.	A.X=value
2.	A.B.X=value
3.	A.B.C.X=value

Where:
**A: Instance Match name**
This is the name that an instance of CargoDeck will match on, to take the label into consideration.
Defaults to the container_name, but can be overwitten using the MATCH|MATCHn environmental variables.
Defaults to the defined container_name

**B: Section name**
This ensures that the value you assign are targeting the correct section.
If not specified, this defaults to 'index'

**C: Receiving name**
This is used to target specific cards, such as when setting a different display name to an existing card.
It also allows full virtual cards to be created, such as if you want to make a section of bookmarks.
When applying multiple lines to a section_header_body and similar, this sorted value will be used to join the lines.

**X: Value key**
This is the key name of the value you want to modify.
Values starting with 'site' are global settings, used across all sections.
Here are the keys in order of usage on the rendered page:

| Key value | Description | Status from v0.1 |
|--|--|--|
|`site_name` |Sets the name of the CargoDeck site |New in 1.0.0<br />Was: `sitename`  |
|`site_icon` |Font Awesom icon  |New in 1.0.0<br />Was: `siteicon` |
|`site_image` |Image in formats understood by browsers |New in 1.0.0<br />Was `siteicon` |
|`site_default_card_icon` |Default icon for all cards without a specific icon specified.  |New in 1.0.0 |
|`site_auto_refresh` |Number of seconds between screen refresh. If not specified or less than 30, refresh is disabled.  |New in 1.0.0 |
|`site_missing_card_text` |Error text to write  |New in 1.0.0  |
|`site_missing_card_icon` |Error icon to use |New in 1.0.0  |
|`site_wrong_section_text`  |Error text if the section does not exist.  |New in 1.0.0|
|`site_wrong_section_icon`  |Font Awesom icon  |New in 1.0.0  |
|`site_expected_section_text`  |Error text if the section does not exist. |New in 1.0.0 |
|`site_expected_section_icon`  |Font Awesom icon |New in 1.0.0 |
|`display_right`  |Move one section to the right side of the navigation bar.  |New in 1.0.0<br />Was `right` |
|`section_name`  | Set sections display name instead of extration from labels-key |New in 1.0.0 |
|`section_expected_body`  | Err. if name not found among sections's (note 1)|New in 1.0.0 |
|`section_direct_link`  |Converts a section into a direct link, so clicking the navigation button opens the specified url.  |New in 1.0.0  |
|`section_header`  |can contain html, use for \<b\>, \<i\>, etc.  |New in 1.0.0<br />Was `header`  |
|`section_header_icon`  |Font Awesom icon  |New in 1.0.0<br />Was `header_icon`  |
|`section_header_body`  |can contain html, use for \<b\>, \<i\>, etc.	(note 1)  |New in 1.0.0<br />Was `intro`  |
|`card_name`  |Set a different name instead of container_name  |New in 1.0.0<br />Was `name`  |
|`card_expected_name`  |Err. if name not found among container_name's or card_name's  |New in 1.0.0  |
|`card_unique_id`  |Assigned to all cards when created, can be overwritten here - mostly for debug purpus, but may be used in a custom template.<br />Defaults to an uuid4 value, such as "cfd3143b-4f78-4c55-b1a9-3e5719bde236"  |New in 1.0.0 |
|`card_note`  |can contain html, use for \<b\>, \<i\>, \<a\> etc. Pull status images from your container?? |New in 1.0.0<br />Was `description`  |
|`card_url`  |The link to goto when a card is clicked.  |New in 1.0.0<br />Was `url`  |
|`card_icon`  | Font Awesom icon |New in 1.0.0<br />Was `icon`  |
|`card_image`	  | Image in formats understood by browsers |New in 1.0.0<br />Was `icon`  |
|`section_footer`  |can contain html, use for \<b\>, \<i\> etc.  |New in 1.0.0  |
|`section_footer_icon`  |Font Awesom icon  |New in 1.0.0  |
|`section_footer_body`  |can contain html, use for \<b\>, \<i\>, etc.	(note 1)  |New in 1.0.0 |
|`site_footer_text`  |can contain html, use for \<b\>, \<i\>, etc.  |New in 1.0.0<br />Was `footer`  |
|`template_debug`  | if set to any value, will create a variable dump in the html source code (Useview page source) |New in 1.0.0 |

Note:
1: All labels ending with _body can, if the section is specified, use a slight hack to specify multiple lines.
This example will create a single  `section_header_body` in the section called **Info**, where the labels will be joined in alpha-sorted order. Do note that these labels does not need to originate from the same container!

        - "CargoDeck.Info.4.section_header_body=This will become line 4.<br>"
        - "CargoDeck.Info.2.section_header_body=This will become line 2.<br>"
        - "CargoDeck.Info.1.section_header_body=This will become line 1.<br>"
        - "CargoDeck.Info.3.section_header_body=This will become line 3.<br>"

## Configuration of the CargoDesk:  Environmental variables
There are a few Environmental variables that affects the operation of CargoDeck:

| Variable | Description |
|--|--|
|`LOGLEVEL` | Defaults to `INFO`.<br /> Options are:<br />1. `DEBUG`: Detailed information,typically of interest only when diagnosing problems.<br />2.  `INFO`: Confirmation that things are working as expected.<br />3.  `WARNING`: An indication that something unexpected happened, or there may be some problem in the near future (e.g. 'disk space low'). The software is still working as expected.<br />4.  `ERROR`: Due to a more serious problem, the software has not been able to perform some function.<br />5.  `CRITICAL`: A very serious error, indicating that the program itself may be unable to continue running.  |
|`PORT` | Specifies the port to be used for the first instance of CargoDesk. Defaults to 80|
|`INSTANCES` |If set to `MULTI`, CargoDesk will spawn as many instances as are defined by the `PORTn` variables. |
|`PORTn` | Where n is from 1 to how many instances you want to create. `PORT` and `PORT1` are the same, but Must be numbered consecutive.|
|`MATCH` |This defaults to the container_name - which defaults to CargoDesk.|
|`MATCHn` |Where n is from 1 to how many instances you want. Defaults to the container_name - which defaults to CargoDesk.  |
|`WORKERS` |Defines how many workers will be assigned to each instance of CargoDesk. Defaults to 1. Max is clamped at 10. |


## Understanding Multiple Workers and Instances

The concepts of *instances* and *workers* are closely interconnected, both resulting in the creation of new processes for running the CargoDesk Application. However, they differ in their functionality. *Instances* represent separate applications running on different port numbers and matching different labels, whereas *workers* collaborate to serve a single application on a single port.

For example, a configuration with a single instance and three workers results in three active processes. In contrast, a configuration of three instances each with three workers generates nine active processes.

Keep in mind that each worker process utilizes system resources, primarily memory. Consequently, while augmenting the worker count can enhance the server's capacity to handle concurrent requests, it also escalates the server's memory usage. Striking an optimal balance tailored to your application's requirements and available resources is crucial.

## The Role of Multiple Workers

The number of worker processes for Gunicorn to spawn per instance is determined by the `WORKERS` environmental variable. Each worker is tasked with handling HTTP requests from clients. Adjusting the number of workers can fine-tune the server's load management capability, thereby improving application performance.

## The Functionality of Multiple Instances

The `INSTANCES` environmental variable, along with `PORTn` and `MATCHn`, determines the number of distinct applications to be initiated, and the labels they serve. Essentially, this is akin to launching a new container independently. This feature is primarily designed for smaller systems like home labs or small workplaces, allowing for enhanced flexibility and utility. It's also an excellent opputinity to hide away some applications on a seperate instance, like my Admin example.

## Reverse Proxy considerations
Many times throughout this text, I've recomended the use of reverse proxying. Personally I prefer Traefik, as it allows me the flexibility to configure almost everything using Docker labels. In fact, Traefik's ability to use Docker labels was the main inspiration for me to create CargoDeck.
In the [docker-compose.yml](https://github.com/f-steff/CargoDeck/blob/main/docker-compose.yml) file thats available on the Github reprository, I've left in the few Traefik configuration labels which I use to configure traefik. They basically only perform these actions: enable the container to use Traefik, setup the docker network and associate a hostname to a Docker port.

For me, Traefik is perfect, but the choise is yours. 

The main reasons I reccommend a Reverse proxy are:
* Simplified configuration: Setting up is resonable straightforward, with minimal adjustments required once it's set up.
* User-friendliness: The system supports hostnames, bypassing the need to remember complex combinations of hostnames and port numbers.
* Enhanced security: The architecture helps protect your backend servers by hiding their details, improving overall security.
* Auto-redirection: It takes care of redirecting HTTP traffic to HTTPS, thereby ensuring secure communications.
* Centralized certificate management: All your site certificates are consolidated and managed from one place, making maintenance easier.

## Todo
* Add separate `section_navigation_icon`, instead of relying on `section_header_icon`. Optionally use images, too.
* If people are really using the Font Awesome option, add environmental variables to configure the subscription plan. Please let me know.
* Add environmental variables similar to `PORTn` to, on an instance basis, to specify the html template to use and  set the number of workers.
* Add custom error files, such as handeling 404 errors, also configureable by labels.
* Improve the css - I'm at my limits here, but I hope theres a css magican in the community..

## Future
This has now gone beyond the PoC that I hacked together over the span of two nights, and is now a very usefull tool that I have set up both in my home lab and internally at my work, too. I'm sure it will meet the needs of many others.

While I've tried to test everything, I'm sure there are still bugs. I'll try fix the issues as I encounter them, but will appriciate freedback from the community, both in regards to bugs but also improvements and feature requests.

## Contributing
Contributions from the community are very welcome. The UI part in particular needs work!
Please get in touch.

## Acknowledgements
- For the dashboard idea and UI, I was inspired by Homer, https://hub.docker.com/r/b4bz/homer
- For the use of labels to configure services, I was inspired by Traefik, https://traefik.io/traefik/
- A big "Thank you" to everyone who provided good online documentation for anything related to Docker, Flask, Gunicorn, and Gevent that I've been relying on to create this tool.
- An even bigger "Thank you" to the creators of Docker, Flask, Gunicorn, Gevent, and Font Awesom, as well as all the other tools that makes this possible.
- 
## Versions
* 2023-08-06 - Version 1.0.0. After several more evenings of work, a very updated version sees the light.
* 2023-07-22 - Version 0.1 was the result of several evenings work, trying to code something better than what I could find. It was introdused to the world in r/selfhosted, but only as an image on Docker Hub.

## License
This project is licensed under the MIT License - see the `LICENSE` file for details.

